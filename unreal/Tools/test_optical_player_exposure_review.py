"""Review-only optical player-camera exposure source-contract checks.

These checks do not claim Unreal-native rendering or creator approval.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
CPP=(ROOT/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
BEGIN="void ApplyOpticalReviewPlayerExposure(UWorld* World, UCameraComponent* Camera)"
END="bool ApplyV5HarborReviewLookdev(UWorld* World)"

class OpticalPlayerExposureSourceContract(unittest.TestCase):
    def helper(self):
        self.assertEqual(CPP.count(BEGIN),1)
        self.assertEqual(CPP.count(END),1)
        return CPP.split(BEGIN,1)[1].split(END,1)[0]

    def test_pie_and_standalone_only(self):
        helper=self.helper()
        self.assertIn("World->WorldType != EWorldType::PIE",helper)
        self.assertIn("World->GetNetMode() != NM_Standalone",helper)
        self.assertIn("!IsValid(Camera)",helper)
        self.assertIn("!World->GetOutermost()",helper)

    def test_review_package_and_exact_scene_only(self):
        helper=self.helper()
        self.assertIn('TEXT("/Game/TSTSS/Review/EngineFocus_V1/")',helper)
        self.assertIn('GetCurrentLevelName(World, true) !=',helper)
        self.assertIn('TEXT("M_EnginePresentationReview")',helper)
        self.assertNotIn('TEXT("VS02_AureateInteriors")',helper)
        self.assertNotIn('TEXT("VS05_DenithFuelShanty")',helper)

    def test_only_gameplay_camera_and_no_physical_sky_disabling(self):
        helper=self.helper()
        for term in ("Camera->PostProcessSettings.bOverride_AutoExposureBias = true;",
                     "Camera->PostProcessSettings.AutoExposureBias = -6.0f;",
                     "Camera->PostProcessBlendWeight = 1.0f;"):
            self.assertIn(term,helper)
        for forbidden in ("r.SkyAtmosphere", "Sun->", "Moon->", "SaveGame",
                          "SetActorLocation", "SetStaticMesh", "SetViewTarget"):
            self.assertNotIn(forbidden,helper)

    def test_opt_in_is_not_a_story_action_and_owns_no_cinematic(self):
        self.assertEqual(CPP.count("ApplyOpticalReviewPlayerExposure(GetWorld(), FollowCamera);"),1)
        begin=CPP.split("void ATSTSSExplorerCharacter::BeginPlay()",1)[1]
        self.assertLess(begin.index("ApplyOpticalReviewPlayerExposure(GetWorld(), FollowCamera);"),
                        begin.index("ApplyV5HarborReviewLookdev(GetWorld());"))
        self.assertIn("void ATSTSSExplorerCharacter::ToggleEngineFocusPreview()",CPP)
        self.assertIn('TEXT("TSTSS_GAMEPLAY_ENGINE_FOCUS_PREVIEW_ONLY")',CPP)

    def test_review_diagnostic_marks_unapproved_status(self):
        helper=self.helper()
        self.assertIn("REVIEW_ONLY bias=-6 sky_enabled=1 map_asset_unchanged=1",helper)

if __name__=="__main__":
    unittest.main()
