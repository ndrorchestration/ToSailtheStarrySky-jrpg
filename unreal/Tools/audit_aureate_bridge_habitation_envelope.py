#!/usr/bin/env python3
"""NONCANONICAL sampled bridge+quarters envelope versus authored four-wing mesh.

Reads the complete reviewed wing GLB. Screens every triangle's conservative
AABB in the rotating habitation module's local frame at 126 ordinary-form
discrete samples; uses TEST-ONLY yaw 0/30/75 from native preview tests.
No CCD, real V2 hull/body, crew passage or approved rotation is established.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import audit_aureate_wing_clearance as wing_audit
from audit_aureate_root_support_routes import form_routes,transform_vertices_np
from aureate_indexed_triangles import read_triangles
from import_aureate_wing_review import preflight as verify_wing_manifest

# Frozen SHA of the *unapproved* review wing, not the finished art.
EXPECTED_WING_SHA256 = "04d7f9461b4cb4475ea98d5e3f7699b68f272f5646362ad7aef0d222ad92ec73"
TEST_ONLY_YAW_DEGREES = {"Skyborne": 0., "Seaborne": 30., "Submersible": 75.}
PIVOT_CM = (0.,0.,50.)
# Engine BasicShapes/Cube is 100cm; Unreal preview mesh scales are noncanonical.
COMPONENT_BOXES_CM = {
    "ForwardBridge_PROXY": {"local_center": (0.,0.,80.),"half_extents":(105.,55.,55.)},
    "LivingQuarters_PROXY": {"local_center":(0.,0.,-25.),"half_extents":(110.,57.5,17.5)},
}
MIN_REVIEW_DISTANCE_CM = 10.0
PROVENANCE = "CONSERVATIVE_SAMPLED_TRIANGLE_AABB_ENVELOPE_NOT_MESH_COLLISION_OR_CCD"


class EnvelopeHold(ValueError):
    pass


def require_actor_source(cpp, header, native_test):
    required_cpp=(
        "BridgeHabitationPivot->SetRelativeLocation(FVector(0, 0, 50));",
        "ForwardBridge->SetRelativeLocation(FVector(0, 0, 80));",
        "LivingQuartersEnvelope->SetRelativeLocation(FVector(0, 0, -25));",
        "ForwardBridge->SetRelativeScale3D(FVector(2.1, 1.1, 1.1));",
        "LivingQuartersEnvelope->SetRelativeScale3D(FVector(2.2, 1.15, .35));",
        "bHabitationReviewLatchedForTransition = bPreviewCentralBridgeHabitation;",
        "if (bHabitationReviewLatchedForTransition && BridgeHabitationPivot)",
        "LivingQuartersEnvelope->SetupAttachment(BridgeHabitationPivot);",
        "ForwardBridge->SetupAttachment(BridgeHabitationPivot);",
    )
    required_header=(
        "bool bPreviewCentralBridgeHabitation = false;",
        "FRotator SkyborneHabitationReviewRotation = FRotator::ZeroRotator;",
        "FRotator SeaborneHabitationReviewRotation = FRotator::ZeroRotator;",
        "FRotator SubmersibleHabitationReviewRotation = FRotator::ZeroRotator;",
    )
    required_native=(
        "Ship->SeaborneHabitationReviewRotation = FRotator(0.f, 30.f, 0.f);",
        "Ship->SubmersibleHabitationReviewRotation = FRotator(0.f, 75.f, 0.f);",
        "TSTSS.Ship.CentralBridgeHabitationReview",
    )
    for tokens,blob,label in ((required_cpp,cpp,"C++ actor"),
                              (required_header,header,"C++ declaration"),
                              (required_native,native_test,"native QA fixture")):
        if any(t not in blob for t in tokens):
            raise EnvelopeHold("Review module geometry/angle source drift: "+label)
    wing_audit.assert_source_contract(cpp,header)


def conservative_box_triangle_candidates(local_vertices, faces, half_extents, np):
    """Count triangles whose *bounding boxes* are within margin of review cube."""
    tris=local_vertices[faces]
    lowest=tris.min(axis=1)
    highest=tris.max(axis=1)
    half=np.asarray(half_extents,dtype=np.float64)
    separation=np.maximum(np.maximum(lowest-half, -half-highest),0.)
    lower_bound=np.sqrt(np.sum(separation*separation,axis=1))
    return int(np.count_nonzero(lower_bound <= MIN_REVIEW_DISTANCE_CM)),float(lower_bound.min())


def to_coupled_local(world, yaw_degrees, center, np):
    """Inverse of pivot + yaw, then subtract child offset, in Unreal centimeters."""
    theta=math.radians(yaw_degrees)
    c,s=math.cos(theta),math.sin(theta)
    shifted=world - np.asarray(PIVOT_CM,dtype=np.float64)
    result=np.empty_like(shifted)
    result[:,0]=shifted[:,0]*c+shifted[:,1]*s
    result[:,1]=-shifted[:,0]*s+shifted[:,1]*c
    result[:,2]=shifted[:,2]
    return result-np.asarray(center,dtype=np.float64)


def run(args, np):
    if args.steps != 20:
        raise EnvelopeHold("Only the 126-pose 20-interval baseline is currently source-bound")
    if hashlib.sha256(args.wing_glb.read_bytes()).hexdigest()!=EXPECTED_WING_SHA256:
        raise EnvelopeHold("Review wing SHA mismatch; do not inherit old envelope screen")
    verify_wing_manifest(args.wing_glb,args.wing_manifest)
    require_actor_source(
        args.cpp.read_text(encoding="utf-8"),
        args.header.read_text(encoding="utf-8"),
        args.native_test.read_text(encoding="utf-8"))
    verts,section_counts=wing_audit.read_vertices(args.wing_glb)
    faces=read_triangles(args.wing_glb)
    if section_counts!=[292,14770,78] or len(faces)!=29424:
        raise EnvelopeHold("Full source-bound wing vertex/triangle count changed")
    vertex_array=np.asarray(verts,dtype=np.float64)
    indices=np.asarray(faces,dtype=np.int64)
    report={"authority":PROVENANCE,
        "wing_glb_sha256":EXPECTED_WING_SHA256,
        "source_revision":args.actor_source_head,
        "angles_test_only_degrees":TEST_ONLY_YAW_DEGREES,
        "pivot_cm":PIVOT_CM,
        "boxes_cm":COMPONENT_BOXES_CM,
        "review_distance_cm":MIN_REVIEW_DISTANCE_CM,
        "sample_count":126,
        "wing_time_observations":504,
        "routes":[],
        "status":"HOLD_MISSING_CONTINUOUS_SWEPT_AND_NATIVE_RENDER_PROOF",
        "limits":[
            "Editor BasicShapes proxy boxes are NOT the V2 geodesic bridge and quarters meshes",
            "Triangle-AABB broad phase can flag proximity where triangles are actually farther away",
            "Test yaw angles are native fixture DEMO values; creator has not approved any angles",
            "This is sampled time only; no continuous collision or pressure/access/crew safety claim",
            "The new module may overlap the real V2 hull intentionally; this test does NOT assess that",
            "Starbourne/Orbiter remains locked; no canonical art or game mode changes",
        ]}
    prev=None
    for src,dst,index,t in form_routes(args.steps):
        pair=(src,dst)
        if pair!=prev:
            row={"from":src,"to":dst,"samples":0,
                 "ForwardBridge_PROXY":{"wing_time_candidates":0,"first_witness":None},
                 "LivingQuarters_PROXY":{"wing_time_candidates":0,"first_witness":None}}
            report["routes"].append(row)
            prev=pair
        row["samples"]+=1
        eased=t*t*(3.-2.*t)
        yaw=TEST_ONLY_YAW_DEGREES[src]+(TEST_ONLY_YAW_DEGREES[dst]-
                                       TEST_ONLY_YAW_DEGREES[src])*eased
        for wing_index in range(4):
            pose=wing_audit.blend(wing_audit.pose(src,wing_index),
                                 wing_audit.pose(dst,wing_index),t)
            world=transform_vertices_np(vertex_array,pose,np)
            for name,box in COMPONENT_BOXES_CM.items():
                local=to_coupled_local(world,yaw,box["local_center"],np)
                candidates,closest_box_lower_bound=conservative_box_triangle_candidates(
                    local,indices,box["half_extents"],np)
                if candidates:
                    target=row[name]
                    target["wing_time_candidates"]+=1
                    if target["first_witness"] is None:
                        target["first_witness"]={
                            "wing_index":wing_index,
                            "sample_index":index,
                            "time_fraction":round(t,5),
                            "candidate_triangle_count":candidates,
                            "min_aabb_separation_lower_bound_cm":round(
                                closest_box_lower_bound,6),
                        }
    if len(report["routes"]) != 6 or any(r["samples"] != 21 for r in report["routes"]):
        raise EnvelopeHold("Incomplete 126-pose source test: fail closed")
    report["total_by_box"]={
        box:sum(r[box]["wing_time_candidates"] for r in report["routes"])
        for box in COMPONENT_BOXES_CM
    }
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("wing_glb","wing_manifest","cpp","header","native_test"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    p.add_argument("--actor-source-head",required=True)
    p.add_argument("--steps",type=int,default=20)
    args=p.parse_args()
    try:
        import numpy as np
        outcome=run(args,np)
    except (ImportError,EnvelopeHold,wing_audit.GeometryHold,ValueError,
            KeyError,IndexError,OSError,TypeError) as exc:
        p.exit(3,"BRIDGE_ENVELOPE_INPUT_HOLD: "+str(exc)+"\n")
    print(json.dumps(outcome,indent=2,sort_keys=True))
    return 2  # Conservative geometry study never authorizes V2 full assembly.


if __name__=="__main__":
    raise SystemExit(main())
