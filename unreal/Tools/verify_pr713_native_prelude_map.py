#!/usr/bin/env python3
"""Actual Unreal Editor V2 Prelude map QA in an isolated source-locked worktree.

This exercises editor-loaded ACTUAL reflected C++ milestone actors, collision
components, out-of-order/order/inspection state and read-only objective text.
It deliberately does NOT run PIE, inject WASD/E/J/F5/F9, save/load a disk
SaveGame, modify the map, or confer physics/art/Chapter 1 approval.

Invoke via UnrealEditor-Cmd.exe -run=pythonscript -script=<this file> with
TSTSS_REVIEW_EXPECTED_HEAD set to the *full* pinned Git commit hash.
Review output remains local under ignored unreal/Saved/NativePreludeMapQA.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone
from uuid import uuid4

import verify_first_wake_v2_independent as reference

EXPECTED_PARENT = "TSTSS_PR713_NativeMapQA_20261102"
MAP_PACKAGE = reference.MAP_PACKAGE
MAP_RELATIVE = reference.MAP_RELATIVE
MAP_SHA256 = reference.MAP_SHA256
STOP_SPECS = reference.STOPS
LABEL_PREFIX = reference.ACTOR_PREFIX


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, timeout=25, check=False,
    )
    if proc.returncode:
        raise RuntimeError("Git source-custody command failed: " + " ".join(args))
    return proc.stdout.strip()


def check_source(project: Path, expected: str) -> dict:
    root = project.parent
    if project.name.lower() != "unreal" or root.name != EXPECTED_PARENT:
        raise RuntimeError("HOLD: not the explicitly named disposable PR713 map worktree")
    if not re.fullmatch("[a-fA-F0-9]{40}", expected):
        raise RuntimeError("HOLD: expected Git HEAD must be 40 hex characters")
    actual = git(root, "rev-parse", "HEAD")
    if actual.lower() != expected.lower():
        raise RuntimeError("HOLD: checkout SHA does not match explicit review request")
    if git(root, "status", "--porcelain"):
        raise RuntimeError("HOLD: review checkout is dirty before map inspection")
    map_path = project / MAP_RELATIVE
    if not map_path.is_file() or digest(map_path) != MAP_SHA256:
        raise RuntimeError("HOLD: committed V2 map SHA-256 changed")
    default_engine = project / "Config" / "DefaultEngine.ini"
    default_input = project / "Config" / "DefaultInput.ini"
    source_bindings = reference.inspect_input_source(project)
    config = default_input.read_text(encoding="utf-8")
    character_cpp = (project / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(
        encoding="utf-8")
    if '+ActionMappings=(ActionName="ReviewObjective",Key=J)' not in config:
        raise RuntimeError("HOLD: J objective key not declared in review config")
    if 'BindAction(TEXT("ReviewObjective")' not in character_cpp:
        raise RuntimeError("HOLD: J input not bound to native review handler")
    for sensitive in (project / "Saved" / "SaveGames" / "first_wake_quick.sav",
                      project / "Saved" / "SaveGames" / "tstss_prelude_pie_quick.sav"):
        if sensitive.exists():
            raise RuntimeError("HOLD: review workspace contains a player or PIE save; do not inspect it")
    return {
        "head": actual,
        "map_path": str(map_path),
        "before_map_hash": digest(map_path),
        "config_hashes": {
            "DefaultEngine.ini": digest(default_engine),
            "DefaultInput.ini": digest(default_input),
        },
        "source_input_bindings": source_bindings,
    }


def check_native(project: Path, initial: dict) -> dict:
    import unreal
    engine = str(unreal.SystemLibrary.get_engine_version())
    if not engine.startswith("5.8.4"):
        raise RuntimeError("HOLD: actual native Unreal Editor is not UE 5.8.4: " + engine)

    # This is Editor WORLD inspection, NOT a Play In Editor or player-run test.
    loaded = unreal.EditorLoadingAndSavingUtils.load_map(MAP_PACKAGE)
    if loaded is None:
        raise RuntimeError("HOLD: Unreal cannot load the tracked Prelude V2 map")
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if subsystem is None:
        raise RuntimeError("HOLD: Editor actor inspection subsystem unavailable")
    all_actors = list(subsystem.get_all_level_actors())
    labels = {}
    for actor in all_actors:
        label = actor.get_actor_label()
        if label.startswith(LABEL_PREFIX):
            if label in labels:
                raise RuntimeError("HOLD: duplicate V2 review actor label: " + label)
            labels[label] = actor

    milestones = [a for a in all_actors if isinstance(a, unreal.TSTSSMilestoneActor)]
    if len(milestones) != len(STOP_SPECS):
        raise RuntimeError("HOLD: not exactly seven native C++ milestone actors")

    stop_actors = {}
    positions = {}
    for label, beat, station in STOP_SPECS:
        actor = labels.get(LABEL_PREFIX + label)
        if not isinstance(actor, unreal.TSTSSMilestoneActor):
            raise RuntimeError("HOLD: missing native milestone actor " + label)
        if bool(actor.get_editor_property("is_inspection_station")) != bool(station):
            raise RuntimeError("HOLD: milestone vs engineering inspection type mismatch " + label)
        mesh = actor.get_component_by_class(unreal.StaticMeshComponent)
        if mesh is None or mesh.get_collision_enabled() == unreal.CollisionEnabled.NO_COLLISION:
            raise RuntimeError("HOLD: milestone is not visibility/trace target " + label)
        stop_actors[label] = actor
        v = actor.get_actor_location()
        positions[label] = [round(v.x, 2), round(v.y, 2), round(v.z, 2)]
    player_start = labels.get(LABEL_PREFIX + "PlayerStart_Ender_REVIEW_PROXY")
    floor = labels.get(LABEL_PREFIX + "Harbor_TraversalFloor")
    sea = labels.get(LABEL_PREFIX + "Ocean_VISUAL_ONLY_NO_BUOYANCY")
    if not isinstance(player_start, unreal.PlayerStart) or floor is None or sea is None:
        raise RuntimeError("HOLD: review spawn, floor or explicitly visual-only ocean missing")
    floor_mesh = floor.get_component_by_class(unreal.StaticMeshComponent)
    sea_mesh = sea.get_component_by_class(unreal.StaticMeshComponent)
    if not floor_mesh or floor_mesh.get_collision_enabled() != unreal.CollisionEnabled.QUERY_AND_PHYSICS:
        raise RuntimeError("HOLD: floor not physical traversal collision")
    if not sea_mesh or sea_mesh.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
        raise RuntimeError("HOLD: decorative ocean has unwanted collision")
    if str(sea_mesh.get_collision_profile_name()).lower() != "nocollision":
        raise RuntimeError("HOLD: visual-only ocean not using NoCollision profile")

    mode = unreal.get_default_object(unreal.TSTSSGameMode)
    pawn = mode.get_editor_property("default_pawn_class")
    if pawn is None or "TSTSSExplorerCharacter" not in str(pawn):
        raise RuntimeError("HOLD: Unreal default GameMode does not spawn explorer pawn")
    state = unreal.new_object(unreal.TSTSSFirstWakeState)
    if str(state.get_review_objective_text()) != "Find Ionia's flyer":
        raise RuntimeError("HOLD: initial objective differs from approved review cue")
    if stop_actors["IoniaHiring"].try_activate(state):
        raise RuntimeError("HOLD: out-of-order Ionia activation was accepted")
    if stop_actors["EngineeringApproval"].try_activate(state):
        raise RuntimeError("HOLD: premature signoff was accepted")
    initial_text = str(state.get_review_objective_text())
    if initial_text != "Find Ionia's flyer":
        raise RuntimeError("HOLD: denied actions changed the initial objective")
    for stop, expected_objective in (
        ("FlyerDiscovery", "Speak with Captain Ionia"),
        ("IoniaHiring", "Board the Aureate Wake"),
        ("AureateBoarding", "Inspect the levitation lift"),
    ):
        if not stop_actors[stop].try_activate(state):
            raise RuntimeError("HOLD: valid native milestone refused " + stop)
        if str(state.get_review_objective_text()) != expected_objective:
            raise RuntimeError("HOLD: objective did not advance after " + stop)
    if stop_actors["EngineeringApproval"].try_activate(state):
        raise RuntimeError("HOLD: engineering signoff incorrectly bypasses inspections")
    for stop in ("ReserveStation", "LiftStation", "PressureStation"):
        if not stop_actors[stop].try_activate(state):
            raise RuntimeError("HOLD: real engine station activation failed " + stop)
        if stop_actors[stop].try_activate(state):
            raise RuntimeError("HOLD: duplicate engineering station accepted " + stop)
    if not stop_actors["EngineeringApproval"].try_activate(state):
        raise RuntimeError("HOLD: real actor signoff failed after all three inspections")
    if str(state.get_review_objective_text()) != "Prepare for the First Wake launch":
        raise RuntimeError("HOLD: signoff objective incorrect")
    if int(state.get_inspection_mask()) != 7:
        raise RuntimeError("HOLD: native engineering mask not 0b111")
    if state.is_chapter_one_act_one():
        raise RuntimeError("HOLD: review scene incorrectly claims Splashdown/Chapter1")

    start_v = player_start.get_actor_location()
    flyer_v = stop_actors["FlyerDiscovery"].get_actor_location()
    distance_cm = math.sqrt((start_v.x - flyer_v.x) ** 2 +
                            (start_v.y - flyer_v.y) ** 2 +
                            (start_v.z - flyer_v.z) ** 2)
    return {
        "native_engine_version": engine,
        "map_loaded_in_editor": True,
        "native_milestone_actor_count": 7,
        "all_seven_collision_targets_present": True,
        "physical_review_floor": True,
        "ocean_explicitly_visual_no_collision": True,
        "actual_reflected_game_mode_pawn_present": True,
        "real_actor_ordered_story_acceptance": True,
        "wrong_order_and_duplicate_interactions_rejected": True,
        "objective_text_reflected_and_correct": True,
        "engineering_inspection_mask": 7,
        "spawn_to_flyer_actor_origin_cm": round(distance_cm, 2),
        "stop_locations_world_cm": positions,
        "chapter_one_act_one": False,
        "actual_pie_player_input_tested": False,
        "actual_savegame_disk_roundtrip_tested": False,
        "native_collision_line_trace_tested": False,
        "render_or_water_physics_approved": False,
        "character_or_ship_art_approved": False,
    }


def final_custody(project: Path, initial: dict) -> None:
    if digest(project / MAP_RELATIVE) != initial["before_map_hash"]:
        raise RuntimeError("HOLD: Unreal modified committed V2 map bytes")
    for name, before in initial["config_hashes"].items():
        if digest(project / "Config" / name) != before:
            raise RuntimeError("HOLD: Unreal modified tracked default configuration " + name)
    if git(project.parent, "rev-parse", "HEAD") != initial["head"]:
        raise RuntimeError("HOLD: Git commit changed during native map QA")
    if git(project.parent, "status", "--porcelain"):
        raise RuntimeError("HOLD: source worktree changed during native map QA")


def main() -> None:
    import unreal
    project = Path(unreal.Paths.project_dir()).resolve()
    expected = os.getenv("TSTSS_REVIEW_EXPECTED_HEAD", "")
    before = check_source(project, expected)
    observed = check_native(project, before)
    final_custody(project, before)

    output_dir = project / "Saved" / "NativePreludeMapQA"
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / (
        before["head"][:12] + "-" +
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") +
        "-" + uuid4().hex[:8] + ".json"
    )
    receipt = {
        "status": "NATIVE_EDITOR_MAP_AND_REAL_ACTORS_PASS_NOT_PIE",
        "source_sha": before["head"],
        "map_sha256": before["before_map_hash"],
        "source_bindings": before["source_input_bindings"],
        **observed,
    }
    # Exclusive create, no report overwrite.
    with destination.open("x", encoding="utf-8") as fp:
        json.dump(receipt, fp, indent=2)
        fp.write("\n")
    unreal.log("TSTSS_NATIVE_PRELUDE_MAP_QA_PASS " + json.dumps({
        "sha": receipt["source_sha"], "actor_count": observed["native_milestone_actor_count"],
        "PIE": "NOT_TESTED", "receipt_path": str(destination),
    }))
    print("TSTSS_NATIVE_PRELUDE_MAP_QA_PASS " + str(destination))


if __name__ == "__main__":
    main()
