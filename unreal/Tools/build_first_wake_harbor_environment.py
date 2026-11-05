#!/usr/bin/env python3
"""First Wake coastal harbor environment V1 — isolated, noncanonical UE5.8 lookdev.

--validate works without Unreal; --build executes only inside a named disposable
Unreal Editor worktree with the ORIGINAL saved V3 asset-world bytes. No PIE or GPU
render claim is made by source-only tests or the native saved-world stage.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path

ROOT_NAME = "TSTSS_EnvironmentHarbor_20261104"
BASE_MAP = "/Game/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3"
DEST_MAP = "/Game/TSTSS/Review/Scenes/FirstWake_HarborEnvironment_20261104_REVIEW_V1"
BASE_REL = "Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3.umap"
DEST_REL = "Content/TSTSS/Review/Scenes/FirstWake_HarborEnvironment_20261104_REVIEW_V1.umap"
BASE_SHA256 = "54b4e266683347fc950a56c8ac8691d99aaddb41d61e304ddf0f5b4d0730e2b5"
PREFIX = "TSTSS_ENV_HARBOR_V1_"
MATERIAL_DIR = "/Game/TSTSS/Review/Environment/FirstWakeHarborV1"
RECEIPT_REL = "Saved/FirstWakeEnvironmentV1/native_harbor_stage.json"

# All coordinates in UE centimeters. Existing playable review path y=0,
# seven milestones x=-2200..1175. Visual scenery stays outside y=+/-400cm.
# x,y,z are mesh centers; scales apply to 100cm BasicShapes primitives.
@dataclass(frozen=True)
class Prop:
    name: str
    mesh: str
    xyz: tuple[float, float, float]
    scale: tuple[float, float, float]
    material: str
    yaw: float = 0.0
    # Sky and ocean only; all new props deliberately have collision disabled.
    kind: str = "scenery"


PALETTE = {
    "quay_stone": ((0.30, 0.35, 0.38), 0.91),
    "harbor_plaster": ((0.60, 0.57, 0.47), 0.82),
    "warm_roof": ((0.37, 0.17, 0.12), 0.88),
    "patina_metal": ((0.14, 0.33, 0.31), 0.49),
    "sail_canvas": ((0.75, 0.67, 0.45), 0.85),
    "coastal_rock": ((0.18, 0.28, 0.29), 0.95),
    "sea_teal": ((0.025, 0.17, 0.24), 0.29),
    "signal_amber": ((0.88, 0.50, 0.15), 0.36),
}

PROPS = (
    Prop("QuaySouthWall", "Cube", (-600, 950, -65), (70, 0.9, 1.4), "quay_stone"),
    Prop("OuterStonePier", "Cube", (-850, 1550, -55), (7, 8, 1.1), "quay_stone"),
    Prop("BoardingGangplankVisual", "Cube", (-950, 1120, 55), (3.5, 6, .25), "patina_metal"),
    Prop("HarborCustomsHouse", "Cube", (-3200, -1550, 330), (6, 4, 6.6), "harbor_plaster"),
    Prop("CustomsRoof", "Cone", (-3200, -1550, 740), (4.7, 3.7, 2.2), "warm_roof"),
    Prop("IoniaOfficeFacade", "Cube", (-1450, -1530, 280), (5.8, 3.4, 5.6), "harbor_plaster"),
    Prop("IoniaOfficeRoof", "Cone", (-1450, -1530, 625), (4.6, 3.3, 1.7), "warm_roof"),
    Prop("HarmonicEngineeringShop", "Cube", (250, -1580, 380), (8.5, 4.2, 7.6), "harbor_plaster"),
    Prop("EngineeringShopRoof", "Cone", (250, -1580, 830), (6.2, 4.3, 2.1), "warm_roof"),
    Prop("WorkshopSmokestack", "Cylinder", (500, -1580, 1060), (0.9, 0.9, 6.1), "patina_metal"),
    Prop("DrydockServiceShed", "Cube", (1275, -1500, 210), (4.8, 3.2, 4.2), "harbor_plaster"),
    Prop("DrydockRoof", "Cone", (1275, -1500, 475), (4.1, 3.2, 1.6), "warm_roof"),
    Prop("CanvasMarketAwning", "Cube", (-2320, -1120, 340), (7, 2.5, 0.15), "sail_canvas"),
    Prop("CopperSignalTower", "Cylinder", (2150, -1300, 450), (1.1, 1.1, 9), "patina_metal"),
    Prop("SignalBeacon", "Sphere", (2150, -1300, 930), (1.2, 1.2, 1.2), "signal_amber"),
    Prop("WaterBeyondHarbor", "Plane", (-800, 5350, -12), (145, 91, 1), "sea_teal", kind="water_visual"),
    Prop("DistantWesternHeadland", "Sphere", (-6000, 5700, -350), (28, 30, 13), "coastal_rock"),
    Prop("DistantEasternHeadland", "Sphere", (5550, 6700, -260), (22, 22, 11), "coastal_rock"),
    Prop("HighInlandRidgeWest", "Cone", (-5050, -5900, 450), (27, 21, 28), "coastal_rock"),
    Prop("HighInlandRidgeEast", "Cone", (2950, -6600, 480), (32, 26, 32), "coastal_rock"),
)

for idx, x in enumerate((-2800, -2050, -1250, -450, 350, 1120, 1900), 1):
    PROPS += (
        Prop(f"QuayBollard_{idx:02d}", "Cylinder", (x, 840, 35), (.55, .55, 1.7), "patina_metal"),
        Prop(f"StreetLampPost_{idx:02d}", "Cylinder", (x, -870, 240), (.17, .17, 4.8), "patina_metal"),
        Prop(f"StreetLampLantern_{idx:02d}", "Sphere", (x, -870, 500), (.58, .58, .65), "signal_amber"),
    )
for idx, x in enumerate((-2940, -2640, -120, 180, 950, 1250), 1):
    PROPS += (
        Prop(f"CargoStack_{idx:02d}", "Cube", (x, -980, 70), (1.7, 1.65, 1.4), "warm_roof"),
    )

# Visual-only scene frame chosen to keep real sky above the horizon in frame.
HERO_CAMERA = (-1850, -3300, 720)
HERO_ROTATION_PYR = (-6.0, 55.0, 0.0)
MILESTONES = (
    "FlyerDiscovery", "IoniaHiring", "AureateBoarding",
    "LiftStation", "PressureStation", "ReserveStation",
    "EngineeringApproval",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_plan() -> dict:
    if len({p.name for p in PROPS}) != len(PROPS):
        raise ValueError("Duplicate harbor environment actor")
    if set(PALETTE) != {p.material for p in PROPS}:
        raise ValueError("Materials and staged palette roles must match")
    if len(MILESTONES) != 7:
        raise ValueError("Original seven-stop Prelude contract missing")
    if any(s.startswith("Starbourne") for s in (p.name for p in PROPS)):
        raise ValueError("No Starbourne player unlock or environmental setpiece")
    for p in PROPS:
        if p.mesh not in {"Cube", "Sphere", "Cylinder", "Cone", "Plane"}:
            raise ValueError("Unsupported source-only engine mesh")
        if not all(math.isfinite(v) for v in (*p.xyz, *p.scale, p.yaw)):
            raise ValueError("Nonfinite review geometry")
        if min(p.scale) <= 0:
            raise ValueError("Nonpositive review geometry")
        # World-space AABB conservative for unrotated square/round primitives.
        half_y = max(p.scale[0], p.scale[1]) * 50 if p.yaw else p.scale[1] * 50
        if abs(p.xyz[1]) - half_y < 400:
            raise ValueError("Harbor scenery intrudes into existing interaction corridor: " + p.name)
    for color, roughness in PALETTE.values():
        if not all(0 <= channel <= 1 for channel in (*color, roughness)):
            raise ValueError("Material channel outside displayable range")
    return {
        "status": "SOURCE_HARBOR_ENVIRONMENT_PLAN_VALID_NOT_STAGED",
        "source": "first_wake_harbor_environment.py",
        "parent": BASE_MAP, "new_map": DEST_MAP,
        "parent_map_sha256": BASE_SHA256,
        "native_review_assets_requested": len(PROPS),
        "native_sky_atmosphere_requested": True,
        "native_fog_requested": True,
        "native_hero_camera_requested": True,
        "material_roles": sorted(PALETTE),
        "props": [p.name for p in PROPS],
        "previous_story_actors_preserved": list(MILESTONES),
        "new_actor_collision_enabled": False,
        "ocean_physics_enabled": False,
        "pie_verified": False,
        "native_render_verified": False,
        "artist_approved": False,
        "production_modified": False,
        "starbourne_unlocked": False,
    }


def build_in_unreal() -> dict:
    plan = validate_plan()
    import unreal
    project = Path(unreal.Paths.project_dir()).resolve()
    if project.name.lower() != "unreal" or project.parent.name != ROOT_NAME:
        raise RuntimeError("HOLD: must use isolated environment-review worktree")
    if not unreal.SystemLibrary.get_engine_version().startswith("5.8.4"):
        raise RuntimeError("HOLD: intended UE5.8 editor not running")
    src, dst = project / BASE_REL, project / DEST_REL
    receipt = project / RECEIPT_REL
    if not src.is_file() or sha256(src) != BASE_SHA256:
        raise RuntimeError("HOLD: original 34-actor saved World missing or changed")
    if dst.exists() or receipt.exists() or unreal.EditorAssetLibrary.does_asset_exist(DEST_MAP):
        raise RuntimeError("HOLD: output already exists; no overwrite")
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: dirty Editor map")
    if any((project / "Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: review SaveGame exists")
    configs = (project / "Config/DefaultEngine.ini", project / "Config/DefaultInput.ini")
    cfg = {p.name: sha256(p) for p in configs}
    meshes = {name: unreal.load_asset("/Engine/BasicShapes/" + name + "." + name)
              for name in ("Cube", "Sphere", "Cylinder", "Cone", "Plane")}
    if not all(isinstance(m, unreal.StaticMesh) for m in meshes.values()):
        raise RuntimeError("HOLD: native BasicShapes unavailable")
    library = unreal.EditorAssetLibrary
    if library.does_directory_exist(MATERIAL_DIR):
        raise RuntimeError("HOLD: existing review-material folder; no replacement")
    # Separate World operation avoids duplicate-then-load GC issue in earlier asset staging.
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not levels.new_level_from_template(DEST_MAP, BASE_MAP):
        raise RuntimeError("HOLD: UE could not create a new level from V3 asset-world")
    actor_system = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    originals = [a.get_actor_label() for a in actor_system.get_all_level_actors()]
    for stop in MILESTONES:
        if originals.count("TSTSS_PRELUDE_REVIEW_" + stop) != 1:
            raise RuntimeError("HOLD: original First Wake milestone absent: " + stop)
    if len(originals) != 34 or any(n.startswith(PREFIX) for n in originals):
        raise RuntimeError("HOLD: base World actor count/labels changed")
    if sum(1 for a in actor_system.get_all_level_actors()
           if isinstance(a, unreal.PlayerStart)) != 1:
        raise RuntimeError("HOLD: original playable PlayerStart lost")

    # Original, local-only UE PBR materials. Engine BasicShapes are review stand-ins,
    # never finished architecture or copyrighted Journey sand/snow resources.
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    if not library.make_directory(MATERIAL_DIR):
        raise RuntimeError("HOLD: cannot create independent review-material directory")
    materials = {}
    for role, (rgb, roughness) in PALETTE.items():
        asset_name = "M_" + role
        material = tools.create_asset(asset_name, MATERIAL_DIR,
                                      unreal.Material, unreal.MaterialFactoryNew())
        if material is None:
            raise RuntimeError("HOLD: material asset creation failed " + role)
        color = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionConstant3Vector, -350, 0)
        color.set_editor_property("constant", unreal.LinearColor(*rgb, 1))
        unreal.MaterialEditingLibrary.connect_material_property(
            color, "", unreal.MaterialProperty.MP_BASE_COLOR)
        r = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionConstant, -350, 200)
        r.set_editor_property("r", roughness)
        unreal.MaterialEditingLibrary.connect_material_property(
            r, "", unreal.MaterialProperty.MP_ROUGHNESS)
        unreal.MaterialEditingLibrary.recompile_material(material)
        if not library.save_loaded_asset(material):
            raise RuntimeError("HOLD: review material did not save " + role)
        materials[role] = material

    added = []
    for prop in PROPS:
        actor = actor_system.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(*prop.xyz),
            unreal.Rotator(0, prop.yaw, 0))
        if actor is None:
            raise RuntimeError("HOLD: harbor spawn failed " + prop.name)
        component = actor.static_mesh_component
        if not component.set_static_mesh(meshes[prop.mesh]):
            raise RuntimeError("HOLD: assigned primitive invalid " + prop.name)
        actor.set_actor_label(PREFIX + prop.name)
        actor.set_actor_scale3d(unreal.Vector(*prop.scale))
        component.set_material(0, materials[prop.material])
        actor.set_actor_enable_collision(False)
        component.set_collision_profile_name("NoCollision")
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        added.append(actor.get_actor_label())

    # Use native atmosphere rather than the older SkySphere texture that
    # rendered black in separate experimental Skybourne captures (#705).
    sky = actor_system.spawn_actor_from_class(
        unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator())
    fog = actor_system.spawn_actor_from_class(
        unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator())
    camera = actor_system.spawn_actor_from_class(
        unreal.CameraActor, unreal.Vector(*HERO_CAMERA), unreal.Rotator(*HERO_ROTATION_PYR))
    if sky is None or fog is None or camera is None:
        raise RuntimeError("HOLD: missing native atmosphere/fog/camera")
    for obj, suffix in ((sky, "NativeSkyAtmosphere"),
                        (fog, "CoastalHeightFog"), (camera, "CoastalHeroCamera")):
        obj.set_actor_label(PREFIX + suffix)
        added.append(obj.get_actor_label())
    # Base directional and sky fill remain in place; avoid double-sun additions.
    suns = [a for a in actor_system.get_all_level_actors()
            if isinstance(a, unreal.DirectionalLight)]
    if len(suns) != 1:
        raise RuntimeError("HOLD: expected exactly one inherited sun")
    suns[0].get_component_by_class(unreal.DirectionalLightComponent).set_editor_property(
        "atmosphere_sun_light", True)
    if not levels.save_current_level():
        raise RuntimeError("HOLD: new Harbor World did not save")
    if not dst.is_file() or sha256(src) != BASE_SHA256:
        raise RuntimeError("HOLD: new map missing or original world mutated")
    if any(sha256(p) != cfg[p.name] for p in configs):
        raise RuntimeError("HOLD: protected configs drifted")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    report = dict(plan, status="NATIVE_HARBOR_MAP_SAVED_PENDING_INDEPENDENT_READBACK",
                  map_sha256=sha256(dst), staged_actor_labels=added,
                  new_actor_count=len(added), previous_actor_count=len(originals),
                  engine_version=unreal.SystemLibrary.get_engine_version())
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
    unreal.log("TSTSS_HARBOR_NATIVE_STAGE_SAVED_NOT_PIE " + report["map_sha256"])
    return report


def main(argv=None):
    if argv is None and os.environ.get("TSTSS_HARBOR_BUILD_EXPLICIT") == "1":
        argv = ["--build"]
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--validate", action="store_true")
    action.add_argument("--build", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(build_in_unreal() if args.build else validate_plan(), indent=2))


if __name__ == "__main__":
    main()
