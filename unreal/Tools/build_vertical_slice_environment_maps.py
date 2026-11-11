#!/usr/bin/env python3
"""Build isolated, review-only 3D Unreal levels for the First Wake vertical slice.

No production maps, saves, default maps, canonical cast meshes or progression
authority are modified. These are environment blockouts, not visual approval.
Use --plan without UE; --build only inside the exact disposable worktree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess

SANDBOX = "TSTSS_VSlice_Environments_20261110"
DEST = "/Game/TSTSS/Review/VerticalSlice"
PARENT = "Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"
PARENT_PACKAGE = "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2"
ORDER = (
    ("VS01_DenithHarbor", "Prelaunch quay, flyer, Ionia and boarding", "prelaunch"),
    ("VS02_AureateInteriors", "Front deck, bridge and harmonic-engine inspection", "prelaunch"),
    ("VS03_FirstWakeSky", "Controlled launch, high atmosphere and drift", "launch"),
    ("VS04_SplashdownSea", "Ocean and isolated native contact-adapter lab", "sea"),
    ("VS05_DenithFuelShanty", "Post-contact fuel stop and tide-worn settlement", "post_contact"),
    ("VS06_SplashdownShore", "Shore exploration and later Lyra introduction staging", "post_contact"),
)
PREFIX = "TSTSS_VS_REVIEW_"
# Everything is dimensioned in Unreal centimeters. These colors are exploratory,
# never substitutes for approved character/ship concept art.
PALETTE = {
    "sand": (0.69, 0.52, 0.33),
    "stone": (0.30, 0.37, 0.40),
    "dark_stone": (0.10, 0.16, 0.21),
    "timber": (0.28, 0.17, 0.105),
    "brass": (0.73, 0.47, 0.14),
    "ocean": (0.025, 0.19, 0.25),
    "aether": (0.10, 0.49, 0.52),
    "cloud": (0.76, 0.83, 0.86),
    "warm": (0.96, 0.59, 0.28),
    "green": (0.21, 0.38, 0.29),
}
ROUTE = (
    ("VS01_DenithHarbor", "VS02_AureateInteriors", "Board ship after Ionia"),
    ("VS02_AureateInteriors", "VS03_FirstWakeSky", "Three checks then launch"),
    ("VS03_FirstWakeSky", "VS04_SplashdownSea", "Physical sea contact"),
    ("VS04_SplashdownSea", "VS05_DenithFuelShanty", "Only after flotation"),
    ("VS05_DenithFuelShanty", "VS06_SplashdownShore", "Post-contact exploration"),
)


def review_plan():
    assert len(ORDER) == len({item[0] for item in ORDER}) == 6
    assert [a for a, _, _ in ROUTE] == [row[0] for row in ORDER[:-1]]
    assert [b for _, b, _ in ROUTE] == [row[0] for row in ORDER[1:]]
    assert all(math.isfinite(x) for x in (320, 460, 1400, 2700))
    return {
        "authority": "DRAFT_3D_ENVIRONMENTS_NOT_PLAYABLE_OR_CANON_APPROVED",
        "target": DEST,
        "levels": [{"name": n, "package": DEST + "/" + n,
                    "description": desc, "gate": gate} for n, desc, gate in ORDER],
        "links": [{"from": a, "to": b, "requirement": why,
                   "runtime_transition_implemented": False} for a, b, why in ROUTE],
        "preserve_first_wake_v2": True,
        "native_water_adaptor_isolated": True,
        "world_globe_not_implemented": True,
        "no_automatic_lyra_recruitment": True,
        "starbourne_locked": True,
        "visual_approval": False,
        "PIE_verified": False,
    }


def assert_sandbox(project):
    project = Path(project).resolve()
    if project.name.lower() != "unreal" or project.parent.name != SANDBOX:
        raise RuntimeError("HOLD: not the isolated vertical-slice environment worktree")
    expected = os.environ.get("TSTSS_VSLICE_EXPECTED_HEAD", "")
    if not re.fullmatch("[0-9a-fA-F]{40}", expected):
        raise RuntimeError("HOLD: explicit exact 40-hex HEAD required")
    def git(*args):
        p = subprocess.run(["git", "-C", str(project.parent), *args],
                           capture_output=True, text=True, timeout=30, check=False)
        if p.returncode:
            raise RuntimeError("HOLD: Git custody unavailable")
        return p.stdout.strip()
    if git("rev-parse", "HEAD").lower() != expected.lower():
        raise RuntimeError("HOLD: worktree head differs from exact requested source")
    if git("status", "--porcelain"):
        raise RuntimeError("HOLD: dirty source worktree, refuse native authoring")
    old = project / PARENT
    if not old.is_file():
        raise RuntimeError("HOLD: immutable native Prelude map missing")
    old_sha = hashlib.sha256(old.read_bytes()).hexdigest()
    if (project / "Content/TSTSS/Review/VerticalSlice").exists():
        raise RuntimeError("HOLD: review content exists; no overwrite/retry")
    if any((project / "Saved/SaveGames").glob("*.sav")) if (project / "Saved/SaveGames").exists() else False:
        raise RuntimeError("HOLD: review worktree has savegames")
    return project, expected.lower(), old_sha


def build():
    import unreal
    project, sha, original = assert_sandbox(unreal.Paths.project_dir())
    plan = review_plan()
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: dirty editor map")
    if unreal.EditorAssetLibrary.does_directory_exist(DEST):
        raise RuntimeError("HOLD: target asset directory already exists")
    if not unreal.EditorAssetLibrary.make_directory(DEST):
        raise RuntimeError("HOLD: cannot create isolated review directory")
    actor_sys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if actor_sys is None:
        raise RuntimeError("HOLD: no EditorActorSubsystem")
    primitive = {k: unreal.load_asset("/Engine/BasicShapes/" + k + "." + k)
                 for k in ("Cube", "Plane", "Sphere", "Cylinder", "Cone")}
    if any(v is None for v in primitive.values()):
        raise RuntimeError("HOLD: required engine geometry absent")

    # Native PBR preview materials; a material creation error is not quietly
    # reclassified as cinematic acceptance.
    materials = {}
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    for name, rgb in PALETTE.items():
        mat_name = "M_VS_" + name.title().replace("_", "")
        mat = asset_tools.create_asset(mat_name, DEST,
                                       unreal.Material, unreal.MaterialFactoryNew())
        if mat is None:
            raise RuntimeError("HOLD: material authoring failed: " + name)
        color = unreal.MaterialEditingLibrary.create_material_expression(
            mat, unreal.MaterialExpressionConstant3Vector, -350, 0)
        color.set_editor_property("constant", unreal.LinearColor(*rgb, 1.0))
        unreal.MaterialEditingLibrary.connect_material_property(
            color, "", unreal.MaterialProperty.MP_BASE_COLOR)
        rough = unreal.MaterialEditingLibrary.create_material_expression(
            mat, unreal.MaterialExpressionConstant, -350, 200)
        rough.set_editor_property("r", 0.45 if name in ("ocean", "brass", "aether") else 0.86)
        unreal.MaterialEditingLibrary.connect_material_property(
            rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
        unreal.MaterialEditingLibrary.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
        materials[name] = mat

    count = {}
    def spawn(cls, label, p, rotation=(0, 0, 0)):
        a = actor_sys.spawn_actor_from_class(
            cls, unreal.Vector(*p),
            unreal.Rotator(pitch=rotation[0], yaw=rotation[1], roll=rotation[2]))
        if a is None:
            raise RuntimeError("HOLD: unable to spawn " + label)
        a.set_actor_label(PREFIX + label)
        count["current"] += 1
        return a

    def prop(name, mesh, location, scale, surface="stone", solid=False, rotation=(0, 0, 0)):
        a = spawn(unreal.StaticMeshActor, name, location, rotation)
        comp = a.get_component_by_class(unreal.StaticMeshComponent)
        if comp is None:
            raise RuntimeError("HOLD: mesh component missing " + name)
        comp.set_static_mesh(primitive[mesh])
        comp.set_material(0, materials[surface])
        a.set_actor_scale3d(unreal.Vector(*scale))
        comp.set_collision_profile_name("BlockAll" if solid else "NoCollision")
        comp.set_collision_enabled(
            unreal.CollisionEnabled.QUERY_AND_PHYSICS if solid
            else unreal.CollisionEnabled.NO_COLLISION)
        return a

    def sign(name, txt, loc, size=37):
        a = spawn(unreal.TextRenderActor, name, loc)
        comp = a.get_component_by_class(unreal.TextRenderComponent)
        if comp is None:
            raise RuntimeError("HOLD: text component missing")
        comp.set_text(txt)
        comp.set_editor_property("world_size", float(size))
        return a

    def light(camera, yaw=20):
        spawn(unreal.DirectionalLight, "SunKey", (0, 0, 2200), (-35, yaw, 0))
        spawn(unreal.SkyLight, "SkyAmbient", (0, 0, 1300))
        for cname, suffix in (("SkyAtmosphere", "Atmosphere"),
                              ("ExponentialHeightFog", "AerialFog")):
            c = getattr(unreal, cname, None)
            if c is not None:
                spawn(c, suffix, (0, 0, 0))
        c = spawn(unreal.CameraActor, "CinematicCompositionCamera", camera[0], camera[1])
        return c

    def player(loc):
        spawn(unreal.PlayerStart, "PlayerStart_Review", loc)

    def harbor():
        # Existing seven real interaction markers and their collision pathway
        # are preserved; scenic geometry lives outside the gameplay corridor.
        for i, x in enumerate((-3400, -2600, -1800, -1000, -200, 600, 1400)):
            prop("QuayPiling_%02d" % i, "Cylinder", (x, 1050, -180),
                 (0.8, 0.8, 4.0), "timber")
            prop("HarborLamp_%02d" % i, "Cylinder", (x, -900, 280),
                 (0.10, 0.10, 5.6), "brass")
            prop("LampGlowHousing_%02d" % i, "Sphere", (x, -900, 565),
                 (0.40, 0.40, 0.40), "warm")
        for i, (x, y, sx, sy) in enumerate((
                (-3100, -1600, 6, 4), (-1900, -1750, 8, 5),
                (-300, -1700, 7, 5), (1700, -1550, 6, 4))):
            prop("HarborWarehouse_%d" % i, "Cube", (x, y, 380),
                 (sx, sy, 7), "stone")
            prop("TimberRoof_%d" % i, "Cube", (x, y, 770),
                 (sx+0.6, sy+0.7, 0.7), "timber")
        prop("SeawardQuayLine", "Cube", (-600, 1080, 40),
             (64, 2, 1.3), "timber")
        prop("OceanDeepVisual", "Plane", (0, 5700, -69),
             (150, 115, 1), "ocean")
        prop("Breakwater", "Cube", (1800, 2900, -20),
             (35, 4, 2), "dark_stone")
        for i in range(8):
            prop("SeaBeacon_%d" % i, "Cylinder",
                 (-3600 + i*1080, 2600, 30), (0.25, 0.25, 4), "brass")
        sign("DENITH_HARBOR_Sign", "DENITH HARBOR   |   FIRST WAKE", (-3300, -950, 740), 68)
        sign("FuelShantyForeshadow", "Harbor fuel shanty  |  closed pending return",
             (-3000, -1200, 270))
        light(((-3400, -3500, 1400), (-14, 35, 0)))

    def ship():
        prop("SeaHull_AuthoringProxy", "Sphere", (0, 0, -245),
             (13, 6.5, 3), "dark_stone")
        prop("MainWalkableDeck", "Cube", (0, 0, -50), (24, 10, 1), "timber", True)
        prop("Forecastle", "Cube", (950, 0, 75), (6, 8, 1.2), "timber", True)
        prop("BridgeDeck", "Cube", (-780, 0, 65), (7, 9, 1.4), "stone", True)
        prop("GeodesicBridgeSilhouette_NotGlass", "Sphere", (-780, 0, 350),
             (3.5, 4.0, 3.0), "aether")
        for i, y in enumerate((-545, 545)):
            prop("DeckRail_PortStarboard_%d" % i, "Cube", (0, y, 130),
                 (25, 0.15, 1), "brass")
        for i, (x, y, yaw) in enumerate((
                (-500, 620, 35), (500, 620, -35),
                (-500, -620, -35), (500, -620, 35))):
            prop("DragonflyWing_%d_Proxy" % i, "Cube", (x, y, 320),
                 (8, 2.3, 0.18), "aether", False, (0, yaw, 11))
        for i, (x, title) in enumerate(((-250, "LIFT"),
                                        (250, "PRESSURE"),
                                        (750, "RESERVE"))):
            prop("HarmonicStation_%s" % title, "Cylinder",
                 (x, -250, 140), (0.9, 0.9, 2.2), "brass")
            prop("InstrumentCore_%s" % title, "Sphere",
                 (x, -250, 270), (0.7, 0.7, 0.7), "aether")
            sign("EngineeringStationLabel_%s" % title,
                 "%s  |  inspection staging only" % title, (x-150, -410, 390))
        prop("MainHarmonicLevitationEngine_Proxy", "Cylinder", (100, 240, 180),
             (2.0, 2.0, 4), "brass")
        player((-1080, 0, 120))
        sign("SHIP_Review", "AUREATE WAKE  |  review-only shipboard volumes",
             (-1150, -500, 730), 44)
        light(((-1800, -2350, 1350), (-17, 42, 0)))

    def sky():
        for i, (x, y, z, s) in enumerate((
                (-5800, 3500, -700, 17), (-1800, -4200, -1400, 22),
                (2500, 4500, -900, 20), (6500, -2500, -1800, 25),
                (9500, 3500, -800, 16), (-8000, -2500, 1100, 13))):
            prop("CloudShelf_%02d" % i, "Sphere", (x, y, z),
                 (s, s*.45, s*.20), "cloud")
        prop("AuroralPath_ReadabilityOnly", "Cube", (1200, 0, 2700),
             (105, 0.18, 0.13), "aether", False, (0, 0, 10))
        prop("FlyingHull_NotActualFlightPawn", "Sphere", (0, 0, 700),
             (8, 4, 2), "dark_stone")
        for i, (x, y, yaw) in enumerate((
                (-250, -480, 35), (250, -480, -35),
                (-250, 480, -35), (250, 480, 35))):
            prop("WingFlightPose_%d" % i, "Cube", (x, y, 960),
                 (5.0, 2.5, 0.12), "aether", False, (0, yaw, 8))
        # No player start, flight pawn or fake physics authority in this map.
        sign("FlightReviewGate", "FIRST WAKE  |  flight gameplay not yet wired",
             (-1300, -1250, 1300), 60)
        light(((-1700, -3500, 1900), (-8, 30, 0)))

    def sea():
        # Show ocean but keep the one native adapter volume isolated.
        prop("OceanHorizon_Visual_NoCollision", "Plane", (0, 0, 316),
             (260, 260, 1), "ocean")
        for i, x in enumerate((-12500, -10300, 11000, 13300)):
            prop("DistantRock_%d" % i, "Sphere", (x, 8500, 120),
                 (16, 12, 7), "dark_stone")
        water = prop("PhysicalWaterProbeVolume", "Cube", (0, 0, -80),
                     (30, 30, 8), "ocean")
        mesh = water.get_component_by_class(unreal.StaticMeshComponent)
        mesh.set_collision_profile_name("OverlapAllDynamic")
        mesh.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
        mesh.set_editor_property("generate_overlap_events", True)
        water.set_editor_property("tags", [unreal.Name("TSTSSWaterVolume")])
        hull_cl = unreal.load_class(None,
            "/Script/ToSailTheStarrySky.TSTSSWaterContactAdapter")
        if hull_cl is None:
            raise RuntimeError("HOLD: native physical water adapter unavailable")
        hull = spawn(hull_cl, "PhysicsHullReviewProxy_NotCanon", (0, 0, 520))
        comp = hull.get_component_by_class(unreal.StaticMeshComponent)
        if comp is None:
            raise RuntimeError("HOLD: real adapter has no mesh")
        comp.set_static_mesh(primitive["Cube"])
        comp.set_material(0, materials["brass"])
        hull.set_actor_scale3d(unreal.Vector(3, 2, 1.2))
        comp.set_collision_profile_name("PhysicsActor")
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        comp.set_editor_property("generate_overlap_events", True)
        comp.set_mobility(unreal.ComponentMobility.MOVABLE)
        comp.set_simulate_physics(False)
        hull.set_editor_property("arm_prototype_physics_on_launch", True)
        hull.set_editor_property("enable_prototype_buoyancy", True)
        sign("SplashdownWarning", "PHYSICAL WATER LAB  |  story + contact gates required",
             (-1400, -1900, 850), 56)
        light(((-3200, -4500, 1600), (-10, 27, 0)))

    def shanty():
        prop("CoastalPlatform", "Cube", (0, 0, -50),
             (34, 26, 1), "sand", True)
        prop("TideShallow_Visual", "Plane", (0, 4000, -66),
             (115, 110, 1), "ocean")
        for i, (x, y) in enumerate((
                (-800,-600), (-800,600), (800,-600), (800,600))):
            prop("ShantyStilt_%d" % i, "Cylinder", (x, y, 120),
                 (0.5, 0.5, 4), "timber")
        prop("FuelShantyCabin", "Cube", (0, 0, 420),
             (17, 12, 6), "timber")
        prop("FuelShantyRoof", "Cube", (0, 0, 765),
             (19, 14, .8), "dark_stone")
        prop("FuelPier", "Cube", (0, 1750, 20),
             (5, 30, .8), "timber", True)
        for i, (x, y) in enumerate(((-1050,-900), (-950,-1300),
                                     (1150,-900), (1250,-1300))):
            prop("ReserveBarrel_%d" % i, "Cylinder", (x, y, 120),
                 (0.55, 0.55, 2.1), "brass")
        sign("FuelShop", "DENITH FUEL SHANTY  |  no reserve grant implemented",
             (-1350, -850, 950), 56)
        player((-1550, -300, 140))
        light(((-2300, -3200, 1650), (-16, 29, 0)))

    def shore():
        prop("SandCoast", "Cube", (0, 0, -80),
             (55, 36, 1.6), "sand", True)
        prop("TidalShelf", "Plane", (0, 3600, -66),
             (110, 92, 1), "ocean")
        for i, (x, y, s) in enumerate((
                (-2100,-1900,9), (-1000,-2300,13), (1600,-2400,11),
                (2900,-1400,7), (-3300,-400,5))):
            prop("BasaltCliff_%d" % i, "Sphere", (x, y, s*35),
                 (s*2.3, s*1.5, s*1.2), "stone")
        for i, (x,y) in enumerate((
                (-2900,450), (-1500,700), (0,800),
                (1500,630), (2900,530))):
            prop("TidalStone_%d" % i, "Sphere", (x,y,55),
                 (2.8,2.2,1), "dark_stone")
        prop("DistantTreeCanopy", "Sphere", (-3000,-2700,1280),
             (5,5,4), "green")
        prop("DistantTreeTrunk", "Cylinder", (-3000,-2700,520),
             (.7,.7,11), "timber")
        player((-2700, -100, 160))
        sign("ShoreBeatStaging", "SPLASHDOWN SHORE  |  Lyra appears only after narrative gate",
             (-2500, -950, 660), 42)
        light(((-4600, -4800, 2400), (-13, 32, 0)))

    authors = (harbor, ship, sky, sea, shanty, shore)
    hashes = {}
    for ix, ((name, _, _), author) in enumerate(zip(ORDER, authors)):
        count["current"] = 0
        world = (unreal.EditorLoadingAndSavingUtils.load_map(PARENT_PACKAGE)
                 if ix == 0 else unreal.EditorLoadingAndSavingUtils.new_blank_map(False))
        if world is None:
            raise RuntimeError("HOLD: map creation failed: " + name)
        author()
        package = DEST + "/" + name
        if not unreal.EditorLoadingAndSavingUtils.save_map(world, package):
            raise RuntimeError("HOLD: could not save map: " + name)
        f = project / "Content/TSTSS/Review/VerticalSlice" / (name + ".umap")
        if not f.is_file():
            raise RuntimeError("HOLD: saved level missing: " + name)
        hashes[name] = {"sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                        "bytes": f.stat().st_size,
                        "new_actors": count["current"]}
        unreal.log("TSTSS_VSLICE_MAP_SAVED " + name + " " + hashes[name]["sha256"])
    if hashlib.sha256((project / PARENT).read_bytes()).hexdigest() != original:
        raise RuntimeError("HOLD: canonical parent review map was mutated")
    report = project / "Saved/VerticalSliceMaps/authoring_receipt.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({
        **plan, "source_head": sha, "parent_sha256_unchanged": original,
        "native_map_staging": hashes, "status": "MAP_FILES_SAVED_NO_PIE_ACCEPTANCE"
    }, indent=2) + "\n", encoding="utf-8")
    unreal.log("TSTSS_VSLICE_SIX_MAPS_SAVED_NOT_PIE")
    return hashes


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan", action="store_true")
    g.add_argument("--build", action="store_true")
    args = p.parse_args()
    print(json.dumps(build() if args.build else review_plan(), indent=2))
