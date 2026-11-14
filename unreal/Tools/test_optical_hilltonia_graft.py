"""Source gate: the #835 camera graft must not erase #836 review route and safety owners."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp"
HEADER = ROOT / "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h"
INPUT = ROOT / "Config/DefaultInput.ini"

class OpticalHilltoniaGraftTests(unittest.TestCase):
    def test_review_navigation_footing_and_fall_recovery_remain(self):
        body = CPP.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for marker in ("TSTSSHilltoniaRouteTelemetry", "HasSupportedReviewFooting",
                       "TSTSSReviewGrounding::ShouldRecover", "TSTSS_REVIEW_FALL_RETURN",
                       "LastHilltoniaProbeWaypoint", "ReviewContinue",
                       "SaveReviewContinueBinding", "GetReviewShipMode"):
            self.assertTrue(marker in body or marker in header, marker)
    def test_optical_does_not_replace_e_or_change_guarded_controls(self):
        body = CPP.read_text(encoding="utf-8")
        inp = INPUT.read_text(encoding="utf-8")
        for name, key in (("Interact", "E"), ("EngineFocusPreview", "C"),
                          ("PIEReviewQuickSave", "F6"), ("ReviewContinue", "F7"),
                          ("QuickLoad", "F9"), ("ReviewObjective", "J"),
                          ("ReviewShoreTravel", "K")):
            self.assertEqual(inp.count(f'ActionName="{name}",Key={key}'), 1)
        self.assertEqual(body.count('BindAction(TEXT("EngineFocusPreview"), IE_Pressed'), 1)
        self.assertIn("if (Milestone->TryActivate(FirstWakeState))", body)
        self.assertIn("RestoreEngineFocusPreview();", body)
        self.assertNotIn("    EngineFocusPreviewIgnoredMove = true;", body)
        self.assertNotIn("    EngineFocusPreviewIgnoredLook = true;", body)

if __name__ == "__main__":
    unittest.main()
