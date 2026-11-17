"""Engine-free regression checks for shipboard Reserve and Signoff approach.

Do not conflate this conservative layout witness with native Unreal PIE.
"""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_engine_room_forecastle_corridor import (
    AUTHORING, MANIFEST, PLAYER, verify, witness,
)

AUTH = AUTHORING.read_text(encoding="utf-8")
SRC = PLAYER.read_text(encoding="utf-8")
LAYOUT = json.loads(MANIFEST.read_text(encoding="utf-8"))


class ShipboardForecastleClearance(unittest.TestCase):
    def test_current_route_is_bounded_and_review_only(self):
        result = verify()
        self.assertEqual(result["station_count"], 4)
        self.assertEqual(result["route_sample_count"], 260)
        self.assertGreaterEqual(result["min_raised_collision_margin_cm"], 35)
        self.assertGreater(result["min_deck_edge_margin_cm"], 100)
        self.assertFalse(result["engagement_verified_in_unreal"])
        self.assertFalse(result["enclosed_engine_room_established"])
        self.assertLess(max(result["witness_e_distances_cm"].values()), 100)

    def test_original_signoff_in_forecastle_fails_closed(self):
        bad = copy.deepcopy(LAYOUT)
        bad["stations"][-1]["location_cm"] = [970, -90, 140]
        altered = SRC.replace("FVector(520.f, 130.f, 140.f)",
                              "FVector(970.f, -90.f, 140.f)")
        with self.assertRaisesRegex(RuntimeError, "EngineeringApproval buried"):
            witness(AUTH, altered, bad)

    def test_original_reserve_in_forecastle_fails_closed(self):
        bad = copy.deepcopy(LAYOUT)
        bad["stations"][2]["location_cm"] = [700, -90, 140]
        altered = SRC.replace("FVector(570.f, -180.f, 140.f)",
                              "FVector(700.f, -90.f, 140.f)")
        with self.assertRaisesRegex(RuntimeError, "ReserveStation buried"):
            witness(AUTH, altered, bad)

    def test_source_manifest_divergence_is_not_allowed(self):
        bad = copy.deepcopy(LAYOUT)
        bad["stations"][-1]["location_cm"][0] += 10
        with self.assertRaisesRegex(RuntimeError, "source/manifest marker drift"):
            witness(AUTH, SRC, bad)

    def test_route_cannot_cut_across_forecastle(self):
        bad = copy.deepcopy(LAYOUT)
        bad["forecastle_route_source_audit"]["approach_waypoints_cm"][3] = [750, -90]
        with self.assertRaisesRegex(RuntimeError, "clips raised Forecastle"):
            witness(AUTH, SRC, bad)

    def test_route_cannot_leave_walkable_deck(self):
        bad = copy.deepcopy(LAYOUT)
        bad["forecastle_route_source_audit"]["approach_waypoints_cm"][2] = [250, -490]
        with self.assertRaisesRegex(RuntimeError, "falls off main deck"):
            witness(AUTH, SRC, bad)

    def test_false_native_or_production_claim_is_rejected(self):
        bad = copy.deepcopy(LAYOUT)
        bad["forecastle_route_source_audit"]["status"] = "NATIVE_PIE_PASS"
        with self.assertRaisesRegex(RuntimeError, "misleading verification claim"):
            witness(AUTH, SRC, bad)
        bad = copy.deepcopy(LAYOUT)
        bad["starbourne_unlocked"] = True
        with self.assertRaisesRegex(RuntimeError, "prohibited authorization"):
            witness(AUTH, SRC, bad)

    def test_unapproved_solid_inventory_cannot_be_silently_ignored(self):
        altered = AUTH.replace(
            'prop("Forecastle", "Cube", (950, 0, 75), (6, 8, 1.2), "timber", True)',
            'prop("Forecastle", "Cube", (950, 0, 75), (6, 8, 1.2), "timber", True)\n'
            '        prop("NewBulkhead", "Cube", (330, 0, 100), (1, 2, 2), "stone", True)')
        with self.assertRaisesRegex(RuntimeError, "unexpected authored solid inventory"):
            witness(altered, SRC, LAYOUT)


if __name__ == "__main__":
    unittest.main()
