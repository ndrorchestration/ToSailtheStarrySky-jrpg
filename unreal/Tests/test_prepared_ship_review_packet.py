"""Fail-closed tests for offline ship review packet verification.

These tests use synthetic receipts and never import, render, or approve assets.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))
from verify_prepared_ship_review import (
    PacketHold, packet_file, read_clearance_receipt, source_state,
    check_recomputed_clearance, validate_camera_plan, capture_plan,
)


def clearance_fixture():
    return {
        "authority": "SAMPLED_GEOMETRY_SCREEN_ONLY_NOT_ENGINE_OR_COLLISION_APPROVED",
        "checked_directed_transitions": 6,
        "time_samples_per_transition": 21,
        "wing_instances": 4,
        "checked_poses": 126,
        "mesh_sample_points": 1240,
        "minimum_proxy_aabb_clearance_cm": 19.94,
        "minimum_interwing_aabb_clearance_cm": 189.85,
    }


class PreparedReviewPacketTests(unittest.TestCase):
    def test_accepts_utf8_and_windows_powershell_utf16le_receipts(self):
        data = clearance_fixture()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clearance.json"
            for encoding in ("utf-8", "utf-16"):
                path.write_text(json.dumps(data), encoding=encoding)
                self.assertEqual(read_clearance_receipt(path), data)

    def test_rejects_invalid_receipt_encoding_or_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clearance.json"
            for blob in (b"\xfe\xff\x00{", b"\xff\xfe\x00", b"[]",
                         b"\xff" * 20001):
                path.write_bytes(blob)
                with self.assertRaises((PacketHold, UnicodeError, ValueError)):
                    read_clearance_receipt(path)

    def test_exact_clearance_receipt_passes(self):
        data = clearance_fixture()
        check_recomputed_clearance(data, copy.deepcopy(data))

    def test_rejects_forged_count_or_clearance_or_status(self):
        original = clearance_fixture()
        for field, value in (
            ("checked_poses", 127),
            ("mesh_sample_points", 1260),
            ("minimum_proxy_aabb_clearance_cm", 9.9),
            ("authority", "NATIVE_UNREAL_PASS"),
        ):
            altered = copy.deepcopy(original)
            altered[field] = value
            with self.subTest(field=field):
                with self.assertRaises(PacketHold):
                    check_recomputed_clearance(altered, original)
        unsafe = copy.deepcopy(original)
        unsafe["minimum_proxy_aabb_clearance_cm"] = 9.0
        with self.assertRaises(PacketHold):
            check_recomputed_clearance(unsafe, unsafe)

    def test_camera_plan_is_four_unapproved_shots(self):
        plan = capture_plan("ShipReview20261101")
        validate_camera_plan(plan)
        self.assertFalse(plan["native_render_verified"])
        self.assertFalse(plan["approved_art"])

    def test_rejects_camera_duplicates_changed_stage_and_false_approval(self):
        original = capture_plan("ShipReview20261101")
        for change in ("duplicate", "stage", "approval", "native", "resolution"):
            plan = copy.deepcopy(original)
            if change == "duplicate":
                plan["shots"][1]["filename"] = plan["shots"][0]["filename"]
            elif change == "stage":
                plan["shots"][0]["story_stage"] = "Chapter 1 Act 1"
            elif change == "approval":
                plan["approved_art"] = True
            elif change == "native":
                plan["native_render_verified"] = True
            else:
                plan["resolution"] = [960, 540]
            with self.subTest(change=change), self.assertRaises(PacketHold):
                validate_camera_plan(plan)

    def test_missing_or_nonfile_packet_input_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(FileNotFoundError):
                packet_file(root, "missing.txt")
            (root / "directory").mkdir()
            with self.assertRaises(PacketHold):
                packet_file(root, "directory")

    def test_rejects_path_escaping_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "packet"
            root.mkdir()
            outer = Path(tmp) / "outside.txt"
            outer.write_text("private", encoding="utf-8")
            with self.assertRaises(PacketHold):
                packet_file(root, "../outside.txt")

    def test_rejects_unpinned_source_commit(self):
        with self.assertRaises(PacketHold):
            source_state(Path("."), "not-an-exact-git-sha")

    def test_source_git_guard_requires_ancestry_and_exact_files(self):
        head = "a" * 40
        base = "b" * 40
        calls = []

        def fake_git(command, **kwargs):
            cmd = command[3:]
            calls.append(cmd)
            if cmd[0] == "rev-parse":
                return subprocess.CompletedProcess(command, 0, stdout=head + "\n", stderr="")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with mock.patch("verify_prepared_ship_review.subprocess.run", side_effect=fake_git):
            self.assertEqual(source_state(Path("."), base)["current_source_sha"], head)
        self.assertTrue(any(c[:2] == ["merge-base", "--is-ancestor"] for c in calls))
        self.assertEqual(sum(c[0] == "diff" for c in calls), 2)

    def test_source_git_guard_rejects_divergence(self):
        base = "b" * 40

        def fake_git(command, **kwargs):
            cmd = command[3:]
            if cmd[0] == "rev-parse":
                return subprocess.CompletedProcess(command, 0, stdout="a" * 40, stderr="")
            if cmd[0] == "diff":
                return subprocess.CompletedProcess(command, 1, stdout="", stderr="")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with mock.patch("verify_prepared_ship_review.subprocess.run", side_effect=fake_git):
            with self.assertRaisesRegex(PacketHold, "diverged"):
                source_state(Path("."), base)


if __name__ == "__main__":
    unittest.main()
