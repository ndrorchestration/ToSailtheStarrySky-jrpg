"""Synthetic negative tests; never presented as native gameplay evidence."""
import unittest
import verify_first_wake_postflotation_stability as v

def example(*, post=80, dry=True, login=True, cvar=True, mutate=None):
    lines=[]
    if login: lines.append("PIE: Server logged in")
    if cvar: lines.append('tstss.FirstWake.WaterTrace = "1"')
    if dry:
        lines.append("LogTemp: Display: TSTSS_WATER_REVIEW_SAMPLE phase=DRY "
                     "world_sec=0.0000 started=0 beat=0 sim=0 hull_z_cm=500.000 "
                     "stable_sec=0.0000 restore_gen=0")
    for index in range(71+post):
        sec=10+0.04*index
        if mutate == "gap" and index >= 88:
            sec += 0.6
        overlap=0 if mutate=="lost_water" and index==88 else 1
        speed=27 if (index<=20 or (mutate=="high_speed" and index==88)) else 4.0
        gen=1 if mutate=="restore_generation" and index==88 else 0
        dt=0.07 if mutate=="wrong_frame_dt" and index==88 else 0.04
        submerged=0 if mutate=="no_immersion" and index==88 else 1
        lower=350 if mutate=="above_surface" and index==88 else 249
        number=float("nan") if mutate=="nan_speed" and index==88 else speed
        beat_before=5 if index<=70 else 6
        beat_after=6 if index==70 else beat_before
        stable=2.0312 if index==70 else 0
        lines.append("LogTemp: Display: TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS "
                     f"world_sec={sec:.4f} dt={dt:.4f} hull_z_cm=309.000 "
                     f"hull_bottom_z_cm={lower:.3f} water_surface_z_cm=320.000 "
                     f"tagged_overlap={overlap} immersed={submerged} submersion=0.54500 "
                     f"vertical_speed_cm_s={number:.3f} stable_sec={stable:.4f} "
                     f"beat_before={beat_before} beat_after={beat_after} "
                     f"sim=1 restore_gen={gen}")
    lines += [f"LogTemp: Display: TSTSS_PIE_REVIEW_E_ACCEPT target={name} "
              "pawn_hit_cm=30.0 objective_after=Review" for name in v.EXPECTED]
    return "\n".join(lines)

class PostFlotationWitnessTest(unittest.TestCase):
    def test_direct_continuous_postflotation_two_seconds_passes_as_synthetic(self):
        result=v.analyze(example())
        self.assertEqual(result["status"],"DIRECT_NATIVE_POST_FLOTATION_TWO_SECONDS_PASS")
        self.assertEqual(result["pre_transition_exact_2s_status"],"HOLD_BELOW_TWO_SECONDS")
        self.assertGreaterEqual(result["post_transition_continuous_seconds"],2.0)
        self.assertFalse(result["authorizes_cinematic_landing"])

    def test_fail_if_not_native_session(self):
        with self.assertRaisesRegex(ValueError,"PIE player login"):
            v.analyze(example(login=False))

    def test_fail_if_review_trace_not_enabled(self):
        with self.assertRaisesRegex(ValueError,"CVar not confirmed"):
            v.analyze(example(cvar=False))

    def test_fail_if_no_actual_dry_prelaunch_negative(self):
        with self.assertRaisesRegex(ValueError,"prelaunch dry frame"):
            v.analyze(example(dry=False))

    def test_fail_if_postflotation_observation_shorter_than_two_seconds(self):
        with self.assertRaisesRegex(ValueError,"no continuous observed"):
            v.analyze(example(post=25))

    def test_fail_on_physics_gap(self):
        with self.assertRaisesRegex(ValueError,"no continuous observed"):
            v.analyze(example(mutate="gap"))

    def test_fail_on_lost_tagged_water(self):
        with self.assertRaisesRegex(ValueError,"no continuous observed"):
            v.analyze(example(mutate="lost_water"))

    def test_fail_on_unsafe_vertical_velocity(self):
        with self.assertRaisesRegex(ValueError,"no continuous observed"):
            v.analyze(example(mutate="high_speed"))

    def test_fail_on_restore_generation_mismatch(self):
        with self.assertRaisesRegex(ValueError,"no continuous observed"):
            v.analyze(example(mutate="restore_generation"))

    def test_fail_on_frame_dt_mismatch(self):
        with self.assertRaisesRegex(ValueError,"no continuous observed"):
            v.analyze(example(mutate="wrong_frame_dt"))

    def test_fail_if_hull_above_surface(self):
        with self.assertRaisesRegex(ValueError,"no continuous observed"):
            v.analyze(example(mutate="above_surface"))

    def test_fail_if_hull_immersion_false(self):
        with self.assertRaisesRegex(ValueError,"no continuous observed"):
            v.analyze(example(mutate="no_immersion"))

    def test_fail_if_nan_speed(self):
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            v.analyze(example(mutate="nan_speed"))

    def test_fail_when_player_milestone_route_missing(self):
        with self.assertRaisesRegex(ValueError,"ten ordered genuine"):
            v.analyze(example().replace("TSTSS_PRELUDE_REVIEW_IoniaHiring", "WRONG_MILESTONE"))

if __name__=="__main__":
    unittest.main()
