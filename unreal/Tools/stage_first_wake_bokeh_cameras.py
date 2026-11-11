#!/usr/bin/env python3
"""First Wake bokeh: guarded UE Editor-only, TWO-PROCESS camera review staging.

Never launches Unreal by itself; never modifies the source maps, settings, saves,
progression, collision or player camera. Offline --plan/--self-test are safe.
Native phase 1 uses Save Map As on VS01; phase 2 MUST run in a fresh UE process.
Do not use EditorAssetLibrary.duplicate_asset on UWorld assets.
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
import sys

WORKTREE = "TSTSS_BokehFocusReview_20261111"
ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "unreal"
SOURCE = "/Game/TSTSS/Review/VerticalSlice/VS01_DenithHarbor"
DEST_ROOT = "/Game/TSTSS/Review/DynamicFocus_V1"
DEST = DEST_ROOT + "/M_DenithHarborBokehStudy"
SOURCE_FILE = PROJECT / "Content/TSTSS/Review/VerticalSlice/VS01_DenithHarbor.umap"
DEST_FILE = PROJECT / "Content/TSTSS/Review/DynamicFocus_V1/M_DenithHarborBokehStudy.umap"
RECEIPTS = PROJECT / "Saved/BokehReviewV1"
PREPARE_RECEIPT = RECEIPTS / "prepare.json"
COMPOSE_RECEIPT = RECEIPTS / "compose.json"
PROFILE_FILE = PROJECT / "DataSource/Cinematics/FirstWakeFocusProfiles.review.json"
PREFIX = "TSTSS_BOKEH_REVIEW_"
SOURCE_CAMERA = "TSTSS_VS_REVIEW_CinematicCompositionCamera"
NEAR_LAMP = "TSTSS_VS_REVIEW_LampGlowHousing_02"
PRACTICAL_LAMPS = (
    "TSTSS_VS_REVIEW_LampGlowHousing_01",
    "TSTSS_VS_REVIEW_LampGlowHousing_03",
    "TSTSS_VS_REVIEW_LampGlowHousing_05",
)
CONFIG_NAMES = ("DefaultEngine.ini", "DefaultInput.ini")
CAMERAS = ("DockWide_DeepFocus", "DockPractical_OpticalFocus",
           "DockPractical_NoDoF_Control")
PRACTICALS = ("PracticalGlow_01", "PracticalGlow_03", "PracticalGlow_05")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError("HOLD: " + reason)


def profile_data() -> dict:
    from validate_first_wake_focus_profiles import validate
    data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    validate(data)
    return data


def plan() -> dict:
    profiles = profile_data()
    shots = {s["id"]: s for s in profiles["shots"]}
    require(set(("FW01_Dock_Establish", "FW02_Ionia_Conversation")).issubset(shots),
            "missing optical preview profile")
    require(len(CAMERAS) == 3 and len(set(CAMERAS)) == 3,
            "review camera inventory")
    require(SOURCE != DEST and DEST.startswith("/Game/TSTSS/Review/"),
            "review destination is not isolated")
    require(SOURCE_FILE != DEST_FILE and DEST_FILE.suffix == ".umap",
            "file path overlap")
    return {
        "schema": "tstss.firstwake.bokeh.native_staging.v1",
        "status": "SOURCE_PLAN_ONLY_NOT_NATIVE_PROOF",
        "engine": "Unreal Engine 5.8.4",
        "source_map": SOURCE,
        "target_review_map": DEST,
        "source_worktree_expected": WORKTREE,
        "review_camera_labels": [PREFIX + n for n in CAMERAS],
        "review_practical_labels": [PREFIX + n for n in PRACTICALS],
        "focus_on_real_world_prop": NEAR_LAMP,
        "copy_method": "UEditorLoadingAndSavingUtils.SaveMapAs_not_UWorld_duplicate_asset",
        "required_phases": ["prepare", "compose"],
        "same_editor_process_for_both_phases": False,
        "includes_real_ionia_character": False,
        "includes_approved_ship_art": False,
        "auto_activates_player_camera": False,
        "changes_gameplay": False,
        "changes_save_data": False,
        "changes_story_progression": False,
        "changes_physics": False,
        "source_profile_ids": ["FW01_Dock_Establish", "FW02_Ionia_Conversation"],
        "native_pie_status": "NOT_TESTED",
        "native_screenshots": "NOT_CAPTURED",
        "qa": "Side-by-side preview via Editor pilot of named camera actors required"
    }


def git(*args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True,
        text=True, timeout=30, check=False)
    require(proc.returncode == 0, "git custody command failed")
    return proc.stdout.strip()


def custody(phase: str) -> dict:
    require(phase in ("prepare", "compose"), "invalid phase")
    require(sys.platform == "win32" and ROOT.name == WORKTREE and PROJECT.is_dir(),
            "not the dedicated Windows review worktree")
    expected = os.environ.get("TSTSS_BOKEH_EXPECTED_HEAD", "").strip().lower()
    require(bool(re.fullmatch(r"[a-f0-9]{40}", expected)),
            "exact-head env TSTSS_BOKEH_EXPECTED_HEAD required")
    require(git("rev-parse", "HEAD").lower() == expected, "exact-head mismatch")
    require(os.environ.get("TSTSS_BOKEH_STAGE_EXPLICIT") == "1",
            "host has not explicitly opted in")
    lines = git("status", "--porcelain", "-uall").splitlines()
    if phase == "prepare":
        require(not lines, "preparation requires clean source worktree")
        require(not PREPARE_RECEIPT.exists() and not COMPOSE_RECEIPT.exists(),
                "review receipt already occupied")
        require(not DEST_FILE.exists() and not DEST_FILE.parent.exists(),
                "review destination occupied")
    else:
        require(PREPARE_RECEIPT.is_file() and not COMPOSE_RECEIPT.exists(),
                "missing preparation receipt or compose already done")
        require(DEST_FILE.is_file(), "prepared review map absent")
        allowed_prefix = "?? unreal/Content/TSTSS/Review/DynamicFocus_V1/"
        require(all(line.startswith(allowed_prefix) for line in lines),
                "tracked or unrelated untracked changes in review worktree")
    require(SOURCE_FILE.is_file(), "native source map absent")
    save_dir = PROJECT / "Saved/SaveGames"
    require(not save_dir.exists() or not list(save_dir.glob("*.sav")),
            "review worktree contains user save games")
    return {
        "source_sha256": digest(SOURCE_FILE),
        "protected_config_sha256": {
            n: digest(PROJECT / "Config" / n) for n in CONFIG_NAMES
        },
        "exact_head": expected,
    }


def check_unchanged(c: dict) -> None:
    require(digest(SOURCE_FILE) == c["source_sha256"], "source map was mutated")
    for name, sha in c["protected_config_sha256"].items():
        require(digest(PROJECT / "Config" / name) == sha,
                "protected Unreal config changed: " + name)


def native_preflight(unreal) -> None:
    require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4"),
            "expected installed UE 5.8.4")
    require(not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(),
            "unsaved map edits in Editor")
    require(not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(),
            "unsaved content in Editor")
    require(unreal.EditorAssetLibrary.does_asset_exist(SOURCE),
            "native VS01 source map not loadable")


def actor_by_label(editor, label: str):
    matches = [a for a in editor.get_all_level_actors()
               if a.get_actor_label() == label]
    require(len(matches) == 1, "expected exactly one source actor " + label)
    return matches[0]


def camera_setup(unreal, editor, label: str, location, rotation,
                 focal_mm: float, f_stop: float, focus_cm: float,
                 disable_dof: bool):
    actor = editor.spawn_actor_from_class(
        unreal.CineCameraActor, location, rotation)
    require(actor is not None, "cine camera spawn failed " + label)
    actor.set_actor_label(PREFIX + label)
    actor.set_actor_enable_collision(False)
    cam = actor.get_cine_camera_component()
    require(cam is not None, "cine camera component missing")
    filmback = cam.get_editor_property("filmback")
    filmback.set_editor_property("sensor_width", 36.0)
    filmback.set_editor_property("sensor_height", 24.0)
    cam.set_editor_property("filmback", filmback)
    cam.set_editor_property("current_focal_length", focal_mm)
    cam.set_editor_property("current_aperture", f_stop)
    focus = cam.get_editor_property("focus_settings")
    focus.set_editor_property(
        "focus_method",
        unreal.CameraFocusMethod.DISABLE if disable_dof
        else unreal.CameraFocusMethod.MANUAL)
    focus.set_editor_property("manual_focus_distance", float(focus_cm))
    focus.set_editor_property("smooth_focus_changes", False)
    focus.set_editor_property("draw_debug_focus_plane", False)
    cam.set_editor_property("focus_settings", focus)
    require(abs(float(cam.get_editor_property("current_focal_length")) - focal_mm) < 0.01,
            "lens focal length was clamped " + label)
    require(abs(float(cam.get_editor_property("current_aperture")) - f_stop) < 0.01,
            "lens f-stop was clamped " + label)
    verified_focus = cam.get_editor_property("focus_settings")
    require(verified_focus.get_editor_property("focus_method") ==
            (unreal.CameraFocusMethod.DISABLE if disable_dof
             else unreal.CameraFocusMethod.MANUAL),
            "focus method did not persist " + label)
    return actor


def distance(a, b) -> float:
    return math.sqrt((float(a.x) - float(b.x)) ** 2
                     + (float(a.y) - float(b.y)) ** 2
                     + (float(a.z) - float(b.z)) ** 2)


def native_stage(phase: str) -> dict:
    info = custody(phase)
    blueprint = plan()
    import unreal as u
    native_preflight(u)
    editor = u.get_editor_subsystem(u.EditorActorSubsystem)
    require(editor is not None, "EditorActorSubsystem unavailable")
    if phase == "prepare":
        require(not u.EditorAssetLibrary.does_directory_exist(DEST_ROOT),
                "target namespace already present in native content registry")
        source_world = u.EditorLoadingAndSavingUtils.load_map(SOURCE)
        require(source_world is not None, "cannot load source level")
        source_actors = editor.get_all_level_actors()
        for label in (SOURCE_CAMERA, NEAR_LAMP, *PRACTICAL_LAMPS):
            actor_by_label(editor, label)
        require(not any(a.get_actor_label().startswith(PREFIX) for a in source_actors),
                "camera review actors already present in source")
        require(u.EditorAssetLibrary.make_directory(DEST_ROOT),
                "failed to create isolated review directory")
        # NEVER call EditorAssetLibrary.duplicate_asset on .umap worlds.
        # UE map re-homing uses Save Map As, followed by a fresh process.
        require(u.EditorLoadingAndSavingUtils.save_map(source_world, DEST),
                "Save Map As failed")
        require(DEST_FILE.is_file(), "target review .umap missing")
        check_unchanged(info)
        receipt = {
            **blueprint, **info,
            "status": "BASE_MAP_SAVED_REQUIRES_FRESH_EDITOR_PROCESS",
            "base_review_map_sha256": digest(DEST_FILE),
            "source_actor_count": len(source_actors)
        }
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        with PREPARE_RECEIPT.open("x", encoding="utf-8") as handle:
            json.dump(receipt, handle, indent=2)
            handle.write("\n")
        u.log("TSTSS_BOKEH_PREPARED_NOT_PIE " + receipt["base_review_map_sha256"])
        return receipt

    prepared = json.loads(PREPARE_RECEIPT.read_text(encoding="utf-8"))
    require(prepared.get("status") == "BASE_MAP_SAVED_REQUIRES_FRESH_EDITOR_PROCESS",
            "invalid or stale preparation stage")
    require(prepared.get("exact_head") == info["exact_head"]
            and prepared.get("source_sha256") == info["source_sha256"]
            and prepared.get("base_review_map_sha256") == digest(DEST_FILE),
            "preparation source receipts do not match")
    world = u.EditorLoadingAndSavingUtils.load_map(DEST)
    require(world is not None, "unable to load prepared review map")
    before = editor.get_all_level_actors()
    require(len(before) == prepared["source_actor_count"],
            "prepared source actor inventory changed")
    require(not any(a.get_actor_label().startswith(PREFIX) for a in before),
            "camera study already staged")
    source_cam = actor_by_label(editor, SOURCE_CAMERA)
    near = actor_by_label(editor, NEAR_LAMP)
    lamp_sources = [actor_by_label(editor, s) for s in PRACTICAL_LAMPS]
    profiles = {s["id"]: s for s in profile_data()["shots"]}
    wide = profiles["FW01_Dock_Establish"]
    shallow = profiles["FW02_Ionia_Conversation"]
    camera_setup(u, editor, CAMERAS[0],
                 source_cam.get_actor_location(),
                 source_cam.get_actor_rotation(),
                 float(wide["lens_mm"]), float(wide["f_stop"]),
                 float(wide["focus_cm"]), False)
    target_pos = near.get_actor_location()
    cam_pos = target_pos + u.Vector(-250.0, -600.0, 110.0)
    cam_rot = u.MathLibrary.find_look_at_rotation(cam_pos, target_pos)
    subject_distance = distance(cam_pos, target_pos)
    camera_setup(u, editor, CAMERAS[1], cam_pos, cam_rot,
                 float(shallow["lens_mm"]), float(shallow["f_stop"]),
                 subject_distance, False)
    camera_setup(u, editor, CAMERAS[2], cam_pos, cam_rot,
                 float(shallow["lens_mm"]), float(shallow["f_stop"]),
                 subject_distance, True)

    # The source harbor spheres are non-emissive provisional geometry.
    # These THREE review-only point lights permit a visible optical A/B study.
    for name, lamp in zip(PRACTICALS, lamp_sources):
        glow = editor.spawn_actor_from_class(
            u.PointLight, lamp.get_actor_location(), u.Rotator(0, 0, 0))
        require(glow is not None, "failed to stage practical light " + name)
        glow.set_actor_label(PREFIX + name)
        glow.set_actor_enable_collision(False)
        light = glow.get_component_by_class(u.PointLightComponent)
        require(light is not None, "point light component missing")
        light.set_editor_property("cast_shadows", False)
        light.set_editor_property("intensity", 850.0)

    after = editor.get_all_level_actors()
    labels = [a.get_actor_label() for a in after]
    new_labels = [s for s in labels if s.startswith(PREFIX)]
    require(len(after) == len(before) + len(CAMERAS) + len(PRACTICALS),
            "unexpected actor count after camera staging")
    require(len(set(new_labels)) == len(new_labels)
            and set(new_labels) == set(blueprint["review_camera_labels"]
                                    + blueprint["review_practical_labels"]),
            "unexpected review actor inventory")
    require(u.EditorLoadingAndSavingUtils.save_map(world, DEST),
            "saving composed review map failed")
    require(DEST_FILE.is_file(), "composed map missing")
    check_unchanged(info)
    receipt = {
        **blueprint, **info,
        "status": "NATIVE_CAMERA_REVIEW_MAP_SAVED_NOT_PIE_OR_SCREENSHOT_APPROVED",
        "base_review_map_sha256": prepared["base_review_map_sha256"],
        "composed_map_sha256": digest(DEST_FILE),
        "composed_map_bytes": DEST_FILE.stat().st_size,
        "camera_count": len(CAMERAS),
        "point_light_count": len(PRACTICALS),
        "new_camera_focus_distance_cm": subject_distance,
        "actor_count": len(after),
        "review_actor_labels": sorted(new_labels),
    }
    with COMPOSE_RECEIPT.open("x", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")
    u.log("TSTSS_BOKEH_CAMERA_REVIEW_SAVED_NOT_PIE " + receipt["composed_map_sha256"])
    return receipt


def offline_self_test() -> dict:
    p = plan()
    require(p["source_map"] != p["target_review_map"], "source/target collision")
    require(p["changes_story_progression"] is False, "story mutation")
    require(p["changes_physics"] is False, "physics mutation")
    require(p["includes_real_ionia_character"] is False,
            "proxy should not claim final character")
    require(p["same_editor_process_for_both_phases"] is False,
            "fresh Editor process required")
    require(len(p["review_camera_labels"]) == 3, "missing A/B camera rig")
    require(len(p["review_practical_labels"]) == 3, "missing practical lights")
    return {
        "status": "OFFLINE_PREFLIGHT_PASS",
        "tests": 7,
        "runtime_admission": "NOT_ESTABLISHED",
        "native_map_staged": False
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--plan", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if os.environ.get("TSTSS_BOKEH_STAGE_EXPLICIT") == "1":
        result = native_stage(os.environ.get("TSTSS_BOKEH_PHASE", ""))
    elif args.self_test:
        result = offline_self_test()
    elif args.plan:
        result = plan()
    else:
        raise SystemExit("HOLD: use --plan or --self-test; native needs explicit gated host")
    print(json.dumps(result, indent=2))
