"""Source-contract guard for the approved Hilltonia posting-board visual pass.

This verifies authoring and quest safety; it is NOT UE native-render approval.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSHilltoniaReviewExtension.cpp").read_text(encoding="utf-8")
HUD = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSFirstWakeReviewHUD.cpp").read_text(encoding="utf-8")
EXPLORER = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")


class ApprovedBoardSourceContract(unittest.TestCase):
    def test_flyer_headline_is_spelled_correctly_in_world_and_quest_hud(self):
        self.assertIn('TEXT("ENGINEER\\nWANTED")', SOURCE)
        self.assertIn('DrawText(TEXT("ENGINEER WANTED")', HUD)
        self.assertIn('TEXT("CAPTAIN IONIA")', SOURCE)

    def test_low_gable_and_named_hilltonia_plaque(self):
        self.assertIn('TEXT("HilltoniaPostingBoardGable")', SOURCE)
        self.assertIn('TEXT("HilltoniaPostingBoardPlaqueText")', SOURCE)
        self.assertIn('TEXT("HILLTONIA\\nPOSTING BOARD")', SOURCE)
        self.assertIn('Place(NoticeRoof, BoardX, BoardY - 35.f, 260.f', SOURCE)
        self.assertIn('Place(NoticeRoof, BoardX, BoardY + 35.f, 260.f', SOURCE)

    def test_paper_and_accents_do_not_own_interaction(self):
        self.assertEqual(SOURCE.count('ComponentTags.Add(TEXT("TSTSS_HILLTONIA_FLYER"))'), 1)
        self.assertIn('NoticePanel->ComponentTags.Add(TEXT("TSTSS_HILLTONIA_FLYER"));', SOURCE)
        for name in ("NamePlaque", "PlaqueTrim", "OtherNotices", "InkRules",
                     "BrassTacks", "GearSeal", "LanternFixture",
                     "FlowerPlanters", "PlanterPots"):
            self.assertIn("HilltoniaPostingBoard" + name, SOURCE)
        for component in ("NoticeHeader", "NoticePlaqueTrim", "NoticePinnedPapers",
                          "NoticePaperInk", "NoticeTacks", "NoticeSeal",
                          "NoticeLantern", "NoticeFlowers", "NoticePots"):
            pattern = re.compile(r'auto\* ' + component + r' = Make\([^;]+?, false\);', re.S)
            self.assertRegex(SOURCE, pattern, component + " must have no collision")
        self.assertIn('Text->SetCollisionEnabled(ECollisionEnabled::NoCollision);', SOURCE)

    def test_lantern_is_review_only_shadow_free(self):
        self.assertIn('HilltoniaPostingBoardWarmLanternLight', SOURCE)
        self.assertIn('LanternLight->SetCastShadows(false);', SOURCE)
        self.assertIn('LanternLight->SetAttenuationRadius(260.f);', SOURCE)

    def test_flyer_story_acceptance_still_lives_outside_civic_art(self):
        self.assertNotIn('AdvanceTo(', SOURCE)
        self.assertNotIn('SaveGameToSlot(', SOURCE)
        self.assertIn('AcceptHilltoniaFlyer()', EXPLORER)
        self.assertIn('DeclineHilltoniaFlyer()', EXPLORER)
        self.assertIn('IsHilltoniaFlyerHit(Hit)', EXPLORER)
        self.assertIn('IsHilltoniaFlyerOpen()', EXPLORER)


if __name__ == "__main__":
    unittest.main()
