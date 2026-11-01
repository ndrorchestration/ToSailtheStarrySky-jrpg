"""Real GPU Unreal 5.8.4 renders of isolated Ender face/hair pilot.

This is a disposable review Automation Test. Outputs directly captured PNGs,
not raster transforms, no save and no canon/material promotion.
"""
from pathlib import Path
import json
import unreal

project=Path(unreal.Paths.project_dir()).resolve()
if "CastAllSandbox" not in project.name:
    raise RuntimeError("Only disposable CastAllSandbox is allowed")
receipt=json.loads((project/"Saved"/"CharacterLookdev"/"ender_fidelity_v2_map.json").read_text(encoding="utf-8"))
if receipt["status"]!="STAGED_NONCANON_REVIEW_MAP":raise RuntimeError("Missing staging proof")
world=unreal.EditorLoadingAndSavingUtils.load_map(receipt["map"])
if world is None:raise RuntimeError("Cannot load study map")
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
candidates=[a for a in actors if a.get_actor_label()=="NONCANON_ENDER_FIDELITY_V2"]
if len(candidates)!=1:raise RuntimeError("Expected exactly one study actor")
mesh=candidates[0].get_component_by_class(unreal.StaticMeshComponent)
if mesh is None or mesh.get_editor_property("static_mesh").get_path_name()!=receipt["mesh"]:
    raise RuntimeError("Unexpected static mesh")

sun=unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.DirectionalLight,unreal.Vector(0,0,500),
    unreal.Rotator(pitch=-35.0,yaw=35.0,roll=0.0),transient=True)
if sun is None:raise RuntimeError("No preview sun")
sun.get_component_by_class(unreal.DirectionalLightComponent).set_editor_property("intensity",0.5)
for x,y in ((350,350),(-350,350),(350,-350),(-350,-350)):
    light=unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PointLight,unreal.Vector(x,y,350),
        unreal.Rotator(pitch=0.0,yaw=0.0,roll=0.0),transient=True)
    if light:
        light.get_component_by_class(unreal.PointLightComponent).set_editor_property("intensity",1500.0)

def camera(name,at,yaw):
    actor=unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CameraActor,unreal.Vector(*at),
        unreal.Rotator(pitch=0.0,yaw=yaw,roll=0.0),transient=True)
    if not actor:raise RuntimeError("Camera spawn failed")
    actor.set_actor_label("STUDY_"+name)
    comp=actor.get_component_by_class(unreal.CameraComponent)
    comp.set_editor_property("field_of_view",44.0)
    settings=comp.get_editor_property("post_process_settings")
    settings.set_editor_property("override_auto_exposure_method",True)
    settings.set_editor_property("auto_exposure_method",unreal.AutoExposureMethod.AEM_MANUAL)
    settings.set_editor_property("override_auto_exposure_bias",True)
    settings.set_editor_property("auto_exposure_bias",5.0)
    comp.set_editor_property("post_process_settings",settings)
    comp.set_editor_property("post_process_blend_weight",1.0)
    return actor

views=[("Ender_v2_front",camera("front",(0,420,106),-90.0)),
       ("Ender_v2_three_quarter",camera("three_quarter",(300,300,106),-135.0))]
folder=project/"Saved"/"CharacterLookdev"/"EnderFidelityV2Native"
if folder.exists() and any(folder.iterdir()):
    raise RuntimeError("Refuse to overwrite render targets")
folder.mkdir(parents=True,exist_ok=True)
if not hasattr(unreal,"AutomationScheduler"):
    raise RuntimeError("PythonAutomationTest plugin not enabled")
print("ENDER_FIDELITY_V2_NATIVE_CAPTURE_QUEUED",len(views))
@unreal.AutomationScheduler.add_latent_command
def execute_captures():
    items=[]
    for name,cam in views:
        requested=str(folder/(name+".png"))
        task=unreal.AutomationLibrary.take_high_res_screenshot(
            1280,720,requested,camera=cam,delay=0.5,force_game_view=True)
        if not task.is_valid_task():raise RuntimeError("Invalid native capture request")
        n=0
        while not task.is_task_done():
            n+=1
            if n>1200:raise RuntimeError("Renderer timeout")
            yield
        items.append({"name":name,"requested":requested,"ticks":n})
        print("ENDER_FIDELITY_V2_NATIVE_CAPTURE_DONE",name,n)
    (folder/"task_receipt.json").write_text(json.dumps(
      {"status":"NATIVE_CAPTURE_TASKS_PASS_NOT_VISUAL_APPROVAL",
      "engine":unreal.SystemLibrary.get_engine_version(),
      "map":receipt["map"],"capture_tasks":items,
      "approved_likeness":False},indent=2)+"\n")
