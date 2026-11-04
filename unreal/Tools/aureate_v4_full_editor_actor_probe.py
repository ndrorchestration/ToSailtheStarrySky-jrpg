"""One-actor test in full Unreal Editor, standalone disposable project only.

No production assets, no existing V4 sandbox, no request_form, no user Editor.
Saves only one dedicated map when actor existence is established.
"""
import hashlib
import json
import traceback
from pathlib import Path
import unreal

ROOT=Path("C:/tmp/TSTSS_AureateV4_ActorPilot_20261103")
PROJ=ROOT/"AureateActorPilot"
PROJECT_FILE=PROJ/"AureateActorPilot.uproject"
OUT=ROOT/"full_editor_actor_probe_receipt.json"
LEVEL="/Game/AureateV4ActorPilot/OneActor_20261103"
REPORT={"state":"NOT_VERIFIED","scope":"NONCANONICAL_SINGLE_ACTOR_PILOT",
        "story_starbourne_player_unlock":False,"gameplay_modified":False,
        "production_map_modified":False,"source_user_editor_modified":False}
if OUT.exists():raise FileExistsError("Existing pilot receipt; refuse repeated probe")
try:
    assert Path(unreal.Paths.project_dir()).resolve()==PROJ.resolve(),"Wrong Unreal project"
    p=json.loads(PROJECT_FILE.read_text(encoding="utf-8-sig"))
    assert p.get("EngineAssociation")=="5.8"
    assert "AUREATE_ONE_ACTOR_PILOT_ONLY" in p.get("Description","")
    assert unreal.SystemLibrary.get_engine_version().startswith("5.8.")
    lib=unreal.EditorAssetLibrary
    if lib.does_asset_exist(LEVEL): raise FileExistsError("Refuse existing pilot map")
    level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    REPORT["engine"]=unreal.SystemLibrary.get_engine_version()
    REPORT["level_subsystem"]=str(level)[:120]
    if hasattr(level,"new_level"):
        created=level.new_level(LEVEL)
    else:
        created=unreal.EditorLevelLibrary.new_level(LEVEL)
    if not created:raise RuntimeError("Could not make fresh pilot map")
    if not level.load_level(LEVEL): raise RuntimeError("Cannot reload pilot map")
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world is None:raise RuntimeError("Full Editor world is missing")
    if len(actors.get_all_level_actors())!=0:
        raise RuntimeError("Expected empty new level")
    primitive=unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if not isinstance(primitive,unreal.StaticMesh):raise RuntimeError("Built-in cube absent")
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,
                                   unreal.Vector(0,0,90),unreal.Rotator(0,0,0))
    if a is None:raise RuntimeError("Full Editor spawn_actor_from_class returned None")
    comp=a.get_component_by_class(unreal.StaticMeshComponent)
    if comp is None:raise RuntimeError("Spawned actor lacked StaticMeshComponent")
    comp.set_static_mesh(primitive)
    comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    a.set_actor_enable_collision(False)
    a.set_actor_label("NONCANONICAL_V4_FULL_EDITOR_ONE_ACTOR_PROBE")
    found=[x for x in actors.get_all_level_actors()
           if x.get_actor_label()=="NONCANONICAL_V4_FULL_EDITOR_ONE_ACTOR_PROBE"]
    if len(found)!=1:raise RuntimeError("Probe actor not observable after spawn")
    if not level.save_current_level():raise RuntimeError("Saving actor pilot level failed")
    mapfile=PROJ/"Content"/"AureateV4ActorPilot"/"OneActor_20261103.umap"
    if not mapfile.is_file():raise RuntimeError("Saved pilot .umap file missing")
    REPORT.update({"state":"NATIVE_FULL_EDITOR_ONE_ACTOR_AND_MAP_SAVE_PASS",
                   "map_path":LEVEL,
                   "map_sha256":hashlib.sha256(mapfile.read_bytes()).hexdigest(),
                   "actor_count":len(found),"actor_label":found[0].get_actor_label(),
                   "review_only_scene_saved":True})
except Exception as exc:
    REPORT["state"]="NATIVE_FULL_EDITOR_ACTOR_PILOT_FAILED"
    REPORT["error"]=str(exc)
    REPORT["trace"]=traceback.format_exc()[-3500:]
finally:
    OUT.write_text(json.dumps(REPORT,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    unreal.log("TSTSS_V4_ACTOR_PILOT "+json.dumps(REPORT,sort_keys=True))
if REPORT["state"]!="NATIVE_FULL_EDITOR_ONE_ACTOR_AND_MAP_SAVE_PASS":
    raise RuntimeError(REPORT.get("error","Actor pilot failed"))
