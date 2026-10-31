"""Offline and mocked UE5.8 screenshot-contract tests; no engine claim."""
from __future__ import annotations

import json
from pathlib import Path
import struct
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Tools"))
import capture_first_wake_review as capture


class Camera:
    def __init__(self, label):
        self.label = label

    def get_actor_label(self, create_if_none=False):
        return self.label


class MeshRef:
    def __init__(self, path):
        self.path = path

    def get_path_name(self):
        return self.path


class Ship(Camera):
    def __init__(self, **properties):
        super().__init__(capture.SHIP_LABEL)
        self.properties = {
            "allow_orbiter_preview": False,
            "authored_wing_mesh": MeshRef(
                "/Game/TSTSS/Review/ShipArt/WingCandidateV2/AureateWake_Wing_Lookdev.AureateWake_Wing_Lookdev"),
            "authored_root_support_mesh": MeshRef(
                "/Game/TSTSS/Review/ShipArt/RootSupportCandidateV1/AureateWake_RootSupport_Lookdev.AureateWake_RootSupport_Lookdev"),
            "use_root_pivoted_wing_pose": True,
        }
        self.properties.update(properties)

    def get_wing_count(self):
        return 4

    def get_root_support_count(self):
        return 4

    def get_hydrofoil_count(self):
        return 2

    def is_transitioning(self):
        return False

    def get_current_form(self):
        return "AureateWakeForm.SKYBORNE"

    def get_editor_property(self, name):
        if name not in self.properties:
            raise AttributeError(name)
        return self.properties[name]


def mocked_unreal(*, map_path=capture.MAP_PATH, ship=None, cameras=None):
    class World:
        def get_path_name(self):
            return map_path + ".FirstWake_Benchmark_V1"

    class EditorSubsystem:
        def get_editor_world(self):
            return World()

    class ActorSubsystem:
        def get_all_level_actors(self):
            return cameras + [ship]

    capture_requests = []
    scheduled = []

    class Library:
        @staticmethod
        def take_high_res_screenshot(w, h, filename, **kwargs):
            capture_requests.append((w, h, filename, kwargs))
            return types.SimpleNamespace(is_valid_task=lambda: True,
                                         is_task_done=lambda: True)

    class Scheduler:
        @staticmethod
        def add_latent_command(callback):
            scheduled.append(callback)
            return callback

    class EditorType:
        pass

    class ActorType:
        pass

    if ship is None:
        ship = Ship()
    if cameras is None:
        cameras = [Camera("TSTSS_REVIEW_Camera_" + c.name) for c in capture.CAMERAS]

    def get_editor_subsystem(cls):
        return EditorSubsystem() if cls is EditorType else ActorSubsystem()

    return types.SimpleNamespace(
        UnrealEditorSubsystem=EditorType, EditorActorSubsystem=ActorType,
        CineCameraActor=Camera, AureateWakePreviewActor=Ship,
        AutomationLibrary=Library, AutomationScheduler=Scheduler,
        get_editor_subsystem=get_editor_subsystem, log=lambda _: None,
        scheduled=scheduled, requests=capture_requests,
    )


def png_chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def make_png(width=capture.WIDTH, height=capture.HEIGHT):
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = (b"\0" + b"\0" * (3 * width)) * height
    return (b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr) +
            png_chunk(b"IDAT", zlib.compress(raw, 9)) + png_chunk(b"IEND", b""))


class CaptureContractTests(unittest.TestCase):
    def test_story_stage_and_camera_source_is_deterministic(self):
        p = capture.capture_plan("Review20261031")
        self.assertEqual(len(p["shots"]), 4)
        self.assertEqual(len(set(s["filename"] for s in p["shots"])), 4)
        self.assertEqual([s["story_stage"] for s in p["shots"]],
                         ["Prelude", "Prelude", "Prelude", "Chapter 1 Act 1"])
        self.assertIn("composition only", p["shots"][3]["intent"])
        self.assertEqual(p["resolution"], [1920, 1080])
        self.assertFalse(p["native_render_verified"])

    def test_reject_unsafe_run_ids(self):
        for bad in ("", "a", "../secret", "A/B/C", "bad name", "a" * 40, "a.png"):
            with self.subTest(name=bad), self.assertRaises(capture.ScreenshotHold):
                capture.capture_plan(bad)

    def test_no_editor_mode_can_build_offline(self):
        with patch.dict(sys.modules, {"unreal": None}):
            with self.assertRaisesRegex(capture.ScreenshotHold, "Unreal Editor Python"):
                capture.preflight_in_editor(capture.capture_plan("Review20261031"))

    def test_editor_preflight_rejects_wrong_map(self):
        unreal = mocked_unreal(map_path="/Game/TSTSS/Chapter01")
        with patch.dict(sys.modules, {"unreal": unreal}):
            with self.assertRaisesRegex(capture.ScreenshotHold, "exact isolated"):
                capture.preflight_in_editor(capture.capture_plan("Review20261031"))
        self.assertFalse(unreal.scheduled)

    def test_editor_preflight_rejects_missing_camera(self):
        unreal = mocked_unreal(cameras=[Camera("TSTSS_REVIEW_Camera_" + c.name)
                                        for c in capture.CAMERAS[:-1]])
        with patch.dict(sys.modules, {"unreal": unreal}):
            with self.assertRaisesRegex(capture.ScreenshotHold, "Missing/duplicate"):
                capture.preflight_in_editor(capture.capture_plan("Review20261031"))
        self.assertFalse(unreal.scheduled)

    def test_editor_preflight_rejects_unreviewed_art_or_orbiter(self):
        for property_name, value in (
            ("allow_orbiter_preview", True),
            ("authored_wing_mesh", None),
            ("authored_root_support_mesh", None),
            ("use_root_pivoted_wing_pose", False),
        ):
            unreal = mocked_unreal(ship=Ship(**{property_name: value}))
            with self.subTest(property=property_name), patch.dict(sys.modules, {"unreal": unreal}):
                with self.assertRaises(capture.ScreenshotHold):
                    capture.preflight_in_editor(capture.capture_plan("Review20261031"))
            self.assertFalse(unreal.scheduled)

    def test_capture_rejects_non_review_mesh_substitution(self):
        for prop in ("authored_wing_mesh", "authored_root_support_mesh"):
            ship = Ship(**{prop: MeshRef("/Game/TSTSS/Gameplay/Ship/Unapproved.Unapproved")})
            unreal = mocked_unreal(ship=ship)
            with self.subTest(property=prop), patch.dict(sys.modules, {"unreal": unreal}):
                with self.assertRaisesRegex(capture.ScreenshotHold, "non-review mesh"):
                    capture.preflight_in_editor(capture.capture_plan("Review20261031"))
            self.assertFalse(unreal.scheduled)

    def test_screenshot_requests_schedule_and_complete_across_editor_ticks(self):
        unreal = mocked_unreal()
        with patch.dict(sys.modules, {"unreal": unreal}):
            plan = capture.capture_plan("Review20261031")
            result = capture.schedule_editor_capture(plan)
            self.assertEqual(result["status"], "CAPTURE_TASKS_SCHEDULED_NOT_VERIFIED")
            self.assertEqual(len(unreal.scheduled), 1)
            # The engine owns the tick-based execution; mocked tests are not screenshots.
            list(unreal.scheduled[0]())
        self.assertEqual(len(unreal.requests), 4)
        for i, req in enumerate(unreal.requests):
            self.assertEqual(req[:2], (1920, 1080))
            self.assertEqual(req[2], plan["shots"][i]["filename"])
            self.assertIsInstance(req[3]["camera"], Camera)
            self.assertFalse(req[3]["capture_hdr"])
            self.assertTrue(req[3]["force_game_view"])

    def test_receipts_require_all_actual_pngs_and_valid_dimensions(self):
        plan = capture.capture_plan("Review20261031")
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            for shot in plan["shots"]:
                (folder / shot["filename"]).write_bytes(make_png())
            results = capture.verify_files(plan, folder)
            self.assertEqual(len(results["shots"]), 4)
            self.assertEqual(results["status"], "PNG_BYTES_VERIFIED_NOT_VISUAL_APPROVAL")
            self.assertTrue(all(len(s["sha256"]) == 64 for s in results["shots"]))
            (folder / plan["shots"][3]["filename"]).unlink()
            with self.assertRaisesRegex(capture.ScreenshotHold, "output missing"):
                capture.verify_files(plan, folder)

    def test_corrupt_crc_and_resolution_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "test.png"
            wrong = make_png(width=1280, height=720)
            path.write_bytes(wrong)
            with self.assertRaisesRegex(capture.ScreenshotHold, "resolution"):
                capture.verify_png(path)
            corrupt = bytearray(make_png())
            corrupt[31] ^= 1
            path.write_bytes(corrupt)
            with self.assertRaisesRegex(capture.ScreenshotHold, "CRC"):
                capture.verify_png(path)

    def test_only_review_world_and_no_story_or_save_mutations(self):
        source = (ROOT / "Tools" / "capture_first_wake_review.py").read_text(encoding="utf-8")
        for forbidden in ("save_map(", "save_current_level(", "spawn_actor_from_class(",
                          "advance_water_beat(", "request_form(", "set_editor_property(",
                          "import_asset(", "run_console_command("):
            self.assertNotIn(forbidden, source)
        self.assertIn("take_high_res_screenshot(", source)
        self.assertIn("add_latent_command", source)
        self.assertIn("is_task_done()", source)


if __name__ == "__main__":
    unittest.main()
