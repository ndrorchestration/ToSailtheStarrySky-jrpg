#!/usr/bin/env python3
"""Reproducible four-form Aureate Wake *review layout contract*, no engine.

The manifest is not actor transforms, a physics rig, a SaveGame form unlock,
a built Unreal scene, or visual approval. It deliberately has no fabricated
pose angles or scale canon. Consume only after a verified real Editor actor test.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

FORMS=("Skybourne","Seabourne","Submersible","Starbourne")
WINGS=("FORE_PORT","FORE_STARBOARD","AFT_PORT","AFT_STARBOARD")
VIEWS=("three_quarter_hero","orthographic_top","side_profile","bridge_hinge_closeup")
ASSET_DIR="/Game/TSTSS/Review/ShipArt/CinematicV4"
GLB_MANIFEST="AureateWake_CinematicDetailV4_Manifest.json"
ORDER=("source_provenance","deterministic_geometry","native_mesh_import",
       "full_editor_single_actor","single_form_scene_assembly",
       "gpu_camera_matched_render","visual_and_mechanical_qa","creator_model_approval")
SKY="AureateWake_SkybourneWingFiligree_V4_REVIEW.glb"
SEA="AureateWake_SeabourneHydrofoilDetail_V4_REVIEW.glb"
SUB="AureateWake_SubmersibleLightRail_V4_REVIEW.glb"
STAR="AureateWake_StarbourneSailMotif_V4_REVIEW.glb"
CORE="AureateWake_SharedExteriorTrim_V4_REVIEW.glb"


def plan():
    return {
      "review_authority":"NONCANONICAL_ONLY_NOT_PRODUCTION",
      "version":"V4_2026-11-03",
      "official_form_names":list(FORMS),
      "source_glb_manifest":GLB_MANIFEST,
      "native_asset_root":ASSET_DIR,
      "active_engine":"UE_5.8.4",
      "shared_vessel":{
        "hull_root":"ONE_PERSISTENT_HULL_FOR_ALL_FOUR",
        "central_pivot":"COMMON_GEODESIC_BRIDGE_AND_LIVING_QUARTERS_REVIEW_COUPLED",
        "forward_bridge":"ONE_FORWARD_FACING_GLASS_BRIDGE",
        "observation_deck":"OPEN_FORWARD_DECK",
        "wing_identity_ids":list(WINGS),
        "shared_detail_glb":CORE,
        "crew_scale":"NEEDS_CREATOR_NATIVE_REVIEW",
        "exact_approved_transformation_angles":"NOT_ESTABLISHED",
      },
      "forms":{
        "Skybourne":{"wing_ids":list(WINGS),"wing_look":"DEPLOYED",
                       "accessories":[{"glb":SKY,"mounts":list(WINGS)}],
                       "review_scene":"Skybourne_HERO_NOT_YET_BUILT"},
        "Seabourne":{"wing_ids":list(WINGS),"wing_look":"STABILIZED_MARINE",
                       "foil_ids":["PORT_FOIL","STARBOARD_FOIL"],
                       "accessories":[{"glb":SEA,"mounts":["PORT_FOIL","STARBOARD_FOIL"]}],
                       "review_scene":"Seabourne_REVIEW_NOT_YET_BUILT"},
        "Submersible":{"wing_ids":list(WINGS),"wing_look":"TUCKED_BUT_IDENTIFIABLE",
                       "accessories":[{"glb":SUB,"mounts":["ONE_SHARED_SHIP_ROOT"]}],
                       "review_scene":"Submersible_REVIEW_NOT_YET_BUILT"},
        "Starbourne":{"wing_ids":list(WINGS),"wing_look":"FOUR_EQUAL_RADIAL_SOLAR_LIGHT_SAILS",
                       "radial_directions":["UP","RIGHT","DOWN","LEFT"],
                       "accessories":[{"glb":STAR,"mounts":list(WINGS)}],
                       "development": "AUTHORIZED_PRIVATE_RESEARCH",
                       "player_story_gate":"LOCKED",
                       "review_scene":"STATIC_OR_DEVELOPER_ONLY_NOT_YET_BUILT"},
      },
      "capture_contract":{"identical_roles_each_form":list(VIEWS),
                          "native_gpu_render_required":True,
                          "actual_pngs":"NOT_ESTABLISHED_FOR_V4",
                          "camera_positions":"TO_BE_AUTHORED_AND_RECORDED"},
      "dependency_order":list(ORDER),
      "gates":{"source_geom_19_tests":"PASS_AT_3859663",
               "native_glb_import":"PASS_AT_2026_11_03",
               "full_editor_single_actor":"BLOCKED_BY_4_2_GIB_RAM_GATE",
               "assembled_scene":"NOT_VERIFIED",
               "gpu_render":"NOT_VERIFIED",
               "continuous_swept_clearance":"NOT_VERIFIED",
               "environment_sky":"BLACK_SKY_HOLD_705",
               "model_art_approval":"NOT_GRANTED",
               "player_starbourne_unlock":"DENIED"},
      "dependencies_separate_prs":{
         "shared_pivot":"#702/#706_UNMERGED",
         "four_wing_kinematics":"#724_UNMERGED",
         "environment":"#705_BLACK_SKY_HOLD",
         "visual_reference":"CREATOR_APPROVED_REFERENCE_SHA_03e3d500",
       },
      "mutations":{"gameplay":False,"scene_saved":False,"native_editor_launched":False,
                   "existing_assets_overwritten":False,"starbourne_player_enabled":False}
    }


def serialized():
    return (json.dumps(plan(),indent=2,sort_keys=True,ensure_ascii=True)+"\n").encode("utf8")


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--check",action="store_true")
    args=p.parse_args(argv)
    dest=args.out.resolve()
    raw=serialized()
    if args.check:
        if not dest.is_file() or dest.read_bytes()!=raw:
            raise SystemExit("REVIEW HOLD: scene manifest absent or modified")
    else:
        if dest.exists():raise SystemExit("REVIEW HOLD: refuse existing scene manifest path")
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(raw)
    print(json.dumps({"path":str(dest),"bytes":len(raw),
                      "sha256":hashlib.sha256(raw).hexdigest(),
                      "editor_scene_built":False,"story_gate_unlocked":False}))


if __name__=="__main__": main()
