"""Unreal 5.8 read-only probe of V2 EmeraldGlass instance base-property overrides."""
from pathlib import Path
import hashlib,json,traceback
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve()
OUT=ROOT/"Saved/CharacterLookdev/GogglesFitV2/NativeImportedMaterialAudit07/emerald_override_receipt.json"
SOURCE=Path(r"C:\Users\Admin\work\TSTSS-V5-FaceAuthorityReview-20261103\V2_Sealed_Goggles_Output\Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL.glb")
MODEL=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
SHA_GLB="5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb"
SHA_MODEL="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
SHA_MAP="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
PATH="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/Accessories/SealedGogglesCandidateV2/Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL/Materials/EmeraldGlass.EmeraldGlass"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guard(b,msg):
    if not b:raise RuntimeError("FAIL_CLOSED "+msg)
guard(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","project")
guard(sha(SOURCE)==SHA_GLB and sha(MODEL)==SHA_MODEL and sha(MAP)==SHA_MAP,"source hash")
guard(not OUT.exists(),"receipt overwrite")
mat=unreal.load_asset(PATH)
guard(mat is not None and mat.get_class().get_name()=="MaterialInstanceConstant","material instance")
OUT.parent.mkdir(parents=True,exist_ok=False)
def inspect_fields(obj,fields):
    out={}
    for x in fields:
        try:out[x]=str(obj.get_editor_property(x))
        except Exception as e:out[x+"_not_available"]=e.__class__.__name__
    return out
record={"status":"INSTANCE_PROPERTIES_STARTED","path":PATH,
        "material_class":mat.get_class().get_name(),
        "source_glb_sha256":SHA_GLB,"source_meta_sha256":SHA_MODEL,"source_map_sha256":SHA_MAP,
        "artist_approved":False,"imported_material_edited":False,
        "gameplay_modified":False}
try:
    parent=mat.get_editor_property("parent")
    record["parent_path"]=parent.get_path_name() if parent else None
    base=mat.get_base_material()
    record["parent_blend_mode"]=str(base.get_editor_property("blend_mode"))
    overrides=mat.get_editor_property("base_property_overrides")
    record["base_property_overrides"]=inspect_fields(overrides,(
      "override_blend_mode","blend_mode","override_two_sided","two_sided",
      "override_shading_model","shading_model","override_opacity_mask_clip_value",
      "opacity_mask_clip_value","override_dithered_lod_transition"))
    for field in ("scalar_parameter_values","vector_parameter_values","texture_parameter_values"):
        try:
            params=mat.get_editor_property(field)
            record[field]=[]
            for p in params:
                try:
                    info=p.get_editor_property("parameter_info")
                    name=str(info.get_editor_property("name"))
                    val=str(p.get_editor_property("parameter_value"))
                    record[field].append({"name":name,"value":val})
                except Exception as e:
                    record[field].append({"inspection_error":str(e)[:180]})
        except Exception as e:
            record[field+"_unavailable"]=e.__class__.__name__
    record["status"]="NATIVE_EMERALD_INSTANCE_OVERRIDES_READ_ONLY_PASS"
except Exception:
    record["status"]="NATIVE_EMERALD_INSTANCE_OVERRIDES_FAILED"
    record["error"]=traceback.format_exc()[-2200:]
finally:
    record["source_glb_after"]=sha(SOURCE)
    record["source_meta_after"]=sha(MODEL)
    record["source_map_after"]=sha(MAP)
    if record["source_glb_after"]!=SHA_GLB or record["source_meta_after"]!=SHA_MODEL or record["source_map_after"]!=SHA_MAP:
        record["status"]="FAIL_SOURCE_HASH_DRIFT"
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",encoding="utf8")
print("TSTSS_EMERALD_NATIVE",record["status"])
print("OVERRIDES",json.dumps(record.get("base_property_overrides",{}),sort_keys=True))
print("SCALARS",json.dumps(record.get("scalar_parameter_values",[]),sort_keys=True))
print("VECTORS",json.dumps(record.get("vector_parameter_values",[]),sort_keys=True))
