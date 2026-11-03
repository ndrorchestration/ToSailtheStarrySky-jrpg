"""Unreal 5.8 disposable import: Ender V3 review geometry only.

Never install in the production game or replace V1/V2 or approved art.
"""
import hashlib
import json
from pathlib import Path
import unreal

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"FidelityCandidates"/"EnderV3"/"Ender_ender_head_landmark_v3.glb"
EXPECTED="0fb1b6e8de8d84ce751ce8bbb97b7ca78174e077acf64f60e127bd0ddb90c2de"
DEST="/Game/ArtLookdev/Characters/EnderLandmarksV3"
EXPECTED_BASE_MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"

def main():
    project=Path(unreal.Paths.project_dir()).resolve()
    if project.name!="CastAllSandbox":
        raise RuntimeError("Refuse non-disposable project")
    version=unreal.SystemLibrary.get_engine_version()
    if not version.startswith("5.8."):
        raise RuntimeError("Unreal 5.8 exact required")
    if not SOURCE.is_file() or hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=EXPECTED:
        raise RuntimeError("V3 source SHA mismatch")
    base=project/"Content"/"ArtLookdev"/"ReviewMaps"/"TSTSS_EnderFidelityV2_Review.umap"
    if not base.is_file() or hashlib.sha256(base.read_bytes()).hexdigest()!=EXPECTED_BASE_MAP_SHA:
        raise RuntimeError("V2 baseline review map missing or modified")
    if unreal.EditorAssetLibrary.does_directory_exist(DEST):
        if unreal.EditorAssetLibrary.list_assets(DEST,recursive=True):
            raise RuntimeError("V3 review destination already occupied")
    receipt=project/"Saved"/"CharacterLookdev"/"ender_head_v3_native_intake.json"
    if receipt.exists():
        raise RuntimeError("V3 intake receipt already exists; refuse overwrite")
    task=unreal.AssetImportTask()
    for k,v in (("filename",str(SOURCE)),("destination_path",DEST),
                ("automated",True),("replace_existing",False),("save",True)):
        task.set_editor_property(k,v)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    meshes=[obj for obj in task.get_objects() if isinstance(obj,unreal.StaticMesh)]
    if len(meshes)!=1:
        raise RuntimeError("Expected exactly one standalone V3 imported StaticMesh")
    mesh=meshes[0]
    bounds=mesh.get_bounding_box()
    height=bounds.max.z-bounds.min.z
    if not (175<=height<=192 and bounds.min.z>=-5):
        raise RuntimeError("V3 source scale/axis error: "+str(height))
    outcome={
        "status":"NATIVE_IMPORT_PASS_ART_UNAPPROVED",
        "source_sha256":EXPECTED,"engine":version,
        "asset":mesh.get_path_name(),"destination":DEST,
        "native_height_with_staff_cm":height,
        "saved_review_map_sha256":EXPECTED_BASE_MAP_SHA,
        "art_approval":False,"creator_approval":False,
        "skin_or_rigged":False,"gameplay_asset":False,
        "baseline_unchanged":True,
    }
    receipt.parent.mkdir(parents=True,exist_ok=True)
    receipt.write_text(json.dumps(outcome,indent=2)+"\n",encoding="utf-8")
    print("TSTSS_ENDER_V3_NATIVE_IMPORT_PASS",json.dumps(outcome,sort_keys=True))

if __name__=="__main__":
    main()
