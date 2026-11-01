"""UE 5.8.4-only immutable import for experimental Ender sculpt (review folder).

Does not touch original five-character native review level or assets.
Source file hash is pinned to the validated candidate generated from this PR.
"""
import hashlib
import json
from pathlib import Path
import os
import unreal

SOURCE = Path(os.environ.get("TSTSS_ENDER_FIDELITY_GLTF",r"C:\TSTSS_EnderFidelityCandidateV1c_20261101\Ender_ender_face_hair_v1.glb"))
EXPECTED_SHA = "3fc37924bb457dfe3b62877ca8709efb693a1c1c73251cf6f5dcfbe012babd38"
DEST = "/Game/ArtLookdev/Characters/EnderFidelityV1"
NAME = "Ender_ender_face_hair_v1"

def main():
    project=Path(unreal.Paths.project_dir()).resolve()
    if "CastAllSandbox" not in project.name:
        raise RuntimeError("Refusing non-disposable Unreal project")
    version=unreal.SystemLibrary.get_engine_version()
    if not version.startswith("5.8."):
        raise RuntimeError("Native receipt only applies to UE 5.8")
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if sha!=EXPECTED_SHA:
        raise RuntimeError("Source SHA mismatch")
    library=unreal.EditorAssetLibrary
    if library.does_directory_exist(DEST) and library.list_assets(DEST, recursive=True):
        raise RuntimeError("Review destination contains assets: no replacement")
    rec=project/"Saved"/"CharacterLookdev"/"ender_fidelity_v1_native_intake.json"
    if rec.exists():
        raise RuntimeError("No overwriting receipt")
    task=unreal.AssetImportTask()
    for key,value in (
        ("filename",str(SOURCE)),("destination_path",DEST),
        ("automated",True),("replace_existing",False),("save",True)
    ):
        task.set_editor_property(key,value)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    meshes=[x for x in task.get_objects() if isinstance(x,unreal.StaticMesh)]
    if len(meshes)!=1:raise RuntimeError("Expected one imported static mesh")
    mesh=meshes[0]
    bounds=mesh.get_bounding_box()
    dz=bounds.max.z-bounds.min.z
    if not (175<=dz<=192 and bounds.min.z>=-5):
        raise RuntimeError("Unexpected candidate imported Z extent: "+str(dz))
    result={"status":"NATIVE_IMPORT_PASS_ART_UNAPPROVED",
      "engine":version,"source_sha256":sha,"asset":mesh.get_path_name(),
      "destination":DEST,"native_height_with_staff_cm":dz,
      "skin_or_rigged":False,"visual_acceptance":False,
      "baseline_cast_unchanged":True,"creator_approval":False}
    rec.parent.mkdir(parents=True,exist_ok=True)
    rec.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("TSTSS_ENDER_FIDELITY_IMPORT_PASS",rec)

if __name__=="__main__":main()
