"""Reopen saved MH4 Ender V5 and verify iris material parameters persisted."""
import hashlib,json
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve()
ASSET=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
OBJ="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase"
EXPECTED_ASSET="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
EXPECTED_MAP="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
TINT=(0.25,0.78,0.24,1.0)
SATURATION=1.35
OUT=ROOT/"Saved/CharacterLookdev/EnderV5EyeLookdev/green_iris_reopen_verification01.json"
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
if ROOT.as_posix().lower()!="c:/mh4/castallsandbox" or OUT.exists():
    raise RuntimeError("FAIL_CLOSED wrong clone or existing receipt")
if sha(ASSET)!=EXPECTED_ASSET or sha(MAP)!=EXPECTED_MAP:
    raise RuntimeError("FAIL_CLOSED expected serialized input hash not found")
character=unreal.load_asset(OBJ)
if not isinstance(character,unreal.MetaHumanCharacter):
    raise RuntimeError("Not a MetaHumanCharacter")
eyes=character.eyes_settings
observed={}
for side in ("eye_left","eye_right"):
    iris=getattr(eyes,side).iris
    color=iris.global_tint
    rgba=[float(color.r),float(color.g),float(color.b),float(color.a)]
    sat=float(iris.global_saturation)
    if any(abs(a-b)>0.001 for a,b in zip(rgba,TINT)) or abs(sat-SATURATION)>0.001:
        raise RuntimeError("FAIL_CLOSED reloaded iris values differ: "+str((side,rgba,sat)))
    observed[side]={"global_tint_rgba":rgba,"saturation":sat}
report={
    "status":"REOPENED_SAVED_V5_GREEN_IRIS_PARAMETER_PASS",
    "source_engine":unreal.SystemLibrary.get_engine_version(),
    "sandbox":"C:/MH4/CastAllSandbox",
    "saved_asset_sha256":sha(ASSET),"review_map_sha256":sha(MAP),
    "observed":observed,
    "native_render_verified":False,"rigged":False,
    "face_landmarks_mapped":False,"creator_likeness_approved":False,
    "canonical_art":False,"source_v5_updated":False,
}
OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("TSTSS_V5_GREEN_IRIS_RELOAD_PASS",str(OUT))
