"""Native UE5.8.4 import proof for original detachable 3D Ender goggles.

Only a separate content-only sandbox, fail closed, no gameplay, no MetaHuman
mesh, no art promotion. Import an unrigged prototype as one StaticMesh.
"""
import hashlib,json,struct,traceback
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
EXPECTED=Path(r"C:\Users\Admin\work\TSTSS-Cast643-UEImport-Sandbox-20261101")
GLB=Path(r"C:\Users\Admin\work\TSTSS-V5-FaceAuthorityReview-20261103\Ender_goggles_noncanonical.glb")
SHA="76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae"
DEST="/Game/ArtLookdev/Characters/Ender/Accessories/GogglesCandidateV1"
RECEIPT=ROOT/"Saved/CharacterLookdev/GogglesCandidateV1/native_import01.json"

def require(ok,why):
    if not ok:raise RuntimeError("FAIL_CLOSED "+why)
require(ROOT.as_posix().lower()==EXPECTED.as_posix().lower(),"project is not content-only Cast643 sandbox")
require((ROOT/"Cast643Review.uproject").is_file(),"sandbox descriptor missing")
require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"engine drift")
require(GLB.is_file() and hashlib.sha256(GLB.read_bytes()).hexdigest()==SHA,"input goggles file drift")
require(not RECEIPT.exists(),"refusing evidence overwrite")
require(not (unreal.EditorAssetLibrary.does_directory_exist(DEST) and
             unreal.EditorAssetLibrary.list_assets(DEST,recursive=True)),"asset destination occupied")
blob=GLB.read_bytes()
require(blob[:4]==b"glTF" and struct.unpack_from("<II",blob,4)==(2,len(blob)),"GLB header invalid")
length,kind=struct.unpack_from("<I4s",blob,12)
require(kind==b"JSON" and length%4==0 and 20+length+8<=len(blob),"JSON chunk malformed")
doc=json.loads(blob[20:20+length])
require(len(doc.get("meshes",[]))==1 and len(doc["meshes"][0]["primitives"])==9,"nine separate material primitives required")
require(not doc.get("skins") and not doc.get("animations"),"static only")
RECEIPT.parent.mkdir(parents=True,exist_ok=True)
record={"status":"IMPORT_ATTEMPT_STARTED","original_art":True,"noncanonical_review_only":True,
  "source_goggles_sha256":SHA,"source_byte_length":len(blob),
  "destination":DEST,"source_mesh_count":1,"source_material_sections":9,
  "source_rigged":False,"source_fitted_to_metahuman":False,
  "source_unit":"meters","engine":unreal.SystemLibrary.get_engine_version(),
  "native_material_visual_approval":False,"gameplay_asset":False,
  "promoted_canon":False}
def save():
    RECEIPT.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n",encoding="utf-8")
save()
try:
    task=unreal.AssetImportTask()
    for key,value in (("filename",str(GLB)),("destination_path",DEST),
                      ("automated",True),("replace_existing",False),("save",True)):
        task.set_editor_property(key,value)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    objs=list(task.get_objects())
    meshes=[x for x in objs if isinstance(x,unreal.StaticMesh)]
    require(len(meshes)==1,"expected one imported StaticMesh got "+str(len(meshes)))
    m=meshes[0]
    bounds=m.get_bounding_box()
    size=[round(abs(getattr(bounds.max,a)-getattr(bounds.min,a)),3) for a in ("x","y","z")]
    require(all(4.0<x<30.0 for x in size),"implausible goggles dimensions in cm "+repr(size))
    mats=m.get_editor_property("static_materials")
    require(len(mats)>=7 and len(mats)<=9,"unexpected material slot count "+str(len(mats)))
    record["unreal_staticmesh_path"]=m.get_path_name()
    record["bounds_cm_xyz"]=size
    record["material_slot_count"]=len(mats)
    record["imported_objects"]=[o.get_path_name() for o in objs]
    record["status"]="STATIC_3D_GOGGLES_NATIVE_IMPORT_PASS_FIT_NOT_VERIFIED"
except Exception:
    record["status"]="IMPORT_FAILED"
    record["error"]=traceback.format_exc()[-3500:]
    unreal.log_error("TSTSS_GOGGLES_IMPORT_FAIL "+record["error"])
finally:
    save()
unreal.log("TSTSS_GOGGLES_NATIVE_RECEIPT "+record["status"]+" "+str(RECEIPT))
print("TSTSS_GOGGLES_NATIVE_RECEIPT",record["status"],str(RECEIPT))
