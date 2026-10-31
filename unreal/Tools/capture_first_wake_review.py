#!/usr/bin/env python3
"""First Wake four-camera native UE5.8 review capture and offline PNG receipts.

--inspect: engine-free capture plan (no images generated).
--capture-in-editor: schedules real Editor screenshot tasks; does not claim completion.
--verify-files: independently validate actual native PNG files after capture.
No scene creation/save, actor spawning, story/water mutation, or Orbiter unlock.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import zlib

from build_first_wake_benchmark import CAMERAS, MAP_PATH, SHIP_POSITION
from bind_first_wake_review_ship_art import SHIP_LABEL, WING_DIR, SUPPORT_DIR, read_property

WIDTH = 1920
HEIGHT = 1080
REVIEW_PREFIX = "TSTSS_UE58_REVIEW"
SHOT_LABELS = (
    ("Prelude", "Harbor and first hiring context"),
    ("Prelude", "Aureate Wake four-wing silhouette"),
    ("Prelude", "Gangway and safe boarding composition"),
    ("Chapter 1 Act 1", "Splashdown composition only; no water physics proof"),
)
AUTHORITY = "REVIEW_CAPTURE_ONLY_NOT_GAMEPLAY_OR_VISUAL_ACCEPTANCE"


class ScreenshotHold(RuntimeError):
    pass


def validate_run_id(run_id: str) -> str:
    if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{5,31}", run_id):
        raise ScreenshotHold("run-id must be 6-32 safe ASCII characters")
    return run_id


def capture_plan(run_id: str) -> dict:
    run_id = validate_run_id(run_id)
    if len(CAMERAS) != 4 or len(SHOT_LABELS) != 4:
        raise ScreenshotHold("Expected four existing, distinct First Wake cameras")
    shots = [
        {"actor_label": "TSTSS_REVIEW_Camera_" + c.name,
         "filename": f"{REVIEW_PREFIX}_{run_id}_{c.name}.png",
         "sequence": i + 1, "story_stage": stage, "intent": intent,
         "camera_location_cm": list(c.location), "camera_target_cm": list(c.target)}
        for i, (c, (stage, intent)) in enumerate(zip(CAMERAS, SHOT_LABELS))
    ]
    if len({s["actor_label"] for s in shots}) != 4 or len({s["filename"] for s in shots}) != 4:
        raise ScreenshotHold("Duplicate shot labels or output filenames")
    return {"map": MAP_PATH, "ship_label": SHIP_LABEL, "ship_position_cm": list(SHIP_POSITION),
            "resolution": [WIDTH, HEIGHT], "shots": shots, "authority": AUTHORITY,
            "native_render_verified": False, "approved_art": False}


def preflight_in_editor(plan: dict) -> list:
    try:
        import unreal
    except ImportError as exc:
        raise ScreenshotHold("Native screenshots require Unreal Editor Python") from exc
    required = ("UnrealEditorSubsystem", "EditorActorSubsystem", "CineCameraActor",
                "AureateWakePreviewActor", "AutomationLibrary", "AutomationScheduler",
                "get_editor_subsystem")
    if any(not hasattr(unreal, name) for name in required):
        raise ScreenshotHold("Unreal Editor capture API / compiled TSTSS module missing")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world is None or world.get_path_name().split(".", 1)[0] != MAP_PATH:
        raise ScreenshotHold("Capture allowed only in the exact isolated First Wake review map")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    selected = []
    for shot in plan["shots"]:
        matches = [a for a in actors if a.get_actor_label(False) == shot["actor_label"]]
        if len(matches) != 1 or not isinstance(matches[0], unreal.CineCameraActor):
            raise ScreenshotHold("Missing/duplicate authentic CineCameraActor " + shot["actor_label"])
        selected.append((shot, matches[0]))
    ships = [a for a in actors if a.get_actor_label(False) == SHIP_LABEL]
    if len(ships) != 1 or not isinstance(ships[0], unreal.AureateWakePreviewActor):
        raise ScreenshotHold("Expected exactly one compiled Aureate Wake review actor")
    ship = ships[0]
    try:
        if (ship.get_wing_count(), ship.get_root_support_count(), ship.get_hydrofoil_count()) != (4, 4, 2):
            raise ScreenshotHold("Ship component inventory changed; stop capture")
        if ship.is_transitioning() or not str(ship.get_current_form()).lower().endswith("skyborne"):
            raise ScreenshotHold("Ship must be stationary in its preflight Skyborne form")
        _, orbiter = read_property(ship, ("allow_orbiter_preview", "b_allow_orbiter_preview"))
        _, wing = read_property(ship, ("authored_wing_mesh",))
        _, root = read_property(ship, ("authored_root_support_mesh",))
        _, pose = read_property(ship, ("use_root_pivoted_wing_pose", "b_use_root_pivoted_wing_pose"))
    except (AttributeError, ValueError, TypeError) as exc:
        raise ScreenshotHold("Unable to inspect native preview actor: " + str(exc)) from exc
    if orbiter:
        raise ScreenshotHold("Hidden Orbiter gate must remain disabled")
    if wing is None or root is None or not pose:
        raise ScreenshotHold("Corrected wing + root support must be bound before cinematic art review")
    # A designer may have reassigned the mesh properties since the safe binder
    # ran. Never capture gameplay/canon assets under review-only provenance.
    for mesh, expected_root in ((wing, WING_DIR), (root, SUPPORT_DIR)):
        try:
            object_path = str(mesh.get_path_name())
        except (AttributeError, ValueError, TypeError) as exc:
            raise ScreenshotHold("Unreal could not resolve review mesh provenance") from exc
        if not object_path.startswith(expected_root) or "." not in object_path[len(expected_root):]:
            raise ScreenshotHold("Ship uses a non-review mesh; capture forbidden")
    return selected


def schedule_editor_capture(plan: dict) -> dict:
    selected = preflight_in_editor(plan)
    import unreal
    # UE5.8: automation screenshots require future editor ticks to finish.
    # Register a latent command instead of claiming screenshot output on request.
    @unreal.AutomationScheduler.add_latent_command
    def _capture_each_shot():
        for shot, camera in selected:
            task = unreal.AutomationLibrary.take_high_res_screenshot(
                WIDTH, HEIGHT, shot["filename"], camera=camera,
                delay=0.35, force_game_view=True, capture_hdr=False)
            if task is None or not task.is_valid_task():
                raise ScreenshotHold("Native screenshot task rejected for " + shot["actor_label"])
            count = 0
            while not task.is_task_done():
                count += 1
                if count > 3600:
                    raise ScreenshotHold("Native screenshot task exceeded tick budget: " + shot["filename"])
                yield
            unreal.log("TSTSS screenshot task finished; verify physical PNG: " + shot["filename"])
            yield
    return {"status": "CAPTURE_TASKS_SCHEDULED_NOT_VERIFIED",
            "shots_requested": len(selected), "run_id": plan["shots"][0]["filename"].split("_")[3],
            "requires_actual_png_file_inspection": True, "authority": AUTHORITY}


def verify_png(path: Path, width: int = WIDTH, height: int = HEIGHT) -> dict:
    data = path.read_bytes()
    if len(data) < 100 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ScreenshotHold("Missing/truncated PNG header: " + path.name)
    offset = 8
    observed = None
    ended = False
    seen_idat = False
    while offset < len(data):
        if len(data) - offset < 12:
            raise ScreenshotHold("Truncated PNG chunk: " + path.name)
        length = struct.unpack_from(">I", data, offset)[0]
        offset += 4
        kind = data[offset:offset + 4]
        offset += 4
        if len(data) - offset < length + 4:
            raise ScreenshotHold("Truncated PNG chunk payload: " + path.name)
        payload = data[offset:offset + length]
        offset += length
        checksum = struct.unpack_from(">I", data, offset)[0]
        offset += 4
        if zlib.crc32(kind + payload) != checksum:
            raise ScreenshotHold("Invalid PNG chunk CRC: " + path.name)
        if observed is None:
            if kind != b"IHDR" or length != 13:
                raise ScreenshotHold("Missing PNG IHDR: " + path.name)
            observed = struct.unpack_from(">II", payload, 0)
            if observed != (width, height):
                raise ScreenshotHold("Unexpected PNG resolution: " + path.name)
        if kind == b"IDAT":
            seen_idat = True
        if kind == b"IEND":
            if not seen_idat:
                raise ScreenshotHold("PNG contains no pixel data: " + path.name)
            if length != 0 or offset != len(data):
                raise ScreenshotHold("Invalid PNG ending/trailing data: " + path.name)
            ended = True
            break
    if not ended:
        raise ScreenshotHold("PNG not complete: " + path.name)
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "resolution": list(observed)}


def verify_files(plan: dict, folder: Path) -> dict:
    if not folder.is_dir():
        raise ScreenshotHold("Screenshot folder does not exist: " + str(folder))
    # Validate *every* screenshot first; never issue a partial receipt.
    receipts = []
    for shot in plan["shots"]:
        path = folder / shot["filename"]
        if not path.is_file():
            raise ScreenshotHold("Native screenshot output missing: " + shot["filename"])
        receipts.append({**shot, **verify_png(path)})
    return {"status": "PNG_BYTES_VERIFIED_NOT_VISUAL_APPROVAL",
            "map": MAP_PATH, "shots": receipts, "authority": AUTHORITY,
            "engine_provenance_requires_editor_logs": True,
            "gameplay_or_water_physics_proven": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inspect", action="store_true")
    mode.add_argument("--capture-in-editor", action="store_true")
    mode.add_argument("--verify-files", action="store_true")
    parser.add_argument("--run-id", default="Baseline01")
    parser.add_argument("--capture-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        plan = capture_plan(args.run_id)
        if args.capture_in_editor:
            result = schedule_editor_capture(plan)
        elif args.verify_files:
            if args.capture_dir is None:
                raise ScreenshotHold("--verify-files requires explicit --capture-dir")
            result = verify_files(plan, args.capture_dir)
        else:
            result = plan
        print(json.dumps(result, indent=2))
    except (ScreenshotHold, OSError, ValueError, TypeError) as exc:
        parser.exit(2, "FIRST WAKE CAPTURE HOLD: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
