"""TSTSS Ender V5: canonical green-eye parameter study ONLY in MH4 clone.

No facial geometry, hair color, rig, textures, original project, or game asset edits.
Output is still noncanonical until native render and creator likeness approval.
"""
import hashlib
import json
import traceback
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
PROJECT=ROOT/"CastAllSandbox.uproject"
ASSET=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
EXPECTED="7d648da499e5756d845faeed221ac4584e51516d1274b766db41d908e1fb17bd"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
OBJ="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase"
OUT=ROOT/"Saved/CharacterLookdev/EnderV5EyeLookdev/green_iris_parameter_study02.json"
TINT=(0.25,0.78,0.24,1.0)
SATURATION=1.35

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
if ROOT.as_posix().lower()!="c:/mh4/castallsandbox":
    raise RuntimeError("FAIL_CLOSED wrong project")
if not PROJECT.is_file() or "green-eye lookdev clone (MH4)" not in PROJECT.read_text(encoding="utf-8-sig"):
    raise RuntimeError("FAIL_CLOSED missing sandbox provenance")
if sha(ASSET)!=EXPECTED or sha(MAP)!=MAP_SHA:
    raise RuntimeError("FAIL_CLOSED changed source asset or map")
if OUT.exists():
    raise FileExistsError("FAIL_CLOSED refuses to overwrite output")
if not unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"):
    raise RuntimeError("FAIL_CLOSED wrong engine")
character=unreal.load_asset(OBJ)
if not isinstance(character,unreal.MetaHumanCharacter):
    raise TypeError("FAIL_CLOSED not the Ender V5 MetaHumanCharacter")
report={
  "status":"NOT_STARTED","source_uasset_sha256":EXPECTED,"source_map_sha256":MAP_SHA,
  "engine":unreal.SystemLibrary.get_engine_version(),
  "sandbox":"C:/MH4/CastAllSandbox","authoring_scope":"IRIS_MATERIAL_PARAMETERS_ONLY",
  "tint_rgba":TINT,"global_saturation":SATURATION,
  "no_face_landmark_edits":True,"no_hair_color_decision":True,
  "no_cloud_request":True,"no_download":True,"no_purchase":True,
  "not_rendered":True,"not_rigged":True,"not_animated":True,
  "creator_accepted":False,"canonical_art_promoted":False,
  "no_game_project_edit":True,"no_original_v5_edit":True,
}
OUT.parent.mkdir(parents=True,exist_ok=True)
def write():
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
write()
try:
    settings=character.eyes_settings
    before={}
    after={}
    for side in ("eye_left","eye_right"):
        eye=getattr(settings,side)
        iris=eye.iris
        before[side]={"tint":repr(iris.global_tint),"saturation":float(iris.global_saturation)}
        iris.global_tint=unreal.LinearColor(*TINT)
        iris.global_saturation=SATURATION
        eye.iris=iris
        setattr(settings,side,eye)
    character.eyes_settings=settings
    result=bool(unreal.EditorAssetLibrary.save_loaded_asset(character, only_if_is_dirty=False))
    if not result:raise RuntimeError("Unreal save_loaded_asset returned false")
    settings=character.eyes_settings
    for side in ("eye_left","eye_right"):
        iris=getattr(settings,side).iris
        after[side]={"tint":repr(iris.global_tint),"saturation":float(iris.global_saturation)}
        if abs(float(iris.global_saturation)-SATURATION)>0.001:
            raise RuntimeError("Eye saturation did not persist in editor")
    report["before"]=before
    report["after"]=after
    report["sandbox_asset_sha256_after"]=sha(ASSET)
    report["sandbox_asset_changed"]=report["sandbox_asset_sha256_after"]!=EXPECTED
    if not report["sandbox_asset_changed"]:
        raise RuntimeError("No serialized asset change detected")
    if sha(MAP)!=MAP_SHA:raise RuntimeError("Review map changed")
    report["status"]="SAVED_GREEN_IRIS_PARAMETERS_NEEDS_NATIVE_RENDER_REVIEW"
except Exception:
    report["status"]="PARAMETER_STUDY_FAILED"
    report["error"]=traceback.format_exc()[-2500:]
    unreal.log_error("TSTSS_V5_GREEN_EYES_FAILED "+report["error"])
finally:
    report["sandbox_asset_sha256_final"]=sha(ASSET)
    report["sandbox_map_sha256_final"]=sha(MAP)
    write()
print("TSTSS_V5_GREEN_EYES",report["status"],str(OUT))
