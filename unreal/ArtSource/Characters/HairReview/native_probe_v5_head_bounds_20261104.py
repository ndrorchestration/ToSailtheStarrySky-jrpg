"""Unreal 5.8.4 real Ender V5 head extent probe, transient and review-only."""
import json,hashlib,traceback
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve()
META=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
MS="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
LS="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
DEST=ROOT/"Saved/CharacterLookdev/EnderHairReviewV1/NativeHeadBounds01"
FILE=DEST/"head_bounds.json"
def require(ok,label):
    if not ok:raise RuntimeError("FAIL_CLOSED "+label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def coords(v):return [round(float(getattr(v,k)),5) for k in ("x","y","z")]
require(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","wrong sandbox")
require("goggles fitting experiment (MH5)" in (ROOT/"CastAllSandbox.uproject").read_text(encoding="utf-8-sig"),"no sandbox marker")
require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"wrong engine")
require(sha(META)==MS and sha(MAP)==LS,"baseline hashes")
require(not DEST.exists(),"never overwrite previous receipt")
DEST.mkdir(parents=True)
record={"status":"IN_PROGRESS","original_art":False,"read_only":True,
        "source_meta_sha256":MS,"source_map_sha256":LS,"face_approved":False,
        "hair_fit_approved":False,"gameplay_modified":False,"source_assets_saved":False}
def save():FILE.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
try:
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(sub.load_level("/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review") is not False,"review map")
    char=unreal.load_asset("/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase")
    require(isinstance(char,unreal.MetaHumanCharacter),"real MHC")
    unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets(assets=[char])
    editor=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
    actor=editor.spawn_meta_human_actor(character=char)
    require(actor is not None,"preview actor")
    record["actor_origin_world_cm"]=coords(actor.get_actor_location())
    record["components"]=[]
    for c in actor.get_components_by_class(unreal.SkeletalMeshComponent):
        row={"name":c.get_name()}
        try:
            origin,ext,radius=c.get_component_bounds()
            row["world_origin_cm"]=coords(origin)
            row["world_extent_cm"]=coords(ext)
            row["radius_cm"]=round(float(radius),4)
        except Exception as ex:row["bounds_unavailable"]=str(ex)[:200]
        for bone in ("head","Head","head_01","FACIAL_C_FacialRoot","neck_01"):
            try:
                idx=int(c.get_bone_index(bone))
                if idx>=0:
                    row.setdefault("probe_bones",{})[bone]={"idx":idx,"world_cm":coords(c.get_socket_location(bone))}
            except Exception:pass
        record["components"].append(row)
    require("Face" in [c["name"] for c in record["components"]],"Face component missing")
    record["meta_sha256_after"]=sha(META)
    record["map_sha256_after"]=sha(MAP)
    require(record["meta_sha256_after"]==MS and record["map_sha256_after"]==LS,"source changed")
    record["status"]="NATIVE_V5_SKELETAL_COMPONENT_BOUNDS_READBACK_PASS_ART_HOLD"
except Exception:
    record["status"]="PROBE_FAILED"
    record["error"]=traceback.format_exc()[-2000:]
    record["meta_sha256_after"]=sha(META)
    record["map_sha256_after"]=sha(MAP)
    save();raise
save()
unreal.log("ENDER_V5_HEAD_BOUNDS "+str(FILE))
