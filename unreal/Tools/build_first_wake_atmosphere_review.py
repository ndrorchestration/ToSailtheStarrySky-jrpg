"""Opt-in UE 5.8.4 atmospheric lookdev on a DUPLICATE First Wake review map.

The live Prelude, persistent world, collision/physics, save slots and production
maps are never modified. Use --validate for portable preflight; --build requires
the actual UE Editor Python module, a clean editor and compiled native actor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = "/Game/TSTSS/Review/Atmosphere_V1"
MAP = ROOT + "/M_FirstWakeAtmosphereReview"
SOURCE_MAP = "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2"
NATIVE_CLASS = "/Script/ToSailTheStarrySky.TSTSSAtmosphereDirector"
CLOUD_ASSET = "/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst"
MATERIALS = ("M_StarsAurora", "M_RainStreak", "M_SnowFlake")
LEGACY_LIGHT_LABELS = (
    "TSTSS_PRELUDE_REVIEW_ReviewDirectionalLight",
    "TSTSS_PRELUDE_REVIEW_ReviewSkyFill",
)

# Original art-direction candidate, never copied from an external game.
STAR_SHADER = r"""
float2 uv = UV;
float t = Time * saturate(MotionScale);
float2 lattice = uv * float2(620.0, 310.0);
float2 cell = floor(lattice);
float2 q = frac(lattice) - 0.5;
float seed = frac(sin(dot(cell,float2(127.1,311.7)))*43758.5453123);
float presence = smoothstep(0.992,0.998,seed);
float radius = length(q);
float aa = max(length(fwidth(lattice)),0.012);
float pin = 1.0-smoothstep(0.025,0.07+aa*0.12,radius);
float twinkle = 0.86+0.14*sin(t*0.7+seed*26.0);
float3 stars = lerp(float3(0.65,0.82,1.0),float3(1.0,0.84,0.69),seed)
             * presence * pin * twinkle * 2.5;
float wiggle = sin(uv.x*22.0 + sin(uv.x*10.0 + t*0.03)*2.0);
float edge = uv.y - (0.58 + wiggle*0.065);
float curtain = exp(-edge*edge*120.0);
float detail = 0.55+0.45*sin(uv.x*43.0+uv.y*13.0 + t*0.09);
float3 aurora = lerp(float3(0.03,0.8,0.47),float3(0.11,0.3,0.92),detail)
              * curtain * detail * saturate(AuroraStrength) * 1.5;
float night = saturate(NightFactor);
return float4((stars+aurora)*night,night*0.80);
"""

PRECIP_SHADER = r"""
float2 p = UV - 0.5;
float r = length(p);
float aa = max(length(fwidth(UV)),0.01);
float alpha = (Mode < 0.5)
    ? (1.0-smoothstep(0.20,0.49,abs(p.x))) *
      (1.0-smoothstep(0.30,0.51,abs(p.y)))
    : (1.0-smoothstep(0.18,0.43+aa,r));
float3 tint = (Mode < 0.5) ? float3(0.47,0.72,0.93)
                          : float3(0.78,0.87,1.00);
return float4(tint*0.70,alpha*0.68);
"""


def validate():
    if ROOT == SOURCE_MAP or not ROOT.startswith("/Game/TSTSS/Review/"):
        raise ValueError("Review destination must not address production or source map")
    if len(MATERIALS) != len(set(MATERIALS)):
        raise ValueError("Duplicate atmosphere material identifiers")
    return {
        "schema": "tstss.atmosphere.review.v1",
        "source_map": SOURCE_MAP,
        "review_map": MAP,
        "engine": "UE 5.8.4",
        "native_stage": "NOT_RUN",
        "gameplay_authority": "NONE",
        "weather_modes": [
            "Clear", "CoastalMist", "Rain", "Storm", "Snow",
            "Blizzard", "AuroralVeil"
        ],
        "materials": list(MATERIALS),
        "shader_sha256": hashlib.sha256(
            (STAR_SHADER+PRECIP_SHADER).encode("utf-8")
        ).hexdigest(),
        "boundaries": [
            "review-only assets", "no production-map writes",
            "no story/save/physical-sea evidence",
            "source tests cannot approve cinematic art"
        ]
    }


def preflight(u):
    if u.EditorAssetLibrary.does_directory_exist(ROOT):
        raise RuntimeError("Atmosphere review destination occupied; refuse overwrite")
    if u.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("Editor has unsaved map edits; refuse")
    if u.EditorLoadingAndSavingUtils.get_dirty_content_packages():
        raise RuntimeError("Editor has unsaved content; refuse")
    if not u.EditorAssetLibrary.does_asset_exist(SOURCE_MAP):
        raise RuntimeError("Cannot duplicate source First Wake review map")
    cls = u.load_class(None, NATIVE_CLASS)
    if cls is None:
        raise RuntimeError("Compiled TSTSSAtmosphereDirector missing; build native Editor")
    cloud = u.load_asset(CLOUD_ASSET)
    if cloud is None:
        raise RuntimeError("Native EngineSky volumetric cloud material missing")
    return cls, cloud


def connect(u, ok, location):
    if not ok:
        raise RuntimeError("Required UE material graph connection failed: " + location)


def compile_asset(u, material):
    result = u.MaterialEditingLibrary.recompile_material(material)
    if result is None or len(result) > 0:
        raise RuntimeError("UE material compiler did not return empty errors: " + str(result))
    if not u.EditorAssetLibrary.save_loaded_asset(material):
        raise RuntimeError("UE material save failed")


def custom_material(u, asset_name, code, inputs, source_nodes):
    edit = u.MaterialEditingLibrary
    m = u.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name, ROOT, u.Material, u.MaterialFactoryNew())
    if m is None:
        raise RuntimeError("Material asset creation failed: " + asset_name)
    m.set_editor_property("blend_mode", u.BlendMode.BLEND_ADDITIVE
                          if asset_name == "M_StarsAurora"
                          else u.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("shading_model", u.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("two_sided", True)
    custom = edit.create_material_expression(m, u.MaterialExpressionCustom)
    custom.set_editor_property("code", code)
    custom.set_editor_property("output_type", u.CustomMaterialOutputType.CMOT_FLOAT4)
    slots = []
    for name in inputs:
        slot = u.CustomInput()
        slot.set_editor_property("input_name", name)
        slots.append(slot)
    custom.set_editor_property("inputs", slots)
    for name, source in source_nodes(m).items():
        connect(u, edit.connect_material_expressions(source, "", custom, name), name)
    rgb = edit.create_material_expression(m, u.MaterialExpressionComponentMask)
    rgb.set_editor_property("r", True)
    rgb.set_editor_property("g", True)
    rgb.set_editor_property("b", True)
    rgb.set_editor_property("a", False)
    opacity = edit.create_material_expression(m, u.MaterialExpressionComponentMask)
    opacity.set_editor_property("r", False)
    opacity.set_editor_property("g", False)
    opacity.set_editor_property("b", False)
    opacity.set_editor_property("a", True)
    connect(u, edit.connect_material_expressions(custom, "", rgb, "Input"), "RGBA color mask")
    connect(u, edit.connect_material_expressions(custom, "", opacity, "Input"), "RGBA alpha mask")
    connect(u, edit.connect_material_property(rgb, "", u.MaterialProperty.MP_EMISSIVE_COLOR),
            "emissive output")
    connect(u, edit.connect_material_property(opacity, "", u.MaterialProperty.MP_OPACITY),
            "opacity output")
    edit.layout_material_expressions(m)
    compile_asset(u, m)
    return m


def build_in_unreal():
    try:
        import unreal as u
    except ImportError as exc:
        raise RuntimeError("--build requires Unreal Editor Python") from exc
    plan = validate()
    cls, cloud = preflight(u)
    if not u.EditorAssetLibrary.make_directory(ROOT):
        raise RuntimeError("Cannot create isolated atmosphere review directory")

    def time_and_uv(m):
        e = u.MaterialEditingLibrary
        uv = e.create_material_expression(m, u.MaterialExpressionTextureCoordinate)
        time = e.create_material_expression(m, u.MaterialExpressionTime)
        night = e.create_material_expression(m, u.MaterialExpressionScalarParameter)
        night.set_editor_property("parameter_name", "NightFactor")
        night.set_editor_property("default_value", 1.0)
        aurora = e.create_material_expression(m, u.MaterialExpressionScalarParameter)
        aurora.set_editor_property("parameter_name", "AuroraStrength")
        aurora.set_editor_property("default_value", 0.0)
        motion = e.create_material_expression(m, u.MaterialExpressionScalarParameter)
        motion.set_editor_property("parameter_name", "MotionScale")
        motion.set_editor_property("default_value", 1.0)
        return {"UV": uv, "Time": time, "NightFactor": night,
                "AuroraStrength": aurora, "MotionScale": motion}

    def precip_nodes(mode):
        def fn(m):
            e = u.MaterialEditingLibrary
            uv = e.create_material_expression(m, u.MaterialExpressionTextureCoordinate)
            constant = e.create_material_expression(m, u.MaterialExpressionConstant)
            constant.set_editor_property("r", float(mode))
            return {"UV": uv, "Mode": constant}
        return fn

    star = custom_material(u, MATERIALS[0], STAR_SHADER,
                           ("UV", "Time", "NightFactor", "AuroraStrength", "MotionScale"), time_and_uv)
    rain = custom_material(u, MATERIALS[1], PRECIP_SHADER,
                           ("UV", "Mode"), precip_nodes(0))
    snow = custom_material(u, MATERIALS[2], PRECIP_SHADER,
                           ("UV", "Mode"), precip_nodes(1))

    if not u.EditorAssetLibrary.duplicate_asset(SOURCE_MAP, MAP):
        raise RuntimeError("Source map duplication failed; source remains untouched")
    world = u.EditorLoadingAndSavingUtils.load_map(MAP)
    if world is None:
        raise RuntimeError("Duplicated map load failed")
    editor = u.get_editor_subsystem(u.EditorActorSubsystem)
    removed = []
    for actor in editor.get_all_level_actors():
        label = actor.get_actor_label()
        if label in LEGACY_LIGHT_LABELS:
            if not editor.destroy_actor(actor):
                raise RuntimeError("Could not remove duplicate-only review light: " + label)
            removed.append(label)
        elif label.startswith("TSTSS_ATMOSPHERE_"):
            raise RuntimeError("Duplicated map already contains another atmosphere controller")
    if set(removed) != set(LEGACY_LIGHT_LABELS):
        raise RuntimeError("Unexpected source review light inventory: " + str(removed))

    actor = editor.spawn_actor_from_class(
        cls, u.Vector(-1000, 0, 200), u.Rotator(0, 0, 0))
    if actor is None:
        raise RuntimeError("Could not instantiate native atmosphere controller")
    actor.set_actor_label("TSTSS_ATMOSPHERE_FirstWake_ReviewOnly")
    actor.set_editor_property("volumetric_cloud_material", cloud)
    actor.set_editor_property("star_aurora_material", star)
    actor.set_editor_property("rain_material", rain)
    actor.set_editor_property("snow_material", snow)
    actor.set_editor_property("initial_clock_hours", 17.0)
    # Autoplay is strictly a lookdev demo; never enable it on production levels.
    actor.set_editor_property("autoplay_review_cycle", True)
    if not u.EditorLoadingAndSavingUtils.save_map(world, MAP):
        raise RuntimeError("Saving atmosphere map failed")

    root = Path(u.Paths.project_dir())
    receipt = root / "Saved" / "AtmosphereReviewV1"
    receipt.mkdir(parents=True, exist_ok=True)
    map_file = root / "Content" / "TSTSS" / "Review" / "Atmosphere_V1" / "M_FirstWakeAtmosphereReview.umap"
    if not map_file.is_file():
        raise RuntimeError("Native map not present after save")
    plan.update(native_stage="MAP_SAVED_NOT_PLAYTESTED",
                map_sha256=hashlib.sha256(map_file.read_bytes()).hexdigest(),
                map_bytes=map_file.stat().st_size,
                removed_duplicate_only_lights=removed)
    receipt_file = receipt / "staging_receipt.json"
    if receipt_file.exists():
        raise RuntimeError("Receipt occupied; refusing evidence overwrite")
    receipt_file.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    u.log("TSTSS_ATMOSPHERE_REVIEW_SAVED " + str(map_file))
    return plan


def main(argv=None):
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--validate", action="store_true")
    modes.add_argument("--build", action="store_true")
    args = parser.parse_args(argv)
    result = build_in_unreal() if args.build else validate()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
