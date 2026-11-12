"""One-off native authoring of a separate corrected First Wake V3 review level.

Source V2 and all production maps remain unchanged. This adds only review art:
movable lighting, atmosphere and correctly facing informational text markers.
No story, physics, collision, item, roster or save changes.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess

SOURCE = "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2"
TARGET = "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V3_VisualReview"
SOURCE_SHA256 = "4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80"
EXPECTED_SOURCE_LIGHTS = {
    "TSTSS_PRELUDE_REVIEW_ReviewDirectionalLight",
    "TSTSS_PRELUDE_REVIEW_ReviewSkyFill",
}
SIGN_PREFIX = "TSTSS_PRELUDE_REVIEW_SIGN_"
OPT_IN = "AUTHOR_V3_REVIEW_VISUAL_ONLY"


def main():
    import unreal as u
    project = Path(u.Paths.project_dir()).resolve()
    repo = project.parent
    expected = os.environ.get("TSTSS_V3_EXPECTED_HEAD", "")
    if repo.name != "TSTSS_DockOpening_20261111" or len(expected) != 40:
        raise RuntimeError("HOLD: wrong isolated worktree or missing SHA")
    if os.environ.get("TSTSS_V3_OPT_IN") != OPT_IN:
        raise RuntimeError("HOLD: explicit visual-review opt-in missing")
    actual = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                           capture_output=True, text=True, check=True).stdout.strip()
    if actual != expected or dirty:
        raise RuntimeError("HOLD: source revision or clean-tree gate failed")
    if not str(u.SystemLibrary.get_engine_version()).startswith("5.8.4"):
        raise RuntimeError("HOLD: native UE 5.8.4 required")
    original = project / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"
    target = project / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V3_VisualReview.umap"
    if not original.is_file() or hashlib.sha256(original.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise RuntimeError("HOLD: source V2 map changed")
    if target.exists() or u.EditorAssetLibrary.does_asset_exist(TARGET):
        raise RuntimeError("HOLD: V3 destination already exists")
    if u.EditorLoadingAndSavingUtils.get_dirty_map_packages() or \
       u.EditorLoadingAndSavingUtils.get_dirty_content_packages():
        raise RuntimeError("HOLD: dirty editor packages")

    world = u.EditorLoadingAndSavingUtils.load_map(SOURCE)
    if world is None:
        raise RuntimeError("HOLD: cannot open original V2")
    world.get_world_settings().set_editor_property("force_no_precomputed_lighting", True)
    editor = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = editor.get_all_level_actors()
    signs = [a for a in actors if a.get_actor_label().startswith(SIGN_PREFIX)]
    originals = [a for a in actors if a.get_actor_label() in EXPECTED_SOURCE_LIGHTS]
    if len(signs) != 7 or {a.get_actor_label() for a in originals} != EXPECTED_SOURCE_LIGHTS:
        raise RuntimeError(f"HOLD: actor inventory changed signs={len(signs)} lights={len(originals)}")
    for actor in signs:
        actor.set_actor_rotation(u.Rotator(0., 180., 0.), False)
        component = actor.get_component_by_class(u.TextRenderComponent)
        if component is None:
            raise RuntimeError("HOLD: missing sign text component")
        component.set_editor_property("world_size", 33.)
    for actor in originals:
        if not editor.destroy_actor(actor):
            raise RuntimeError("HOLD: failed to remove a placeholder static light")

    def spawn(cls, label, xyz):
        actor = editor.spawn_actor_from_class(cls, u.Vector(*xyz), u.Rotator(0., 0., 0.))
        if actor is None:
            raise RuntimeError("HOLD: visual actor spawn failed: " + label)
        actor.set_actor_label("TSTSS_V3_REVIEW_" + label)
        return actor

    def movable(actor, cls):
        component = actor.get_component_by_class(cls)
        if not component:
            raise RuntimeError("HOLD: missing lighting component")
        component.set_mobility(u.ComponentMobility.MOVABLE)
        return component

    # Source-locked harbor_day profile from existing tstss_lighting_review.py.
    sun = spawn(u.DirectionalLight, "HarborDay_SunKey", (0, 0, 1800))
    sun.set_actor_rotation(u.Rotator(-43., 138., 0.), False)
    sc = movable(sun, u.DirectionalLightComponent)
    sc.set_editor_property("intensity", 75000.)
    sc.set_light_color(u.LinearColor(1.0, .91, .79, 1.), False)
    sc.set_atmosphere_sun_light(True)

    sky = spawn(u.SkyLight, "HarborDay_DynamicFill", (0, 0, 1400))
    sk = movable(sky, u.SkyLightComponent)
    sk.set_editor_property("intensity", 1.15)
    sk.set_real_time_capture(True)
    spawn(u.SkyAtmosphere, "HarborDay_SkyAtmosphere", (0, 0, 0))

    fog = spawn(u.ExponentialHeightFog, "HarborDay_Depth", (0, 0, 0))
    fc = fog.get_component_by_class(u.ExponentialHeightFogComponent)
    if fc is None:
        raise RuntimeError("HOLD: fog component missing")
    fc.set_editor_property("fog_density", .003)
    fc.set_editor_property("fog_height_falloff", .28)

    lamp = spawn(u.PointLight, "HarborDay_Practical", (-2200., -100., 340.))
    pc = movable(lamp, u.PointLightComponent)
    pc.set_editor_property("intensity_units", u.LightUnits.LUMENS)
    pc.set_editor_property("intensity", 1500.)
    pc.set_editor_property("attenuation_radius", 1000.)
    pc.set_light_color(u.LinearColor(1., .79, .55, 1.), False)

    pp = spawn(u.PostProcessVolume, "HarborDay_Exposure", (0., 0., 0.))
    pp.set_editor_property("unbound", True)
    settings = pp.get_editor_property("settings")
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", 0.)
    pp.set_editor_property("settings", settings)

    # Saving to a new package rather than modifying V2 in-place is required.
    if not u.EditorLoadingAndSavingUtils.save_map(world, TARGET):
        raise RuntimeError("HOLD: V3 Save As failed")
    if not target.is_file():
        raise RuntimeError("HOLD: V3 map absent")
    if hashlib.sha256(original.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise RuntimeError("HOLD: V2 original map changed during Save As")
    receipt = {
        "status":"NATIVE_V3_REVIEW_SAVED_NO_RUNTIME_APPROVAL",
        "exact_source_head":expected,
        "source_map":SOURCE, "source_sha256":SOURCE_SHA256,
        "new_map":TARGET,
        "new_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
        "new_bytes":target.stat().st_size,
        "signs_rotated":len(signs), "old_lights_removed":len(originals),
        "new_lighting_profile":"harbor_day",
        "force_no_precomputed_lighting":True,
        "story_or_gameplay_modified":False,
        "new_game_route_changed":False,
        "visual_review":"NOT_YET", "pie_or_fall_test":"NOT_YET",
        "approved":False, "merged":False
    }
    out = project / "Saved/OpeningDockReview/v3_native_visual_authoring.json"
    with out.open("x", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2)
    u.log("TSTSS_V3_VISUAL_REVIEW_CREATED " + receipt["new_sha256"])
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
