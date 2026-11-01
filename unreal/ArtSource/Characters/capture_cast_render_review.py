"""UE5.8 renderer-enabled review captures of isolated, noncanonical static cast.

This script never saves the level or modifies the playable game. Requires the
previous all-cast intake and fresh-reload evidence in a disposable project.
"""
import json
import os
from pathlib import Path
import sys
import unreal

if not hasattr(unreal, 'AutomationScheduler'):
    raise RuntimeError('PythonAutomationTest plugin is required for latent screenshot capture')

EXPECTED = ("Ender", "Ionia", "Lyra", "Reson", "Aepex")
MAP = "/Game/ArtLookdev/ReviewMaps/TSTSS_CastLineup_Review"
PROJECT = Path(unreal.Paths.project_dir()).resolve()
EVIDENCE = PROJECT / "Saved" / "CharacterLookdev"
OUT = EVIDENCE / "RendererReview_20261101_v5"
if "CastAllSandbox" not in PROJECT.name:
    raise RuntimeError("Refuse renderer test outside disposable CastAllSandbox")
if not (EVIDENCE / "cast_lineup_reload.json").is_file():
    raise RuntimeError("Missing independent persisted-map reload verification")
if OUT.exists() and any(OUT.iterdir()):
    raise RuntimeError("Existing renderer evidence: no overwrite")
OUT.mkdir(parents=True, exist_ok=True)
world = unreal.EditorLoadingAndSavingUtils.load_map(MAP)
if world is None:
    raise RuntimeError("Review map did not reload")
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
by_label = {a.get_actor_label(): a for a in actors}
for name in EXPECTED:
    actor = by_label.get("LOOKDEV_STATIC_" + name)
    if actor is None:
        raise RuntimeError("Missing cast actor " + name)
    comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    mesh = comp.get_editor_property("static_mesh") if comp else None
    if mesh is None or not mesh.get_path_name().startswith("/Game/ArtLookdev/Characters/" + name + "/"):
        raise RuntimeError("Unexpected mesh for " + name)
# Native importer has already converted source geometry into upright Z-up centimetres.
# Never apply an experimental actor roll to a visually reviewed character.
for name in EXPECTED:
    actor = by_label["LOOKDEV_STATIC_" + name]
    bounds = actor.get_component_by_class(unreal.StaticMeshComponent).get_editor_property("static_mesh").get_bounding_box()
    if bounds.min.z < -5 or bounds.max.z < 150:
        raise RuntimeError(name + ": unexpected imported vertical bounds")
    rot = actor.get_actor_rotation()
    if any(abs(v) > 0.01 for v in (rot.pitch, rot.yaw, rot.roll)):
        raise RuntimeError(name + ": unexpected review actor rotation")
if "CALIBRATION_180CM_NONCANON" not in by_label:
    raise RuntimeError("Calibration actor absent")

# Scene lighting and cameras are temporary editor actors; the source map
# remains on disk unchanged and no save_current_level is invoked.
sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.DirectionalLight, unreal.Vector(0, 0, 450),
    unreal.Rotator(-35, 35, 0), transient=True)
if sun is None:
    raise RuntimeError("Temporary directional light could not spawn")
sun.get_component_by_class(unreal.DirectionalLightComponent).set_editor_property('intensity', 0.5)
for pos in ((450, -450, 300), (-450, -450, 300), (50, 50, 300), (50, -950, 300)):
    light = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PointLight, unreal.Vector(*pos), unreal.Rotator(0, 0, 0), transient=True)
    if light is not None:
        light.get_component_by_class(unreal.PointLightComponent).set_editor_property("intensity", 1500.0)

def cam(label, pos, yaw, fov):
    c = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CameraActor, unreal.Vector(*pos), unreal.Rotator(0, yaw, 0), transient=True)
    if c is None:
        raise RuntimeError("Cannot spawn camera " + label)
    c.set_actor_label("REVIEW_CAMERA_" + label)
    component = c.get_component_by_class(unreal.CameraComponent)
    if component is None:
        raise RuntimeError('Camera component unavailable')
    component.set_editor_property('field_of_view', float(fov))
    settings = component.get_editor_property('post_process_settings')
    settings.set_editor_property('override_auto_exposure_method', True)
    settings.set_editor_property('auto_exposure_method', unreal.AutoExposureMethod.AEM_MANUAL)
    settings.set_editor_property('override_auto_exposure_bias', True)
    settings.set_editor_property('auto_exposure_bias', 5.0)
    component.set_editor_property('post_process_settings', settings)
    component.set_editor_property('post_process_blend_weight', 1.0)
    return c

cameras = [
    ("Ender_front", cam("Ender_front", (420, -460, 102), 180, 44), (1280, 720)),
    ("Ender_profile", cam("Ender_profile", (0, -180, 102), -90, 44), (1280, 720)),
    ("Ender_back", cam("Ender_back", (-420, -460, 102), 0, 44), (1280, 720)),
    ("Ender_three_quarter", cam("Ender_three_quarter", (280, -180, 105), -135, 44), (1280, 720)),
    ("Five_cast_lineup", cam("Five_cast_lineup", (900, 0, 113), 180, 63), (1280, 720)),
]
print("TSTSS_RENDER_CAPTURE_QUEUED", PROJECT, len(cameras))
results = []
@unreal.AutomationScheduler.add_latent_command
def take_captures():
    # Engine tick scheduler is required; immediate screenshot calls can
    # appear to succeed without writing a rendered PNG.
    for label, camera, (width, height) in cameras:
        target = str(OUT / (label + ".png"))
        task = unreal.AutomationLibrary.take_high_res_screenshot(
            width, height, target, camera=camera, delay=0.5, force_game_view=True)
        if not task.is_valid_task():
            raise RuntimeError("Invalid screenshot task for " + label)
        ticks = 0
        while not task.is_task_done():
            ticks += 1
            if ticks > 1200:
                raise RuntimeError("Screenshot task did not finish: " + label)
            yield
        results.append({"name": label, "requested_path": target, "ticks": ticks})
        print("TSTSS_RENDER_TASK_DONE", label, ticks)
    report = {"status": "SCREENSHOT_TASKS_COMPLETED_NOT_IMAGE_VALIDATED",
              "engine": unreal.SystemLibrary.get_engine_version(),
              "map": MAP, "renderer_requested": True, "noncanonical": True,
              "reference_accepted": False, "captured": results}
    (EVIDENCE / "render_task_receipt_v5.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("TSTSS_RENDER_TASKS_RECORDED")




