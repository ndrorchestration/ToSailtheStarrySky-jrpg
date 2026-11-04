"""TSTSS Ender sealed goggles V2; native UE 5.8.4 isolated StaticMesh import.

REVIEW ONLY: refuse production project, asset overwrites, changed source hashes.
Never edit MetaHuman, V1 rejected glasses candidate, review map, or game.
"""
from pathlib import Path
import hashlib,json,struct,traceback
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
SOURCE=Path(r"C:\Users\Admin\work\TSTSS-V5-FaceAuthorityReview-20261103\V2_Sealed_Goggles_Output\Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL.glb")
SRC_SHA="5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb"
ORIGINAL_PACKAGE_GLB_SHA="e46af39346a953c36c010e6f103ff700b8d13ed32a41cf44c0af3b69f0c296d0"
META=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
META_SHA="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
DEST="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/Accessories/SealedGogglesCandidateV2"
RECEIPT=ROOT/"Saved/CharacterLookdev/GogglesFitV2/native_import01.json"

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(x,m):
    if not x:raise RuntimeError("FAIL_CLOSED "+m)
check(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","Only existing isolated MH5 project allowed")
check((ROOT/"CastAllSandbox.uproject").is_file(),"MH5 project descriptor absent")
check(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"UE version drift")
check(SOURCE.is_file() and digest(SOURCE)==SRC_SHA,"V2 regenerated source SHA drift")
check(META.is_file() and MAP.is_file() and digest(META)==META_SHA and digest(MAP)==MAP_SHA,"MetaHuman or map changed")
check(not RECEIPT.exists(),"Existing receipt forbidden")
lib=unreal.EditorAssetLibrary
check(not (lib.does_directory_exist(DEST) and lib.list_assets(DEST,recursive=True)),"V2 import destination occupied")
blob=SOURCE.read_bytes()
check(blob[:4]==b"glTF" and struct.unpack_from("<II",blob,4)==(2,len(blob)),"GLB binary header")
length,kind=struct.unpack_from("<I4s",blob,12)
check(kind==b"JSON" and length%4==0,"JSON chunk malformed")
doc=json.loads(blob[20:20+length])
check(len(doc.get("meshes",[]))==1 and len(doc["meshes"][0]["primitives"])==11,"V2 source mesh or sections changed")
check(len(doc.get("materials",[]))==11,"V2 materials changed")
check(not doc.get("skins") and not doc.get("animations"),"V2 must remain unrigged")
RECEIPT.parent.mkdir(parents=True,exist_ok=True)
report={"status":"STARTED","source":"NEONTIC_SEMANTIC_REBUILD_FROM_ORIGINAL_V2_GENERATOR",
 "source_glb_sha256":SRC_SHA,"original_package_glb_sha256":ORIGINAL_PACKAGE_GLB_SHA,
 "original_binary_parity_claim":False,"source_byte_length":len(blob),
 "engine":unreal.SystemLibrary.get_engine_version(),"project":str(ROOT),"destination":DEST,
 "source_material_count":11,"source_triangles":57288,
 "fitted_to_metahuman":False,"visual_material_approval":False,"head_collision_pass":False,
 "rig_verified":False,"gameplay_modified":False,"character_source_modified":False,
 "review_map_modified":False,"canon_promoted":False,"V1_replaced":False}
def save():RECEIPT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
save()
try:
    task=unreal.AssetImportTask()
    for name,value in (("filename",str(SOURCE)),("destination_path",DEST),
                       ("automated",True),("replace_existing",False),("save",True)):
        task.set_editor_property(name,value)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    all_objects=list(task.get_objects())
    meshes=[a for a in all_objects if isinstance(a,unreal.StaticMesh)]
    check(len(meshes)==1,"Expected one native V2 StaticMesh: "+str(len(meshes)))
    mesh=meshes[0]
    slots=mesh.get_editor_property("static_materials")
    check(len(slots)==11,"Unreal material slot mismatch "+str(len(slots)))
    box=mesh.get_bounding_box()
    xyz=[round(float(abs(getattr(box.max,a)-getattr(box.min,a))),4) for a in "xyz"]
    check(all(abs(a-b)<0.25 for a,b in zip(xyz,[19.2,8.02,19.171])),
          "Unexpected converted source axes/size "+repr(xyz))
    report.update(status="NATIVE_V2_SEALED_GOGGLES_STATICMESH_IMPORT_PASS_FIT_PENDING",
        native_mesh=mesh.get_path_name(),material_slots=len(slots),
        unreal_mesh_bounds_xyz_cm=xyz,
        imported_object_paths=[a.get_path_name() for a in all_objects])
except Exception:
    report["status"]="V2_IMPORT_FAILED"
    report["error"]=traceback.format_exc()[-4500:]
    unreal.log_error("TSTSS_V2_GOGGLES_IMPORT "+report["error"])
finally:
    report["meta_sha256_after"]=digest(META)
    report["map_sha256_after"]=digest(MAP)
    report["glb_sha256_after"]=digest(SOURCE)
    if report["meta_sha256_after"]!=META_SHA or report["map_sha256_after"]!=MAP_SHA or report["glb_sha256_after"]!=SRC_SHA:
        report["status"]="FAIL_SOURCE_INTEGRITY_DRIFT"
    save()
unreal.log("TSTSS_V2_GOGGLES_NATIVE_IMPORT "+report["status"]+" "+str(RECEIPT))
print("TSTSS_V2_GOGGLES_NATIVE_IMPORT",report["status"],str(RECEIPT))
