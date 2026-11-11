"""Portable fail-closed tests; no Unreal starts, no map writes."""
import os
from pathlib import Path
import tempfile
from unittest import TestCase,main,mock
import tstss_slice_enemy_combat_sandbox as sandbox

class ReviewCombatSandboxTests(TestCase):
    def test_source_only_plan_keeps_existing_map(self):
        plan=sandbox.validate()
        self.assertEqual(plan["status"],"SOURCE_PLAN_ONLY_NOT_PIE")
        self.assertNotEqual(plan["native_combat_review_map"],plan["source_gallery"])
        self.assertFalse(plan["pie_gameplay_verified"])
        self.assertFalse(plan["campaign_save_modified"])
        self.assertFalse(plan["auto_story_encounter"])

    def test_reject_wrong_project_without_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(sandbox.subprocess,"run") as git:
                with self.assertRaisesRegex(RuntimeError,"exact dedicated"):
                    sandbox.checked_project(Path(tmp)/"unreal")
                git.assert_not_called()

    def test_reject_missing_exact_head_without_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/sandbox.ROOT_NAME/"unreal"
            folder.mkdir(parents=True)
            with mock.patch.dict(os.environ,{},clear=True):
                with mock.patch.object(sandbox.subprocess,"run") as git:
                    with self.assertRaisesRegex(RuntimeError,"full expected"):
                        sandbox.checked_project(folder)
                    git.assert_not_called()

    def test_reject_stale_head(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/sandbox.ROOT_NAME/"unreal"
            folder.mkdir(parents=True)
            def fake(cmd,**kw):
                return mock.Mock(returncode=0,stdout="a"*40)
            with mock.patch.dict(os.environ,{sandbox.EXPECTED_HEAD_ENV:"b"*40}):
                with mock.patch.object(sandbox.subprocess,"run",side_effect=fake):
                    with self.assertRaisesRegex(RuntimeError,"HEAD changed"):
                        sandbox.checked_project(folder)

    def test_reject_dirty_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/sandbox.ROOT_NAME/"unreal"
            folder.mkdir(parents=True)
            def fake(cmd,**kw):
                return mock.Mock(returncode=0,
                    stdout="a"*40 if "rev-parse" in cmd else "?? unsafe-file")
            with mock.patch.dict(os.environ,{sandbox.EXPECTED_HEAD_ENV:"a"*40}):
                with mock.patch.object(sandbox.subprocess,"run",side_effect=fake):
                    with self.assertRaisesRegex(RuntimeError,"dirty worktree"):
                        sandbox.checked_project(folder)

    def test_reject_original_map_hash_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/sandbox.ROOT_NAME/"unreal"
            gallery=folder/sandbox.BASE_FILE
            gallery.parent.mkdir(parents=True)
            gallery.write_bytes(b"not the verified map")
            def fake(cmd,**kw):
                return mock.Mock(returncode=0,
                    stdout="a"*40 if "rev-parse" in cmd else "")
            with mock.patch.dict(os.environ,{sandbox.EXPECTED_HEAD_ENV:"a"*40}):
                with mock.patch.object(sandbox.subprocess,"run",side_effect=fake):
                    with self.assertRaisesRegex(RuntimeError,"SHA differs"):
                        sandbox.checked_project(folder)

    def test_refuse_target_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/sandbox.ROOT_NAME/"unreal"
            source=folder/sandbox.BASE_FILE
            dest=folder/sandbox.TARGET_FILE
            source.parent.mkdir(parents=True)
            source.write_bytes(b"safe synthetic gallery")
            dest.write_bytes(b"do not overwrite")
            marker=dest.read_bytes()
            def fake(cmd,**kw):
                return mock.Mock(returncode=0,
                    stdout="a"*40 if "rev-parse" in cmd else "")
            with mock.patch.dict(os.environ,{sandbox.EXPECTED_HEAD_ENV:"a"*40}):
                with mock.patch.object(sandbox.subprocess,"run",side_effect=fake):
                    with mock.patch.object(sandbox,"sha256",return_value=sandbox.BASE_SHA256):
                        with self.assertRaisesRegex(RuntimeError,"refuse overwrite"):
                            sandbox.checked_project(folder)
            self.assertEqual(dest.read_bytes(),marker)

    def test_cpp_combat_bench_preserves_protagonist_recruitment(self):
        root=Path(sandbox.__file__).resolve().parents[1]
        base=root/"Source/ToSailTheStarrySky"
        header=(base/"Public/Enemies/TSTSSSliceEnemyReviewSession.h").read_text(encoding="utf-8")
        impl=(base/"Private/Enemies/TSTSSSliceEnemyReviewSession.cpp").read_text(encoding="utf-8")
        actor=(base/"Private/Enemies/TSTSSSliceEnemyReviewBattleConsole.cpp").read_text(encoding="utf-8")
        for token in ("EnderOnly","IoniaRecruited","AfterSplashdown"):
            self.assertIn(token,header)
        self.assertIn('Member.LearnedSkills.Add(ReviewStrikeId)',impl)
        self.assertIn('FTSTSSSliceEnemyCatalog::TryMakeReviewWave',impl)
        self.assertIn('UTSTSSSliceEnemyReviewAI::TryActReviewEnemy',impl)
        self.assertIn('Next->InitializeEncounter(Crew, CandidatePartyIds, Wave)',impl)
        self.assertIn('EKeys::F7',actor)
        self.assertIn('EKeys::F8',actor)
        self.assertIn('EKeys::F9',actor)
        self.assertIn('EKeys::J',actor)
        self.assertIn('EKeys::K',actor)
        self.assertIn("#if UE_BUILD_SHIPPING",impl)
        self.assertIn("#if UE_BUILD_SHIPPING",actor)

if __name__=="__main__":
    main()
