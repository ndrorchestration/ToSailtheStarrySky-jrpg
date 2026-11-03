"""Ender V5: native MetaHuman authoring feasibility, intentionally NOT likeness.

Requires isolated disposable Unreal Engine 5.8 sandbox with MetaHumanCharacter
enabled only in sandbox .uproject. Does not convert V4 mesh, apply a preset,
rig, download assets, assemble characters, authorize licenses or modify game.
"""
import json
import hashlib
from pathlib import Path
import unreal

DEST="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy"
NAME="MHC_EnderV5_UnapprovedBase"
MAP_REL="Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"

def main():
    project=Path(unreal.Paths.project_dir()).resolve()
    cfg=project/"CastAllSandbox.uproject"
    if project.name!="CastAllSandbox" or not cfg.is_file():
        raise RuntimeError("PRODUCTION_GUARD: refuse non-disposable Unreal project")
    manifest=json.loads(cfg.read_text(encoding="utf-8"))
    if "Disposable TSTSS Ender V5" not in manifest.get("Description",""):
        raise RuntimeError("PRODUCTION_GUARD: expected isolated V5 sandbox marker")
    if not any(p.get("Name")=="MetaHumanCharacter" and p.get("Enabled") is True
               for p in manifest.get("Plugins",[])):
        raise RuntimeError("MetaHuman Character plugin not explicitly enabled in sandbox")
    if not unreal.SystemLibrary.get_engine_version().startswith("5.8."):
        raise RuntimeError("EXPECTED_UNREAL_5_8")
    mapfile=project/MAP_REL
    if not mapfile.is_file() or hashlib.sha256(mapfile.read_bytes()).hexdigest()!=MAP_SHA:
        raise RuntimeError("Preserved review map source drift")
    folder=project/"Saved"/"CharacterLookdev"/"EnderV5MetaHuman"
    receipt=folder/"native_metahuman_authoring_receipt.json"
    if receipt.exists() or unreal.EditorAssetLibrary.does_directory_exist(DEST):
        raise RuntimeError("Refuse overwrite of earlier MetaHuman authoring proof")
    folder.mkdir(parents=True,exist_ok=False)
    info={
        "status":"STARTED_NOT_YET_VERIFIED",
        "engine":unreal.SystemLibrary.get_engine_version(),
        "project_name":project.name,
        "project_guard":"DISPOSABLE_V5_ONLY",
        "plugin":"MetaHumanCharacter",
        "asset_path":DEST+"/"+NAME+"."+NAME,
        "imported_from_v4_mesh":False,
        "prior_glb_modified":False,
        "approved_character_replaced":False,
        "production_pawn_changed":False,
        "source_art_measured_from_2d":False,
        "likeness_approved":False,
        "skeleton_generated":False,
        "rigged":False,
        "assembly_completed":False,
        "meta_human_authoring_bases_only":True,
        "saved_reference_map_sha256":MAP_SHA,
    }
    def write():
        receipt.write_text(json.dumps(info,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    write()
    if not hasattr(unreal,"MetaHumanCharacter") or not hasattr(unreal,"MetaHumanCharacterFactoryNew"):
        info["status"]="BLOCKED_PYTHON_METAHUMAN_CLASS_NOT_EXPOSED"
        write()
        raise RuntimeError(info["status"])
    factory=unreal.new_object(unreal.MetaHumanCharacterFactoryNew)
    created=unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name=NAME, package_path=DEST,
        asset_class=unreal.MetaHumanCharacter, factory=factory)
    if created is None or not isinstance(created,unreal.MetaHumanCharacter):
        info["status"]="BLOCKED_METAHUMAN_ASSET_FACTORY"
        write()
        raise RuntimeError(info["status"])
    if created.get_path_name()!=info["asset_path"]:
        raise RuntimeError("Unexpected native asset path")
    info["native_asset_created"]=True
    if not unreal.EditorAssetLibrary.save_asset(created.get_path_name(),only_if_is_dirty=False):
        info["status"]="BLOCKED_METAHUMAN_SAVE_FAILED";write()
        raise RuntimeError(info["status"])
    info["native_asset_saved"]=True
    if not hasattr(unreal,"MetaHumanCharacterEditorSubsystem"):
        info["status"]="BLOCKED_EDITOR_SUBSYSTEM_MISSING"
        write()
        raise RuntimeError(info["status"])
    sub=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
    info["editor_subsystem_present"]=sub is not None
    if sub is None:
        info["status"]="BLOCKED_EDITOR_SUBSYSTEM_NOT_AVAILABLE"
        write()
        raise RuntimeError(info["status"])
    registered=False
    try:
        registered=bool(sub.try_add_object_to_edit(created))
        info["registered_for_face_edit"]=registered
        if not registered:
            info["status"]="METAHUMAN_ASSET_SAVED_BUT_FACE_REGISTRATION_BLOCKED"
            write()
            raise RuntimeError(info["status"])
        landmarks=sub.get_face_landmarks(character=created)
        info["face_landmarks_count"]=len(landmarks) if landmarks is not None else 0
        if info["face_landmarks_count"]<20:
            info["status"]="METAHUMAN_ASSET_SAVED_BUT_LANDMARK_DATA_UNAVAILABLE"
            write()
            raise RuntimeError(info["status"])
        first=landmarks[0]
        info["first_landmark_xyz_native_unreal"]=[round(float(first.x),4),round(float(first.y),4),round(float(first.z),4)]
        info["native_face_landmark_edit_surface_verified"]=True
        info["status"]="NATIVE_METAHUMAN_AUTHORING_BASE_PASS_ART_HOLD"
    finally:
        if registered:
            sub.remove_object_to_edit(created)
        after=hashlib.sha256(mapfile.read_bytes()).hexdigest()
        if after!=MAP_SHA:
            info["status"]="FAIL_CLOSED_REVIEW_MAP_SHA_CHANGED"
            write()
            raise RuntimeError(info["status"])
        write()
    print("TSTSS_ENDER_V5_METAHUMAN_NATIVE_PROBE",json.dumps(info,sort_keys=True))
    if info["status"]!="NATIVE_METAHUMAN_AUTHORING_BASE_PASS_ART_HOLD":
        raise RuntimeError(info["status"])

if __name__=="__main__":
    main()
