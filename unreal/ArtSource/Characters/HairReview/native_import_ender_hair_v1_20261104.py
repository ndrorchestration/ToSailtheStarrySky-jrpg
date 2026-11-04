"""Gated UE5.8.4 native Ender original hair StaticMesh intake, isolated MH5 only."""
import hashlib,json,struct,traceback
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve()
SRC=Path(r"C:\TSTSS_EnderHairNativeV1_20261104\unreal\ArtSource\Characters\HairReview\Candidates\Ender_DarkCopper_LayeredHair_V1_NONCANONICAL.glb")
SHA="01bb9f400454d633c5e887cd47a12fd1af34e5bbf6b7c05ab6a5929b0a6db562"
META=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
MS="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
LS="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
DEST="/Game/ArtLookdev/Characters/EnderHairStaticV1_NONCANONICAL"
RECEIPT=ROOT/"Saved/CharacterLookdev/EnderHairReviewV1/native_import01.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,label):
    if not ok:raise RuntimeError("FAIL_CLOSED "+label)
require(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","only MH5")
require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"wrong engine")
require((ROOT/"CastAllSandbox.uproject").is_file(),"missing sandbox descriptor")
require(SRC.is_file() and sha(SRC)==SHA,"source hair GLB drift")
require(META.is_file() and MAP.is_file() and sha(META)==MS and sha(MAP)==LS,"MetaHuman/map drift")
require(not RECEIPT.exists(),"never overwrite evidence")
lib=unreal.EditorAssetLibrary
require(not (lib.does_directory_exist(DEST) and lib.list_assets(DEST,recursive=True)),
        "review hair destination occupied")
data=SRC.read_bytes()
require(data[:4]==b"glTF" and struct.unpack_from("<II",data,4)==(2,len(data)),
        "GLB header")
n,typ=struct.unpack_from("<I4s",data,12)
require(typ==b"JSON" and n%4==0,"GLB document")
doc=json.loads(data[20:20+n])
require(len(doc["meshes"])==1 and len(doc["meshes"][0]["primitives"])==5,
        "exact 5 material primitives")
require(len(doc["materials"])==5 and not doc.get("skins") and not doc.get("animations"),
        "static review only")
require(doc.get("extras",{}).get("creator_approved") is False,
        "not approved")
RECEIPT.parent.mkdir(parents=True,exist_ok=True)
record={"status":"IN_PROGRESS","source_glb_sha256":SHA,"engine":unreal.SystemLibrary.get_engine_version(),
        "project":str(ROOT),"review_destination":DEST,"source_material_count":5,
        "approved_facial_likeness":False,"actual_hair_fit_verified":False,
        "creator_approved":False,"skeletal_mesh":False,"live_hair_groom":False,
        "gameplay_changed":False,"original_meta_modified":False,"review_map_modified":False,
        "goggles_v2_changed":False,"canon_promoted":False}
def save():RECEIPT.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
save()
try:
    task=unreal.AssetImportTask()
    for key,val in (("filename",str(SRC)),("destination_path",DEST),
                    ("automated",True),("replace_existing",False),("save",True)):
        task.set_editor_property(key,val)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    objects=list(task.get_objects())
    meshes=[x for x in objects if isinstance(x,unreal.StaticMesh)]
    require(len(meshes)==1,"one real StaticMesh")
    mesh=meshes[0]
    slots=mesh.get_editor_property("static_materials")
    require(len(slots)==5,"five materials must import")
    bounds=mesh.get_bounding_box()
    converted=[round(float(abs(getattr(bounds.max,a)-getattr(bounds.min,a))),4) for a in "xyz"]
    expected=[23.0297,18.7177,24.3367]
    require(all(abs(v-e)<.6 for v,e in zip(converted,expected)),
            "UE converted size/axis drift: "+repr(converted))
    record.update(status="NATIVE_ENDER_HAIR_STATIC_IMPORT_PASS_FIT_AND_ART_HOLD",
        imported_mesh=mesh.get_path_name(),native_material_slots=len(slots),
        native_bounds_xyz_cm=converted,
        imported_asset_paths=[x.get_path_name() for x in objects])
except Exception:
    record["status"]="IMPORT_FAILED"
    record["error"]=traceback.format_exc()[-3000:]
    unreal.log_error(record["error"])
finally:
    record["meta_sha256_after"]=sha(META)
    record["map_sha256_after"]=sha(MAP)
    record["glb_sha256_after"]=sha(SRC)
    if record["meta_sha256_after"]!=MS or record["map_sha256_after"]!=LS or record["glb_sha256_after"]!=SHA:
        record["status"]="FAIL_SOURCE_DRIFT"
    save()
unreal.log("TSTSS_ENDER_HAIR_IMPORT "+record["status"]+" "+str(RECEIPT))
print("TSTSS_ENDER_HAIR_IMPORT",record["status"])
