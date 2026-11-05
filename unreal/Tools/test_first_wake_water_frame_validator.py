"""Synthetic parser controls only; not actual Unreal physics verification."""
import unittest
import verify_first_wake_water_frame_trace as validator

def sample_log(gap_at=None, lose_immersion_at=None, have_dry=True):
    lines=["PIE: Server logged in"]
    if have_dry:
        lines.append(
            "LogTemp: Display: TSTSS_WATER_REVIEW_SAMPLE phase=DRY "
            "world_sec=4.0000 started=0 beat=0 sim=0 hull_z_cm=500.000 "
            "stable_sec=0.0000 restore_gen=0")
    for i in range(105):
        t=20+(i+1)*0.02
        if gap_at is not None and i>=gap_at:
            t+=0.65
        stable=(i+1)*0.02
        immersed=0 if i==lose_immersion_at else 1
        lines.append(
            "LogTemp: Display: TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS "
            f"world_sec={t:.4f} dt=0.0200 hull_z_cm=-20.000 "
            "hull_bottom_z_cm=-80.000 water_surface_z_cm=320.000 "
            f"tagged_overlap=1 immersed={immersed} submersion=0.55000 "
            f"vertical_speed_cm_s=5.000 stable_sec={stable:.4f} "
            f"beat_before=5 beat_after={6 if i==104 else 5} "
            "sim=1 restore_gen=0")
    return "\n".join(lines)

class FailClosedWaterFrameValidatorTest(unittest.TestCase):
    def test_dry_sample_after_physics_does_not_prove_prelaunch(self):
        lines = sample_log().splitlines()
        lines.append(lines.pop(1))
        with self.assertRaises(ValueError):
            validator.analyze('\n'.join(lines))

    def test_nonfinite_hull_measurements_are_rejected(self):
        log = sample_log().replace('hull_z_cm=-20.000', 'hull_z_cm=nan')
        with self.assertRaises(ValueError):
            validator.analyze(log)

    def test_compressed_world_clock_cannot_prove_two_seconds(self):
        lines = sample_log().splitlines()
        index = 0
        for n, line in enumerate(lines):
            if 'phase=PHYSICS' in line:
                start = line.index('world_sec=') + len('world_sec=')
                end = line.index(' ', start)
                lines[n] = line[:start] + f'{20 + index * 0.001:.4f}' + line[end:]
                index += 1
        with self.assertRaises(ValueError):
            validator.analyze('\n'.join(lines))

    def test_contiguous_two_second_series_passes_only_as_synthetic(self):
        x=validator.analyze(sample_log())
        self.assertEqual(x["status"],"DIRECT_NATIVE_WATER_FLOTATION_TIMESERIES_PASS")
        self.assertGreaterEqual(x["window_seconds_sum_dt"],2.0)
        self.assertFalse(x["authorizes_cinematic_shot"])

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

