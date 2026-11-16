"""One-shot gated native Unreal 5.8.4 V3 STATIC hair intake in disposable MH5.

Do not run concurrently with another Unreal Editor / LiveCoding session.
The operator MUST first separately verify workspace ownership, RAM/disk gates,
source HEAD and existing project. This does not attach or approve hair.
Designed to be passed to UE Editor Python ONLY, never launched automatically.
"""
from __future__ import annotations

import hashlib
import json
import traceback
from pathlib import Path

import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
SOURCE=Path(r"C:\TSTSS_EnderHairNativeV1_20261104\unreal\ArtSource\Characters\HairReview\CandidatesV3\Ender_BroadLayerHair_V3_NONCANONICAL.glb")
SOURCE_SHA="bd8286a142294a86784180099db6e8298dc85367632c5a3673fcec50d893d09e"
META=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
META_SHA="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
DEST="/Game/ArtLookdev/Characters/EnderHairStaticV3_NONCANONICAL"
RECEIPT=ROOT/"Saved/CharacterLookdev/EnderHairReviewV3/native_import_v3.json"

def require(condition,label):
    if not condition:
        raise RuntimeError("TSTSS_V3_NATIVE_IMPORT_HOLD "+label)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

# All important preflight happens BEFORE any import or receipt write.
require(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","WRONG_DISPOSABLE_PROJECT")
require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),
        "WRONG_ENGINE")
require((ROOT/"CastAllSandbox.uproject").is_file(),"MISSING_PROJECT_DESCRIPTOR")
require(SOURCE.is_file() and sha(SOURCE)==SOURCE_SHA,"SOURCE_GLB_MISSING_OR_DRIFT")
require(META.is_file() and MAP.is_file(),"ORIGINAL_FACE_OR_MAP_MISSING")
require(sha(META)==META_SHA and sha(MAP)==MAP_SHA,"ORIGINAL_FACE_OR_MAP_DRIFT")
require(not RECEIPT.exists(),"NEVER_OVERWRITE_PREVIOUS_RECEIPT")
lib=unreal.EditorAssetLibrary
require(not (lib.does_directory_exist(DEST) and lib.list_assets(DEST,recursive=True)),
        "NATIVE_IMPORT_DESTINATION_NOT_EMPTY")
raw=SOURCE.read_bytes()
require(raw[:4]==b"glTF","NOT_GLB")
n=int.from_bytes(raw[12:16],"little")
require(raw[16:20]==b"JSON" and n>100 and n%4==0,
        "INVALID_GLB_HEADER")
doc=json.loads(raw[20:20+n])
require(len(doc.get("meshes",[]))==1 and
        len(doc["meshes"][0]["primitives"])==4 and
        len(doc.get("materials",[]))==4,"V3_STATIC_FOUR_MATERIAL_CONTRACT")
require("skins" not in doc and "animations" not in doc and
        doc.get("extras",{}).get("creator_approved") is False and
        doc.get("extras",{}).get("native_render_verified") is False,
        "V3_STATIC_ART_HOLD_CONTRACT")

RECEIPT.parent.mkdir(parents=True,exist_ok=True)
result={
    "status":"IN_PROGRESS_NONCANONICAL",
    "engine":unreal.SystemLibrary.get_engine_version(),
    "project":str(ROOT),
    "source_sha256":SOURCE_SHA,
    "native_dest":DEST,
    "not_creator_approved":True,
    "no_face_or_goggles_fit_claim":True,
    "no_skeletal_or_animation_claim":True,
    "production_actor_changed":False,
    "original_map_changed":False,
}
def persist():
    RECEIPT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")

persist()
try:
    task=unreal.AssetImportTask()
    for key,value in (
        ("filename",str(SOURCE)),
        ("destination_path",DEST),
        ("automated",True),
        ("replace_existing",False),
        ("save",True),
    ):
        task.set_editor_property(key,value)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    meshes=[obj for obj in task.get_objects() if isinstance(obj,unreal.StaticMesh)]
    require(len(meshes)==1,"ONE_IMPORTED_STATIC_MESH")
    mesh=meshes[0]
    require(len(mesh.get_editor_property("static_materials"))==4,"FOUR_IMPORTED_MATERIAL_SLOTS")
    bound=mesh.get_bounding_box()
    cm=[abs(float(getattr(bound.max,a)-getattr(bound.min,a))) for a in "xyz"]
    # Compare UNORDERED edge lengths. A glTF->Unreal axis permutation is possible;
    # this check must NOT be described as a correct upright/oriented native import.
    expected=(23.7763,23.9919,19.7045)
    require(all(abs(x-y)<.8 for x,y in zip(sorted(cm),sorted(expected))),
            "SOURCE_DIMENSION_MISMATCH_OR_UNPROVEN_UNITS: "+repr(cm))
    result.update(
        status="V3_STATIC_IMPORT_PASS_ART_AND_ORIENTATION_HOLD",
        imported_static_mesh=mesh.get_path_name(),
        imported_material_slots=4,
        imported_bounding_dimensions_xyz_cm=cm,
        original_approved_hair=False,
        genuine_native_screenshot=False,
        scalp_clearance_verified=False,
        orientation_verified=False,
    )
except Exception:
    result["status"]="NATIVE_IMPORT_FAILED_DO_NOT_PROMOTE"
    result["error"]=traceback.format_exc()[-3500:]
    unreal.log_error(result["error"])
finally:
    result["source_sha256_after"]=sha(SOURCE)
    result["meta_sha256_after"]=sha(META)
    result["map_sha256_after"]=sha(MAP)
    if (result["source_sha256_after"]!=SOURCE_SHA or
            result["meta_sha256_after"]!=META_SHA or
            result["map_sha256_after"]!=MAP_SHA):
        result["status"]="FAIL_CLOSED_ORIGINAL_ASSET_DRIFT"
    persist()
unreal.log("TSTSS_ENDER_V3_NATIVE_IMPORT "+result["status"]+" "+str(RECEIPT))
print("TSTSS_ENDER_V3_NATIVE_IMPORT",result["status"])
