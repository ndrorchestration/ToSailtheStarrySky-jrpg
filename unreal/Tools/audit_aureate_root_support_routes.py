#!/usr/bin/env python3
"""V2 wing root/hull brass support *targeted* full-route surface-contact screen.

REVIEW ONLY. Tests two specific source-defined interfaces (wing hinge and
venation vs four brass tubes), across 126 discrete ordinary-form poses.
NOT clearance for the other V2 hull facets, bridge, supports, or swept time.
Uses installed NumPy only for conservative broad-phase acceleration, and the
independent standard-library exact triangle-triangle distance for candidates.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import audit_aureate_wing_clearance as wing_audit
from audit_aureate_v2_crosslane_envelope import (
    EXPECTED_WING_SOURCE_HEAD, EXPECTED_WING_GLB_SHA,
    EXPECTED_V2_SOURCE_HEAD, require_exact_v2_artifacts, V2ReviewHold,
)
from aureate_indexed_triangles import read_triangles
from aureate_triangle_narrowphase import triangle_triangle_sq
from import_aureate_wing_review import preflight as verify_wing_manifest

FORMS = ("Skyborne", "Seaborne", "Submersible")
# Derived from the SHA-pinned deterministic GLB primitive topology.
WING_MEMBRANE_END = 580
WING_VENATION_END = 29280
WING_HINGE_END = 29424
HULL_SUPPORT_START = 240
SUPPORT_TRIANGLES_PER_TUBE = 32
HULL_SUPPORT_END = 368
THRESHOLD_CM = 10.0


def form_routes(steps=20):
    """All directed ordinary forms, 21 exact sampled times per route by default."""
    if type(steps) is not int or steps < 20 or steps > 100:
        raise V2ReviewHold("Require 20 to 100 finite sampling intervals")
    return [(src, dst, i, i / steps)
            for src, dst in itertools.permutations(FORMS, 2)
            for i in range(steps + 1)]


def source_sections(wing_faces, hull_faces):
    if len(wing_faces) != WING_HINGE_END or len(hull_faces) != 1950:
        raise V2ReviewHold("Frozen triangle topology changed: refuse index-range aliases")
    if HULL_SUPPORT_START + SUPPORT_TRIANGLES_PER_TUBE * 4 != HULL_SUPPORT_END:
        raise V2ReviewHold("Invalid tube topology")
    return {
        "venation": wing_faces[WING_MEMBRANE_END:WING_VENATION_END],
        "hinge": wing_faces[WING_VENATION_END:WING_HINGE_END],
        "tubes": [hull_faces[HULL_SUPPORT_START + i*SUPPORT_TRIANGLES_PER_TUBE:
                             HULL_SUPPORT_START + (i+1)*SUPPORT_TRIANGLES_PER_TUBE]
                  for i in range(4)],
    }


def transform_vertices_np(vertices, transform, np):
    xyz, quat, scale=transform
    s=vertices * np.asarray(scale, dtype=np.float64)
    qv=np.asarray(quat[1:], dtype=np.float64)
    uv=np.cross(qv,s)
    uuv=np.cross(qv,uv)
    return s+2*(quat[0]*uv+uuv)+np.asarray(xyz,dtype=np.float64)


def nearby_triangle_pairs_np(wing_tri, tube_tri, cutoff_cm, np):
    """AABB-expanded candidate pairs, exact threshold must be checked later."""
    low=tube_tri.min(axis=(0,1))-cutoff_cm
    high=tube_tri.max(axis=(0,1))+cutoff_cm
    wlo=wing_tri.min(axis=1)
    whi=wing_tri.max(axis=1)
    coarse=np.nonzero(np.all((whi>=low)&(wlo<=high),axis=1))[0]
    if not len(coarse):
        return [], 0
    hlow=tube_tri.min(axis=1)
    hhigh=tube_tri.max(axis=1)
    sublo=wlo[coarse]
    subhi=whi[coarse]
    gap=np.maximum(np.maximum(sublo[:,None,:]-hhigh[None,:,:],
                              hlow[None,:,:]-subhi[:,None,:]),0)
    indices=np.argwhere(np.sum(gap*gap,axis=2) <= cutoff_cm*cutoff_cm)
    return ((int(coarse[i]),int(j)) for i,j in indices), int(len(indices))


def screen_category(world, wing_faces, tube_triangles, np, threshold_cm=THRESHOLD_CM):
    """One wing pose vs all four support tubes, fail-closed at first near surface.

    Returns a witness and the number of exact triangle comparisons performed.
    This is NOT the minimum distance across all 4 tubes or all times if stopped.
    """
    if threshold_cm <= 0: raise V2ReviewHold("Nonpositive exclusion distance")
    faces=np.asarray(wing_faces,dtype=np.int64)
    wing_tri=world[faces]
    tests=0
    broadphase_candidates=0
    for tube_index,tube_tri in enumerate(tube_triangles):
        pairs, candidates=nearby_triangle_pairs_np(wing_tri,tube_tri,threshold_cm,np)
        broadphase_candidates+=candidates
        for wi,bi in pairs:
            a=tuple(tuple(float(x) for x in p) for p in wing_tri[wi])
            b=tuple(tuple(float(x) for x in p) for p in tube_tri[bi])
            d2=triangle_triangle_sq(a,b)
            tests+=1
            if d2 < threshold_cm*threshold_cm:
                return {"under_threshold":True,
                        "first_witness_distance_cm":round(math.sqrt(max(0.,d2)),6),
                        "support_tube_index":tube_index,
                        "wing_category_triangle_index":wi,
                        "hull_support_triangle_index":HULL_SUPPORT_START+
                              tube_index*SUPPORT_TRIANGLES_PER_TUBE+bi,
                        "tested_exact_triangle_pairs":tests,
                        "broadphase_candidate_pairs":broadphase_candidates,
                        "distance_interpretation":"FIRST_WITNESS_NOT_GLOBAL_MINIMUM"}
    return {"under_threshold":False,
            "first_witness_distance_cm":None,
            "support_tube_index":None,
            "tested_exact_triangle_pairs":tests,
            "broadphase_candidate_pairs":broadphase_candidates}


def run_source_bound(args, np):
    if args.wing_source_head != EXPECTED_WING_SOURCE_HEAD:
        raise V2ReviewHold("Unexpected wing C++ actor source head")
    if args.v2_source_head != EXPECTED_V2_SOURCE_HEAD:
        raise V2ReviewHold("Unexpected V2 model source head")
    if hashlib.sha256(args.wing_glb.read_bytes()).hexdigest() != EXPECTED_WING_GLB_SHA:
        raise V2ReviewHold("Unexpected full-wing review GLB bytes")
    verify_wing_manifest(args.wing_glb,args.wing_manifest)
    require_exact_v2_artifacts(args.v2_manifest,args.hull_glb,args.bridge_glb)
    wing_audit.assert_source_contract(args.cpp.read_text(encoding="utf-8"),
                                      args.header.read_text(encoding="utf-8"))
    wing,wing_counts=wing_audit.read_vertices(args.wing_glb)
    hull,hull_counts=wing_audit.read_vertices(args.hull_glb)
    wing_faces=read_triangles(args.wing_glb)
    hull_faces=read_triangles(args.hull_glb)
    sections=source_sections(wing_faces,hull_faces)
    wing_np=np.asarray(wing,dtype=np.float64)
    hull_np=np.asarray(hull,dtype=np.float64)
    tubes=[hull_np[np.asarray(face,dtype=np.int64)]
           for face in sections["tubes"]]
    report={"authority":"NONCANONICAL_REVIEW_TARGETED_ROOT_SUPPORT_TRIANGLE_SCREEN",
            "wing_actor_source_head":args.wing_source_head,
            "v2_hull_source_head":args.v2_source_head,
            "sha256":{
                "wing":EXPECTED_WING_GLB_SHA,
                "hull":hashlib.sha256(args.hull_glb.read_bytes()).hexdigest(),
            },
            "position_counts":{"wing":wing_counts,"hull":hull_counts},
            "sampling":{"directed_routes":6,"samples_per_route":args.steps+1,
                        "total_route_samples":6*(args.steps+1),
                        "wing_instances_per_sample":4,
                        "sample_classification":"DISCRETE_NOT_SWEPT"},
            "interfaces_checked":{
                "wing_venation_triangles":len(sections["venation"]),
                "wing_hinge_triangles":len(sections["hinge"]),
                "hull_brass_support_tubes":4,
                "triangles_per_support_tube":32,
                "threshold_cm":THRESHOLD_CM,
            },
            "routes":[],
            "limits":[
                "The ONLY hull portions screened are the first four brass wing-root support tubes",
                "All four tubes checked against each transformed wing, with no joint exemptions",
                "No full V2 hull, bridge or unrelated wing-pair narrow-phase is claimed",
                "Finite time samples do not prove swept collision safety",
                "Any near-support proximity is HOLD pending creator-approved attachment design",
                "Orbiter direct transitions remain forbidden and visual art remains review-only",
            ],
        }
    group_key=None
    for src,dst,index,t in form_routes(args.steps):
        key=(src,dst)
        if key != group_key:
            entry={"from":src,"to":dst,"pose_samples":0,
                   "venation_under_10cm_wing_samples":0,
                   "hinge_under_10cm_wing_samples":0,
                   "venation_first_witness":None,
                   "hinge_first_witness":None,
                   "total_exact_pairs_checked":0}
            report["routes"].append(entry)
            group_key=key
        entry["pose_samples"]+=1
        for wing_index in range(4):
            tr=wing_audit.blend(wing_audit.pose(src,wing_index),
                                wing_audit.pose(dst,wing_index),t)
            world=transform_vertices_np(wing_np,tr,np)
            for name in ("venation","hinge"):
                outcome=screen_category(world,sections[name],tubes,np)
                entry["total_exact_pairs_checked"]+=outcome["tested_exact_triangle_pairs"]
                if outcome["under_threshold"]:
                    entry[name+"_under_10cm_wing_samples"]+=1
                    if entry[name+"_first_witness"] is None:
                        entry[name+"_first_witness"]={
                            "wing_index":wing_index,
                            "time_fraction":round(t,6),
                            "sample_index":index,
                            **outcome,
                        }
    report["total_venation_under_10cm_wing_samples"]=sum(
        x["venation_under_10cm_wing_samples"] for x in report["routes"])
    report["total_hinge_under_10cm_wing_samples"]=sum(
        x["hinge_under_10cm_wing_samples"] for x in report["routes"])
    report["all_route_samples_completed"]=all(
        r["pose_samples"] == args.steps+1 for r in report["routes"])
    if not report["all_route_samples_completed"]:
        raise V2ReviewHold("Incomplete sampling: cannot issue route receipt")
    report["root_support_screen_status"] = (
        "NEAR_SUPPORT_SURFACE_HOLD"
        if (report["total_venation_under_10cm_wing_samples"] or
            report["total_hinge_under_10cm_wing_samples"])
        else "NO_NEAR_SUPPORT_FOUND_NOT_FULL_CLEARANCE")
    report["status"]="HOLD_V2_ASSEMBLY_NOT_CONTINUOUSLY_VERIFIED"
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("wing_glb","wing_manifest","hull_glb","bridge_glb",
                 "v2_manifest","cpp","header"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    p.add_argument("--wing-source-head",required=True)
    p.add_argument("--v2-source-head",required=True)
    p.add_argument("--steps",type=int,default=20)
    args=p.parse_args()
    try:
        import numpy as np
        report=run_source_bound(args,np)
    except (ImportError,V2ReviewHold,wing_audit.GeometryHold,ValueError,
            KeyError,IndexError,OSError,TypeError) as exc:
        p.exit(3,"ROOT_SUPPORT_INPUT_HOLD: "+str(exc)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    return 2  # This *targeted* QA cannot authorize full V2 hull clearance.


if __name__=="__main__":
    raise SystemExit(main())
