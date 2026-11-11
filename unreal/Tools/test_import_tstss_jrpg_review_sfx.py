"""Portable negative checks. No Unreal Editor or audio playback."""
import os
from pathlib import Path
import tempfile
from unittest import TestCase,main,mock
import import_tstss_jrpg_review_sfx as imp

class ReviewSFXImportTests(TestCase):
    def test_plan_is_review_only_and_not_claimed_imported(self):
        info=imp.plan()
        self.assertEqual(len(info["expected_source_names"]),4)
        self.assertFalse(info["native_import_proven"])
        self.assertFalse(info["audio_playback_proven"])
        self.assertFalse(info["shipping_or_canon_status_changed"])
    def test_wrong_root_denied_before_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(imp.subprocess,"run") as proc:
                with self.assertRaisesRegex(RuntimeError,"separate review"):
                    imp.checked_project(Path(tmp)/"unreal")
                proc.assert_not_called()
    def test_missing_exact_head_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/imp.ROOT_NAME/"unreal"
            project.mkdir(parents=True)
            with mock.patch.dict(os.environ,{},clear=True):
                with mock.patch.object(imp.subprocess,"run") as proc:
                    with self.assertRaisesRegex(RuntimeError,"exact full"):
                        imp.checked_project(project)
                    proc.assert_not_called()
    def test_changed_head_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/imp.ROOT_NAME/"unreal"
            project.mkdir(parents=True)
            with mock.patch.dict(os.environ,{imp.HEAD_ENV:"c"*40}):
                with mock.patch.object(imp.subprocess,"run",
                    return_value=mock.Mock(returncode=0,stdout="b"*40)):
                    with self.assertRaisesRegex(RuntimeError,"source drift"):
                        imp.checked_project(project)
    def test_dirty_review_checkout_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/imp.ROOT_NAME/"unreal"
            project.mkdir(parents=True)
            def git(cmd,**kwargs):
                return mock.Mock(returncode=0,stdout="b"*40
                    if "rev-parse" in cmd else "?? stray")
            with mock.patch.dict(os.environ,{imp.HEAD_ENV:"b"*40}):
                with mock.patch.object(imp.subprocess,"run",side_effect=git):
                    with self.assertRaisesRegex(RuntimeError,"dirty worktree"):
                        imp.checked_project(project)
    def test_source_hash_drift_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/imp.ROOT_NAME/"unreal"
            file=project/imp.SOURCE_DIR/"SFX_EncounterSting.wav"
            file.parent.mkdir(parents=True)
            file.write_bytes(b"tampered")
            def git(cmd,**kwargs):
                return mock.Mock(returncode=0,stdout="b"*40
                    if "rev-parse" in cmd else "")
            with mock.patch.dict(os.environ,{imp.HEAD_ENV:"b"*40}):
                with mock.patch.object(imp.subprocess,"run",side_effect=git):
                    with self.assertRaisesRegex(RuntimeError,"WAV digest drift"):
                        imp.checked_project(project)

if __name__=="__main__":
    main()
