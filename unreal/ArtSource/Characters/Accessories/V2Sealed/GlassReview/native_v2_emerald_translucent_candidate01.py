"""Fail-closed isolated V2 lens material candidate, Unreal 5.8.4.

Clone only the existing imported EmeraldGlass MaterialInstanceConstant. Enable
the *instance's* translucent blend-mode override in the clone, NOT the original
asset. Keep review-only; no game merge or MetaHuman/gameplay edits.
"""
import hashlib,json,traceback
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
SOURCE="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/Accessories/SealedGogglesCandidateV2/Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL/Materials/EmeraldGlass.EmeraldGlass"
DEST="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/Accessories/V2GlassReview/MI_EmeraldGlass_Translucent_ReviewOnly"
DISK=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/Accessories/SealedGogglesCandidateV2/Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL/Materials/EmeraldGlass.uasset"
META=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
GLB=Path(r"C:\Users\Admin\work\TSTSS-V5-FaceAuthorityReview-20261103\V2_Sealed_Goggles_Output\Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL.glb")
OUT=ROOT/"Saved/CharacterLookdev/GogglesFitV2/V2GlassMaterialReview01/candidate_receipt.json"
SHA_SOURCE_MAT="7cc4c66de27c3dad87a80c25d34eacc5606bd50d8b6969e239a8481637f00846"
SHA_META="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
SHA_MAP="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
SHA_GLB="5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guard(cond,msg):
    if not cond:raise RuntimeError("FAIL_CLOSED "+msg)
guard(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","only disposable MH5")
guard(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"engine changed")
guard(sha(DISK)==SHA_SOURCE_MAT and sha(META)==SHA_META and sha(MAP)==SHA_MAP and sha(GLB)==SHA_GLB,"source hashes")
guard(not OUT.exists(),"receipt already exists")
library=unreal.EditorAssetLibrary
guard(not library.does_asset_exist(DEST),"refuse overwrite candidate material")
orig=unreal.load_asset(SOURCE)
guard(orig is not None and orig.get_class().get_name()=="MaterialInstanceConstant","original glass instance")
origov=orig.get_editor_property("base_property_overrides")
guard(not origov.get_editor_property("override_blend_mode"),"source already overrides blend")
guard(str(orig.get_base_material().get_editor_property("blend_mode")).endswith("BLEND_OPAQUE: 0>"),"source parent changed")
OUT.parent.mkdir(parents=True,exist_ok=True)
receipt={"status":"CANDIDATE_CREATION_STARTED","source_material":SOURCE,"review_candidate":DEST,
 "source_original_material_sha256":SHA_SOURCE_MAT,
 "source_meta_sha256":SHA_META,"source_map_sha256":SHA_MAP,"source_goggles_sha256":SHA_GLB,
 "source_material_edited":False,"game_assets_edited":False,
 "author_approved":False,"physically_correct_glass_approved":False,
 "head_fit_verified":False,"rendered_in_unreal":False}
def save():OUT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf8")
save()
try:
    candidate=library.duplicate_asset(SOURCE,DEST)
    guard(candidate is not None,"material duplicate failed")
    ov=candidate.get_editor_property("base_property_overrides")
    ov.set_editor_property("override_blend_mode",True)
    ov.set_editor_property("blend_mode",unreal.BlendMode.BLEND_TRANSLUCENT)
    candidate.set_editor_property("base_property_overrides",ov)
    guard(library.save_loaded_asset(candidate),"candidate save failed")
    readback=unreal.load_asset(DEST)
    over=readback.get_editor_property("base_property_overrides")
    receipt["candidate_override_blend_mode"]=bool(over.get_editor_property("override_blend_mode"))
    receipt["candidate_blend_mode"]=str(over.get_editor_property("blend_mode"))
    guard(receipt["candidate_override_blend_mode"],"translucent override not enabled")
    guard("BLEND_TRANSLUCENT" in receipt["candidate_blend_mode"],"translucent blend mode not set")
    receipt["status"]="NATIVE_V2_EMERALD_GLASS_CLONE_TRANSLUCENT_OVERRIDE_PASS_REVIEW_ONLY"
except Exception:
    receipt["status"]="CANDIDATE_CREATION_FAILED"
    receipt["error"]=traceback.format_exc()[-3000:]
    unreal.log_error("TSTSS_V2_EMERALD_CANDIDATE_FAIL "+receipt["error"])
finally:
    receipt["source_material_after_sha256"]=sha(DISK)
    receipt["source_meta_after_sha256"]=sha(META)
    receipt["source_map_after_sha256"]=sha(MAP)
    receipt["source_glb_after_sha256"]=sha(GLB)
    if receipt["source_material_after_sha256"]!=SHA_SOURCE_MAT or receipt["source_meta_after_sha256"]!=SHA_META or receipt["source_map_after_sha256"]!=SHA_MAP or receipt["source_glb_after_sha256"]!=SHA_GLB:
        receipt["status"]="FAIL_PROTECTED_SOURCE_ASSET_MUTATED"
    save()
print("TSTSS_V2_EMERALD_CANDIDATE",receipt["status"],DEST)
