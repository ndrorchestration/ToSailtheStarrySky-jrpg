"""Import detachable Ender V1 goggles into an MH5-only Unreal review clone.

Exact source and clone hashes must match. Never edit face asset, map, gameplay
assets, or existing imported goggles. Imported art is noncanonical review-only.
"""
import hashlib,json,struct,traceback
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve()
GLB=Path(r"C:\Users\Admin\work\TSTSS-V5-FaceAuthorityReview-20261103\Ender_goggles_noncanonical.glb")
ORIG=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
SOURCE_SHA="76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae"
META_SHA="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
DEST="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/Accessories/GogglesCandidateV1"
RECEIPT=ROOT/"Saved/CharacterLookdev/GogglesFitV1/native_import01.json"
def require(x,m):
    if not x:raise RuntimeError("FAIL_CLOSED "+m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
require(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","not isolated MH5")
require("goggles fitting experiment (MH5)" in (ROOT/"CastAllSandbox.uproject").read_text(encoding="utf-8-sig"),"clone identity")
require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"engine")
require(GLB.is_file() and sha(GLB)==SOURCE_SHA,"source GLB drift")
require(sha(ORIG)==META_SHA and sha(MAP)==MAP_SHA,"original source drift")
require(not RECEIPT.exists(),"existing receipt")
library=unreal.EditorAssetLibrary
require(not (library.does_directory_exist(DEST) and library.list_assets(DEST,recursive=True)),"destination occupied")
blob=GLB.read_bytes()
require(blob[:4]==b"glTF" and struct.unpack_from("<II",blob,4)==(2,len(blob)),"GLB header")
n,kind=struct.unpack_from("<I4s",blob,12)
require(kind==b"JSON" and n%4==0,"GLB JSON")
doc=json.loads(blob[20:20+n])
require(len(doc["meshes"])==1 and len(doc["meshes"][0]["primitives"])==9 and not doc.get("skins"),"GLB structure")
RECEIPT.parent.mkdir(parents=True,exist_ok=True)
record={"status":"IMPORT_STARTED","project":str(ROOT),"source_glb_sha256":SOURCE_SHA,
        "source_original_metahuman_sha256":META_SHA,"source_map_sha256":MAP_SHA,
        "target":DEST,"art_review_only":True,"fitted_to_face":False,
        "rigged":False,"face_sculpted":False,"visual_acceptance":False,
        "game_integrated":False,"canonical":False}
def save():RECEIPT.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",encoding="utf-8")
save()
try:
    task=unreal.AssetImportTask()
    for name,value in (("filename",str(GLB)),("destination_path",DEST),
                       ("automated",True),("replace_existing",False),("save",True)):
        task.set_editor_property(name,value)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    objects=list(task.get_objects())
    meshes=[x for x in objects if isinstance(x,unreal.StaticMesh)]
    require(len(meshes)==1,"expected exactly one StaticMesh")
    mesh=meshes[0]
    low,high=(mesh.get_bounding_box().min,mesh.get_bounding_box().max)
    dims=[round(abs(getattr(high,a)-getattr(low,a)),5) for a in "xyz"]
    require(abs(dims[0]-18.218)<0.1 and abs(dims[1]-6.1)<0.1 and
            abs(dims[2]-15.35)<0.1,"mesh dimensions or axes drift "+repr(dims))
    slots=mesh.get_editor_property("static_materials")
    require(len(slots)==9,"expected nine material slots")
    record["static_mesh_path"]=mesh.get_path_name()
    record["bounds_min_xyz_cm"]=[round(getattr(low,a),5) for a in "xyz"]
    record["bounds_max_xyz_cm"]=[round(getattr(high,a),5) for a in "xyz"]
    record["bounds_xyz_cm"]=dims
    record["material_slot_count"]=len(slots)
    record["imported_objects"]=[o.get_path_name() for o in objects]
    record["status"]="MH5_NATIVE_GOGGLES_IMPORT_PASS_POSITIONING_PENDING"
except Exception:
    record["status"]="IMPORT_FAILED"
    record["error"]=traceback.format_exc()[-3100:]
    unreal.log_error("TSTSS_MH5_GOGGLES_IMPORT_FAIL "+record["error"])
finally:
    record["meta_sha256_after"]=sha(ORIG)
    record["map_sha256_after"]=sha(MAP)
    if record["meta_sha256_after"]!=META_SHA or record["map_sha256_after"]!=MAP_SHA:
        record["status"]="FAIL_SOURCE_ASSET_HASH_DRIFT"
    save()
print("TSTSS_MH5_GOGGLES_IMPORT",record["status"],str(RECEIPT))
