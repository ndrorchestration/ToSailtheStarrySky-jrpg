"""Synthetic mutation tests for the V5-only native sea physics log verifier."""
import unittest

from verify_first_wake_v5_native_water import analyze, E_TARGETS, MAPS, TRACE_CVAR


def fixture(post_frames=22):
    events = ["LogPlayLevel: PIE: Server logged in", TRACE_CVAR]
    events += [f"TSTSS_PIE_REVIEW_E_ACCEPT target={target} pawn_hit_cm=210.0"
               for target in E_TARGETS]

    def travel(map_name):
        events.append(
            "TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT "
            f"destination={map_name}")
        events.append(f"LogLoad: LoadMap: {map_name}")

    for map_name in MAPS[:3]:
        travel(map_name)

    def phys(t, before, after, stable, *, immerse=True, speed=4.0):
        overlap = "1" if immerse else "0"
        bottom = 249.0 if immerse else 460.0
        submersion = .54 if immerse else 0.
        events.append(
            "LogTemp: Display: TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS "
            f"world_sec={t:.4f} dt=0.1000 hull_z_cm=309.000 "
            f"hull_bottom_z_cm={bottom:.3f} water_surface_z_cm=320.000 "
            f"tagged_overlap={overlap} immersed={overlap} "
            f"submersion={submersion:.5f} vertical_speed_cm_s={speed:.3f} "
            f"stable_sec={stable:.4f} beat_before={before} beat_after={after} "
            "sim=1 restore_gen=1")

    phys(.1, 4, 4, 0, immerse=False, speed=0)
    phys(.2, 4, 5, 0, speed=-530)
    for i in range(22):
        phys(.4+i*.1, 5, 5, i*.1)
    phys(2.6, 5, 6, 2.2)
    for i in range(post_frames):
        phys(2.7+i*.1, 6, 6, 0., speed=.1)
    travel(MAPS[3])
    return "\n".join(events)+"\n"


class MultiMapV5NativeWaterContract(unittest.TestCase):
    def test_valid_source_fixture_only_not_physical_evidence(self):
        result = analyze(fixture())
        self.assertEqual(result["status"],
                         "DIRECT_NATIVE_V5_MULTIMAP_PROXY_FLOATATION_PASS")
        self.assertEqual(result["earned_E_count"], 7)
        self.assertGreaterEqual(result["direct_preflotation_stable_s"], 2.0)
        self.assertGreaterEqual(result["direct_postflotation_stable_s"], 2.0)
        for key in ("native_player_flight_verified", "cinematic_visual_approved",
                    "disk_restart_verified", "human_keyboard_playthrough",
                    "actual_hull_ship_mesh_approved"):
            self.assertFalse(result[key])

    def test_missing_or_reordered_player_progression_fails(self):
        baseline=fixture()
        wrong=baseline.replace(E_TARGETS[3], "TSTSS_PRELUDE_REVIEW_FAKE", 1)
        with self.assertRaisesRegex(ValueError, "seven earned"):
            analyze(wrong)
        with self.assertRaisesRegex(ValueError, "K travel"):
            analyze(baseline.replace(MAPS[2], "/Game/FAKE", 1))

    def test_no_pie_or_trace_cvar_fails(self):
        baseline=fixture()
        for broken in (baseline.replace("PIE: Server logged in", "PIE: not logged in"),
                       baseline.replace(TRACE_CVAR, "tstss.FirstWake.WaterTrace = \"0\"")):
            with self.assertRaises(ValueError):
                analyze(broken)

    def test_teleportation_or_unimmersed_transition_fails(self):
        baseline=fixture()
        row=next(x for x in baseline.splitlines() if "beat_before=5 beat_after=6" in x)
        with self.assertRaises(ValueError):
            analyze(baseline.replace(row, row.replace("immersed=1", "immersed=0"), 1))
        with self.assertRaises(ValueError):
            analyze(baseline.replace(row,
                row.replace("vertical_speed_cm_s=4.000","vertical_speed_cm_s=80.000"), 1))

    def test_stable_counter_not_sufficient_without_measured_window(self):
        baseline=fixture()
        row=next(x for x in baseline.splitlines() if "world_sec=1.5000" in x)
        with self.assertRaises(ValueError):
            analyze(baseline.replace(row,
                row.replace("vertical_speed_cm_s=4.000","vertical_speed_cm_s=30.000"), 1))
        transition=next(x for x in baseline.splitlines()
                        if "beat_before=5 beat_after=6" in x)
        with self.assertRaises(ValueError):
            analyze(baseline.replace(transition,
                transition.replace("stable_sec=2.2000","stable_sec=1.0000"), 1))

    def test_post_transition_directly_observed_two_seconds(self):
        with self.assertRaisesRegex(ValueError, "postflotation"):
            analyze(fixture(post_frames=7))

    def test_duplicate_flota_or_mixed_dry_stage_rejected(self):
        baseline=fixture()
        row=next(x for x in baseline.splitlines() if "beat_before=5 beat_after=6" in x)
        with self.assertRaises(ValueError):
            analyze(baseline.replace(row, row+"\n"+row, 1))
        with self.assertRaisesRegex(ValueError, "mixed V3"):
            analyze(baseline+"\n"+row.replace("phase=PHYSICS","phase=DRY")+"\n")

    def test_out_of_order_coastal_K_rejected(self):
        baseline=fixture()
        q=("TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT "
           "destination="+MAPS[3]+"\nLogLoad: LoadMap: "+MAPS[3]+"\n")
        self.assertIn(q,baseline)
        wrong=baseline.replace(q,"",1).replace(
            "LogTemp: Display: TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS",
            q+"LogTemp: Display: TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS",1)
        with self.assertRaisesRegex(ValueError, "chronology"):
            analyze(wrong)


if __name__ == "__main__":
    unittest.main()
