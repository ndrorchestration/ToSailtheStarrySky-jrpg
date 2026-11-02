#!/usr/bin/env python3
"""Reversible original-vs-variant wing/root-support contact study at Skyborne t0.

SOURCE QA ONLY. This compares the original V2 brass support tubes with
an independently SHA-pinned experimental tube recipe. It never accepts the
variant as production art or claims that a shortened/lowered tube still connects.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import audit_aureate_wing_clearance as wing_audit
from audit_aureate_v2_crosslane_envelope import (
    EXPECTED_WING_GLB_SHA, EXPECTED_WING_SOURCE_HEAD,
    EXPECTED_V2_SOURCE_HEAD, require_exact_v2_artifacts, V2ReviewHold,
)
from aureate_indexed_triangles import read_triangles
from aureate_triangle_narrowphase import nearest_surface
from audit_aureate_root_support_routes import (
    source_sections, form_routes, screen_category, transform_vertices_np,
    THRESHOLD_CM as ROOT_SCREEN_THRESHOLD,
)
from prepare_aureate_v2_support_variant import (
    EXPERIMENTAL_SUPPORT_RECIPE, BASE_SUPPORT_RECIPE,
    BASE_SOURCE_SHA, BASELINE_HULL_SHA, BASELINE_BRIDGE_SHA,
    HULL_FILE, BRIDGE_FILE,
)

FROZEN_CANDIDATE_HULL_SHA = "3e57722d962ecc834c292748673c37c6d372a6fbf2f3fe50d18b0b80180c23dd"
HULL_SUPPORT_START = 240
HULL_SUPPORT_END = 368
THRESHOLD_CM = 10.0


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_candidate(receipt_file: Path, candidate_dir: Path, baseline_dir: Path):
    report=json.loads(receipt_file.read_text(encoding="utf-8"))
    if (report.get("authority") != "NONCANONICAL_ROOT_SUPPORT_DIAGNOSTIC_DO_NOT_IMPORT_AS_ART" or
        report.get("base_v2_source_head") != EXPECTED_V2_SOURCE_HEAD or
        report.get("base_source_shas") != BASE_SOURCE_SHA or
        report.get("original_support_recipe") != BASE_SUPPORT_RECIPE or
        report.get("experiment_support_recipe") != EXPERIMENTAL_SUPPORT_RECIPE or
        report.get("approval") != "NOT_GRANTED" or
        report.get("orbiter_authorized") is not False or
        report.get("structural_mount_integrity") != "UNVERIFIED"):
        raise V2ReviewHold("Candidate recipe approval/provenance mismatch")
    if (report.get("original_mesh_sha256") !=
        {"hull":BASELINE_HULL_SHA, "bridge":BASELINE_BRIDGE_SHA} or
        report.get("candidate_mesh_sha256") !=
        {"hull":FROZEN_CANDIDATE_HULL_SHA, "bridge":BASELINE_BRIDGE_SHA}):
        raise V2ReviewHold("Changed candidate recipe/model SHA: HOLD")
    for folder, hull_expected in ((baseline_dir,BASELINE_HULL_SHA),
                                  (candidate_dir,FROZEN_CANDIDATE_HULL_SHA)):
        if sha(folder/HULL_FILE) != hull_expected or sha(folder/BRIDGE_FILE) != BASELINE_BRIDGE_SHA:
            raise V2ReviewHold("Candidate or baseline bytes not source-bound")
    return report


def screen_at_endpoint(wing, wing_faces, original, candidate, hull_faces):
    parts=source_sections(wing_faces,hull_faces)
    tube_faces=hull_faces[HULL_SUPPORT_START:HULL_SUPPORT_END]
    body_orig=[tuple(x) for x in original]
    body_cand=[tuple(x) for x in candidate]
    rows=[]
    for wing_index in range(4):
        xyz,quat,sc=wing_audit.blend(wing_audit.pose("Skyborne",wing_index),
                                    wing_audit.pose("Seaborne",wing_index),0.)
        world=[]
        for p in wing:
            q=wing_audit.qrot(quat,tuple(p[i]*sc[i] for i in range(3)))
            world.append(tuple(q[i]+xyz[i] for i in range(3)))
        one={"wing_index":wing_index}
        for section in ("hinge","venation"):
            for label,body in (("baseline",body_orig),("candidate",body_cand)):
                result=nearest_surface(world,parts[section],body,tube_faces,
                                       threshold_cm=THRESHOLD_CM)
                one[section+"_"+label]={
                    "candidate_minimum_cm":result["min_surface_cm_among_aabb_candidates"],
                    "under_10cm":result["below_threshold"],
                    "exact_triangle_pairs":result["triangle_pairs_narrow_phase_checked"]}
        rows.append(one)
    return rows


def run(args):
    if (args.wing_source_head != EXPECTED_WING_SOURCE_HEAD or
        args.v2_source_head != EXPECTED_V2_SOURCE_HEAD or
        sha(args.wing_glb) != EXPECTED_WING_GLB_SHA):
        raise V2ReviewHold("Source/wing GLB provenance changed")
    wing_audit.assert_source_contract(
        args.cpp.read_text(encoding="utf-8"),
        args.header.read_text(encoding="utf-8"))
    require_exact_v2_artifacts(
        args.baseline_dir/"AureateWake_FidelityV2_Manifest.json",
        args.baseline_dir/HULL_FILE,args.baseline_dir/BRIDGE_FILE)
    verify_candidate(args.recipe_receipt,args.candidate_dir,args.baseline_dir)
    wp,_=wing_audit.read_vertices(args.wing_glb)
    original,oc=wing_audit.read_vertices(args.baseline_dir/HULL_FILE)
    candidate,cc=wing_audit.read_vertices(args.candidate_dir/HULL_FILE)
    wf=read_triangles(args.wing_glb)
    original_faces=read_triangles(args.baseline_dir/HULL_FILE)
    candidate_faces=read_triangles(args.candidate_dir/HULL_FILE)
    if original_faces!=candidate_faces or oc!=cc:
        raise V2ReviewHold("Candidate changed index topology or primitive position counts")
    rows=screen_at_endpoint(wp,wf,original,candidate,original_faces)
    return {
        "authority":"NONCANONICAL_SKYBORNE_T0_SUPPORT_VARIANT_COMPARISON_ONLY",
        "wing_sha256":EXPECTED_WING_GLB_SHA,
        "original_hull_sha256":BASELINE_HULL_SHA,
        "candidate_hull_sha256":FROZEN_CANDIDATE_HULL_SHA,
        "threshold_cm":THRESHOLD_CM,
        "four_wing_endpoint_results":rows,
        "status":"HOLD_MOUNT_CONNECTIVITY_AND_FULL_ROUTE_COLLISION_NOT_VERIFIED",
        "meaning":"Larger gaps could be caused by severing intended supports; not approval",
        "not_verified":[
            "Full V2 hull, bridge or all ordinary transitions on candidate",
            "Actual fastener/hinge structural continuity or cinematic art",
            "Native Unreal model import, D3D12 capture or continuous swept collision",
            "Approved creator art or Orbiter authorization"]
    }


def read_verified_json_receipt(path: Path):
    """Read only normal UTF-8 or PowerShell BOM-marked UTF-16 LE receipts.

    Encoding compatibility never bypasses the immutable SHA/source/count
    validation that follows. Reject undecorated UTF-16 and unknown encodings.
    """
    blob=path.read_bytes()
    if blob.startswith(bytes((255,254))):
        decoded=blob.decode("utf-16")
    elif blob.startswith(bytes((239,187,191))):
        decoded=blob.decode("utf-8-sig")
    else:
        decoded=blob.decode("utf-8")
    result=json.loads(decoded)
    if not isinstance(result,dict):
        raise V2ReviewHold("Expected JSON object source receipt")
    return result


def compare_full_route(args, wing_positions, wing_faces, candidate_vertices,
                       hull_faces, candidate_hull_sha):
    """Candidate full-route test; baseline provenance and counts independently verified.

    Return category totals for sampled wing-times, NOT min distances or CCD.
    This does not approve the variant even when count decreases to zero.
    """
    try:
        import numpy as np
    except ImportError as exc:
        raise V2ReviewHold("NumPy required for real full-route candidate test") from exc
    baseline=read_verified_json_receipt(args.baseline_route_receipt)
    if (baseline.get("sha256",{}).get("wing") != EXPECTED_WING_GLB_SHA or
        baseline.get("sha256",{}).get("hull") != BASELINE_HULL_SHA or
        baseline.get("all_route_samples_completed") is not True or
        baseline.get("total_venation_under_10cm_wing_samples") != 164 or
        baseline.get("total_hinge_under_10cm_wing_samples") != 256 or
        baseline.get("sampling",{}).get("total_route_samples") != 126 or
        baseline.get("wing_actor_source_head") != EXPECTED_WING_SOURCE_HEAD or
        baseline.get("v2_hull_source_head") != EXPECTED_V2_SOURCE_HEAD or
        baseline.get("root_support_screen_status") != "NEAR_SUPPORT_SURFACE_HOLD"):
        raise V2ReviewHold("Original V2 126-pose receipt/source totals changed: HOLD")
    parts=source_sections(wing_faces,hull_faces)
    np_hull=np.asarray(candidate_vertices,dtype=np.float64)
    tubes=[np_hull[np.asarray(hull_faces[240+32*i:240+32*(i+1)],
                               dtype=np.int64)] for i in range(4)]
    wp=np.asarray(wing_positions,dtype=np.float64)
    by_route=[]
    group_key=None
    for src,dst,index,t in form_routes(steps=20):
        key=(src,dst)
        if key!=group_key:
            by_route.append({"from":src,"to":dst,
                             "pose_samples":0,
                             "venation_under_10cm_wing_samples":0,
                             "hinge_under_10cm_wing_samples":0,
                             "first_venation_witness":None,
                             "first_hinge_witness":None})
            group_key=key
        route=by_route[-1]
        route["pose_samples"]+=1
        for wing_index in range(4):
            tr=wing_audit.blend(wing_audit.pose(src,wing_index),
                                wing_audit.pose(dst,wing_index),t)
            world=transform_vertices_np(wp,tr,np)
            for section in ("venation","hinge"):
                outcome=screen_category(world,parts[section],tubes,np,
                                        ROOT_SCREEN_THRESHOLD)
                if outcome["under_threshold"]:
                    route[section+"_under_10cm_wing_samples"]+=1
                    key="first_"+section+"_witness"
                    if route[key] is None:
                        route[key]={"wing_index":wing_index,
                                    "sample_index":index,
                                    "time_fraction":round(t,6),
                                    **outcome}
    ven=sum(r["venation_under_10cm_wing_samples"] for r in by_route)
    hinge=sum(r["hinge_under_10cm_wing_samples"] for r in by_route)
    if len(by_route)!=6 or any(r["pose_samples"]!=21 for r in by_route):
        raise V2ReviewHold("Not all 126 candidate route configurations completed")
    return {
        "authority":"TRIAL_HULL_126_POSE_TARGETED_SUPPORT_TRIANGLES_ONLY",
        "candidate_hull_sha256":candidate_hull_sha,
        "baseline_hull_sha256":BASELINE_HULL_SHA,
        "baseline_observation_counts":{
            "venation":164,"hinge":256},
        "candidate_observation_counts":{
            "venation":ven,"hinge":hinge},
        "route_breakdown":by_route,
        "wing_time_observations":504,
        "review_status":"HOLD_EXPERIMENT_NOT_STRUCTURALLY_OR_ARTISTICALLY_ACCEPTED",
        "limits":"No full hull/bridge, swept collision or approved attachment; first witnesses are not minima",
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wing-glb",required=True,type=Path)
    parser.add_argument("--baseline-dir",required=True,type=Path)
    parser.add_argument("--candidate-dir",required=True,type=Path)
    parser.add_argument("--recipe-receipt",required=True,type=Path)
    parser.add_argument("--cpp",required=True,type=Path)
    parser.add_argument("--header",required=True,type=Path)
    parser.add_argument("--wing-source-head",required=True)
    parser.add_argument("--v2-source-head",required=True)
    parser.add_argument("--baseline-route-receipt",type=Path,
                        help="Full 126-pose parent source-bound receipt for comparison")
    args=parser.parse_args()
    try:
        data=run(args)
        if args.baseline_route_receipt is not None:
            verified_candidate=verify_candidate(
                args.recipe_receipt,args.candidate_dir,args.baseline_dir)
            wing,_=wing_audit.read_vertices(args.wing_glb)
            candidate,_=wing_audit.read_vertices(args.candidate_dir/HULL_FILE)
            faces=read_triangles(args.wing_glb)
            hull_faces=read_triangles(args.candidate_dir/HULL_FILE)
            data["full_route_targeted_support_comparison"]=compare_full_route(
                args,wing,faces,candidate,hull_faces,
                verified_candidate["candidate_mesh_sha256"]["hull"])
            data["not_verified"]=[
                "Complete V2 hull, glass bridge, wing-to-wing clearance and full mesh interactions",
                "Continuous swept motion between the 126 support-only sample configurations",
                "Fastener/hinge structural continuity and visual geometry quality",
                "Native Unreal import, assembled D3D12 captures, creator art approval and Orbiter"]

    except (V2ReviewHold,wing_audit.GeometryHold,ValueError,OSError,KeyError,TypeError) as exc:
        parser.exit(3,"CANDIDATE_INPUT_HOLD: "+str(exc)+"\n")
    print(json.dumps(data,sort_keys=True,indent=2))
    return 2


if __name__=="__main__":
    raise SystemExit(main())
