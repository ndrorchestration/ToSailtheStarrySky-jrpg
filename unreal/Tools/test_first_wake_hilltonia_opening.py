"""The Hilltonia review must separate reading, accepting and the waypoint."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
INK = (ROOT / "Config/DefaultInput.ini").read_text(encoding="utf-8")

def method(name, next_name):
    return CPP.split("ATSTSSExplorerCharacter::" + name + "(", 1)[1].split(
        "ATSTSSExplorerCharacter::" + next_name + "(", 1)[0]

class HilltoniaOpeningTests(unittest.TestCase):
    def test_read_and_decline_leave_the_authoritative_beat_untouched(self):
        read = method("Interact", "ShowObjectiveReview")
        board = read.split("if (IsHilltoniaFlyerHit(Hit))", 1)[1].split(
            "if (ATSTSSMilestoneActor* Milestone", 1)[0]
        self.assertIn("IsInsidePlayerReach(", board)
        self.assertIn("bHilltoniaFlyerRead = true", board)
        self.assertIn("return;", board)
        self.assertNotIn("AdvanceTo(", board)
        self.assertNotIn("AdvanceTo(", method("DeclineHilltoniaFlyer", "GetHilltoniaCaptainWaypoint"))

    def test_acceptance_rechecks_active_prompt_and_waypoint_uses_the_story_beat(self):
        accept = method("AcceptHilltoniaFlyer", "DeclineHilltoniaFlyer")
        self.assertLess(accept.index("!IsHilltoniaFlyerOpen()"),
                        accept.index("AdvanceTo(ETSTSSFirstWakeBeat::FlyerDiscovered)"))
        opened = method("IsHilltoniaFlyerOpen", "AcceptHilltoniaFlyer")
        self.assertIn("GetRestoreGeneration() == HilltoniaFlyerGeneration", opened)
        self.assertIn("IsInsidePlayerReach(", opened)
        waypoint = method("GetHilltoniaCaptainWaypoint", "SetupPlayerInputComponent")
        self.assertIn("!FirstWakeState->HasStarted()", waypoint)
        self.assertIn("GetCurrentBeat() != ETSTSSFirstWakeBeat::FlyerDiscovered", waypoint)
        self.assertIn("HilltoniaCaptain->GetActorLocation()", waypoint)
        self.assertIn('ActionName="AcceptHilltoniaFlyer",Key=Enter', INK)
        self.assertIn('ActionName="DeclineHilltoniaFlyer",Key=BackSpace', INK)

    def test_failed_spawn_cannot_retire_the_legacy_flyer(self):
        start = method("StartHilltoniaOpening", "IsHilltoniaFlyerHit")
        self.assertLess(start.index("!HasSupportedReviewFooting("),
                        start.index("bHilltoniaOpeningActive = true"))
        self.assertLess(start.index("!TeleportTo("),
                        start.index("OldFlyer->SetActorEnableCollision(false)"))

if __name__ == "__main__":
    unittest.main()
