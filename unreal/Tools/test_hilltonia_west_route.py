"""Synthetic falsification for the west-road review; not native walking proof."""
import math
import unittest
from pathlib import Path
from check_hilltonia_runtime_route import assess, RouteNotEstablished, WAYPOINTS
from test_hilltonia_runtime_route import record

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSHilltoniaReviewExtension.cpp").read_text(encoding="utf-8")
EXPECTED_WEST = ("DOCK_TOWN_SEAM", "TOWN_MAIN_STREET", "VILLAGE_SQUARE",
                 "TOWN_WEST_END", "WEST_ROAD", "GREENWOOD_WEST", "WEST_ROAD",
                 "TOWN_WEST_END", "VILLAGE_SQUARE", "TOWN_MAIN_STREET", "DOCK_TOWN_SEAM")

def west_fixture():
    lines = []
    t = 2.
    for index, name in enumerate(EXPECTED_WEST):
        x, y, _ = WAYPOINTS[name]
        lines.append(record("WAYPOINT", name, t, x, y))
        if index == len(EXPECTED_WEST) - 1:
            break
        nx, ny, _ = WAYPOINTS[EXPECTED_WEST[index + 1]]
        for step in range(1, 6):
            f = step / 6.
            sx, sy = x + (nx-x)*f, y + (ny-y)*f
            label = next((key for key, (wx, wy, r) in WAYPOINTS.items()
                          if math.hypot(sx-wx, sy-wy) <= r + .15), "UNMARKED")
            lines.append(record("SAMPLE", label, t+step*2., sx, sy))
        t += 12.
    return lines

class WestRoute(unittest.TestCase):
    def test_complete_west_round_trip(self):
        result = assess("\n".join(west_fixture()), route="west")
        self.assertEqual(result["waypoint_events"], 11)
        self.assertGreater(result["measured_distance_cm"], 20000.)
        self.assertFalse(result["creator_visual_approval"])

    def test_missing_greenwood_turnaround_fails(self):
        lines = [x for x in west_fixture() if "name=GREENWOOD_WEST" not in x]
        with self.assertRaises(RouteNotEstablished):
            assess("\n".join(lines), route="west")

    def test_unsupported_west_sample_fails(self):
        lines = west_fixture()
        index = next(i for i, x in enumerate(lines)
                     if "ROUTE_SAMPLE" in x and "x=-13" in x)
        lines[index] = lines[index].replace("footing=1", "footing=0")
        with self.assertRaisesRegex(RouteNotEstablished, "Unsupported or airborne"):
            assess("\n".join(lines), route="west")

    def test_forest_understory_is_noncolliding(self):
        self.assertIn('TEXT("HilltoniaWestUnderstory")', SOURCE)
        self.assertRegex(SOURCE, r'TEXT\("HilltoniaWestUnderstory"\),\s*Sphere,\s*Canopy,\s*false\)')
        self.assertIn("Place(WestUnderstory,", SOURCE)

if __name__ == "__main__":
    unittest.main()
