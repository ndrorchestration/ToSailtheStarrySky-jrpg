#!/usr/bin/env python3
"""First Wake ENGINE optical review: guarded two-Editor-process staging.

This is a bounded disposable camera comparison, NOT playable integration.
Phase 1 Save Map As -> exit UE; phase 2 fresh UE process -> stage four
dormant cine cameras and one disabled review receiver. Never change source
maps, shipped art, real gameplay camera, physics, save games or progression.
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

from stage_first_wake_bokeh_cameras import (
    actor_by_label, camera_setup, digest, distance, git, profile_data, require,
)

WORKTREE = "TSTSS_BokehFocusReview_20261111"
ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "unreal"
SOURCE = "/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors"
DEST_ROOT = "/Game/TSTSS/Review/EngineFocus_V1"
DEST = DEST_ROOT + "/M_EnginePresentationReview"
SOURCE_FILE = PROJECT / "Content/TSTSS/Review/VerticalSlice/VS02_AureateInteriors.umap"
DEST_FILE = PROJECT / "Content/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview.umap"
RECEIPTS = PROJECT / "Saved/EngineFocusReviewV1"
PREPARE_RECEIPT = RECEIPTS / "prepare.json"
COMPOSE_RECEIPT = RECEIPTS / "compose.json"
PREFIX = "TSTSS_BOKEH_ENGINE_REVIEW_"
SOURCE_CAMERA = "TSTSS_VS_REVIEW_CinematicCompositionCamera"
GAUGE = "TSTSS_VS_REVIEW_InstrumentCore_LIFT"
ENGINE = "TSTSS_VS_REVIEW_MainHarmonicLevitationEngine_Proxy"
NATIVE_RECEIVER = "/Script/ToSailTheStarrySky.TSTSSReviewFocusReceiver"
CAMERAS = (
    "EngineeringWide_DeepFocus",
    "EngineInspection_Optical",
    "EngineInspection_NoDoF",
    "EngineResponse_Optical",
)
RECEIVER = "EngineReceiver_DisabledByDefault"
CONFIGS = ("DefaultEngine.ini", "DefaultInput.ini")


def plan() -> dict:
    data = profile_data()
    shots = {row["id"]: row for row in data["shots"]}
    inspection = shots["FW03_Engine_Inspection"]
    reveal = shots["FW04_Engine_Awakening"]
    require(inspection["lens_mm"] == 65 and inspection["f_stop"] == 2.8,
            "inspector lens profile drift")
    require(reveal["lens_mm"] == 50 and reveal["f_stop"] == 4,
            "engine reveal lens profile drift")
    require(SOURCE != DEST and DEST.startswith("/Game/TSTSS/Review/"),
            "review destination not isolated")
    require(DEST_ROOT != "/Game/TSTSS/Review/DynamicFocus_V1",
            "engine review must not collide with harbor staging")
    require(len(CAMERAS) == len(set(CAMERAS)) == 4,
            "review camera names must be distinct")
    require(RECEIVER not in CAMERAS and
            "M_EnginePresentationReview" in DEST, "native review map mismatch")
    require(SOURCE_FILE.is_file(), "committed VS02 native source package missing")
    # This checks the serialized .umap name table, not instantiated actor
    # existence or render quality; native readback must still verify actors.
    package_bytes = SOURCE_FILE.read_bytes()
    for actor_name in (SOURCE_CAMERA, GAUGE, ENGINE):
        require(actor_name.encode("ascii") in package_bytes,
                "required engine source actor name absent from native package: " + actor_name)
    return {
        "schema": "tstss.firstwake.engine_focus.staging.review.v1",
        "engine": "Unreal Engine 5.8.4",
        "status": "SOURCE_PLAN_ONLY_NO_NATIVE_MAP_OR_PIE",
        "source_map": SOURCE,
        "target_review_map": DEST,
        "source_worktree_expected": WORKTREE,
        "expected_source_actor_labels": [SOURCE_CAMERA, GAUGE, ENGINE],
        "new_actor_labels": [PREFIX + x for x in (*CAMERAS, RECEIVER)],
        "new_camera_count": len(CAMERAS),
        "new_receivers": 1,
        "receivers_enabled": False,
        "requires_compiled_cine_receiver": NATIVE_RECEIVER,
        "two_independent_editor_processes": True,
        "copy_method": "EditorLoadingAndSavingUtils.save_map(source_world, DEST)",
        "auto_switches_player_camera": False,
        "changes_gameplay": False,
        "changes_save_data": False,
        "changes_story_progression": False,
        "changes_physics": False,
        "includes_approved_character_or_ship_art": False,
        "camera_comparison": "same position, angle, focal length, aperture; Manual versus Disable DOF",
        "requires_single_owned_world_atmosphere_for_live_pie_focus": True,
        "native_render": "NOT_RUN",
        "native_pie": "NOT_RUN",
    }


def custody(phase: str) -> dict:
    require(phase in ("prepare", "compose"), "invalid staging phase")
    require(sys.platform == "win32" and ROOT.name == WORKTREE
            and (PROJECT / "ToSailTheStarrySky.uproject").is_file(),
            "only the dedicated Windows review worktree may stage")
    head = os.environ.get("TSTSS_ENGINE_FOCUS_EXPECTED_HEAD", "").strip().lower()
    require(bool(re.fullmatch(r"[a-f0-9]{40}", head))
            and git("rev-parse", "HEAD").lower() == head,
            "exact Git commit required")
    require(os.environ.get("TSTSS_ENGINE_FOCUS_STAGE_EXPLICIT") == "1",
            "explicit host opt-in not present")
    require(SOURCE_FILE.is_file(), "committed native source map missing")
    existing = git("status", "--porcelain", "-uall").splitlines()
    if phase == "prepare":
        require(not existing, "source checkout must be pristine")
        require(not DEST_FILE.parent.exists()
                and not PREPARE_RECEIPT.exists()
                and not COMPOSE_RECEIPT.exists(),
                "destination or receipt occupied")
    else:
        require(PREPARE_RECEIPT.is_file() and DEST_FILE.is_file(),
                "prepared map and receipt required in a fresh editor process")
        require(not COMPOSE_RECEIPT.exists(), "composition already completed")
        require(all(line.startswith(
            "?? unreal/Content/TSTSS/Review/EngineFocus_V1/")
                    for line in existing),
                "tracked or unrelated local changes in review worktree")
    saved = PROJECT / "Saved/SaveGames"
    require(not saved.exists() or not list(saved.glob("*.sav")),
            "do not stage on a worktree containing real SaveGames")
    return {
        "exact_head": head,
        "source_sha256": digest(SOURCE_FILE),
        "protected_config_sha256": {
            name: digest(PROJECT / "Config" / name) for name in CONFIGS
        },
    }


def protect_source(custody_data: dict) -> None:
    require(digest(SOURCE_FILE) == custody_data["source_sha256"],
            "immutable source map hash changed")
    for name, original in custody_data["protected_config_sha256"].items():
        require(digest(PROJECT / "Config" / name) == original,
                "protected config changed: " + name)


def editor_preflight(u) -> None:
    require(u.SystemLibrary.get_engine_version().startswith("5.8.4"),
            "native 5.8.4 engine required")
    require(not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
            and not u.EditorLoadingAndSavingUtils.get_dirty_content_packages(),
            "unsaved editor map/content cannot be discarded")
    require(u.EditorAssetLibrary.does_asset_exist(SOURCE),
            "native source scene cannot be loaded")


def guarded_camera(u, editor, label: str, location, rotation,
                   lens_mm: float, aperture: float,
                   focus_cm: float, disable_dof: bool):
    # Reuse the established optical authoring logic; relabel into a
    # different, explicitly owned engine-scene namespace before any save.
    camera = camera_setup(u, editor, label, location, rotation,
                          lens_mm, aperture, focus_cm, disable_dof)
    camera.set_actor_label(PREFIX + label)
    require(camera.get_actor_label() == PREFIX + label,
            "review CineCamera label did not persist")
    return camera


def stage(phase: str) -> dict:
    c = custody(phase)
    p = plan()
    import unreal as u
    editor_preflight(u)
    editor = u.get_editor_subsystem(u.EditorActorSubsystem)
    require(editor is not None, "EditorActorSubsystem unavailable")

    if phase == "prepare":
        require(not u.EditorAssetLibrary.does_directory_exist(DEST_ROOT),
                "engine-focus destination already exists in asset registry")
        source_world = u.EditorLoadingAndSavingUtils.load_map(SOURCE)
        require(source_world is not None, "unable to open existing engine review map")
        actors = editor.get_all_level_actors()
        for label in (SOURCE_CAMERA, GAUGE, ENGINE):
            actor_by_label(editor, label)
        require(not any(a.get_actor_label().startswith(PREFIX) for a in actors),
                "engine source already contains review camera artifacts")
        require(u.EditorAssetLibrary.make_directory(DEST_ROOT),
                "cannot create isolated engine review package path")
        # Save Map As, NEVER UWorld duplicate_asset: known UE issue.
        require(u.EditorLoadingAndSavingUtils.save_map(source_world, DEST),
                "engine source Save Map As failed")
        require(DEST_FILE.is_file(), "native review copy missing from disk")
        protect_source(c)
        receipt = {
            **p, **c,
            "status": "ENGINE_REVIEW_MAP_SAVED_REQUIRES_FRESH_EDITOR",
            "source_actor_count": len(actors),
            "base_review_map_sha256": digest(DEST_FILE),
        }
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        with PREPARE_RECEIPT.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2)
            stream.write("\n")
        u.log("TSTSS_ENGINE_FOCUS_PREPARED_NOT_PIE " +
              receipt["base_review_map_sha256"])
        return receipt

    prepared = json.loads(PREPARE_RECEIPT.read_text(encoding="utf-8"))
    require(prepared.get("status") ==
            "ENGINE_REVIEW_MAP_SAVED_REQUIRES_FRESH_EDITOR",
            "prepared receipt status does not admit composition")
    require(prepared.get("exact_head") == c["exact_head"]
            and prepared.get("source_sha256") == c["source_sha256"]
            and prepared.get("base_review_map_sha256") == digest(DEST_FILE),
            "source head or unmodified map receipt mismatch")
    receiver_cls = u.load_class(None, NATIVE_RECEIVER)
    require(receiver_cls is not None,
            "guarded C++ optical receiver missing; build native UHT/C++ first")
    world = u.EditorLoadingAndSavingUtils.load_map(DEST)
    require(world is not None, "cannot open isolated review copy")
    before = editor.get_all_level_actors()
    require(len(before) == prepared["source_actor_count"],
            "native map copy actor inventory drift")
    require(not any(a.get_actor_label().startswith(PREFIX) for a in before),
            "engine review camera already staged")
    source_cam = actor_by_label(editor, SOURCE_CAMERA)
    gauge = actor_by_label(editor, GAUGE)
    engine = actor_by_label(editor, ENGINE)
    shots = {s["id"]: s for s in profile_data()["shots"]}
    inspect = shots["FW03_Engine_Inspection"]
    reveal = shots["FW04_Engine_Awakening"]
    base_pos = source_cam.get_actor_location()
    base_rot = source_cam.get_actor_rotation()
    guarded_camera(u, editor, CAMERAS[0], base_pos, base_rot,
                   28.0, 5.6, 2500.0, False)

    gauge_pos = gauge.get_actor_location()
    inspect_pos = gauge_pos + u.Vector(-350., -610., 135.)
    inspect_rot = u.MathLibrary.find_look_at_rotation(inspect_pos, gauge_pos)
    focus_cm = distance(inspect_pos, gauge_pos)
    require(65.0 <= focus_cm <= 12000.0,
            "authored gauge camera has an invalid manual focus range")
    focus_cam = guarded_camera(
        u, editor, CAMERAS[1], inspect_pos, inspect_rot,
        float(inspect["lens_mm"]), float(inspect["f_stop"]), focus_cm, False)
    guarded_camera(
        u, editor, CAMERAS[2], inspect_pos, inspect_rot,
        float(inspect["lens_mm"]), float(inspect["f_stop"]), focus_cm, True)

    engine_pos = engine.get_actor_location()
    reveal_pos = engine_pos + u.Vector(-450., -850., 210.)
    reveal_rot = u.MathLibrary.find_look_at_rotation(reveal_pos, engine_pos)
    reveal_cm = distance(reveal_pos, engine_pos)
    require(65.0 <= reveal_cm <= 12000.0, "engine reveal focus range invalid")
    guarded_camera(
        u, editor, CAMERAS[3], reveal_pos, reveal_rot,
        float(reveal["lens_mm"]), float(reveal["f_stop"]), reveal_cm, False)

    receiver = editor.spawn_actor_from_class(
        receiver_cls, inspect_pos, u.Rotator(0., 0., 0.))
    require(receiver is not None, "cannot spawn compiled native focus receiver")
    receiver.set_actor_label(PREFIX + RECEIVER)
    receiver.set_editor_property("staged_review_camera", focus_cam)
    receiver.set_editor_property("authored_engine_focus_anchor", gauge)
    # Do NOT set bExplicitReviewOptIn true. Explicit scene operator signoff
    # and a genuinely owned atmosphere director are still outstanding.
    require(receiver.get_editor_property("explicit_review_opt_in") is False,
            "focus receiver unexpectedly auto-enabled")
    require(receiver.get_editor_property("staged_review_camera") == focus_cam
            and receiver.get_editor_property("authored_engine_focus_anchor") == gauge,
            "focus receiver bindings failed readback")

    after = editor.get_all_level_actors()
    new = [a.get_actor_label() for a in after
           if a.get_actor_label().startswith(PREFIX)]
    require(len(after) == len(before) + len(CAMERAS) + 1,
            "unexpected actor count after engine camera authoring")
    require(set(new) == set(p["new_actor_labels"]) and len(new) == len(set(new)),
            "review actor inventory differs from planned camera + receiver set")
    require(u.EditorLoadingAndSavingUtils.save_map(world, DEST),
            "composed native engine review map failed to save")
    require(DEST_FILE.is_file(), "composed review map missing")
    protect_source(c)
    receipt = {
        **p, **c, "status": "ENGINE_CINE_REVIEW_MAP_SAVED_NOT_PIE_OR_VISUAL_APPROVED",
        "base_review_map_sha256": prepared["base_review_map_sha256"],
        "composed_map_sha256": digest(DEST_FILE),
        "composed_bytes": DEST_FILE.stat().st_size,
        "new_actor_count": len(new),
        "focus_cm_inspection": focus_cm,
        "focus_cm_engine_reveal": reveal_cm,
        "receiver_remains_disabled": True,
        "actor_labels": sorted(new),
    }
    with COMPOSE_RECEIPT.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    u.log("TSTSS_ENGINE_CINE_REVIEW_COMPOSED_NOT_PIE " +
          receipt["composed_map_sha256"])
    return receipt


def self_test() -> dict:
    p = plan()
    require(p["new_camera_count"] == 4 and p["new_receivers"] == 1,
            "expected optical A/B rig and receiver")
    require(p["receivers_enabled"] is False
            and p["auto_switches_player_camera"] is False,
            "no opt-in or gameplay ownership deviation")
    require(p["target_review_map"] != p["source_map"],
            "source map cannot be a destination")
    require(p["copy_method"] == "EditorLoadingAndSavingUtils.save_map(source_world, DEST)"
            and p["two_independent_editor_processes"],
            "required two-process safe Save Map As route missing")
    require(all(not p[k] for k in ("changes_gameplay", "changes_save_data",
                                  "changes_story_progression",
                                  "changes_physics")),
            "presentation authoring may not mutate game state")
    return {
        "status": "ENGINE_FOCUS_OFFLINE_PREFLIGHT_PASS",
        "positive_checks": 5,
        "native_map_created": False,
        "native_compilation": "NOT_RUN",
        "visual_acceptance": "NOT_ESTABLISHED",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--plan", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if os.environ.get("TSTSS_ENGINE_FOCUS_STAGE_EXPLICIT") == "1":
        output = stage(os.environ.get("TSTSS_ENGINE_FOCUS_PHASE", ""))
    elif args.self_test:
        output = self_test()
    elif args.plan:
        output = plan()
    else:
        raise SystemExit("HOLD: review native stage requires explicit opt-in")
    print(json.dumps(output, indent=2))
