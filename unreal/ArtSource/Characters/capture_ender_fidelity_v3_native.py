"""Isolated Unreal 5.8 native closeup capture: Ender V3 NOT approved art.

Requires previously SHA-proven native V3 static mesh import, unchanged V2 map.
Transient actor/cameras/lights only; never save level, import, or replace assets.
"""
import hashlib
import json
from pathlib import Path
import unreal

PROJECT=Path(unreal.Paths.project_dir()).resolve()
if PROJECT.name!="CastAllSandbox":
    raise RuntimeError("Refusing production Unreal project")
SOURCE_SHA="0fb1b6e8de8d84ce751ce8bbb97b7ca78174e077acf64f60e127bd0ddb90c2de"
MAP="/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
REC=PROJECT/"Saved"/"CharacterLookdev"/"ender_head_v3_native_intake.json"
r=json.loads(REC.read_text(encoding="utf-8"))
if r["status"]!="NATIVE_IMPORT_PASS_ART_UNAPPROVED" or r["source_sha256"]!=SOURCE_SHA:
    raise RuntimeError("Unverified V3 native receipt")
if not r["asset"].startswith("/Game/ArtLookdev/Characters/EnderLandmarksV3/"):
    raise RuntimeError("Native asset points outside review destination")
if r["creator_approval"] is not False or r["skin_or_rigged"] is not False:
    raise RuntimeError("Art state improperly promoted")
MAP_PATH=PROJECT/"Content"/"ArtLookdev"/"ReviewMaps"/"TSTSS_EnderFidelityV2_Review.umap"
before=hashlib.sha256(MAP_PATH.read_bytes()).hexdigest()
if before!=MAP_SHA:
    raise RuntimeError("Original review map SHA drift")
if unreal.EditorLoadingAndSavingUtils.load_map(MAP) is None:
    raise RuntimeError("V2 saved disposable reference map missing")
existing=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
v2=[actor for actor in existing if actor.get_actor_label()=="NONCANON_ENDER_FIDELITY_V2"]
if len(v2)!=1:
    raise RuntimeError("Expected original V2 actor exactly once")
v2[0].set_actor_location(unreal.Vector(15000,0,0),False,False)  # transient, NOT saved
mesh=unreal.load_asset(r["asset"])
if not isinstance(mesh,unreal.StaticMesh):
    raise RuntimeError("V3 must remain imported StaticMesh, not a skeletal pawn")
actor=unreal.EditorLevelLibrary.spawn_actor_from_object(
    mesh,unreal.Vector(0,0,0),unreal.Rotator(pitch=0.0,yaw=0.0,roll=0.0))
if actor is None:raise RuntimeError("Could not spawn native V3 preview actor")
actor.set_actor_label("NONCANON_ENDER_HEAD_V3_TRANSIENT")
actor.set_actor_enable_collision(False)
sun=unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.DirectionalLight,unreal.Vector(0,0,450),
    unreal.Rotator(pitch=-35.0,yaw=35.0,roll=0.0),transient=True)
if sun is None:raise RuntimeError("No comparison sun")
sun.get_component_by_class(unreal.DirectionalLightComponent).set_editor_property("intensity",0.45)
for xyz in ((300,240,270),(-300,240,270),(0,-350,290)):
    lamp=unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PointLight,unreal.Vector(*xyz),
        unreal.Rotator(pitch=0.0,yaw=0.0,roll=0.0),transient=True)
    if lamp is None:raise RuntimeError("Studio point light unavailable")
    lamp.get_component_by_class(unreal.PointLightComponent).set_editor_property("intensity",750.0)

def cam(name,xyz,yaw):
    camera=unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CameraActor,unreal.Vector(*xyz),
        unreal.Rotator(pitch=0.0,yaw=yaw,roll=0.0),transient=True)
    if camera is None:raise RuntimeError("Camera spawn failure "+name)
    camera.set_actor_label("NONCANON_ENDER_V3_"+name)
    comp=camera.get_component_by_class(unreal.CameraComponent)
    comp.set_editor_property("field_of_view",40.0)
    settings=comp.get_editor_property("post_process_settings")
    settings.set_editor_property("override_auto_exposure_method",True)
    settings.set_editor_property("auto_exposure_method",unreal.AutoExposureMethod.AEM_MANUAL)
    settings.set_editor_property("override_auto_exposure_bias",True)
    settings.set_editor_property("auto_exposure_bias",3.0)
    comp.set_editor_property("post_process_settings",settings)
    comp.set_editor_property("post_process_blend_weight",1.0)
    return camera

VIEWS=[
    ("v3_head_front",cam("front",(0,175,151),-90.0)),
    ("v3_head_three_quarter",cam("three_quarter",(120,120,151),-135.0)),
    ("v3_head_profile",cam("profile",(175,0,151),-180.0)),
]
OUT=PROJECT/"Saved"/"CharacterLookdev"/"EnderHeadV3Native"
if OUT.exists():raise RuntimeError("Refusing overwrite of prior V3 render receipt")
OUT.mkdir(parents=True)
if not hasattr(unreal,"AutomationScheduler"):
    raise RuntimeError("No native screenshot automation plugin")
print("ENDER_V3_NATIVE_CAPTURE_QUEUED",len(VIEWS))
@unreal.AutomationScheduler.add_latent_command
def capture():
    tasks=[]
    for name,camera in VIEWS:
        requested=str(OUT/(name+".png"))
        t=unreal.AutomationLibrary.take_high_res_screenshot(
            1280,720,requested,camera=camera,delay=.5,force_game_view=True)
        if not t.is_valid_task():
            raise RuntimeError("Unreal refused screenshot request")
        ticks=0
        while not t.is_task_done():
            ticks+=1
            if ticks>1200:raise RuntimeError("Unreal screenshot timeout "+name)
            yield
        tasks.append({"name":name,"requested":requested,"ticks":ticks})
        print("ENDER_V3_NATIVE_CAPTURE_TASK_DONE",name,ticks)
    after=hashlib.sha256(MAP_PATH.read_bytes()).hexdigest()
    if after!=before:
        raise RuntimeError("Baseline map modified: fail closed")
    receipt={
      "status":"V3_NATIVE_SCREENSHOT_TASKS_COMPLETE_PIXEL_QA_PENDING",
      "engine":unreal.SystemLibrary.get_engine_version(),
      "map":MAP,"saved_map_sha256_before":before,"saved_map_sha256_after":after,
      "asset":r["asset"],"source_sha256":SOURCE_SHA,
      "views":[name for name,_ in VIEWS],
      "capture_tasks":tasks,
      "unrigged":True,"creator_likeness_approved":False,
      "source_modified":False,"production_map_modified":False,
    }
    (OUT/"capture_task_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
