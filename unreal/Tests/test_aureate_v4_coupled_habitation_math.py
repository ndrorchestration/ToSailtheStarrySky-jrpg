"""Noncanonical rigid-parent geometry tests; not a physics/Unreal proof."""
import math
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Tools"))
import aureate_v4_coupled_habitation_math as pivot

class CoupledHabitationContract(unittest.TestCase):
    def args(self,form="Skybourne",degrees=20):
        return dict(form=form,pivot=[0,0,0],bridge=[120,0,50],
                    quarters=[0,20,20],axis=[0,1,0],degrees=degrees)

    def test_zero_rotation_does_not_shift_both(self):
        r=pivot.review_pose(**self.args(degrees=0))
        self.assertEqual(r["bridge_before_xyz_cm"],r["bridge_after_xyz_cm"])
        self.assertEqual(r["quarters_before_xyz_cm"],r["quarters_after_xyz_cm"])

    def test_quarter_turn_both_rotate_together(self):
        r=pivot.review_pose(**self.args(degrees=90))
        self.assertTrue(r["relative_distance_preserved"])
        self.assertAlmostEqual(r["bridge_after_xyz_cm"][2],-120,places=5)
        self.assertAlmostEqual(r["quarters_after_xyz_cm"][0],20,places=5)
        self.assertFalse(r["runtime_component_attached"])

    def test_all_three_ordinary_forms_only(self):
        for form in pivot.STATES:
            r=pivot.review_pose(**self.args(form=form))
            self.assertEqual(r["form"],form)
            self.assertFalse(r["source_pose_creator_approved"])

    def test_starbourne_runtime_form_is_not_admitted(self):
        for form in ("Starbourne","Orbiter","INVALID",""):
            with self.subTest(form=form):
                with self.assertRaisesRegex(ValueError,"no orbital"):
                    pivot.review_pose(**self.args(form=form))

    def test_nan_and_inf_angles_fail_closed(self):
        for angle in (float("nan"),float("inf"),-float("inf")):
            with self.assertRaisesRegex(ValueError,"nonfinite"):
                pivot.review_pose(**self.args(degrees=angle))

    def test_nonfinite_vectors_and_zero_axis_rejected(self):
        for vector in ([float("nan"),1,2],[1,float("inf"),2],[float("-inf"),1,2]):
            for field in ("pivot","bridge","quarters","axis"):
                kwargs=self.args()
                kwargs[field]=vector
                with self.assertRaisesRegex(ValueError,"nonfinite"):
                    pivot.review_pose(**kwargs)
        with self.assertRaisesRegex(ValueError,"zero"):
            pivot.review_pose(**{**self.args(),"axis":[0,0,0]})

    def test_review_bounded_one_turn_and_centimeter_space(self):
        for angle in (-361,361):
            with self.assertRaisesRegex(ValueError,"one turn"):
                pivot.review_pose(**self.args(degrees=angle))
        with self.assertRaisesRegex(ValueError,"bounded"):
            pivot.review_pose(**{**self.args(),"pivot":[2e6,0,0]})

    def test_reverse_rotation_restores_points(self):
        before=(150,-30,40)
        center=(12,5,-2)
        rotated=pivot.rotate_axis(before,center,(1,1,1),33)
        restored=pivot.rotate_axis(rotated,center,(1,1,1),-33)
        for a,b in zip(before,restored):
            self.assertAlmostEqual(a,b,places=8)

    def test_invariants_not_gameplay_or_physics_claims(self):
        r=pivot.review_pose(**self.args())
        self.assertFalse(r["continuous_swept_collision_verified"])
        self.assertFalse(r["pressure_envelope_verified"])
        self.assertFalse(r["starbourne_player_unlocked"])
        self.assertFalse(r["source_pose_creator_approved"])
        self.assertEqual(r["authority"],"COUPLED_HABITATION_GEOMETRY_REVIEW_ONLY")

if __name__=="__main__":unittest.main()
