"""Source geometry for the forest-town-dock review route; not a native walk."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSHilltoniaReviewExtension.cpp").read_text(encoding="utf-8")
HUD = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSFirstWakeReviewHUD.cpp").read_text(encoding="utf-8")

class ForestTownDock(unittest.TestCase):
    def test_straight_west_road_overlaps_town_and_reaches_greenwood(self):
        self.assertIn("for (int32 Step = 0; Step < 11; ++Step)", CPP)
        self.assertIn("Place(WestRoad, -9650.f - 600.f * Step, RoadCenterY, -30.f", CPP)
        old_road_west = -9050 - 310
        next_road_east = -9650 + 310
        forest_road_west = -9650 - 10 * 600 - 310
        self.assertGreater(next_road_east, old_road_west)
        self.assertLessEqual(forest_road_west, -15500)

    def test_land_buffer_and_western_land_support_new_route(self):
        self.assertIn("Place(CoastalBuffer, -7000.f, 3250.f, -90.f, 70.f, 37.f, 1.6f)", CPP)
        self.assertIn("Place(WesternGround, -14000.f, -1300.f, -90.f, 80.f, 70.f, 1.6f)", CPP)
        self.assertGreater(3250 - 1850, 0)
        self.assertLess(3250 - 1850, 1600)
        self.assertLessEqual(-14000 - 4000, -15960)
        self.assertGreater(-14000 + 4000, -10500)
        self.assertEqual(-90 + 1.6 * 50, -10)

    def test_village_is_moved_inland_and_greenwood_has_clear_corridor(self):
        self.assertIn("for (const float X : {-5750.f, -6950.f, -9200.f})", CPP)
        self.assertIn('TEXT("HilltoniaWestForestTrunks")', CPP)
        self.assertIn("const float Y = Side * (1050.f + Row * 650.f)", CPP)
        self.assertGreater(1050 - 27.5, 390 + 35)

    def test_hud_directs_west_to_greenwood_and_east_to_harbor(self):
        self.assertIn('GREENWOOD  |  EAST: HILLTONIA / HARBOR', HUD)
        self.assertIn('WEST: GREENWOOD / EAST: SQUARE', HUD)
        self.assertIn('Position.X >= -16200.f', HUD)

if __name__ == "__main__":
    unittest.main()
