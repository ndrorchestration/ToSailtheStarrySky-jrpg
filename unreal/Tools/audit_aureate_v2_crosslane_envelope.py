#!/usr/bin/env python3
"""Conservative, source-bound cross-branch V2 hull / 4-wing clearance admission.

The V2 body lives in a DIFFERENT unmerged draft. This tool cannot approve
body meshes, Blender/Unreal rendering or collision. AABB overlap is a HOLD
for precise surface/structural review, not proof of a mesh intersection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import audit_aureate_wing_clearance as wing_audit
from import_aureate_wing_review import preflight as verify_wing_manifest
from aureate_indexed_triangles import read_triangles
from aureate_triangle_narrowphase import nearest_surface

STATUS_HOLD = "HOLD_V2_BROAD_PHASE_NEEDS_NARROW_PHASE"
STATUS_SCREEN = "BROAD_PHASE_SCREEN_ONLY_NOT_CONTINUOUS_CLEARANCE"
APPROVED_REFERENCE_SHA = "03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13"
EXPECTED_V2_SOURCE_HEAD = "cc58d518ca397158df27be366e4dc506a84497c9"
EXPECTED_WING_SOURCE_HEAD = "b43303e0afe2150d5a1956023194d9ee5abb4b2e"
EXPECTED_WING_GLB_SHA = "04d7f9461b4cb4475ea98d5e3f7699b68f272f5646362ad7aef0d222ad92ec73"
HULL_NAME = "AureateWake_WhiteGoldHull_V2_REVIEW.glb"
BRIDGE_NAME = "AureateWake_BlueGlassBridge_V2_REVIEW.glb"
EXPECTED_V2_GLB_HASHES = {
    HULL_NAME: "efed53b0b1847646d675bb2efe30dbb9af1aaeafb3cbf2e2ef314bb697cb2388",
    BRIDGE_NAME: "b9a5e43ad6759f4f06e1d3634c80c74616307d267de5f3330b04382cf9e822d1",
}
BRIDGE_TRANSLATION_CM = (240., 0., 95.)


class V2ReviewHold(ValueError):
    pass


def require_exact_v2_artifacts(manifest_path: Path, hull: Path, bridge: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise V2ReviewHold("Invalid V2 manifest object")
    if (manifest.get("status") != "NONCANONICAL_REVIEW_NOT_ART_ACCEPTED" or
        manifest.get("original_creator_approved_reference_sha256") != APPROVED_REFERENCE_SHA or
        manifest.get("source_to_gltf_scale") != 0.01 or
        manifest.get("axis_remap") != "UE_X_FORWARD_Z_UP_TO_GLTF_Y_UP" or
        manifest.get("orbiter_authorized") is not False or
        manifest.get("gameplay_modified") is not False or
        manifest.get("creator_3d_art_approval") != "NOT_GRANTED"):
        raise V2ReviewHold("V2 manifest provenance/authority changed: HOLD")
    hashes = manifest.get("sha256")
    if not isinstance(hashes, dict) or set(hashes) != {HULL_NAME, BRIDGE_NAME}:
        raise V2ReviewHold("V2 manifest names or SHA entries changed: HOLD")
    if hashes != EXPECTED_V2_GLB_HASHES:
        raise V2ReviewHold("V2 manifest differs from approved-review source hashes: HOLD")
    for path, name in ((hull, HULL_NAME), (bridge, BRIDGE_NAME)):
        if path.name != name:
            raise V2ReviewHold("Unexpected V2 candidate filename")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != hashes[name]:
            raise V2ReviewHold("V2 candidate SHA mismatch: " + name)
    return hashes


def extents(points, translation=(0., 0., 0.)):
    if not points:
        raise V2ReviewHold("Cannot screen an empty 3D asset")
    return tuple(tuple(
        (min if k == 0 else max)(p[i] for p in points) + translation[i]
        for i in range(3)) for k in range(2))


def evaluate(vertices, hull_box, bridge_box, *, steps=20):
    if steps < 20:
        raise V2ReviewHold("Require at least 20 intervals per directed form transition")
    with patch.object(wing_audit, "CUBE_HULL", hull_box), \
         patch.object(wing_audit, "CUBE_BRIDGE", bridge_box):
        try:
            result = wing_audit.audit(vertices, steps=steps)
        except wing_audit.GeometryHold as exc:
            return {"status": STATUS_HOLD, "first_broad_phase_hold": str(exc)}
    return {"status": STATUS_SCREEN, "sampled_aabb_screen": result}


def run(args):
    if args.wing_source_head != EXPECTED_WING_SOURCE_HEAD:
        raise V2ReviewHold("Unknown wing actor source revision: verify pose source first")
    if hashlib.sha256(args.wing_glb.read_bytes()).hexdigest() != EXPECTED_WING_GLB_SHA:
        raise V2ReviewHold("Unexpected review-wing GLB bytes; do not inherit prior clearance")
    if args.v2_source_head != EXPECTED_V2_SOURCE_HEAD:
        raise V2ReviewHold("Unknown V2 source revision: update only after independent review")
    verify_wing_manifest(args.wing_glb, args.wing_manifest)
    wing_audit.assert_source_contract(
        args.cpp.read_text(encoding="utf-8"),
        args.header.read_text(encoding="utf-8"))
    hashes = require_exact_v2_artifacts(args.v2_manifest, args.hull_glb, args.bridge_glb)
    source_cpp = args.cpp.read_text(encoding="utf-8")
    if not any(marker in source_cpp for marker in (
            "ForwardBridge->SetRelativeLocation(FVector(240, 0, 95));",
            "ForwardBridge->SetRelativeLocation(FVector(240.f, 0.f, 95.f));")):
        raise V2ReviewHold("Bridge actor placement changed; cannot reuse prior coordinates")
    wing, wc = wing_audit.read_vertices(args.wing_glb)
    hull, hc = wing_audit.read_vertices(args.hull_glb)
    bridge, bc = wing_audit.read_vertices(args.bridge_glb)
    hb = extents(hull)
    bb = extents(bridge, BRIDGE_TRANSLATION_CM)
    result = evaluate(wing, hb, bb, steps=args.steps)
    # Independently inspect actual triangles only at the first flagged endpoint.
    # An endpoint HOLD is not a certificate for the rest of the motion path.
    if args.narrow_phase_skyborne:
        wing_faces=read_triangles(args.wing_glb)
        hull_faces=read_triangles(args.hull_glb)
        bridge_faces=read_triangles(args.bridge_glb)
        if len(wing_faces)!=29424 or len(hull_faces)!=1950:
            raise V2ReviewHold("Frozen GLB triangle topology has changed")
        # Source-generated fourth/third mesh sections give 144 hinge triangles
        # after the first 29,280 wing faces. The original V2 hull() starts its
        # gold-trim primitive after 240 shell triangles; its FIRST FOUR tubes
        # (32 triangles each) are the four root-to-fairing details.
        # These are only *candidate intended joints*, not authorized contacts.
        hinge_first=29280
        support_first,support_end=240,368
        candidate_joint_pair=lambda wi,bi: (
            wi>=hinge_first and support_first<=bi<support_end)
        translated_bridge=[tuple(p[i]+BRIDGE_TRANSLATION_CM[i]
                                 for i in range(3)) for p in bridge]
        per_root=[]
        for wing_index in range(4):
            transform=wing_audit.blend(
                wing_audit.pose("Skyborne",wing_index),
                wing_audit.pose("Seaborne",wing_index),0.)
            xyz,quat,scale=transform
            transformed=[]
            for p in wing:
                rotated=wing_audit.qrot(quat,tuple(p[i]*scale[i] for i in range(3)))
                transformed.append(tuple(rotated[i]+xyz[i] for i in range(3)))
            hull_result=nearest_surface(transformed,wing_faces,hull,hull_faces)
            # This is a separate diagnostic with only the candidate
            # hinge-to-support-tube pairs omitted. The primary all-triangle
            # result above remains authoritative and HOLD if under threshold.
            other_surface=nearest_surface(
                transformed,wing_faces,hull,hull_faces,
                exclude_pair=candidate_joint_pair)
            bridge_result=nearest_surface(transformed,wing_faces,
                                          translated_bridge,bridge_faces)
            per_root.append({"wing_index":wing_index,
                             "hull_surface":hull_result,
                             "hull_other_than_hinge_to_support_tube":other_surface,
                             "bridge_surface":bridge_result})
        result["skyborne_t0_triangle_narrow_phase"]={
            "authority":"ONE_ENDPOINT_TRIANGLE_SURFACE_SCREEN_NOT_CCD",
            "candidate_contact_pair_ranges":{"wing_hinge_triangles":[29280,29424],
                                             "hull_first_four_brass_support_tubes":[240,368],
                                             "meaning":"hypothesis only; no approval or collision exemption"},
            "wing_results":per_root,
            "disposition":("HOLD_ROOT_SURFACES_WITHIN_10_CM"
                           if any(v["hull_surface"]["below_threshold"] or
                                  v["bridge_surface"]["below_threshold"] for v in per_root)
                           else "SKYBORNE_ENDPOINT_ONLY_PASS_NOT_FULL_ROUTE")}
    return {
        "authority": "CROSS_LANE_CONSERVATIVE_AABB_REVIEW_ONLY",
        "wing_actor_source_head": args.wing_source_head,
        "v2_body_source_head": args.v2_source_head,
        "v2_artifact_sha256": hashes,
        "wing_sha256": hashlib.sha256(args.wing_glb.read_bytes()).hexdigest(),
        "primitive_position_counts": {"wing": wc, "hull": hc, "bridge": bc},
        "v2_hull_world_aabb_cm": hb, "v2_bridge_world_aabb_cm": bb,
        "v2_bridge_actor_translation_cm": BRIDGE_TRANSLATION_CM,
        "steps_per_directed_transition": args.steps,
        **result,
        "limits": [
            "Full-mesh AABB broad phase can flag intentional joints and false intersections",
            "AABB screen is not triangle-level narrow phase or continuous swept collision",
            "No native UE4/UE5 imported actor placement, physics, or visual approval is established",
            "Authoritative four-form creator artwork unchanged and Orbiter remains locked"
        ],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("wing_glb", "wing_manifest", "hull_glb", "bridge_glb",
                 "v2_manifest", "cpp", "header"):
        p.add_argument("--" + name.replace("_", "-"), required=True, type=Path)
    p.add_argument("--wing-source-head", required=True)
    p.add_argument("--v2-source-head", required=True)
    p.add_argument("--steps", type=int, default=20)
    p.add_argument("--narrow-phase-skyborne", action="store_true",
                   help="Exact triangle-surface distance only at Skyborne t0; not swept collision")
    a = p.parse_args(argv)
    try:
        outcome = run(a)
    except (V2ReviewHold, wing_audit.GeometryHold, OSError, ValueError, KeyError,
            IndexError) as exc:
        p.exit(3, "CROSS_LANE_INPUT_HOLD: " + str(exc) + "\n")
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return 2 if outcome["status"] == STATUS_HOLD else 0


if __name__ == "__main__":
    raise SystemExit(main())
