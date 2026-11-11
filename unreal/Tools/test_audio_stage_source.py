#!/usr/bin/env python3
"""Engine-free negative tests for guarded disposable First Wake audio map staging."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_audio_preview_samples import generate
import stage_first_wake_audio_qa as stage

SHA = "b" * 40
GIB = 1024 ** 3
ROOT = Path(__file__).resolve().parents[1]

class TestAudioStageSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        cls.project = root / "TSTSS_AudioReview_20261111" / "unreal"
        cls.project.mkdir(parents=True)
        (cls.project / "ToSailTheStarrySky.uproject").write_text("{}",encoding="utf-8")
        cls.wav = root / "scratch-wavs"
        generate(cls.wav)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def invoke(self, *, stage_opt=stage.STAGE_OPT_IN,
               import_opt=stage.IMPORT_OPT_IN,
               sha=SHA, git_sha=SHA, branch_code=1, dirty="",
               ram=8*GIB, disk=20*GIB):
        env = {
            "TSTSS_AUDIO_STAGE_OPT_IN": stage_opt,
            "TSTSS_AUDIO_REVIEW_OPT_IN": import_opt,
            "TSTSS_AUDIO_EXPECTED_SOURCE_SHA": sha,
            "TSTSS_AUDIO_REVIEW_SOURCE": str(self.wav),
        }
        def fake_git(_root, *parts):
            if parts == ("rev-parse", "HEAD"):
                return git_sha
            if parts == ("status", "--porcelain", "--untracked-files=no"):
                return dirty
            raise AssertionError("Unexpected Git API: " + repr(parts))

        with mock.patch.dict(os.environ, env, clear=False), \
             mock.patch.object(stage, "_git", side_effect=fake_git), \
             mock.patch.object(stage.subprocess, "run",
                               return_value=SimpleNamespace(returncode=branch_code)), \
             mock.patch.object(stage, "available_ram_bytes", return_value=ram), \
             mock.patch.object(stage.shutil, "disk_usage",
                               return_value=SimpleNamespace(free=disk)):
            return stage.preflight(self.project)

    def test_positive_exact_head_detached_synthetic_only(self):
        root, paths, sha = self.invoke()
        self.assertEqual(root, self.project.parent)
        self.assertEqual(sha, SHA)
        self.assertEqual(len(paths), 10)
        self.assertEqual({p.name for p in paths}, stage.EXPECTED)

    def test_no_implicit_staging_authorization(self):
        with self.assertRaisesRegex(RuntimeError, "staging opt-in"):
            self.invoke(stage_opt="")
        with self.assertRaisesRegex(RuntimeError, "import opt-in"):
            self.invoke(import_opt="")

    def test_no_missing_or_wrong_git_identity(self):
        with self.assertRaisesRegex(RuntimeError, "Full explicit source SHA"):
            self.invoke(sha="1234")
        with self.assertRaisesRegex(RuntimeError, "differs from explicit"):
            self.invoke(git_sha="c" * 40)
        with self.assertRaisesRegex(RuntimeError, "detached"):
            self.invoke(branch_code=0)
        with self.assertRaisesRegex(RuntimeError, "Could not establish detached"):
            self.invoke(branch_code=128)
        with self.assertRaisesRegex(RuntimeError, "Tracked source is dirty"):
            self.invoke(dirty=" M unreal/Config/DefaultEngine.ini")

    def test_admission_blocks_resource_contention(self):
        with self.assertRaisesRegex(RuntimeError, "6.5 GiB"):
            self.invoke(ram=3 * GIB)
        with self.assertRaisesRegex(RuntimeError, "14 GiB"):
            self.invoke(disk=8 * GIB)

    def test_no_main_or_non_audio_worktree(self):
        with self.assertRaisesRegex(RuntimeError, "non-AudioReview"):
            alt = Path(self.temp.name) / "main" / "unreal"
            alt.mkdir(parents=True, exist_ok=True)
            (alt / "ToSailTheStarrySky.uproject").write_text("{}",encoding="utf-8")
            with mock.patch.dict(os.environ, {
                "TSTSS_AUDIO_STAGE_OPT_IN": stage.STAGE_OPT_IN,
                "TSTSS_AUDIO_REVIEW_OPT_IN": stage.IMPORT_OPT_IN,
                "TSTSS_AUDIO_EXPECTED_SOURCE_SHA": SHA,
            }):
                stage.preflight(alt)

    def test_qa_map_placement_is_explicit_and_non_overwriting(self):
        script = (ROOT / "Tools" / "stage_first_wake_audio_qa.py").read_text(encoding="utf-8")
        self.assertIn("new_level_from_template(DEST_MAP, SOURCE_MAP)", script)
        self.assertIn("assets.does_asset_exist(DEST_MAP)", script)
        self.assertIn("EditorActorSubsystem", script)
        self.assertIn("SoundWave", script)
        self.assertIn("save_current_level()", script)
        self.assertIn("save_asset(path, False)", script)
        for actor in ("TSTSSAudioCueBankActor", "TSTSSAudioEnvironmentDirector",
                      "TSTSSHarborAudioZone", "TSTSSFootstepAudioDirector"):
            self.assertIn(actor, script)
        self.assertIn("STAGED_QA_UNAUDITIONED_NOT_RELEASE_AUTHORIZED", script)
        self.assertNotIn("delete_asset(", script)
        self.assertNotIn("replace_existing = True", script)
        self.assertNotIn("ship_allowed = True", script)
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("/Content/TSTSS/Audio/QAReview/", ignore)
        self.assertTrue((ROOT / "Content" / "TSTSS" / "Review" /
                         "VerticalSlice" / "VS01_DenithHarbor.umap").is_file())

if __name__ == "__main__":
    unittest.main()
