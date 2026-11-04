"""One reversible Ionia footing correction in a NEW noncanonical First Wake V4 review World."""
from pathlib import Path
import hashlib,json,traceback
import unreal
PROJECT=Path("C:/TSTSS_AssetAssembly_20261104/unreal")
OLD="/Game/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3"
NEW="/Game/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V4_IONIA_FOOTING"
OLD_FILE=PROJECT/"Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3.umap"
NEW_FILE=PROJECT/"Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V4_IONIA_FOOTING.umap"
BASE=PROJECT/"Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"
OLD_SHA="54b4e266683347fc950a56c8ac8691d99aaddb41d61e304ddf0f5b4d0730e2b5"
BASE_SHA="4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80"
RECEIPT=PROJECT/"Saved/AssetAssemblyEvidence/ionia_footing_new_world_v4_native_20261104.json"
LABEL="TSTSS_ASSET_REVIEW_IONIA_STATIC_REVIEW_NOT_NPC"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(cond,msg):
    if not cond:raise RuntimeError("IONIA_V4_HOLD "+msg)
def trip(v):return [round(float(v.x),5),round(float(v.y),5),round(float(v.z),5)]
require(Path(unreal.Paths.project_dir()).resolve()==PROJECT.resolve(),"project path")
require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"engine version")
require(OLD_FILE.is_file() and sha(OLD_FILE)==OLD_SHA,"source review map hash")
require(BASE.is_file() and sha(BASE)==BASE_SHA,"original prelude map hash")
require(not NEW_FILE.exists() and not RECEIPT.exists(),"unique destination already exists")
require(not list((PROJECT/"Saved/SaveGames").glob("*.sav")),"protected saves exist")
record={"status":"NOT_STARTED","source_map_sha_expected":OLD_SHA,"base_map_sha_expected":BASE_SHA,
        "art_authority":"NONCANONICAL_VIEW_ONLY","asset_modified":False,
        "production_game_modified":False,"art_approved":False,"starbourne_unlocked":False,
        "animated_rig_verified":False,"visual_composition_approved":False,
        "destination_map":NEW,"exact_scene_control":"ONE_NEW_MAP_ONLY"}
try:
    lib=unreal.EditorAssetLibrary
    require(lib.does_asset_exist(OLD),"source map missing in registry")
    require(not lib.does_asset_exist(NEW),"new map path occupied")
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(bool(levels.new_level_from_template(NEW,OLD)),"native new-map operation failed")
    actorapi=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=list(actorapi.get_all_level_actors())
    require(len(actors)==34,"original actor count changed")
    matches=[a for a in actors if a.get_actor_label()==LABEL]
    require(len(matches)==1,"Ionia model not unique")
    ionia=matches[0]
    before=ionia.get_actor_location()
    center,ext=ionia.get_actor_bounds(False)
    old_foot=float(center.z-ext.z)
    require(-168.0 < old_foot < -163.0,"Ionia bounds unexpected; fail without manual guess")
    offset=-old_foot
    adjusted=unreal.Vector(before.x,before.y,before.z+offset)
    require(ionia.set_actor_location(adjusted,False,False) is not False,
            "native actor translation rejected")
    after_center,after_ext=ionia.get_actor_bounds(False)
    new_foot=float(after_center.z-after_ext.z)
    require(abs(new_foot)<0.02,"Ionia remains below/above ground: "+str(new_foot))
    require(abs(float(after_center.x-center.x))<0.02 and
            abs(float(after_center.y-center.y))<0.02,"horizontal placement drift")
    labels=[a.get_actor_label() for a in actors]
    require(sum(a.startswith("TSTSS_ASSET_REVIEW_") for a in labels)==10,
            "staged assets incomplete")
    require(sum(isinstance(a,unreal.PlayerStart) for a in actors)==1,"PlayerStart incomplete")
    for stop in ("FlyerDiscovery","IoniaHiring","AureateBoarding","LiftStation","PressureStation","ReserveStation","EngineeringApproval"):
        require(labels.count("TSTSS_PRELUDE_REVIEW_"+stop)==1,"First Wake order actor missing "+stop)
    require(not any("STARBOURNE" in label.upper() for label in labels),"Starbourne must stay closed")
    require(bool(levels.save_current_level()),"new native World save failed")
    require(NEW_FILE.is_file() and NEW_FILE.stat().st_size>20000,"missing saved World")
    require(sha(OLD_FILE)==OLD_SHA and sha(BASE)==BASE_SHA,"source map or original changed")
    record.update({"status":"NEW_NATIVE_V4_IONIA_FOOTING_WORLD_SAVED_PENDING_SEPARATE_READBACK",
         "old_world_sha256_after":sha(OLD_FILE),"base_world_sha256_after":sha(BASE),
         "new_world_sha256":sha(NEW_FILE),"original_ionia_actor_location_cm":trip(before),
         "new_ionia_actor_location_cm":trip(ionia.get_actor_location()),
         "old_ionia_foot_z_cm":round(old_foot,5),
         "new_ionia_foot_z_cm":round(new_foot,5),"ionia_translation_z_cm":round(offset,5),
         "actor_count":len(actors),"staged_art_count":10,"first_wake_milestones":7,
         "player_start_count":1,"new_world_saved":True,
         "independent_readback_verified":False})
    unreal.log("FIRSTWAKE_IONIA_V4_NEW_WORLD_SAVED "+record["new_world_sha256"])
except Exception:
    record["status"]="V4_IONIA_STAGE_HOLD"
    record["error"]=traceback.format_exc()[-4500:]
    unreal.log_error("FIRSTWAKE_IONIA_V4_HOLD "+record["error"])
finally:
    RECEIPT.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n",encoding="utf8")
if record["status"]!="NEW_NATIVE_V4_IONIA_FOOTING_WORLD_SAVED_PENDING_SEPARATE_READBACK":
    raise RuntimeError("V4 stage not accepted")
