"""Independent second UE5.8.4 process for noncanonical Ionia V4 footing World."""
from pathlib import Path
import unreal,json,hashlib,traceback
PROJECT=Path("C:/TSTSS_AssetAssembly_20261104/unreal")
NEW="/Game/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V4_IONIA_FOOTING"
NEW_FILE=PROJECT/"Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V4_IONIA_FOOTING.umap"
V3=PROJECT/"Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3.umap"
BASE=PROJECT/"Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"
SHA="09ee6d30805bcb54a2b29f0dbfe7ec8975ea9e8abd15c1f8dda1fdf975c2ce3a"
V3_SHA="54b4e266683347fc950a56c8ac8691d99aaddb41d61e304ddf0f5b4d0730e2b5"
BASE_SHA="4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80"
OLD_BOUNDS=Path("C:/TSTSS_Review/firstwake_v3_native_geometry_bounds_20261104.json")
RECEIPT=PROJECT/"Saved/AssetAssemblyEvidence/ionia_footing_v4_independent_readback_20261104.json"
LABEL="TSTSS_ASSET_REVIEW_IONIA_STATIC_REVIEW_NOT_NPC"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(q,msg):
    if not q:raise RuntimeError("IONIA_READBACK_HOLD "+msg)
def coords(v):return [round(float(v.x),4),round(float(v.y),4),round(float(v.z),4)]
require(Path(unreal.Paths.project_dir()).resolve()==PROJECT.resolve(),"project path")
require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"wrong engine")
require(sha(NEW_FILE)==SHA and sha(V3)==V3_SHA and sha(BASE)==BASE_SHA,"source custody")
require(OLD_BOUNDS.is_file() and not RECEIPT.exists(),"prior evidence or destination")
report={"status":"HOLD","independent_engine_process":True,"native_world":NEW,
        "source_sha":SHA,"source_map_modified":False,"visual_art_approved":False,
        "gameplay_verified":False,"starbourne_unlocked":False}
try:
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(levels.load_level(NEW) is not False,"load saved V4 map")
    actors=list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
    require(len(actors)==34,"actor count")
    labels=[a.get_actor_label() for a in actors]
    require(sum(x.startswith("TSTSS_ASSET_REVIEW_") for x in labels)==10,"asset count")
    require(sum(isinstance(a,unreal.PlayerStart) for a in actors)==1,"player spawn")
    for name in ("FlyerDiscovery","IoniaHiring","AureateBoarding","LiftStation","PressureStation","ReserveStation","EngineeringApproval"):
        require(labels.count("TSTSS_PRELUDE_REVIEW_"+name)==1,"milestone "+name)
    require(not any("STARBourNE".upper() in x.upper() for x in labels),"locked form")
    old=json.loads(OLD_BOUNDS.read_text(encoding="utf8"))
    bylabel={e["label"]:e for e in old["entries"] if e["is_staged"]}
    current={a.get_actor_label():a for a in actors if a.get_actor_label().startswith("TSTSS_ASSET_REVIEW_")}
    require(set(bylabel)==set(current),"staged identity changed")
    for label,actor in current.items():
        center,ext=actor.get_actor_bounds(False)
        if label==LABEL:
            foot=float(center.z-ext.z)
            require(abs(foot)<0.02,"Ionia footing still below ground")
            require(abs(float(actor.get_actor_location().z)-165.5862)<0.05,
                    "Ionia review actor height drift")
            require(abs(float(actor.get_actor_location().x)-bylabel[label]["position_cm"][0])<0.05,
                    "Ionia x changed")
            require(abs(float(actor.get_actor_location().y)-bylabel[label]["position_cm"][1])<0.05,
                    "Ionia y changed")
            report["ionia_foot_z_cm"]=round(foot,5)
            report["ionia_actor_position_cm"]=coords(actor.get_actor_location())
        else:
            xyz=coords(actor.get_actor_location())
            expected=bylabel[label]["position_cm"]
            require(all(abs(a-b)<0.05 for a,b in zip(xyz,expected)),
                    "unrelated staged actor moved: "+label)
    require(sha(NEW_FILE)==SHA and sha(V3)==V3_SHA and sha(BASE)==BASE_SHA,"postload map mutation")
    report.update({"status":"INDEPENDENT_NATIVE_IONIA_FOOTING_V4_READBACK_PASS_NOT_PIE",
                   "actor_count":len(actors),"art_actor_count":len(current),"milestones":7,
                   "v4_map_sha256":sha(NEW_FILE),"v3_map_sha256_unchanged":sha(V3),
                   "base_map_sha256_unchanged":sha(BASE),"all_other_staged_actors_unchanged":True})
    unreal.log("IONIA_V4_INDEPENDENT_NATIVE_READBACK_PASS "+SHA)
except Exception:
    report["status"]="INDEPENDENT_IONIA_V4_READBACK_HOLD"
    report["error"]=traceback.format_exc()[-4800:]
    unreal.log_error("IONIA_V4_INDEPENDENT_READBACK_HOLD "+report["error"])
finally:
    RECEIPT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
if report["status"]!="INDEPENDENT_NATIVE_IONIA_FOOTING_V4_READBACK_PASS_NOT_PIE":
    raise RuntimeError("Independent Ionia V4 readback HOLD")
