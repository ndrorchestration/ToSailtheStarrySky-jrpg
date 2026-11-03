"""Independent native MetaHuman V5 authoring receipt/provenance checks.

Cannot establish Ender likeness, installed optional content, licensed downloads,
animation, or asset promotion. Verifies bytes and log alongside native receipt.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
ASSET="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase"
NOT_APPROVED=(
    "approved_character_replaced","assembly_completed","imported_from_v4_mesh",
    "likeness_approved","prior_glb_modified","production_pawn_changed",
    "rigged","skeleton_generated","source_art_measured_from_2d",
)

def verify_native(receipt,asset,log,project,map_file):
    data=json.loads(Path(receipt).read_text(encoding="utf-8"))
    proj=json.loads(Path(project).read_text(encoding="utf-8-sig"))
    assert "Disposable TSTSS Ender V5" in proj["Description"]
    assert proj.get("EngineAssociation")=="5.8"
    assert any(p.get("Name")=="MetaHumanCharacter" and p.get("Enabled")
               for p in proj.get("Plugins",[]))
    assert data.get("status")=="NATIVE_METAHUMAN_AUTHORING_BASE_PASS_ART_HOLD"
    assert data.get("asset_path")==ASSET
    assert data.get("project_guard")=="DISPOSABLE_V5_ONLY"
    assert data.get("project_name")=="CastAllSandbox"
    assert str(data.get("engine","")).startswith("5.8.")
    assert data.get("plugin")=="MetaHumanCharacter"
    for k in ("native_asset_created","native_asset_saved",
              "native_face_landmark_edit_surface_verified",
              "editor_subsystem_present","registered_for_face_edit",
              "meta_human_authoring_bases_only"):
        assert data.get(k) is True,k
    for k in NOT_APPROVED:
        assert data.get(k) is False,k
    count=data.get("face_landmarks_count")
    assert isinstance(count,int) and not isinstance(count,bool) and 20<=count<=500
    first=data.get("first_landmark_xyz_native_unreal")
    assert isinstance(first,list) and len(first)==3
    assert all(isinstance(v,(int,float)) and math.isfinite(v) for v in first)
    actual_map=hashlib.sha256(Path(map_file).read_bytes()).hexdigest()
    assert actual_map==data.get("saved_reference_map_sha256")==MAP_SHA
    contents=Path(asset).read_bytes()
    assert 100_000<=len(contents)<=30_000_000
    assert contents.startswith(bytes.fromhex("c1832a9e")), "Expected Unreal package signature"
    log_text=Path(log).read_text(encoding="utf-8",errors="replace")
    for marker in ("TSTSS_ENDER_V5_METAHUMAN_NATIVE_PROBE",
                   "Test Completed. Result={Success} Name={test_ender_v5_metahuman_native}",
                   "TEST COMPLETE. EXIT CODE: 0",
                   "Mounting Engine plugin MetaHumanCharacter"):
        assert marker in log_text,marker
    # Missing optional content is an independent blocker, never assumed present.
    missing="MetaHuman Optional Content folder not found" in log_text
    missing_skin="skin editing will be disabled" in log_text
    if missing and not missing_skin:
        raise AssertionError("Optional data warning inconsistent with skin state")
    compile_risk="AssetCompile memory estimate is greater than available" in log_text
    return {
      "status":"V5_NATIVE_METAHUMAN_AUTHORING_BASE_VERIFIED_ART_HOLD",
      "headless_native_asset_creation":True,
      "native_python_face_landmark_access":True,
      "face_landmarks_count":count,
      "asset_sha256":hashlib.sha256(contents).hexdigest(),
      "asset_bytes":len(contents),
      "map_sha256":actual_map,
      "metahuman_optional_content_missing":missing,
      "skin_editing_disabled":missing_skin,
      "low_memory_compilation_warning":compile_risk,
      "artist_resemblance_reviewed":False,
      "creator_likeness_approved":False,
      "rig_or_animation_validated":False,
      "game_project_modified":False,
      "metahuman_binary_copied_into_git":False,
      "next_gate":"Creator reference registered to MetaHuman facial landmark sheet and core content available, before sculpt/assembly",
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for n in ("receipt","asset","log","project","map_file"):
        p.add_argument(n,type=Path)
    args=p.parse_args()
    print(json.dumps(verify_native(args.receipt,args.asset,args.log,args.project,args.map_file),indent=2))
