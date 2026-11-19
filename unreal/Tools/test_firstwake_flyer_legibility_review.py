"""Review-only source contracts for Hilltonia flyer legibility.
A source PASS never means GPU or creator visual acceptance.
"""
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] /
          "Source/ToSailTheStarrySky/Private/TSTSSHilltoniaReviewExtension.cpp"
          ).read_text(encoding="utf8")

STAGE = SOURCE.split("bool Apply(UWorld* World,", 1)[1]


class FlyerLegibilityReviewTests(unittest.TestCase):
    def test_explicit_review_scope_and_single_flyer_tag(self):
        for token in ("EWorldType::PIE", "NM_Standalone",
                      'StartsWith(TEXT("/Game/TSTSS/Review/"))',
                      'TEXT("FirstWake_PreludeInteraction_V5_VisualReview")'):
            self.assertIn(token, SOURCE)
        self.assertEqual(STAGE.count('NoticePanel->ComponentTags.Add(TEXT("TSTSS_HILLTONIA_FLYER"))'), 1)

    def test_lighter_paper_darker_sharp_ink(self):
        self.assertIn('TEXT("HilltoniaPostingBoardFlyerPaper"),\n                             Cube, Brass, false)', STAGE)
        self.assertIn('TEXT("ENGINEER\\nWANTED")', STAGE)
        self.assertIn("25.f, FColor(45, 37, 28)", STAGE)
        self.assertIn('TEXT("CAPTAIN IONIA")', STAGE)
        self.assertIn("14.f, FColor(58, 46, 34)", STAGE)

    def test_bounded_local_fill_and_previous_gable(self):
        for token in (
            "Place(NoticeRoof, BoardX, BoardY - 35.f, 260.f, 2.95f, .79f, .10f, 0.f, -25.f)",
            "Place(NoticeRoof, BoardX, BoardY + 35.f, 260.f, 2.95f, .79f, .10f, 0.f, 25.f)",
            'TEXT("HilltoniaPostingFlyerFill")',
            "const FVector FillPosition(BoardX, BoardY - 115.f, 220.f)",
            "const FVector FlyerCenter(BoardX, BoardY - 13.f, 180.f)",
            "FlyerFill->SetAttenuationRadius(190.f)",
            "FlyerFill->SetIntensity(1350.f)",
            "FlyerFill->SetCastShadows(false)",
        ):
            self.assertIn(token, STAGE)
        self.assertNotIn("SetIntensity(560.f)", STAGE)

    def test_no_new_world_or_quest_authority(self):
        scene = STAGE.split("// The Green is a small open", 1)[0]
        for token in ("TryActivate(", "AdvanceTo(", "SaveGame(", "SavePackage(",
                      "RequestForm(", "OpenLevel(", "SetDefaultGameMode(",
                      "bIsInspectionStation ="):
            self.assertNotIn(token, scene)
        self.assertIn("Cube, Brass, false", scene)
        self.assertIn("NoticePanel->ComponentTags.Add", scene)


if __name__ == "__main__":
    unittest.main()