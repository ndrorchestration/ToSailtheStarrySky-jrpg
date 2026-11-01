"""Disposable Unreal 5.8.4 editor comparison: Ender V1 and V2 side-by-side.

The reviewer must separately check the *real native report PNG files*. Success
in this Editor Python Automation Test only proves capture tasks completed.
No asset imports, map saves, or promotion to playable characters are allowed.

Install a tiny wrapper in the sandbox Content/Python/test_ender_compare_native.py:
    import runpy
    runpy.run_path(r"<checkout>/unreal/ArtSource/Characters/capture_ender_comparison_native.py")
Run Editor.Python.CastAllSandbox.test_ender_compare_native with D3D11 SM5.
"""
import hashlib
import json
from pathlib import Path
import sys
import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ender_comparison_contract import (  # noqa: E402
    CAMERAS, CANDIDATE_POSITIONS, EXPECTED, MAP,
    check_project, load_intake_receipts, review_plan,
)

PROJECT = check_project(unreal.Paths.project_dir())
PLAN = review_plan()
ASSETS = load_intake_receipts(PROJECT)
MAP_ON_DISK = PROJECT / "Content" / (MAP.removeprefix("/Game/") + ".umap")
if not MAP_ON_DISK.is_file():
    raise RuntimeError("Required native review map file missing")
MAP_SHA_BEFORE = hashlib.sha256(MAP_ON_DISK.read_bytes()).hexdigest()
LEVEL = unreal.EditorLoadingAndSavingUtils.load_map(MAP)
if LEVEL is None:
    raise RuntimeError("Required disposable V2 review level missing")

existing = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
v2_actors = [a for a in existing if a.get_actor_label() == "NONCANON_ENDER_FIDELITY_V2"]
if len(v2_actors) != 1:
    raise RuntimeError("Required V2 review actor not unique")
v2_actor = v2_actors[0]
component = v2_actor.get_component_by_class(unreal.StaticMeshComponent)
if component is None or component.get_editor_property("static_mesh").get_path_name() != ASSETS["EnderV2"]:
    raise RuntimeError("Unexpected V2 mesh in review level")

v1_mesh = unreal.load_asset(ASSETS["EnderV1"])
if not isinstance(v1_mesh, unreal.StaticMesh):
    raise RuntimeError("Existing V1 StaticMesh has not been natively imported")

# Only transient review-session actor transforms. NO EditorAssetLibrary save calls.
loc_v2 = CANDIDATE_POSITIONS["EnderV2"]
v2_actor.set_actor_location(unreal.Vector(*loc_v2), False, False)
loc_v1 = CANDIDATE_POSITIONS["EnderV1"]
v1_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
    v1_mesh, unreal.Vector(*loc_v1),
    unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0))
if v1_actor is None:
    raise RuntimeError("Could not spawn V1 noncanonical comparison actor")
v1_actor.set_actor_label("NONCANON_ENDER_COMPARISON_V1_TRANSIENT")
for actor in (v1_actor, v2_actor):
    actor.set_actor_enable_collision(False)

sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.DirectionalLight, unreal.Vector(0, 0, 450),
    unreal.Rotator(pitch=-35.0, yaw=35.0, roll=0.0), transient=True)
if sun is None:
    raise RuntimeError("Unable to stage equal comparison lighting")
sun.get_component_by_class(unreal.DirectionalLightComponent).set_editor_property("intensity", 0.5)
for x, y in ((360, 380), (-360, 380), (360, -380), (-360, -380)):
    light = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PointLight, unreal.Vector(x, y, 350),
        unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0), transient=True)
    if light is None:
        raise RuntimeError("Point light unavailable")
    light.get_component_by_class(unreal.PointLightComponent).set_editor_property("intensity", 1500.0)


def review_camera(name, xyz, yaw, fov):
    camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CameraActor, unreal.Vector(*xyz),
        unreal.Rotator(pitch=0.0, yaw=float(yaw), roll=0.0), transient=True)
    if camera is None:
        raise RuntimeError("Comparison camera unavailable: " + name)
    camera.set_actor_label("REVIEW_ONLY_" + name)
    comp = camera.get_component_by_class(unreal.CameraComponent)
    if comp is None:
        raise RuntimeError("CameraComponent missing")
    comp.set_editor_property("field_of_view", float(fov))
    setting = comp.get_editor_property("post_process_settings")
    setting.set_editor_property("override_auto_exposure_method", True)
    setting.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    setting.set_editor_property("override_auto_exposure_bias", True)
    setting.set_editor_property("auto_exposure_bias", 5.0)
    comp.set_editor_property("post_process_settings", setting)
    comp.set_editor_property("post_process_blend_weight", 1.0)
    return camera


CAMERA_ACTORS = [(name, review_camera(name, xyz, yaw, fov)) for name, xyz, yaw, fov in CAMERAS]
OUTPUT = PROJECT / "Saved" / "CharacterLookdev" / "EnderComparisonV1V2Native"
if OUTPUT.exists():
    raise RuntimeError("Native comparison review output exists: refuse overwrite")
OUTPUT.mkdir(parents=True)
if not hasattr(unreal, "AutomationScheduler"):
    raise RuntimeError("Requires Python Automation Test plugin in disposable project")

print("TSTSS_ENDER_COMPARISON_QUEUED", len(CAMERA_ACTORS))


@unreal.AutomationScheduler.add_latent_command
def capture_pair():
    tasks = []
    for name, camera in CAMERA_ACTORS:
        requested = str(OUTPUT / (name + ".png"))
        task = unreal.AutomationLibrary.take_high_res_screenshot(
            1280, 720, requested, camera=camera, delay=0.5, force_game_view=True)
        if not task.is_valid_task():
            raise RuntimeError("Unreal did not accept capture task: " + name)
        ticks = 0
        while not task.is_task_done():
            ticks += 1
            if ticks > 1200:
                raise RuntimeError("Native capture task timed out: " + name)
            yield
        tasks.append({"name": name, "requested": requested, "ticks": ticks})
        print("TSTSS_ENDER_COMPARISON_TASK_DONE", name, ticks)
    map_sha_after = hashlib.sha256(MAP_ON_DISK.read_bytes()).hexdigest()
    if map_sha_after != MAP_SHA_BEFORE:
        raise RuntimeError("Review map was modified during comparison capture")
    receipt = {
        **PLAN,
        "status": "UNREAL_SCREENSHOT_TASKS_COMPLETE_NATIVE_PNG_QA_PENDING",
        "engine": unreal.SystemLibrary.get_engine_version(),
        "source_sha256": {name: EXPECTED[name]["sha256"] for name in EXPECTED},
        "asset_paths": ASSETS,
        "saved_review_map_sha256_before": MAP_SHA_BEFORE,
        "saved_review_map_sha256_after": map_sha_after,
        "capture_tasks": tasks,
        "reference_likeness_approved": False,
        "source_files_modified": False,
        "saved_unreal_map_modified": False,
    }
    (OUTPUT / "capture_task_receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
