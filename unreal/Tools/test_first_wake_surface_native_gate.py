"""Synthetic fixture checks ONLY; never represent an actual UE Editor native pass."""
from __future__ import annotations
from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SRC = Path(__file__).with_name("first_wake_surface_textures.py")
SPEC = importlib.util.spec_from_file_location("surfacegate", SRC)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
HEAD = "b" * 40

class Native35GateSyntheticFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "unreal"
        registry = self.root / "Tools/Verify-Unreal.ps1"
        registry.parent.mkdir(parents=True)
        self.names = [f"TSTSS.SyntheticFixture{i:02d}" for i in range(35)]
        registry.write_text("\n".join("    '" + n + "'" for n in self.names), encoding="utf-8")
        self.folder = self.root / "Saved/MigrationEvidence/synthetic"
        self.folder.mkdir(parents=True)
        (self.folder / "AutomationReport").mkdir()
        (self.folder / "build.log").write_text("synthetic test only", encoding="utf-8")
        (self.folder / "automation.log").write_text("synthetic test only", encoding="utf-8")
        (self.folder / "head.txt").write_text(HEAD, encoding="utf-8")
        self.report = {"succeeded": 35, "failed": 0, "notRun": 0,
                       "tests": [{"fullTestPath": n, "state": "Success"} for n in self.names]}
        self.receipt = {
            "status": "WIN64_EDITOR_BUILD_AND_NATIVE_AUTOMATIONS_PASS_CLEAN_SOURCE",
            "source_sha": HEAD, "unreal_version": "5.8.4",
            "required_native_tests": 35, "pie_player_input": "NOT_TESTED",
            "visual_approval": "NOT_TESTED"}
        self.save()

    def save(self):
        report_file = self.folder / "AutomationReport/index.json"
        report_file.write_text(json.dumps(self.report), encoding="utf-8")
        self.receipt["report_sha256"] = hashlib.sha256(report_file.read_bytes()).hexdigest()
        (self.folder / "verified-native.json").write_text(
            json.dumps(self.receipt), encoding="utf-8")

    def gate(self, head=HEAD):
        with patch.object(module, "PROJECT", self.root):
            return module.verified_native_35_gate(head)

    def test_fully_matching_synthetic_fixture_accepted_as_logic_only(self):
        self.assertTrue(self.gate().endswith("verified-native.json"))

    def test_stale_or_missing_exact_head_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "no same-head"):
            self.gate("c" * 40)
        (self.folder / "head.txt").write_text("c" * 40, encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "no same-head"):
            self.gate()

    def test_duplicate_and_missing_named_tests_rejected(self):
        self.report["tests"][1]["fullTestPath"] = self.names[0]
        self.save()
        with self.assertRaisesRegex(RuntimeError, "no same-head"):
            self.gate()
        self.report["tests"][1]["fullTestPath"] = self.names[1]
        self.report["tests"][1]["state"] = "NotRun"
        self.save()
        with self.assertRaisesRegex(RuntimeError, "no same-head"):
            self.gate()

    def test_missing_build_or_invalid_report_digest_rejected(self):
        self.receipt["report_sha256"] = "0" * 64
        (self.folder / "verified-native.json").write_text(json.dumps(self.receipt), encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "no same-head"):
            self.gate()
        self.save()
        (self.folder / "build.log").unlink()
        with self.assertRaisesRegex(RuntimeError, "no same-head"):
            self.gate()

    def test_wrong_engine_version_rejected(self):
        self.receipt["unreal_version"] = "5.8.3"
        self.save()
        with self.assertRaisesRegex(RuntimeError, "no same-head"):
            self.gate()

if __name__ == "__main__":
    unittest.main()
