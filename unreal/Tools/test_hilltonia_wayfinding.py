"""Source QA for noninteractive Hilltonia waypoint signs.

These tests verify source placement and non-collision, not native 3D text
orientation or readability. Real D3D screenshots remain required.
"""
from pathlib import Path
import math
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT / "Source/ToSailTheStarrySky/Private/"
       "TSTSSHilltoniaReviewExtension.cpp").read_text(encoding="utf-8")
PATTERN = re.compile(
    r'WayfindingSign\(Owner, Root, TEXT\("([^"]+)"\),\s*'
    r'TEXT\("([^"]+)"\),\s*'
    r'FVector\((-?\d+(?:\.\d*)?)f,\s*(-?\d+(?:\.\d*)?)f,\s*'
    r'(-?\d+(?:\.\d*)?)f\),\s*(-?\d+(?:\.\d*)?)f\);'
)


def signs():
    return {
        name: (label, float(x), float(y), float(z), float(yaw))
        for name, label, x, y, z, yaw in PATTERN.findall(CPP)
    }


def distance_to_road(x, y):
    def dist_to_rectangle(cx, cy, half_x, half_y):
        return math.hypot(max(abs(x - cx) - half_x, 0.0),
                          max(abs(y - cy) - half_y, 0.0))
    roads = [
        dist_to_rectangle(-3650 - i * 600, -150, 310, 390)
        for i in range(10)
    ]
    roads += [
        dist_to_rectangle(-7350, -620 - i * 500, 180, 260)
        for i in range(6)
    ]
    return min(roads)


class HilltoniaWayfindingContract(unittest.TestCase):
    def test_four_unambiguous_town_and_forest_signs(self):
        observed = signs()
        self.assertEqual(len(observed), 4)
        self.assertEqual(set(observed), {
            "HilltoniaLandwardEntrySign",
            "HilltoniaWoodlandTurnoffSign",
            "HilltoniaForestEdgeReturnSign",
            "HilltoniaTownWestReturnSign",
        })
        self.assertEqual(
            observed["HilltoniaLandwardEntrySign"][0],
            "HILLTONIA  |  WOODLAND ROAD"
        )
        self.assertIn("FOREST TRAIL", observed["HilltoniaWoodlandTurnoffSign"][0])
        self.assertIn("RETURN TO HILLTONIA",
                      observed["HilltoniaForestEdgeReturnSign"][0])
        self.assertIn("RETURN TO HARBOR",
                      observed["HilltoniaTownWestReturnSign"][0])

    def test_wayfinders_outside_capsule_supported_walkway(self):
        # A 35-cm-radius walking capsule must not collide with signboards
        # situated on the side verge of a 620cm/520cm road segment.
        for name, (_, x, y, z, yaw) in signs().items():
            with self.subTest(name=name):
                self.assertGreater(
                    distance_to_road(x, y), 35.0,
                    "Decorative sign too close to the collision route"
                )
                self.assertGreater(z, 180.0)
                self.assertIn(yaw, (0.0, 90.0))

    def test_signs_have_no_collision_or_quest_authority(self):
        self.assertIn(
            "Text->SetCollisionEnabled(ECollisionEnabled::NoCollision);", CPP
        )
        self.assertIn("Text->SetMobility(EComponentMobility::Movable);", CPP)
        self.assertIn("TownSigns(Owner, Root);", CPP)
        self.assertIn("wayfinding_signs=4", CPP)
        for prohibited in (
            "SpawnActor<ATSTSSMilestoneActor>",
            "AdvanceTo(", "OpenLevel(", "SaveGameToSlot(",
            "TeleportTo(", "CreateWidget(",
        ):
            self.assertNotIn(prohibited, CPP)

    def test_distinct_turnoff_near_branch_and_far_end_near_street_end(self):
        s = signs()
        _, tx, ty, _, _ = s["HilltoniaWoodlandTurnoffSign"]
        self.assertLess(abs(tx + 7350.0), 380.0)
        self.assertLess(abs(ty + 620.0), 120.0)
        _, fx, fy, _, _ = s["HilltoniaForestEdgeReturnSign"]
        self.assertLess(abs(fx + 7350.0), 380.0)
        self.assertLess(abs(fy + 3120.0), 250.0)
        _, ex, _, _, _ = s["HilltoniaTownWestReturnSign"]
        self.assertLess(abs(ex + 9050.0), 370.0)

    def test_no_saving_new_map_assets(self):
        for forbidden in ("SavePackage(", "SaveCurrentLevel(",
                          "EditorLoadingAndSavingUtils", "Modify(", "MarkPackageDirty("):
            self.assertNotIn(forbidden, CPP)
        self.assertIn("saved_map_unchanged=1", CPP)


if __name__ == "__main__":
    unittest.main()
