"""Source safety and construction checks; native visual review is separate."""
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] /
          "Source/ToSailTheStarrySky/Private/TSTSSHilltoniaReviewExtension.cpp").read_text(encoding="utf-8")

class SignReadability(unittest.TestCase):
    def test_sign_has_opaque_noncolliding_backing(self):
        sign = SOURCE.split("void WayfindingSign(", 1)[1].split("void TownSigns(", 1)[0]
        self.assertIn('TEXT("%s_Backboard")', sign)
        self.assertIn("Board->SetCollisionEnabled(ECollisionEnabled::NoCollision)", sign)
        self.assertIn("Board->SetMaterial(0, BoardMaterial)", sign)

    def test_sign_has_separate_centered_opposite_faces(self):
        sign = SOURCE.split("void WayfindingSign(", 1)[1].split("void TownSigns(", 1)[0]
        self.assertIn("Location + FaceNormal * 10.f", sign)
        self.assertIn("Location - FaceNormal * 10.f", sign)
        self.assertIn("Yaw + 180.f", sign)
        self.assertIn("EHTA_Center", sign)
        self.assertIn("ECollisionEnabled::NoCollision", sign)

if __name__ == "__main__":
    unittest.main()
