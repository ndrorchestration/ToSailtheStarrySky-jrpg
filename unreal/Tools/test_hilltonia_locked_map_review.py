"""Review-only Hilltonia geography: source checks, not native traversal."""
import re
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] /
          "Source/ToSailTheStarrySky/Private/TSTSSHilltoniaReviewExtension.cpp").read_text(encoding="utf-8")

class LockedMapReview(unittest.TestCase):
    def test_market_green_and_greenwood_are_named(self):
        self.assertIn('TEXT("THE GREEN  |  MARKET")', SOURCE)
        self.assertIn('TEXT("GREENWOOD  |  FOREST EDGE")', SOURCE)

    def test_backdrop_foliage_cannot_block_player_or_interactions(self):
        for name in ("HilltoniaBackdropTrunks", "HilltoniaBackdropCrowns",
                     "HilltoniaUnderstory"):
            self.assertRegex(SOURCE, r'TEXT\("' + name + r'"\),\s*\w+,\s*\w+,\s*false\)')

    def test_review_remains_scoped_to_existing_standalone_world(self):
        self.assertIn('World->GetNetMode() != NM_Standalone', SOURCE)
        self.assertIn('TEXT("FirstWake_PreludeInteraction_V5_VisualReview")', SOURCE)
        self.assertIn('#if WITH_EDITOR', SOURCE)

if __name__ == "__main__":
    unittest.main()
