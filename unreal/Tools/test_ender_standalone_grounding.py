"""Private review mesh grounding contract; native visual review remains required."""
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1]/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp"
CPP=P.read_text(encoding="utf8")
def section(s):
    return s.split("// Ground only the exact opt-in standalone private body.",1)[1].split("// Prior PR #812 visual bridge",1)[0]
def valid(s):
    try: b=section(s)
    except IndexError: return False
    return all(x in b for x in (
      "if (bPrivateStandalone", "Body->GetAttachParent() == GetCapsuleComponent()",
      "Body->GetRelativeLocation().IsNearlyZero(0.1f)",
      "Body->UpdateBounds();", "Body->Bounds.Origin.Z - Body->Bounds.BoxExtent.Z",
      "GetCapsuleComponent()->GetScaledCapsuleHalfHeight()",
      "FMath::IsFinite(Correction)", "HeightCm >= 140.f", "HeightCm <= 220.f",
      "Correction >= -120.f", "Correction <= -45.f",
      "Body->AddWorldOffset(FVector(0.f, 0.f, Correction))",
      "TSTSS_PRIVATE_ENDER_GROUNDING_REVIEW"))
class PrivateBodyGrounding(unittest.TestCase):
    def test_bounded_private_adjustment(self): self.assertTrue(valid(CPP))
    def test_safety_gate_mutations_are_rejected(self):
        for gate in ("if (bPrivateStandalone", "Body->GetRelativeLocation().IsNearlyZero(0.1f)",
                     "HeightCm >= 140.f", "Correction >= -120.f", "Correction <= -45.f"):
            with self.subTest(gate=gate):
                self.assertFalse(valid(CPP.replace(gate,"REMOVED_GATE",1)))
if __name__=="__main__": unittest.main()
