"""Check the civic preview against the expanded Hilltonia layout, not UE runtime."""
from pathlib import Path
import math
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
    "Source/ToSailTheStarrySky/Private/TSTSSHilltoniaReviewExtension.cpp").read_text(encoding="utf-8")

def coordinate(name):
    match = re.search(r"constexpr float " + name + r" = (-?[0-9.]+)f;", SOURCE)
    if not match:
        raise AssertionError("missing " + name)
    return float(match.group(1))

def distance_to_box(x, y, bx, by, hx, hy):
    return math.hypot(max(abs(x-bx)-hx, 0), max(abs(y-by)-hy, 0))

def building_boxes():
    # Read the current review geometry, so a later town move fails safely.
    xs = re.search(r"for \(const float X : \{([^}]+)\}\)", SOURCE)
    ys = re.search(r"for \(const float Y : \{([^}]+)\}\)", SOURCE)
    home = re.search(r"Place\(Buildings, X, Y, 158\.f, ([\d.]+)f, ([\d.]+)f", SOURCE)
    hall = re.search(r"Place\(Buildings, (-?[\d.]+)f, (-?[\d.]+)f, 190\.f, ([\d.]+)f, ([\d.]+)f", SOURCE)
    if not all((xs, ys, home, hall)):
        raise AssertionError("cannot read current building layout")
    parse = lambda s: [float(v.strip().rstrip("f")) for v in s.split(",")]
    hx, hy = (float(v)*50 for v in home.groups())
    boxes = [(x,y,hx,hy) for x in parse(xs.group(1)) for y in parse(ys.group(1))]
    bx,by,sx,sy = map(float,hall.groups())
    return boxes + [(bx,by,sx*50,sy*50)]

class CivicIntegration(unittest.TestCase):
    def test_fountain_and_notice_are_present_but_do_not_advance_story(self):
        for name in ("HilltoniaRoundStoneFountain", "HilltoniaFountainDecorativeWater",
                     "HilltoniaPostingBoardPanel", "HilltoniaPostingFlyerPreview"):
            self.assertIn(name, SOURCE)
        for action in ("AdvanceTo(", "InspectStation(", "SaveGameToSlot("):
            self.assertNotIn(action, SOURCE)

    def test_fountain_clears_hall_houses_and_road(self):
        x, y = coordinate("FountainX"), coordinate("FountainY")
        self.assertGreaterEqual(y - 160 - 240, 75)
        for bx, by, hx, hy in building_boxes():
            self.assertGreaterEqual(distance_to_box(x,y,bx,by,hx,hy) - 160, 75)

    def test_older_fountain_location_would_overlap_the_moved_house(self):
        clearance = min(distance_to_box(-7200, 600, *box) - 160
                        for box in building_boxes())
        self.assertLess(clearance, 0)

    def test_board_clears_buildings_road_and_fountain(self):
        x, y = coordinate("BoardX"), coordinate("BoardY")
        fx, fy = coordinate("FountainX"), coordinate("FountainY")
        self.assertGreaterEqual(y - 12 - 240, 100)
        for bx, by, hx, hy in building_boxes():
            self.assertGreaterEqual(distance_to_box(x,y,bx,by,hx,hy) - 128, 50)
        self.assertGreaterEqual(math.hypot(x-fx,y-fy) - 160 - 128, 75)

if __name__ == "__main__":
    unittest.main()
