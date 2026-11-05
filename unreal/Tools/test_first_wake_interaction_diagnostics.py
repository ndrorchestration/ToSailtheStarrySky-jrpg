"""Source regression guard for opt-in First Wake E-interaction diagnostics.

This verifies the instrumentation's source contract, not native C++ compilation,
actual camera ray collision, story progression, or Play In Editor acceptance.
"""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "Source" /
          "ToSailTheStarrySky" / "Private" / "TSTSSExplorerCharacter.cpp")


class TestFirstWakeInteractionDiagnostics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")

    def test_default_off_and_no_shipping_log(self):
        self.assertRegex(
            self.text,
            r"#if !UE_BUILD_SHIPPING\s+//[^\n]*\n//[^\n]*\nTAutoConsoleVariable<int32>\s+"
            r"CVarFirstWakeInteractionTrace\(\s*TEXT\("
            r'"tstss.FirstWake.InteractionTrace"\),\s*0')
        self.assertRegex(
            self.text, r"#if !UE_BUILD_SHIPPING[\s\S]*?"
            r"if \(CVarFirstWakeInteractionTrace.GetValueOnGameThread\(\) == 0\)"
            r"[\s\S]*?UE_LOG\(LogTemp, Display")

    def test_outcomes_distinguish_camera_reach_and_story(self):
        for code in (
            "trace_disabled", "visibility_miss",
            "visibility_hit_non_milestone", "outside_pawn_reach",
            "story_or_repeat_rejected", "accepted",
        ):
            with self.subTest(code=code):
                self.assertIn(f'TEXT("{code}")', self.text)
        for field in (
            "pawn=", "camera=", "forward=", "hit_actor=", "hit_component=",
            "impact=", "pawn_hit_cm=", "max_reach_cm=",
            "beat_before=", "beat_after=",
        ):
            self.assertIn(field, self.text)

    def test_original_interaction_guards_remain(self):
        self.assertEqual(
            1, self.text.count("LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Query)"))
        self.assertEqual(
            1, self.text.count("TSTSSInteractionReach::IsInsidePlayerReach("))
        self.assertEqual(1, self.text.count("Milestone->TryActivate(FirstWakeState)"))
        self.assertIn(
            "TSTSSInteractionReach::GetCameraTraceLength(Start, PawnLocation, InteractionDistance)",
            self.text)
        self.assertNotIn("SetCollisionEnabled(ECollisionEnabled::NoCollision)", self.text)


if __name__ == "__main__":
    unittest.main()
