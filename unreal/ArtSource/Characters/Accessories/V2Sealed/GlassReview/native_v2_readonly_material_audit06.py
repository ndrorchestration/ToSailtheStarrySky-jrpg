"""Read-only native Unreal V2 goggles Material inspection in isolated MH5.

No material editing, no asset saving, no actor or scene setup. This checks
whether the imported EmeraldGlass material's blend mode is translucent.
"""
import hashlib,json,traceback
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
ORIG=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
GLB=Path(r"C:\Users\Admin\work\TSTSS-V5-FaceAuthorityReview-20261103\V2_Sealed_Goggles_Output\Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL.glb")
IMPORT=ROOT/"Saved/CharacterLookdev/GogglesFitV2/native_import01.json"
OUT=ROOT/"Saved/CharacterLookdev/GogglesFitV2/NativeImportedMaterialAudit06/material_audit_receipt.json"
SHA_META="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
SHA_MAP="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
SHA_GLB="5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(cond,msg):
    if not cond:raise RuntimeError("FAIL_CLOSED "+msg)
require(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","not isolated MH5")
require((ROOT/"CastAllSandbox.uproject").is_file(),"missing project descriptor")
require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"engine version changed")
require(not OUT.exists(),"refuse evidence overwrite")
require(sha(ORIG)==SHA_META and sha(MAP)==SHA_MAP and sha(GLB)==SHA_GLB,"source changed")
imp=json.loads(IMPORT.read_text(encoding="utf8"))
require(imp.get("status")=="NATIVE_V2_SEALED_GOGGLES_STATICMESH_IMPORT_PASS_FIT_PENDING","import receipt not accepted")
asset=unreal.load_asset(imp["native_mesh"])
require(isinstance(asset,unreal.StaticMesh),"missing actual imported StaticMesh")
slots=asset.get_editor_property("static_materials")
require(len(slots)==11,"wrong material-slot count")
OUT.parent.mkdir(parents=True,exist_ok=False)
result={"status":"NATIVE_MATERIAL_AUDIT_STARTED","engine":unreal.SystemLibrary.get_engine_version(),
"project":str(ROOT),"mesh":asset.get_path_name(),"slot_count":len(slots),
"source_original_meta_sha256":SHA_META,"source_map_sha256":SHA_MAP,
"source_goggles_glb_sha256":SHA_GLB,"asset_saved":False,
"level_saved":False,"source_material_modified":False,
"artist_material_approved":False,"physical_goggles_fit_verified":False,
"gameplay_asset_promoted":False,"slots":[]}
def save():OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
try:
    for i,slot in enumerate(slots):
        record={"index":i,"imported_slot_name":str(slot.get_editor_property("material_slot_name"))}
        obj=slot.get_editor_property("material_interface")
        if obj is None:
            record["missing_interface"]=True
        else:
            record["material_class"]=obj.get_class().get_name()
            record["material_path"]=obj.get_path_name()
            base=obj
            try:
                base=obj.get_base_material()
            except Exception:
                pass
            record["base_material_path"]=base.get_path_name() if base else None
            for key in ("blend_mode","shading_model","two_sided",
                        "translucency_lighting_mode","opacity_mask_clip_value"):
                try:
                    prop=base.get_editor_property(key)
                    record[key]=str(prop)
                except Exception as ex:
                    record[key+"_unavailable"]=ex.__class__.__name__
        result["slots"].append(record)
    # Never claim translucency from a glTF alpha factor alone.
    result["emerald_slots"]=[r for r in result["slots"]
                           if "emerald" in r["imported_slot_name"].lower()
                           or "emerald" in r.get("material_path","").lower()]
    result["status"]="NATIVE_IMPORTED_MATERIAL_PROPERTIES_READ_ONLY_PASS"
except Exception:
    result["status"]="NATIVE_MATERIAL_AUDIT_FAILED"
    result["error"]=traceback.format_exc()[-3500:]
finally:
    result["source_meta_sha256_after"]=sha(ORIG)
    result["source_map_sha256_after"]=sha(MAP)
    result["source_glb_sha256_after"]=sha(GLB)
    if result["source_meta_sha256_after"]!=SHA_META or result["source_map_sha256_after"]!=SHA_MAP or result["source_glb_sha256_after"]!=SHA_GLB:
        result["status"]="FAIL_SOURCE_MUTATED"
    save()
print("TSTSS_V2_MATERIAL_AUDIT",result["status"],"SLOTS",len(result["slots"]))
for x in result["emerald_slots"]:
    print("EMERALD_SLOT",json.dumps(x,sort_keys=True))
