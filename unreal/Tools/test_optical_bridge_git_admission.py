"""Exercise real Git admission without launching Unreal or modifying maps."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


TOOLS = Path(__file__).resolve().parent
BRANCH = "review/ue58-optical-integration-stage-20261115"


def load_review_script(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    fake_unreal = types.SimpleNamespace(
        SystemLibrary=types.SimpleNamespace(get_engine_version=lambda: "5.8.4-test"))
    with mock.patch.dict(sys.modules, {"unreal": fake_unreal}):
        spec.loader.exec_module(module)
    return module


class GitAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "TSTSS_843_OpticalIntegrated_20261115"
        self.root.mkdir()
        self.git("init", "-q", "-b", BRANCH)
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Checkout Test")
        self.git("config", "commit.gpgsign", "false")
        (self.root / "source.txt").write_text("base", encoding="utf-8")
        self.git("add", "source.txt")
        self.git("commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD")
        (self.root / "source.txt").write_text("descendant", encoding="utf-8")
        self.git("commit", "-qam", "descendant")
        self.head = self.git("rev-parse", "HEAD")

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.root), *args],
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def test_stager_checks_actual_git_ancestry_and_pinned_head(self):
        stage = load_review_script("stage_vs02_optical_bridge_reach")
        # The artificial engine version stops execution after checkout admission,
        # before any map, asset, or Editor API can be touched.
        stage.u.SystemLibrary.get_engine_version = lambda: "0.0.0-test"
        with mock.patch.object(stage, "ROOT", self.root), \
             mock.patch.object(stage, "INTEGRATION_BASE", self.base), \
             mock.patch.object(stage, "OLD_BRANCH_HEAD", self.head), \
             mock.patch.dict(os.environ, {"TSTSS_BRIDGE_REACH_STAGE_EXPLICIT": "1"}):
            with self.assertRaisesRegex(RuntimeError, "wrong native Unreal version"):
                stage.stage()
            with mock.patch.object(stage, "INTEGRATION_BASE", "f" * 40):
                with self.assertRaisesRegex(RuntimeError, "lacks telemetry base"):
                    stage.stage()
            with mock.patch.object(stage, "OLD_BRANCH_HEAD", self.base):
                with self.assertRaisesRegex(RuntimeError, "checkout SHA mismatch"):
                    stage.stage()
            self.git("checkout", "-qb", "review/unapproved")
            with self.assertRaisesRegex(RuntimeError, "unauthorized checkout or branch"):
                stage.stage()
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_readback_rejects_changed_head_after_recorded_stage(self):
        readback = load_review_script("readback_vs02_optical_bridge_reach")
        stage_receipt = Path(self.temp.name) / "stage.json"
        backup = Path(self.temp.name) / "backup.umap"
        receipt = Path(self.temp.name) / "readback.json"
        stage_receipt.write_text(json.dumps({"head_at_stage": self.head,
                                            "status": "SENTINEL"}), encoding="utf-8")
        backup.write_bytes(b"not a real map")
        with mock.patch.object(readback, "ROOT", self.root), \
             mock.patch.object(readback, "INTEGRATION_BASE", self.base), \
             mock.patch.object(readback, "STAGE", stage_receipt), \
             mock.patch.object(readback, "BACKUP", backup), \
             mock.patch.object(readback, "RECEIPT", receipt):
            # Valid identity reaches the deliberately invalid receipt status.
            with self.assertRaisesRegex(RuntimeError, "stage native result"):
                readback.inspect()
            (self.root / "source.txt").write_text("new head", encoding="utf-8")
            self.git("commit", "-qam", "changed head")
            with self.assertRaisesRegex(RuntimeError, "checkout SHA mismatch"):
                readback.inspect()
        self.assertFalse(receipt.exists())
        self.assertEqual(self.git("status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
