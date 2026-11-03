"""First Wake V2 authored traversal footprint geometry checks (not UE or PIE).

This tests the actual review plan validation and rejects layouts in which
a marker falls off the collision floor or begins within E interaction reach.
No tracked .umap, actor, art, save slot, or installed engine is modified.
"""
from dataclasses import replace
import math
import unittest
from unittest.mock import patch

import build_first_wake_prelude_interaction as plan


class PreludeFootprintTests(unittest.TestCase):
    def test_current_plan_footprint_and_far_initial_flyer(self):
        report = plan.validate_plan()
        g = report["authoring_geometry_only"]
        self.assertEqual(g["floor_x_cm"], [-3750.0, 2550.0])
        self.assertEqual(g["floor_y_cm"], [-700.0, 700.0])
        self.assertEqual(g["floor_top_z_cm"], 0.0)
        self.assertEqual(g["spawn_to_flyer_nearest_xy_edge_cm"], 542.5)
        self.assertTrue(g["all_seven_marker_footprints_on_floor"])
        self.assertFalse(g["native_visibility_or_pie_tested"])

    def test_spawn_cannot_begin_on_flyer_within_300cm(self):
        with patch.object(plan, "PLAYER_SPAWN", (-2455.0, 0.0, 130.0)):
            with self.assertRaisesRegex(ValueError, "already within 300cm"):
                plan.validate_plan()

    def test_spawn_cannot_be_off_collision_floor(self):
        with patch.object(plan, "PLAYER_SPAWN", (-4000.0, 0.0, 130.0)):
            with self.assertRaisesRegex(ValueError, "outside traversal floor"):
                plan.validate_plan()

    def test_marker_cannot_leave_x_extent(self):
        old = plan.STOPS
        altered = tuple(replace(s, x=2530.0) if s.label == "EngineeringApproval" else s for s in old)
        with patch.object(plan, "STOPS", altered):
            with self.assertRaisesRegex(ValueError, "outside traversal floor"):
                plan.validate_plan()

    def test_marker_cannot_leave_y_extent(self):
        old = plan.STOPS
        altered = tuple(replace(s, y=730.0) if s.label == "LiftStation" else s for s in old)
        with patch.object(plan, "STOPS", altered):
            with self.assertRaisesRegex(ValueError, "outside traversal floor"):
                plan.validate_plan()

    def test_narrow_floor_cannot_claim_full_route(self):
        with patch.object(plan, "FLOOR_SCALE", (10.0, 14.0, 2.0)):
            with self.assertRaisesRegex(ValueError, "outside traversal floor"):
                plan.validate_plan()

    def test_floor_must_have_positive_size(self):
        with patch.object(plan, "FLOOR_SCALE", (63.0, -14.0, 2.0)):
            with self.assertRaisesRegex(ValueError, "must be positive"):
                plan.validate_plan()

    def test_floor_top_must_match_authored_height(self):
        with patch.object(plan, "FLOOR_LOCATION", (-600.0, 0.0, 200.0)):
            with self.assertRaisesRegex(ValueError, "floor top has drifted"):
                plan.validate_plan()

    def test_pawn_cannot_spawn_below_floor(self):
        with patch.object(plan, "PLAYER_SPAWN", (-2780.0, 0.0, -100.0)):
            with self.assertRaisesRegex(ValueError, "below the floor"):
                plan.validate_plan()

    def test_nonfinite_marker_coordinate_denied(self):
        old = plan.STOPS
        altered = tuple(replace(s, y=math.nan) if s.label == "PressureStation" else s for s in old)
        with patch.object(plan, "STOPS", altered):
            with self.assertRaisesRegex(ValueError, "Nonfinite"):
                plan.validate_plan()

    def test_nonfinite_start_denied(self):
        with patch.object(plan, "PLAYER_SPAWN", (-2780.0, math.inf, 130.0)):
            with self.assertRaisesRegex(ValueError, "Nonfinite"):
                plan.validate_plan()

    def test_no_early_activation_when_marker_widens(self):
        with patch.object(plan, "REVIEW_MARKER_HALF_WIDTH_CM", 320.0):
            with self.assertRaisesRegex(ValueError, "already within 300cm"):
                plan.validate_plan()

    def test_review_plan_never_claims_actual_player_collision_proof(self):
        g = plan.validate_spatial_review_plan()
        self.assertFalse(g["native_visibility_or_pie_tested"])
        self.assertEqual(set(g), {
            "floor_x_cm", "floor_y_cm", "floor_top_z_cm",
            "spawn_to_flyer_nearest_xy_edge_cm",
            "all_seven_marker_footprints_on_floor",
            "native_visibility_or_pie_tested",
        })


if __name__ == "__main__":
    unittest.main()
