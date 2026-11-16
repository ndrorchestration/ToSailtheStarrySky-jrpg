"""Refusal and source-parity regression gates without starting Unreal."""
import os
from pathlib import Path
import tempfile
from unittest import TestCase, main, mock
import tstss_jrpg_hybrid_review_map as review


class HybridReviewPlanTests(TestCase):
    def test_independent_v2_no_unauthorized_story_mutation(self):
        info=review.plan()
        self.assertNotEqual(info["target_map"],info["source_map"])
        self.assertTrue(info["original_gallery_preserved"])
        self.assertTrue(info["combat_map_preserved"])
        self.assertEqual(info["random_min_distance_cm"],1800)
        self.assertEqual(info["random_guaranteed_by_cm"],5700)
        self.assertFalse(info["pie_controls_tested"])
        self.assertFalse(info["world_story_enemy_placement_approved"])

    def test_bad_root_fails_before_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(review.subprocess,"run") as proc:
                with self.assertRaisesRegex(RuntimeError,"wrong isolated"):
                    review.checked_project(Path(tmp)/"unreal")
                proc.assert_not_called()

    def test_missing_exact_head_fails_before_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/review.ROOT_NAME/"unreal"
            project.mkdir(parents=True)
            with mock.patch.dict(os.environ,{},clear=True):
                with mock.patch.object(review.subprocess,"run") as proc:
                    with self.assertRaisesRegex(RuntimeError,"full exact"):
                        review.checked_project(project)
                    proc.assert_not_called()

    def test_stale_head_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/review.ROOT_NAME/"unreal"
            project.mkdir(parents=True)
            with mock.patch.dict(os.environ,{review.SOURCE_HEAD_ENV:"b"*40}):
                with mock.patch.object(review.subprocess,"run",
                    return_value=mock.Mock(returncode=0,stdout="a"*40)):
                    with self.assertRaisesRegex(RuntimeError,"HEAD drift"):
                        review.checked_project(project)

    def test_dirty_worktree_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/review.ROOT_NAME/"unreal"
            project.mkdir(parents=True)
            def git(cmd,**kwargs):
                return mock.Mock(returncode=0,stdout="a"*40
                    if "rev-parse" in cmd else "?? unexpected-change")
            with mock.patch.dict(os.environ,{review.SOURCE_HEAD_ENV:"a"*40}):
                with mock.patch.object(review.subprocess,"run",side_effect=git):
                    with self.assertRaisesRegex(RuntimeError,"dirty review"):
                        review.checked_project(project)

    def test_verified_v1_asset_integrity_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/review.ROOT_NAME/"unreal"
            f=project/review.BASE_FILE
            f.parent.mkdir(parents=True)
            f.write_bytes(b"incorrect")
            def git(cmd,**kwargs):
                return mock.Mock(returncode=0,stdout="a"*40
                    if "rev-parse" in cmd else "")
            with mock.patch.dict(os.environ,{review.SOURCE_HEAD_ENV:"a"*40}):
                with mock.patch.object(review.subprocess,"run",side_effect=git):
                    with self.assertRaisesRegex(RuntimeError,"V1 map changed"):
                        review.checked_project(project)

    def test_target_overwrite_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/review.ROOT_NAME/"unreal"
            for p in (review.BASE_FILE,review.ORIGINAL_GALLERY):
                f=project/p
                f.parent.mkdir(parents=True,exist_ok=True)
                f.write_bytes(b"source")
            target=project/review.NEW_FILE
            target.write_bytes(b"keep")
            def git(cmd,**kwargs):
                return mock.Mock(returncode=0,stdout="a"*40
                    if "rev-parse" in cmd else "")
            with mock.patch.dict(os.environ,{review.SOURCE_HEAD_ENV:"a"*40}):
                with mock.patch.object(review.subprocess,"run",side_effect=git):
                    with mock.patch.object(review,"digest",side_effect=[
                        review.BASE_HASH,review.GALLERY_HASH]):
                        with self.assertRaisesRegex(RuntimeError,"refuse existing V2"):
                            review.checked_project(project)
            self.assertEqual(target.read_bytes(),b"keep")

    def test_cpp_review_adapter_and_biome_tables(self):
        source=Path(review.__file__).resolve().parents[1]
        base=source/"Source/ToSailTheStarrySky"
        h=(base/"Public/Encounter/TSTSSJRPGEncounterDirector.h").read_text()
        cpp=(base/"Private/Encounter/TSTSSJRPGEncounterDirector.cpp").read_text()
        field=(base/"Private/Encounter/TSTSSJRPGEncounterFieldReview.cpp").read_text()
        for token in ("HarborOutskirts","Woodland","Coast","Highlands"):
            self.assertIn(token,h)
        for token in ("bSafeZone","bShipTravel","bAreaAuthorized","bPartyAuthorized",
                      "bStorySequenceActive","bScriptedEncounterApproved"):
            self.assertIn(token,h)
        for preset in ("Review_HarborBanditPatrol","Review_WoodlandSporeline",
                       "Review_CoastalHunters","Review_HighlandStalkers"):
            self.assertIn(preset,cpp)
        for token in ("TryRecordWalking","TryHandoffToBattle",
                      "TryReturnToExploration","TryRequestExplicitScriptedWave"):
            self.assertIn(token,field)
        self.assertIn("TSTSSReviewOnly",field)
        self.assertIn("#if UE_BUILD_SHIPPING",field)
        self.assertIn("TryRetreatReviewBattle",field)
        self.assertIn("TryCompleteBattle(ActiveTicketSerial)",field)
        self.assertIn("EKeys::Escape",field)
        self.assertIn("EKeys::J",field)
        self.assertIn("EKeys::K",field)
        self.assertIn("BattleConsole->DisableInput(PC)",field)
        self.assertNotIn("BattleConsole->EnableInput(PC)",field)


if __name__=="__main__":
    main()
