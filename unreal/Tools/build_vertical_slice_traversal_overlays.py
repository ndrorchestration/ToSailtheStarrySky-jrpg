#!/usr/bin/env python3
"""Create additive PIE-only traversal overlays for the six saved environment maps.

Never overwrites the native source maps and never alters persistence or physics
authority. These maps use simple review navigation, NOT finished flight gameplay.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_vertical_slice_environment_maps as original

ROOT_NAME = original.SANDBOX
SOURCE_DIR = "Content/TSTSS/Review/VerticalSlice"
DEST = "/Game/TSTSS/Review/VerticalSliceTraversal"
SCENE_NAMES = tuple(name + "_TraversalReviewV1" for name, _, _ in original.ORDER)
SCENE_PACKAGES = tuple(DEST + "/" + name for name in SCENE_NAMES)
GATES = (
    ("DenithHarbor", (-650.0, 450.0, 90.0)),
    ("AureateInteriors", (1050.0, 330.0, 90.0)),
    ("FirstWakeSky", (3000.0, 0.0, 90.0)),
    ("SplashdownSea", (-1900.0, -1600.0, 540.0)),
    ("DenithFuelShanty", (1050.0, 900.0, 90.0)),
)
CUE = (
    "Board ship  |  Ionia required",
    "Launch corridor  |  signed-off and launched required",
    "Sea contact lab  |  NOT a landing or flight proof",
    "Fuel shanty  |  physical stable flotation required",
    "Shore  |  post-contact empty reserve inspected",
)
ACTOR_PREFIX = "TSTSS_ROUTE_REVIEW_"
# Center x/y, walkable top z, half-width x/y; centimeter units.
SAFE_REVIEW_FLOORS = (
    (-600, 0, 0, 3150, 700),
    (0, 0, 0, 1200, 500),
    (500, 0, 0, 4500, 450),
    (-2600, -1600, 450, 1300, 500),
    (0, 0, 0, 1700, 1300),
    (0, 0, 0, 2750, 1800),
)


def validate_plan():
    names = tuple(name for name, _, _ in original.ORDER)
    if len(names) != len(SCENE_PACKAGES) or len(names) != 6 or len(GATES) != 5:
        raise RuntimeError("HOLD: six levels and five routes required")
    if not all(item[0] == names[idx].replace("VS%02d_" % (idx + 1), "")
               for idx, item in enumerate(GATES)):
        raise RuntimeError("HOLD: route ordering drift")
    if "VS04_SplashdownSea" not in names or len(SAFE_REVIEW_FLOORS) != len(names):
        raise RuntimeError("HOLD: water lab or floor bounds missing")
    for index, (_, xyz) in enumerate(GATES):
        cx, cy, top, hx, hy = SAFE_REVIEW_FLOORS[index]
        if not (abs(xyz[0] - cx) < hx - 100 and
                abs(xyz[1] - cy) < hy - 100 and
                top <= xyz[2] <= top + 150):
            raise RuntimeError("HOLD: gate does not fit safe walkable floor")
    return {
        "kind": "SOURCE_ONLY_TRAVERSAL_OVERLAY_PLAN",
        "base_maps": [original.DEST + "/" + name for name in names],
        "new_maps": list(SCENE_PACKAGES),
        "transfer_order": [list(x) for x in GATES],
        "input": "Existing E interaction, 300cm pawn proximity",
        "authority": "PIE_ONLY_ILLUSTRATIVE_WALK_ROUTE",
        "preserves_physical_water_gate": True,
        "no_shipping_approval": True,
        "no_automatic_landing": True,
        "no_automatic_recruitment": True,
        "no_starbourne": True,
        "inter_level_PIE_tested": False,
        "fall_prevention_barriers_proposed": True,
        "native_collision_barrier_tested": False,
    }


def require_sandbox(project):
    project = Path(project).resolve()
    if project.name.lower() != "unreal" or project.parent.name != ROOT_NAME:
        raise RuntimeError("HOLD: traversal overlay must use isolated review worktree")
    sha = os.environ.get("TSTSS_TRAVERSAL_EXPECTED_HEAD", "")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
        raise RuntimeError("HOLD: explicit source HEAD required")
    p = subprocess.run(["git", "-C", str(project.parent), "rev-parse", "HEAD"],
                       capture_output=True, text=True, timeout=20)
    if p.returncode != 0 or p.stdout.strip().lower() != sha.lower():
        raise RuntimeError("HOLD: wrong source head")
    p = subprocess.run(["git", "-C", str(project.parent), "status", "--porcelain"],
                       capture_output=True, text=True, timeout=20)
    if p.returncode or p.stdout.strip():
        raise RuntimeError("HOLD: dirty source checkout")
    report = project / "Docs/Evidence/vertical_slice_map_authoring_20261110.json"
    if not report.exists():
        raise RuntimeError("HOLD: missing original native map receipts")
    hashes = json.loads(report.read_text(encoding="utf-8"))["native_map_staging"]
    for name, _, _ in original.ORDER:
        source = project / SOURCE_DIR / (name + ".umap")
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != hashes[name]["sha256"]:
            raise RuntimeError("HOLD: base map is not original verified bytes: " + name)
    if (project / "Content/TSTSS/Review/VerticalSliceTraversal").exists():
        raise RuntimeError("HOLD: traversal overlay files already exist")
    if (project / "Saved/SaveGames").exists() and list((project / "Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: save files present")
    return project, sha.lower(), hashes


def enum_value(enum_type, name):
    target = name.replace("_", "").upper()
    matches = [getattr(enum_type, k) for k in dir(enum_type)
               if k.isupper() and k.replace("_", "") == target]
    if len(matches) != 1:
        raise RuntimeError("HOLD: unexpected native enum: " + name)
    return matches[0]


def build():
    import unreal
    project, sha, hashes = require_sandbox(unreal.Paths.project_dir())
    if unreal.EditorAssetLibrary.does_directory_exist(DEST):
        raise RuntimeError("HOLD: target asset directory exists")
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: cannot author with dirty maps")
    if not unreal.EditorAssetLibrary.make_directory(DEST):
        raise RuntimeError("HOLD: failed to create additive traversal directory")
    route_class = unreal.load_class(
        None, "/Script/ToSailTheStarrySky.TSTSSReviewRouteGate")
    marker_class = unreal.load_class(
        None, "/Script/ToSailTheStarrySky.TSTSSMilestoneActor")
    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if route_class is None or marker_class is None or cube is None:
        raise RuntimeError("HOLD: new compiled route class and existing milestone class required")
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if subsystem is None:
        raise RuntimeError("HOLD: missing EditorActorSubsystem")

    def spawn(cls, name, xyz):
        actor = subsystem.spawn_actor_from_class(
            cls, unreal.Vector(*xyz), unreal.Rotator(pitch=0, yaw=0, roll=0))
        if actor is None:
            raise RuntimeError("HOLD: cannot spawn " + name)
        actor.set_actor_label(name)
        return actor

    def box(name, xyz, scale, solid):
        actor = spawn(unreal.StaticMeshActor, ACTOR_PREFIX + name, xyz)
        comp = actor.get_component_by_class(unreal.StaticMeshComponent)
        if comp is None:
            raise RuntimeError("HOLD: missing static mesh component")
        comp.set_static_mesh(cube)
        actor.set_actor_scale3d(unreal.Vector(*scale))
        comp.set_collision_profile_name("BlockAll" if solid else "NoCollision")
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS
                                   if solid else unreal.CollisionEnabled.NO_COLLISION)
        return actor

    def sign(name, phrase, xyz):
        actor = spawn(unreal.TextRenderActor, ACTOR_PREFIX + name, xyz)
        comp = actor.get_component_by_class(unreal.TextRenderComponent)
        if comp is None:
            raise RuntimeError("HOLD: TextRender missing")
        comp.set_text(phrase)
        comp.set_editor_property("world_size", 37.0)

    def marker(name, xyz, beat=None, inspection=None):
        actor = spawn(marker_class, "TSTSS_SPLASHDOWN_GREYBOX_" + name, xyz)
        mesh = actor.get_component_by_class(unreal.StaticMeshComponent)
        if mesh is None:
            raise RuntimeError("HOLD: native milestone collision missing")
        mesh.set_static_mesh(cube)
        actor.set_actor_scale3d(unreal.Vector(0.65, 0.65, 1.6))
        mesh.set_collision_profile_name("BlockAll")
        mesh.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        if inspection is not None:
            actor.set_editor_property("is_inspection_station", True)
            actor.set_editor_property("inspection_station",
                                      enum_value(unreal.TSTSSInspectionStation, inspection))
        else:
            if beat in ("SeaContact", "FlotationConfirmed"):
                raise RuntimeError("HOLD: cannot author milestone capable of faking water physics")
            actor.set_editor_property("milestone", enum_value(unreal.TSTSSFirstWakeBeat, beat))
        return actor

    result = {}
    for index, (base, _, _) in enumerate(original.ORDER):
        source_package = original.DEST + "/" + base
        world = unreal.EditorLoadingAndSavingUtils.load_map(source_package)
        if world is None:
            raise RuntimeError("HOLD: failed to load source level: " + base)

        if index == 1:
            # Actual E-driven milestone actors allow stage continuity. Existing
            # geometry is inert and nonblocking.
            marker("ShipLiftReview", (-250, -250, 90), inspection="Lift")
            marker("ShipPressureReview", (225, -250, 90), inspection="Pressure")
            marker("ShipReserveReview", (700, -250, 90), inspection="Reserve")
            marker("ShipEngineeringApprovalReview", (1000, -210, 90),
                   beat="EngineeringChecked")
            marker("ShipLaunchReview", (1090, 130, 90), beat="Launched")
            sign("ShipReviewDisclaimer",
                 "Review proxy: lift, pressure, reserve, signoff, then launch",
                 (-920, -340, 400))
        elif index == 2:
            # Source flight map has no pawn or collision floor. This temporary
            # review corridor is specifically NOT player-driven flight.
            box("SkyTraversalWalkway", (500, 0, -100), (90, 9, 2), True)
            spawn(unreal.PlayerStart, ACTOR_PREFIX + "SkyReviewStart",
                  (-3100, 0, 130))
            sign("SkyWalkDisclaimer",
                 "Temporary walk route | NOT actual atmospheric gameplay",
                 (-2800, -320, 370))
        elif index == 3:
            # Physical water is at 320 cm. Place the human review platform
            # above its surface and away from the active hull physics probe.
            box("SeaObserverDeck", (-2600, -1600, 350), (26, 10, 2), True)
            spawn(unreal.PlayerStart, ACTOR_PREFIX + "SeaObserverStart",
                  (-3400, -1600, 580))
            sign("SeaObserverDisclaimer",
                 "Water result requires real stabilized hull contact",
                 (-3200, -1830, 800))
        elif index == 4:
            marker("FuelShantyEmptyReserveReview", (-1000, -800, 90),
                   beat="EmptyReserveInspected")
            sign("PostContactDisclaimer",
                 "Fuel resolution review only; no inventory authority",
                 (-1200, 850, 520))
        elif index == 5:
            sign("ShoreEndOfReview",
                 "Chapter 1 shoreline | party and NPC systems not yet bound",
                 (-2450, -880, 740))

        # Preview containment: user playtests have previously walked off
        # unfinished dock/map bounds. Lightweight physical edge barriers stop
        # a fall without using teleports, story grants or disabling gravity.
        # Each tuple is floor center XY, walkable top Z and XY half-extents.
        cx, cy, top, hx, hy = SAFE_REVIEW_FLOORS[index]
        barrier_height = top + 120
        box("SafeEdgeWest", (cx-hx+35, cy, barrier_height),
            (0.35, (2*hy-70)/100, 2.4), True)
        box("SafeEdgeEast", (cx+hx-35, cy, barrier_height),
            (0.35, (2*hy-70)/100, 2.4), True)
        box("SafeEdgeSouth", (cx, cy-hy+35, barrier_height),
            ((2*hx-70)/100, 0.35, 2.4), True)
        # Shanty has an intentionally authored seaward pier, so leave its
        # center approach open instead of placing a wall across the pier.
        if index == 4:
            for side, x in (("West", -1000), ("East", 1000)):
                box("SafeEdgeNorth" + side, (x, cy+hy-35, barrier_height),
                    (13, 0.35, 2.4), True)
        else:
            box("SafeEdgeNorth", (cx, cy+hy-35, barrier_height),
                ((2*hx-70)/100, 0.35, 2.4), True)

        if index < len(GATES):
            _, xyz = GATES[index]
            gate = spawn(route_class, ACTOR_PREFIX + "Gate_" + base, xyz)
            component = gate.get_component_by_class(unreal.StaticMeshComponent)
            if component is None:
                raise RuntimeError("HOLD: review gate interaction collision missing")
            component.set_static_mesh(cube)
            gate.set_actor_scale3d(unreal.Vector(0.70, 0.70, 1.8))
            component.set_collision_profile_name("BlockAll")
            component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            gate.set_editor_property(
                "departure_stage",
                enum_value(unreal.TSTSSReviewMap, base.split("_", 1)[1]))
            sign("GateCue_" + base, CUE[index], (xyz[0]-200, xyz[1]-95, xyz[2]+180))

        destination = SCENE_PACKAGES[index]
        if not unreal.EditorLoadingAndSavingUtils.save_map(world, destination):
            raise RuntimeError("HOLD: map save failed: " + destination)
        path = project / "Content/TSTSS/Review/VerticalSliceTraversal" / (SCENE_NAMES[index] + ".umap")
        if not path.is_file():
            raise RuntimeError("HOLD: level not saved: " + destination)
        orig_file = project / SOURCE_DIR / (base + ".umap")
        if hashlib.sha256(orig_file.read_bytes()).hexdigest() != hashes[base]["sha256"]:
            raise RuntimeError("HOLD: original verified level mutated: " + base)
        result[SCENE_NAMES[index]] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size, "source_map": source_package,
            "runtime_traversal_PIE_verified": False,
        }
        unreal.log("TSTSS_TRAVERSAL_MAP_SAVED " + SCENE_NAMES[index])
    receipt = project / "Saved/VerticalSliceMaps/traversal_overlay_receipt.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({
        "source_head": sha, "results": result,
        "status": "NATIVE_TRAVERSAL_MAPS_SAVED_NOT_PIE_TESTED"
    }, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--plan", action="store_true")
    actions.add_argument("--build", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build() if args.build else validate_plan(), indent=2))
