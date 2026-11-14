"""Fail-closed source checks for native accepted-story change notifications."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
H = (ROOT / "Source/ToSailTheStarrySky/Public/TSTSSFirstWakeState.h")
S = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSFirstWakeState.cpp")
C = (ROOT / "Source/ToSailTheStarrySky/Private/Review/TSTSSPresentationCoordinatorSubsystem.cpp")
N = (ROOT / "Source/ToSailTheStarrySky/Private/Tests/TSTSSRulesTests.cpp")

class AcceptedChangeGraftTests(unittest.TestCase):
    def test_owner_notifies_and_optics_subscribes(self):
        h,s,c,n=[p.read_text(encoding="utf-8") for p in (H,S,C,N)]
        self.assertIn("DECLARE_MULTICAST_DELEGATE(FOnTSTSSFirstWakeAcceptedChange)", h)
        self.assertIn("FOnTSTSSFirstWakeAcceptedChange& OnAcceptedChange()", h)
        self.assertEqual(s.count("AcceptedChange.Broadcast();"), 7)
        self.assertIn("OnAcceptedChange().AddUObject(",c)
        self.assertIn("OnAcceptedChange().Remove(StoryChangedHandle)",c)
        self.assertIn("Only accepted changes notify",n)
        self.assertIn("Rejected restore preserved delegate count",n)
    def test_portable_water_fixture_owns_only_delegate_type(self):
        harness = (ROOT / "Tools/check_water_landing_rewind_compiled.py").read_text(encoding="utf-8")
        self.assertIn("#define DECLARE_MULTICAST_DELEGATE(Name)", harness)
        self.assertIn("void Broadcast() const {}", harness)
        self.assertIn("Callback delivery is verified in native UE tests", harness)

    def test_rejected_paths_still_return_without_notification(self):
        s=S.read_text(encoding="utf-8")
        self.assertIn("if (RequestedBeat != ETSTSSFirstWakeBeat::FlyerDiscovered)",s)
        self.assertIn("if (Current >= Last || Requested != Current + 1)",s)
        self.assertIn("if ((InspectionMask & Bit) != 0) return false;",s)
        self.assertIn("(!bWasStarted && (SavedBeat != ETSTSSFirstWakeBeat::FlyerDiscovered",s)

if __name__ == "__main__": unittest.main()
