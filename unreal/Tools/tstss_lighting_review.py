"""TSTSS First Wake lighting look development, source checked and review only.

Eleven motivated looks may be staged into new, distinct Unreal 5.8.4 review maps.
Existing source map, production maps, gameplay, physics and saves are read-only.
This is NOT native image proof, approved art, or a runtime weather controller.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path

PROJECT_PARENT = "TSTSS_Lighting_20261110"
BASE_MAP = "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2"
DEST_ROOT = "/Game/TSTSS/Review/Lighting"
ORIGINAL_LIGHT_LABELS = {
    "TSTSS_PRELUDE_REVIEW_ReviewDirectionalLight",
    "TSTSS_PRELUDE_REVIEW_ReviewSkyFill",
}
SOURCE_SCENES_UNCHANGED = True

@dataclass(frozen=True)
class Look:
    name: str
    story_beat: str
    location: str
    outdoor: bool
    solar_pitch: float
    solar_yaw: float
    sun_lux: float
    sky_intensity: float
    fog_density: float
    fog_falloff: float
    practical_lumens: float
    exposure_bias_ev: float
    sun_rgb: tuple[float, float, float]
    practical_rgb: tuple[float, float, float]
    rationale: str

# Sun angles are REVIEW directions, not geographic/time-of-day canon.
# Practical lamps are placed at review-blockout markers, not approved ship geometry.
LOOKS = (
    Look("harbor_day", "Flyer discovery", "Harbor", True, -43, 138, 75000, 1.15, 0.003, 0.28, 1500, 0.0, (1.0,.91,.79), (1.,.79,.55), "Readable daylight, deck shadow and sea edge"),
    Look("harbor_dusk", "Ionia hiring", "Harbor", True, -10, 133, 11000, .8, .006, .24, 2500, -.15, (1.,.63,.37), (1.,.78,.48), "Warm sky countered by practical face fill"),
    Look("harbor_night_review", "Optional low-light legibility A/B, not story chronology", "Harbor night lookdev", True, 3, 123, .05, .42, .011, .2, 1800, .35, (.45,.54,.82), (1.,.78,.51), "Lantern and moonlike low-key legibility without asserting starfield completion"),
    Look("engineering", "Harmonic inspection", "Engineering", False, -23, 125, 7000, .35, .002, .35, 3200, .25, (.92,.82,.64), (1.,.78,.43), "Warm motivated tools, gauges and hands; no magical skill assumed"),
    Look("bridge", "Departure authorization", "Bridge", False, -20, 153, 18500, .65, .002, .4, 2400, -.1, (1.,.82,.63), (1.,.84,.69), "Interior faces readable against forward windows"),
    Look("ascent", "First Wake lift", "High sky", True, -32, 122, 50000, 1.3, .001, .45, 600, -.2, (.96,.91,.8), (.73,.84,1.), "Sun and atmosphere support ship silhouette"),
    Look("auroral_twilight", "Auroral route", "High sky", True, -4, 123, 900, .6, .001, .45, 1300, .2, (.62,.72,1.), (.55,.84,1.), "Restrained cool fill, not a neon wash"),
    Look("phase_drift", "Engine instability", "Aureate Wake", False, -8, 130, 600, .3, .004, .3, 3800, -.15, (.66,.77,.98), (1.,.31,.18), "Controlled warning key without blacking out cues"),
    Look("storm_descent", "Emergency descent", "Storm sky", True, -27, 135, 9500, .45, .013, .2, 900, -.1, (.74,.82,.91), (.98,.7,.42), "Overcast diffuse visibility; lightning authored separately"),
    Look("sea_contact", "Physical splashdown", "Water", True, -12, 133, 6500, .55, .012, .23, 1200, -.15, (.82,.87,.95), (.98,.81,.58), "Readable waterline and spray; does not signal physics success"),
    Look("shore_aftermath", "Lyra after landing", "Shore", True, -16, 115, 18000, .8, .009, .25, 1400, .05, (1.,.81,.58), (1.,.85,.68), "Coastal depth and compassionate human readability"),
)

# World-position anchors are in the existing V2 disposable harbor blockout.
# Later authentic levels must author their own named anchors.
PRACTICAL_ANCHORS = {
    "harbor_day": (-2200., -100., 340.),
    "harbor_dusk": (-1550., -110., 340.),
    "harbor_night_review": (-2200., -100., 340.),
    "engineering": (225., 520., 340.),
    "bridge": (-900., 440., 360.),
    "ascent": (-900., 440., 400.),
    "auroral_twilight": (-900., 440., 400.),
    "phase_drift": (225., 520., 340.),
    "storm_descent": (-900., 440., 400.),
    "sea_contact": (-500., 1600., 300.),
    "shore_aftermath": (-1550., -110., 340.),
}

def destination(key: str) -> str:
    if key not in {look.name for look in LOOKS}:
        raise ValueError("Unknown lighting look")
    return f"{DEST_ROOT}/FirstWake_{key}_Lighting_V1"

def validate() -> dict:
    names = [look.name for look in LOOKS]
    if len(names) != 11 or len(set(names)) != 11 or set(names) != set(PRACTICAL_ANCHORS):
        raise ValueError("Exactly eleven unique source-anchored looks are required")
    for look in LOOKS:
        values = (look.solar_pitch, look.solar_yaw, look.sun_lux,
                  look.sky_intensity, look.fog_density, look.fog_falloff,
                  look.practical_lumens, look.exposure_bias_ev,
                  *look.sun_rgb, *look.practical_rgb, *PRACTICAL_ANCHORS[look.name])
        if not all(math.isfinite(x) for x in values):
            raise ValueError("Nonfinite light property in " + look.name)
        if not (-90 <= look.solar_pitch <= 90 and 0 <= look.solar_yaw < 360):
            raise ValueError("Invalid sun direction in " + look.name)
        if not (0 <= look.sun_lux <= 120000 and 0 <= look.sky_intensity <= 3):
            raise ValueError("Unsafe key/sky luminance in " + look.name)
        if not (0 <= look.fog_density <= .05 and .01 <= look.fog_falloff <= 2):
            raise ValueError("Fog range rejected in " + look.name)
        if not (0 <= look.practical_lumens <= 10000 and abs(look.exposure_bias_ev) <= 2):
            raise ValueError("Practical / exposure cap rejected in " + look.name)
        if any(not (0 <= x <= 1) for x in (*look.sun_rgb, *look.practical_rgb)):
            raise ValueError("Color is outside display-safe linear preview interval")
        if destination(look.name) == BASE_MAP or not destination(look.name).startswith(DEST_ROOT + "/"):
            raise ValueError("Review destination violated")
    if names.index("shore_aftermath") < names.index("sea_contact"):
        raise ValueError("Aftermath cannot precede physical contact in the shot plan")
    return {"status": "SOURCE_PLAN_ONLY_NO_NATIVE_OR_VISUAL_APPROVAL",
            "engine": "Unreal 5.8.4", "source_map": BASE_MAP,
            "looks": [asdict(look) | {"destination_map": destination(look.name)}
                      for look in LOOKS],
            "production_content_modified": False,
            "night_day_runtime_interpolation_implemented": False,
            "water_contact_evidence_generated": False,
            "weather_simulation_implemented": False,
            "creator_art_approved": False}

def check_disposable_project(project_dir: str) -> Path:
    p = Path(project_dir).resolve()
    if p.name.lower() != "unreal" or p.parent.name != PROJECT_PARENT:
        raise RuntimeError("Refuse non-dedicated lighting worktree")
    if not (p / "ToSailTheStarrySky.uproject").is_file():
        raise RuntimeError("Expected Unreal project absent")
    return p

def stage_native(key: str) -> dict:
    plan = validate()
    look = next((item for item in LOOKS if item.name == key), None)
    if look is None:
        raise ValueError("Unrecognized lighting profile")
    import unreal
    project = check_disposable_project(unreal.Paths.project_dir())
    dest = destination(key)
    if unreal.EditorAssetLibrary.does_asset_exist(dest):
        raise RuntimeError("Refuse overwrite of existing native lighting review map")
    if not unreal.EditorAssetLibrary.does_asset_exist(BASE_MAP):
        raise RuntimeError("Source V2 review level absent")
    dirty = unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    if dirty:
        raise RuntimeError("Dirty Editor map; do not discard someone's work")
    if not unreal.EditorAssetLibrary.does_directory_exist(DEST_ROOT):
        unreal.EditorAssetLibrary.make_directory(DEST_ROOT)
    if not unreal.EditorAssetLibrary.duplicate_asset(BASE_MAP, dest):
        raise RuntimeError("Failed duplicating review map; source untouched")
    world = unreal.EditorLoadingAndSavingUtils.load_map(dest)
    if world is None:
        raise RuntimeError("Failed loading isolated duplicated map")
    ws = world.get_world_settings()
    ws.set_editor_property("force_no_precomputed_lighting", True)
    editor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for actor in editor.get_all_level_actors():
        if actor.get_actor_label() in ORIGINAL_LIGHT_LABELS:
            if not editor.destroy_actor(actor):
                raise RuntimeError("Failed to remove pre-existing static review light")
            removed += 1
    if removed != 2:
        raise RuntimeError("Exactly two V2 placeholder lights required; found " + str(removed))

    def spawn(cls, suffix, xyz):
        actor = editor.spawn_actor_from_class(cls, unreal.Vector(*xyz),
                                              unreal.Rotator(0., 0., 0.))
        if actor is None:
            raise RuntimeError("Could not stage " + suffix)
        actor.set_actor_label("TSTSS_LIGHTING_REVIEW_" + key + "_" + suffix)
        return actor

    def movable_component(actor, cls):
        comp = actor.get_component_by_class(cls)
        if comp is None:
            raise RuntimeError("Missing native lighting component")
        comp.set_mobility(unreal.ComponentMobility.MOVABLE)
        return comp

    def linear(rgb):
        return unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.)

    sun = spawn(unreal.DirectionalLight, "SunKey", (0., 0., 1800.))
    sun.set_actor_rotation(unreal.Rotator(look.solar_pitch, look.solar_yaw, 0.), False)
    sc = movable_component(sun, unreal.DirectionalLightComponent)
    sc.set_editor_property("intensity", look.sun_lux)
    sc.set_light_color(linear(look.sun_rgb), False)
    sc.set_editor_property("atmosphere_sun_light", True)

    sky = spawn(unreal.SkyLight, "DynamicSkyFill", (0., 0., 1400.))
    sk = movable_component(sky, unreal.SkyLightComponent)
    sk.set_editor_property("intensity", look.sky_intensity)
    sk.set_editor_property("real_time_capture", True)
    spawn(unreal.SkyAtmosphere, "AtmosphericScattering", (0., 0., 0.))

    fog = spawn(unreal.ExponentialHeightFog, "DistanceDepth", (0., 0., 0.))
    fc = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    if fc is None:
        raise RuntimeError("Missing fog component")
    fc.set_editor_property("fog_density", look.fog_density)
    fc.set_editor_property("fog_height_falloff", look.fog_falloff)

    lamp = spawn(unreal.PointLight, "MotivatedPractical", PRACTICAL_ANCHORS[key])
    pc = movable_component(lamp, unreal.PointLightComponent)
    pc.set_editor_property("intensity", look.practical_lumens)
    pc.set_editor_property("attenuation_radius", 1000.)
    pc.set_light_color(linear(look.practical_rgb), False)
    pc.set_editor_property("cast_shadows", True)

    pp = spawn(unreal.PostProcessVolume, "UnboundExposureGuard", (0., 0., 0.))
    pp.set_editor_property("unbound", True)
    settings = pp.get_editor_property("settings")
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", look.exposure_bias_ev)
    pp.set_editor_property("settings", settings)

    if not unreal.EditorLoadingAndSavingUtils.save_map(world, dest):
        raise RuntimeError("Lighting review map save failed")
    map_path = project / "Content" / "TSTSS" / "Review" / "Lighting" / (dest.rsplit("/", 1)[-1] + ".umap")
    if not map_path.is_file():
        raise RuntimeError("Expected native map bytes absent after save")
    receipt = {
        "status": "NATIVE_MAP_STAGED_NO_GPU_IMAGE_OR_ART_APPROVAL",
        "source_map": BASE_MAP, "destination_map": dest,
        "look": asdict(look), "placeholder_lights_replaced": removed,
        "force_no_precomputed_lighting_requested": True,
        "map_sha256": hashlib.sha256(map_path.read_bytes()).hexdigest(),
        "map_bytes": map_path.stat().st_size,
        "native_gpu_capture": False, "player_playthrough": False,
        "production_content_modified": False
    }
    out = project / "Saved" / "LightingReview"
    out.mkdir(parents=True, exist_ok=True)
    path = out / (key + "_native_staging_receipt.json")
    if path.exists():
        raise RuntimeError("Existing evidence receipt; refuse overwrite")
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    unreal.log("TSTSS_LIGHTING_NATIVE_STAGED " + dest)
    return receipt

def main(argv=None):
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--validate", action="store_true")
    modes.add_argument("--stage", choices=[look.name for look in LOOKS])
    args = parser.parse_args(argv)
    result = validate() if args.validate else stage_native(args.stage)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
