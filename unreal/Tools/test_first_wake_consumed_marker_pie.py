"""Source-only guard for nonblocking *consumed* PIE review markers.

These tests do not assert native collision correctness; that needs a real
Unreal Editor run and input evidence bound to the exact new commit.
"""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "Source/ToSailTheStarrySky/Private/TSTSSMilestoneActor.cpp")


class ConsumedReviewMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.method = cls.source.split("bool ATSTSSMilestoneActor::TryActivate(", 1)[1].split(
            "\n#if WITH_EDITOR\nvoid ATSTSSMilestoneActor::ReconcileReviewCollisionAfterRestore(", 1
        )[0]

    def test_already_authorized_story_state_remains_the_only_gate(self):
        s = self.method
        self.assertEqual(s.count("State->InspectStation(InspectionStation)"), 1)
        self.assertEqual(s.count("State->AdvanceTo(Milestone)"), 1)
        self.assertEqual(s.count("if (!bSucceeded) return false;"), 1)
        self.assertEqual(s.count("OnMilestoneActivated();"), 1)
        self.assertLess(s.index("if (!bSucceeded) return false;"),
                        s.index("SetCollisionResponseToChannel("))
        self.assertLess(s.index("OnMilestoneActivated();"),
                        s.index("SetCollisionResponseToChannel("))

    def test_only_editor_pie_named_review_actors_can_become_nonblocking(self):
        s = self.method
        self.assertEqual(s.count("#if WITH_EDITOR"), 1)
        self.assertEqual(s.count("#endif"), 1)
        self.assertIn("World->WorldType == EWorldType::PIE", s)
        self.assertIn('GetActorLabel().StartsWith(TEXT("TSTSS_PRELUDE_REVIEW_"))', s)
        self.assertIn('GetActorLabel().StartsWith(TEXT("TSTSS_SPLASHDOWN_GREYBOX_"))', s)
        # Both known review namespaces are under the same exact PIE-only gate.
        self.assertRegex(s, r'World->WorldType == EWorldType::PIE &&\s*\(')
        self.assertIn("IsValid(InteractionMesh)", s)
        self.assertLess(s.index("#if WITH_EDITOR"),
                        s.index("SetCollisionResponseToChannel("))
        self.assertLess(s.index("IsValid(InteractionMesh)"),
                        s.index("SetCollisionResponseToChannel("))

    def test_camera_visibility_and_physical_pawn_passage_only(self):
        s = self.method
        self.assertEqual(s.count(
            "SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore)"), 1)
        self.assertEqual(s.count(
            "SetCollisionResponseToChannel(ECC_Pawn, ECR_Ignore)"), 1)
        self.assertNotIn("SetCollisionEnabled(ECollisionEnabled::NoCollision)",s)
        self.assertNotIn("SetActorLocation(", s)
        self.assertNotIn("SetActorRotation(", s)
        self.assertNotIn("SaveGameToSlot(", s)

    def test_initial_marker_still_blocks_visibility_until_accepted(self):
        constructor = self.source.split(
            "ATSTSSMilestoneActor::ATSTSSMilestoneActor()",1)[1].split(
            "bool ATSTSSMilestoneActor::TryActivate(",1)[0]
        self.assertIn(
            "SetCollisionResponseToChannel(ECC_Visibility, ECR_Block)",
            constructor)
        self.assertNotIn("SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore)", constructor)
        self.assertIn("SetCollisionResponseToAllChannels(ECR_Ignore)", constructor)


if __name__ == "__main__":
    unittest.main()
