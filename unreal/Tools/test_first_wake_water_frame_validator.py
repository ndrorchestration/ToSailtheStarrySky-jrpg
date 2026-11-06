"""Synthetic parser controls only; not actual Unreal physics verification."""
import unittest
import verify_first_wake_water_frame_trace as validator

def sample_log(gap_at=None, lose_immersion_at=None, have_dry=True, *,
               count=105, period=0.02, reported_dt=None, credit_first=False):
    lines=["PIE: Server logged in"]
    if have_dry:
        lines.append(
            "LogTemp: Display: TSTSS_WATER_REVIEW_SAMPLE phase=DRY "
            "world_sec=4.0000 started=0 beat=0 sim=0 hull_z_cm=500.000 "
            "stable_sec=0.0000 restore_gen=0")
    for i in range(count):
        t=20+(i+1)*period
        if gap_at is not None and i>=gap_at:
            t+=0.65
        stable=(i+1)*period if credit_first else i*period
        dt=period if reported_dt is None else reported_dt
        immersed=0 if i==lose_immersion_at else 1
        lines.append(
            "LogTemp: Display: TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS "
            f"world_sec={t:.4f} dt={dt:.4f} hull_z_cm=-20.000 "
            "hull_bottom_z_cm=-80.000 water_surface_z_cm=320.000 "
            f"tagged_overlap=1 immersed={immersed} submersion=0.55000 "
            f"vertical_speed_cm_s=5.000 stable_sec={stable:.4f} "
            f"beat_before=5 beat_after={6 if i==count-1 else 5} "
            "sim=1 restore_gen=0")
    return "\n".join(lines)

class FailClosedWaterFrameValidatorTest(unittest.TestCase):
    def test_contiguous_two_second_series_passes_only_as_synthetic(self):
        x=validator.analyze(sample_log())
        self.assertEqual(x["status"],"DIRECT_NATIVE_WATER_FLOTATION_TIMESERIES_PASS")
        self.assertGreaterEqual(x["window_seconds_elapsed_world"],2.0)
        self.assertGreaterEqual(x["window_seconds_sum_dt"],2.0)
        self.assertFalse(x["authorizes_cinematic_shot"])

    def test_eight_frames_cannot_credit_unwitnessed_first_delta(self):
        # The previous validator summed all eight dt values (=2.0s), even
        # though eight actual timestamps only span seven 0.25s intervals.
        old_gate_log = sample_log(count=8, period=0.25, credit_first=True)
        with self.assertRaisesRegex(ValueError, "incomplete or discontinuous"):
            validator.analyze(old_gate_log)

    def test_nine_real_observations_span_exactly_two_seconds(self):
        trace = sample_log(count=9, period=0.25)
        result = validator.analyze(trace)
        self.assertEqual(result["window_samples"], 9)
        self.assertEqual(result["window_seconds_elapsed_world"], 2.0)
        self.assertEqual(result["window_seconds_sum_dt"], 2.0)
        self.assertEqual(result["stable_seconds_at_transition"], 2.0)

    def test_clock_delta_disagreement_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "incomplete or discontinuous"):
            validator.analyze(sample_log(period=0.03, reported_dt=0.02))

    def test_native_counter_cannot_exceed_observed_window(self):
        trace = sample_log()
        self.assertIn("stable_sec=2.0800", trace)
        with self.assertRaisesRegex(ValueError, "native stable timer exceeds"):
            validator.analyze(trace.replace("stable_sec=2.0800",
                                            "stable_sec=2.5000"))

    def test_claimed_immersion_must_match_actual_hull_water_geometry(self):
        invalid = sample_log().replace("hull_bottom_z_cm=-80.000",
                                       "hull_bottom_z_cm=500.000")
        with self.assertRaisesRegex(ValueError, "incomplete or discontinuous"):
            validator.analyze(invalid)

    def test_nonfinite_physical_timestamp_rejected(self):
        trace = sample_log().replace("world_sec=22.1000", "world_sec=nan")
        with self.assertRaisesRegex(ValueError, "nonfinite physical"):
            validator.analyze(trace)

    def test_restore_generation_change_breaks_window(self):
        trace = sample_log()
        lines = trace.splitlines()
        for index in range(80, len(lines)):
            lines[index] = lines[index].replace("restore_gen=0", "restore_gen=1")
        with self.assertRaisesRegex(ValueError, "incomplete or discontinuous"):
            validator.analyze("\\n".join(lines))

    def test_missing_dry_negative_fails(self):
        with self.assertRaisesRegex(ValueError,"dry/physics bounded"):
            validator.analyze(sample_log(have_dry=False))

    def test_missing_immersion_breaks_window(self):
        with self.assertRaisesRegex(ValueError,"incomplete or discontinuous"):
            validator.analyze(sample_log(lose_immersion_at=70))

    def test_observation_gap_breaks_window(self):
        with self.assertRaisesRegex(ValueError,"incomplete or discontinuous"):
            validator.analyze(sample_log(gap_at=90))

    def test_no_native_pie_login_fails(self):
        with self.assertRaisesRegex(ValueError,"no real native PIE login"):
            validator.analyze(sample_log().replace("PIE: Server logged in",""))

    def test_no_frame_beat_transition_fails(self):
        with self.assertRaisesRegex(ValueError,"exactly one"):
            validator.analyze(sample_log().replace("beat_after=6","beat_after=5"))

if __name__=="__main__":
    unittest.main()
