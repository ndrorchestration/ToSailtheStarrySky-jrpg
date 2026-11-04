"""Read-only inspect imported GLTF M_Default parent opacity graph in MH5."""
from pathlib import Path
import hashlib,json,traceback
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve()
OUT=ROOT/"Saved/CharacterLookdev/GogglesFitV2/NativeImportedMaterialAudit08/parent_opacity_receipt.json"
PARENT="/InterchangeAssets/gltf/M_Default.M_Default"
SOURCE="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/Accessories/SealedGogglesCandidateV2/Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL/Materials/EmeraldGlass.EmeraldGlass"
if ROOT.as_posix().lower()!="c:/mh5/castallsandbox" or OUT.exists():
    raise RuntimeError("FAIL_CLOSED project or evidence collision")
m=unreal.load_asset(SOURCE);base=unreal.load_asset(PARENT)
if not isinstance(m,unreal.MaterialInstanceConstant) or not isinstance(base,unreal.Material):
    raise RuntimeError("FAIL_CLOSED expected native material graph not found")
OUT.parent.mkdir(parents=True,exist_ok=False)
record={"status":"OPACITY_GRAPH_INSPECTION_STARTED",
        "imported_instance_path":SOURCE,"parent_path":PARENT,
        "parent_blend_mode":str(base.get_editor_property("blend_mode")),
        "asset_saved":False,"material_modified":False,
        "actual_translucency_in_capture_verified":False}
for pname in ("opacity","opacity_mask","base_color","metallic","roughness","refraction"):
    try:
        pin=base.get_editor_property(pname)
        record[pname+"_pin"]=str(pin)[:250]
        try:record[pname+"_expression"]=str(pin.get_editor_property("expression"))[:300]
        except Exception as e:record[pname+"_expression_error"]=e.__class__.__name__
    except Exception as e:record[pname+"_pin_unavailable"]=e.__class__.__name__
try:
    editor=unreal.MaterialEditingLibrary
    for pname in ("MP_OPACITY","MP_BASE_COLOR","MP_REFRACTION"):
        try:
            prop=getattr(unreal.MaterialProperty,pname)
            node=editor.get_material_property_input_node(base,prop)
            record[pname+"_input_node"]=str(node)[:280]
        except Exception as e:
            record[pname+"_query_error"]=str(e)[:160]
except Exception:
    record["editor_query_unavailable"]=True
record["status"]="PARENT_GRAPH_OPACITY_READ_ONLY_REPORT"
OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",encoding="utf8")
print("TSTSS_V2_PARENT_OPACITY_REPORT",json.dumps(record,sort_keys=True))
