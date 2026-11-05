#!/usr/bin/env python3
"""Opt-in, noncanonical UE5 First Wake launch/physical-water greybox authoring.

Creates a NEW V3 review map from the immutable tracked seven-stop V2 Prelude.
Contains a prototype hull/water observer, not approved Aureate Wake geometry.
No Editor/PIE has been executed by this source-only script's checks.
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

import build_first_wake_prelude_interaction as v2
import verify_first_wake_v2_independent as locked

SANDBOX = "TSTSS_FirstWakeSplashdownSandbox_20261103"
MAP = "/Game/TSTSS/Review/FirstWake_LaunchWaterGreybox_V1"
ASSET_PATH = "Content/TSTSS/Review/FirstWake_LaunchWaterGreybox_V1.umap"
ORIGINAL_MAP = "Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"
PREFIX = "TSTSS_SPLASHDOWN_GREYBOX_"
EXTRA_STOPS = (
    ("LaunchMarker", 1580.0, "Launched", "08  Authorize First Wake launch  [E]"),
    ("EmptyReserveMarker", 1990.0, "EmptyReserveInspected",
     "09  Investigate reserves AFTER flotation  [E]"),
    ("ReturnBerthMarker", 2370.0, "ReturnedToBerth",
     "10  Return to berth AFTER empty reserve  [E]"),
)
# Isolated water-physics lab is off the existing dock. Unreal centimeters.
WATER_LOCATION = (3600.0, 2500.0, -80.0)
WATER_SCALE = (15.0, 14.0, 8.0)
HULL_LOCATION = (3600.0, 2500.0, 500.0)
HULL_SCALE = (3.0, 2.0, 1.2)


def validate_plan() -> dict:
    old = v2.validate_plan()
    floor_min, floor_max = old["authoring_geometry_only"]["floor_x_cm"]
    all_names = [stop.label for stop in v2.STOPS]
    all_names.extend(stop[0] for stop in EXTRA_STOPS)
    if len(all_names) != len(set(all_names)):
        raise RuntimeError("Greybox marker names must be distinct from Prelude")
    previous = v2.STOPS[-1].x
    for name, x, beat, _ in EXTRA_STOPS:
        if x <= previous or x - v2.REVIEW_MARKER_HALF_WIDTH_CM <= floor_min or (
                x + v2.REVIEW_MARKER_HALF_WIDTH_CM >= floor_max):
            raise RuntimeError("Greybox recovery stop outside ordered traversal floor: " + name)
        previous = x
    if [stop[2] for stop in EXTRA_STOPS] != [
            "Launched", "EmptyReserveInspected", "ReturnedToBerth"]:
        raise RuntimeError("First Wake review story beats must remain ordered")
    water_z = WATER_LOCATION[2] + WATER_SCALE[2] * 50.0
    first_hull_bottom = HULL_LOCATION[2] - HULL_SCALE[2] * 50.0
    if (not all(math.isfinite(x) for x in (
            *WATER_LOCATION, *WATER_SCALE, *HULL_LOCATION, *HULL_SCALE)) or
            min(*WATER_SCALE, *HULL_SCALE) <= 0 or
            first_hull_bottom <= water_z or
            abs(HULL_LOCATION[0] - WATER_LOCATION[0]) > 100 or
            abs(HULL_LOCATION[1] - WATER_LOCATION[1]) > 100):
        raise RuntimeError("Prototype hull must start above a bounded water surface")
    # The lab is physically separated from Ender's traversal dock.
    if WATER_LOCATION[0] <= floor_max + 200 or WATER_LOCATION[1] <= 2000:
        raise RuntimeError("Physical greybox must not obstruct Prelude traversal")
    return {
        "status": "SOURCE_AUTHORED_GREYBOX_PLAN_NOT_EDITOR_OR_PIE",
        "new_map": MAP, "immutable_parent_map": v2.REVIEW_MAP,
        "parent_map_sha256": locked.MAP_SHA256,
        "parent_stop_count": len(v2.STOPS),
        "new_stops": [{"label": n, "x_cm": x, "beat": beat}
                      for n, x, beat, _ in EXTRA_STOPS],
        "water_tag": "TSTSSWaterVolume",
        "water_center_cm": WATER_LOCATION, "water_scale": WATER_SCALE,
        "water_surface_top_cm": water_z,
        "hull_initial_center_cm": HULL_LOCATION, "hull_scale": HULL_SCALE,
        "hull_initial_bottom_cm": first_hull_bottom,
        "proto_buoyancy_explicitly_opted_in": True,
        "ship_geometry_approved": False,
        "playable_or_cinematic_approved": False,
        "real_physics_verified": False,
        "native_build_or_pie_tested": False,
        "early_lyra_recruited": False,
        "starbourne_unlocked": False,
        "protected_map_changed": False,
    }


def require_sandbox(project: Path) -> tuple[Path, str]:
    project = project.resolve()
    root = project.parent
    if project.name.lower() != "unreal" or root.name != SANDBOX:
        raise RuntimeError("HOLD: author only in explicitly named disposable Splashdown greybox sandbox")
    expected = os.environ.get("TSTSS_GREYBOX_EXPECTED_HEAD", "")
    if not re.fullmatch("[0-9a-fA-F]{40}", expected):
        raise RuntimeError("HOLD: exact 40-character TSTSS_GREYBOX_EXPECTED_HEAD required")
    def git(*args: str) -> str:
        p = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                           text=True, timeout=20, check=False)
        if p.returncode:
            raise RuntimeError("HOLD: Git custody command failed")
        return p.stdout.strip()
    if git("rev-parse", "HEAD").lower() != expected.lower():
        raise RuntimeError("HOLD: greybox checkout SHA differs from explicit request")
    if git("status", "--porcelain"):
        raise RuntimeError("HOLD: greybox sandbox must be clean before Editor authoring")
    old = project / ORIGINAL_MAP
    if not old.is_file() or hashlib.sha256(old.read_bytes()).hexdigest() != locked.MAP_SHA256:
        raise RuntimeError("HOLD: immutable V2 Prelude map bytes changed")
    if (project / ASSET_PATH).exists():
        raise RuntimeError("HOLD: new review map already exists, refusing overwrite")
    save_dir = project / "Saved/SaveGames"
    if save_dir.exists() and list(save_dir.glob("*.sav")):
        raise RuntimeError("HOLD: greybox sandbox has SaveGame files; leave them untouched")
    for name in ("DefaultInput.ini", "DefaultEngine.ini"):
        if not (project / "Config" / name).is_file():
            raise RuntimeError("HOLD: protected default config file missing")
    return project, expected.lower()


def reflected_enum(enum_type, name: str):
    target = name.replace("_", "").upper()
    matches = [getattr(enum_type, key) for key in dir(enum_type)
               if key.isupper() and key.replace("_", "") == target]
    if len(matches) != 1:
        raise RuntimeError("HOLD: ambiguous reflected native beat " + name)
    return matches[0]


def build_in_unreal() -> dict:
    plan = validate_plan()
    import unreal  # Only in the real Editor commandlet/asset authoring context.

    project, expected_head = require_sandbox(Path(unreal.Paths.project_dir()))
    if unreal.EditorAssetLibrary.does_asset_exist(MAP):
        raise RuntimeError("HOLD: target map exists in asset registry; no overwrite")
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: another dirty Editor map exists; no discard")
    parent_map = project / ORIGINAL_MAP
    original_hash = hashlib.sha256(parent_map.read_bytes()).hexdigest()

    world = unreal.EditorLoadingAndSavingUtils.load_map(v2.REVIEW_MAP)
    if world is None:
        raise RuntimeError("HOLD: immutable V2 Prelude map did not load")
    editor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    milestone_class = unreal.load_class(None, v2.MILESTONE_CLASS)
    hull_class = unreal.load_class(None, "/Script/ToSailTheStarrySky.TSTSSWaterContactAdapter")
    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if editor is None or milestone_class is None or hull_class is None or cube is None:
        raise RuntimeError("HOLD: actual native classes, Editor subsystem or BasicShapes cube missing")

    def spawn(cls, label, location):
        actor = editor.spawn_actor_from_class(
            cls, unreal.Vector(*location),
            unreal.Rotator(pitch=0, yaw=0, roll=0))
        if actor is None:
            raise RuntimeError("HOLD: cannot spawn actual review actor " + label)
        actor.set_actor_label(PREFIX + label)
        return actor

    for name, x, beat, caption in EXTRA_STOPS:
        marker = spawn(milestone_class, name, (x, 0, 90))
        mesh = marker.get_component_by_class(unreal.StaticMeshComponent)
        if mesh is None:
            raise RuntimeError("HOLD: milestone has no native collision mesh")
        mesh.set_static_mesh(cube)
        marker.set_actor_scale3d(unreal.Vector(0.75, 0.75, 1.6))
        mesh.set_collision_profile_name("BlockAll")
        mesh.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        marker.set_editor_property("is_inspection_station", False)
        marker.set_editor_property("milestone", reflected_enum(unreal.TSTSSFirstWakeBeat, beat))
        sign = spawn(unreal.TextRenderActor, "SIGN_" + name, (x - 175.0, 100.0, 250.0))
        text = sign.get_component_by_class(unreal.TextRenderComponent)
        if text is None:
            raise RuntimeError("HOLD: milestone has no readable label component")
        text.set_text(caption)
        text.set_editor_property("world_size", 45.0)

    water = spawn(unreal.StaticMeshActor, "LAB_WaterVolume_NotCanonicalOcean", WATER_LOCATION)
    water_mesh = water.get_component_by_class(unreal.StaticMeshComponent)
    if water_mesh is None:
        raise RuntimeError("HOLD: water lab has no collision volume")
    water_mesh.set_static_mesh(cube)
    water.set_actor_scale3d(unreal.Vector(*WATER_SCALE))
    water_mesh.set_collision_profile_name("OverlapAllDynamic")
    water_mesh.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
    # UE 5.8 Python exposes overlap generation as a reflected read/write
    # property, not a set_generate_overlap_events() component method.
    water_mesh.set_editor_property("generate_overlap_events", True)
    if not water_mesh.get_editor_property("generate_overlap_events"):
        raise RuntimeError("HOLD: water overlap events were not enabled")
    water.set_editor_property("tags", [unreal.Name("TSTSSWaterVolume")])

    hull = spawn(hull_class, "LAB_AureateHullPhysicsProxy_NotCanon", HULL_LOCATION)
    hull_mesh = hull.get_component_by_class(unreal.StaticMeshComponent)
    if hull_mesh is None:
        raise RuntimeError("HOLD: native water adapter has no Hull mesh")
    hull_mesh.set_static_mesh(cube)
    hull.set_actor_scale3d(unreal.Vector(*HULL_SCALE))
    hull_mesh.set_collision_profile_name("PhysicsActor")
    hull_mesh.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    hull_mesh.set_editor_property("generate_overlap_events", True)
    if not hull_mesh.get_editor_property("generate_overlap_events"):
        raise RuntimeError("HOLD: hull overlap events were not enabled")
    hull_mesh.set_mobility(unreal.ComponentMobility.MOVABLE)
    # The player must authorize launch before gravity can drop the hull.
    # Runtime opt-in arms this exact dry pose on the real Launched story beat.
    hull_mesh.set_simulate_physics(False)
    hull.set_editor_property("arm_prototype_physics_on_launch", True)
    hull.set_editor_property("enable_prototype_buoyancy", True)
    # Native bAutoBindPlayerStory defaults true: story authority still requires
    # First Wake launch, actual overlap, finite velocity and two stable seconds.
    # This is a controlled synthetic hull, NOT a real authored Aureate Wake.

    if not unreal.EditorLoadingAndSavingUtils.save_map(world, MAP):
        raise RuntimeError("HOLD: Editor could not save NEW greybox map")
    if hashlib.sha256(parent_map.read_bytes()).hexdigest() != original_hash:
        raise RuntimeError("HOLD: original tracked Prelude map changed")
    output = project / ASSET_PATH
    if not output.is_file():
        raise RuntimeError("HOLD: new UE map file not materialized")
    report = project / "Saved/SplashdownGreyboxV1/staging_receipt.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    result = dict(plan, status="NEW_GREYBOX_MAP_SAVED_NOT_PIE",
                  tested_git_head=expected_head,
                  new_map_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    with report.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    unreal.log("TSTSS_SPLASHDOWN_GREYBOX_SAVED_NOT_PLAYTESTED " + str(output))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--validate", action="store_true")
    actions.add_argument("--build", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(build_in_unreal() if args.build else validate_plan(), indent=2))


if __name__ == "__main__":
    main()
