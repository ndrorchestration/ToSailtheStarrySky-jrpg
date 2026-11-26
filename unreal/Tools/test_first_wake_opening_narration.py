"""Engine-free source contract; native Sequencer playback and visual QA remain separate."""
import re
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "Source" / "ToSailTheStarrySky"
CUES = (SOURCE / "Private/TSTSSFirstWakeOpeningCues.h").read_text(encoding="utf-8")
WIDGET = (SOURCE / "Private/TSTSSOpeningReviewWidget.cpp").read_text(encoding="utf-8")
HEADER = (SOURCE / "Public/TSTSSOpeningReviewWidget.h").read_text(encoding="utf-8")
BUILD = (SOURCE / "ToSailTheStarrySky.Build.cs").read_text(encoding="utf-8")
ROWS = re.findall(r'\{(\d+(?:\.\d+)?)(?:f), TEXT\("([^"]*)"\), TEXT\("([^"]*)"\), (true|false)\}', CUES)

class FirstWakeOpeningContract(unittest.TestCase):
    def test_cue_clock(self):
        self.assertEqual(len(ROWS), 12)
        starts = [float(row[0]) for row in ROWS]
        self.assertEqual(starts[0], 0)
        self.assertTrue(all(a < b for a, b in zip(starts, starts[1:])))
        self.assertLess(starts[-1], 86)

    def test_exact_creator_line_and_dialogue(self):
        last_thought = "Sometimes, all that's required is a road, a little curiosity, and believing in yourself... even if you're the only one that does."
        spoken = [i for i, row in enumerate(ROWS) if row[3] == "true"]
        self.assertEqual(spoken, [9, 10])
        self.assertEqual(ROWS[spoken[0]-1][2], last_thought)
        self.assertIn("frequency", ROWS[spoken[0]][2])
        self.assertIn("Discover Hilltonia", ROWS[-1][2])

    def test_opt_in_and_single_map_handoff(self):
        self.assertIn('#if !UE_BUILD_SHIPPING', WIDGET)
        self.assertIn('TSTSSFirstWakeNarrationReview', WIDGET)
        self.assertEqual(WIDGET.count('UGameplayStatics::OpenLevel('), 1)
        self.assertIn('FirstWake_PreludeInteraction_V5_VisualReview', WIDGET)
        self.assertIn('if (!FPackageName::DoesPackageExist(PreludeMap))', WIDGET)
        self.assertIn('Controller->SetInputMode(FInputModeGameOnly())', WIDGET)

    def test_native_sequence_and_clock(self):
        self.assertIn('ULevelSequencePlayer::CreateLevelSequencePlayer', WIDGET)
        self.assertIn('GetCurrentTime().AsSeconds()', WIDGET)
        self.assertIn('GetDuration().AsSeconds()', WIDGET)
        self.assertIn('GetStartTime().AsSeconds()', WIDGET)
        self.assertIn('reason=early_end', WIDGET)
        self.assertIn('Opening storyboard', WIDGET)
        self.assertIn('"LevelSequence"', BUILD)
        self.assertIn('"MovieScene"', BUILD)

    def test_skip_and_cleanup(self):
        self.assertIn('Skip->OnClicked.AddDynamic(this, &UTSTSSOpeningReviewWidget::FinishOpening)', WIDGET)
        self.assertIn('bOpeningCompleted = true;', WIDGET)
        self.assertIn('OnFinished.RemoveDynamic', WIDGET)
        self.assertIn('OpeningActor->Destroy()', WIDGET)
        self.assertIn('void UTSTSSOpeningReviewWidget::NativeDestruct()\n{\n    StopOpening();', WIDGET)
        self.assertIn('void OnOpeningSequenceFinished();', HEADER)

if __name__ == "__main__":
    unittest.main()
