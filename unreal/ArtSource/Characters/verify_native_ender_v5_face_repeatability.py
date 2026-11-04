"""Read-only Ender V5 landmark repeatability audit; no character saves."""
import hashlib,json,math
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve()
ALLOWED={
"c:/mh2/castallsandbox":"7d648da499e5756d845faeed221ac4584e51516d1274b766db41d908e1fb17bd",
"c:/mh4/castallsandbox":"2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"}
ROOT_KEY=ROOT.as_posix().lower()
if ROOT_KEY not in ALLOWED:raise RuntimeError("Refuse other project")
ASSET=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
BASELINE=Path(r"C:\MH2\CastAllSandbox\Saved\CharacterLookdev\EnderV5LandmarkAtlas\native_landmark_index.json")
OBJ="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase"
OUT=ROOT/"Saved/CharacterLookdev/V5Repeatability/landmark_diff01.json"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
if sha(ASSET)!=ALLOWED[ROOT_KEY] or sha(BASELINE)!="9abcca28c03b21c13a5a1f35bc5b2126393debbc63c494e268c6df18d74eafed" or OUT.exists():
    raise RuntimeError("FAIL_CLOSED input hash or output reused")
char=unreal.load_asset(OBJ)
sub=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
if char is None or sub is None:raise RuntimeError("No native MetaHuman editor")
registered=False
try:
    registered=bool(sub.try_add_object_to_edit(char))
    if not registered:raise RuntimeError("Cannot register")
    native=sub.get_face_landmarks(character=char)
    if native is None or len(native)!=79:raise RuntimeError("Unexpected index count")
    pts=[[round(float(v.x),5),round(float(v.y),5),round(float(v.z),5)] for v in native]
finally:
    if registered:sub.remove_object_to_edit(char)
baseline=json.loads(BASELINE.read_bytes())["points"]
diff=[]
for index,(observed,expected) in enumerate(zip(pts,[p["xyz_cm"] for p in baseline])):
    dist=math.dist(observed,expected)
    if dist!=0:
        diff.append({"index":index,"distance_cm":round(dist,7),"expected_cm":expected,"observed_cm":observed})
diff.sort(key=lambda x:-x["distance_cm"])
record={
"status":"NATIVE_REPEATABILITY_DIFFERENCES_MEASURED_NOT_INTERPRETED",
"source_asset_sha256":sha(ASSET),"project":ROOT.as_posix(),
"source_native_json_sha256":sha(BASELINE),
"native_count":79,
"exact_coordinate_matches":79-len(diff),
"mismatch_count":len(diff),
"maximum_difference_cm":diff[0]["distance_cm"] if diff else 0,
"diff_count_over_0_001_cm":sum(x["distance_cm"]>.001 for x in diff),
"diff_count_over_0_01_cm":sum(x["distance_cm"]>.01 for x in diff),
"diff_count_over_0_1_cm":sum(x["distance_cm"]>.1 for x in diff),
"first_20_differences":diff[:20],
"no_geometry_change_claim":True,"no_asset_edits":True,
"face_approved":False,"rigged":False}
if sha(ASSET)!=ALLOWED[ROOT_KEY]:raise RuntimeError("Source edited during read")
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("TSTSS_V5_REPEATABILITY",ROOT_KEY,record["mismatch_count"],record["maximum_difference_cm"])
