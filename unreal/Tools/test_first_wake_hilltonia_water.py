"""Synthetic mutation suite for creator-route proxy-water log parser.

All fixtures are invented strings to exercise fail-closed logic, NEVER proof
of an executed native Unreal session. PR #849's old seven-pier-E fixture
is deliberately incompatible with this scope.
"""
import unittest
from pathlib import Path
from verify_first_wake_hilltonia_water import (
    analyze, FLYER_READ, FLYER_ACCEPT, E_TARGETS, MAPS, TRACE_CVAR,
)

SOURCE=(Path(__file__).resolve().parents[1]/
        "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text("utf-8")

def fixture(post_frames=22):
    rows=["LogPlayLevel: PIE: Server logged in", TRACE_CVAR,
          FLYER_READ, FLYER_ACCEPT]
    def action(label):
        rows.append(f"TSTSS_PIE_REVIEW_E_ACCEPT target={label} pawn_hit_cm=210.0")
    def travel(path):
        rows.append("TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination="+path)
        rows.append("LogLoad: LoadMap: "+path)
    for name in E_TARGETS[:2]:
        action(name)
    travel(MAPS[0])
    for name in E_TARGETS[2:]:
        action(name)
    travel(MAPS[1])
    travel(MAPS[2])
    def phys(t,before,after,stable,*,immerse=True,speed=4.0):
        overlap="1" if immerse else "0"
        bottom=249.0 if immerse else 460.0
        submersion=.54 if immerse else 0.
        rows.append(
            "LogTemp: Display: TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS "
            f"world_sec={t:.4f} dt=0.1000 hull_z_cm=309.000 "
            f"hull_bottom_z_cm={bottom:.3f} water_surface_z_cm=320.000 "
            f"tagged_overlap={overlap} immersed={overlap} "
            f"submersion={submersion:.5f} vertical_speed_cm_s={speed:.3f} "
            f"stable_sec={stable:.4f} beat_before={before} beat_after={after} "
            "sim=1 restore_gen=1")
    phys(.1,4,4,0,immerse=False,speed=0)
    phys(.2,4,5,0,speed=-530)
    for i in range(22):
        phys(.4+i*.1,5,5,i*.1)
    phys(2.6,5,6,2.2)
    for i in range(post_frames):
        phys(2.7+i*.1,6,6,0,speed=.1)
    return "\n".join(rows)+"\n"

class CreatorHilltoniaWaterLog(unittest.TestCase):
    def test_synthetic_good_fixture_is_log_contract_only(self):
        result=analyze(fixture())
        self.assertEqual(result["status"],
                         "HILLTONIA_LOG_CONTRACT_PASS_NATIVE_NOT_AUTHENTICATED")
        self.assertEqual(result["earned_E_count"],6)
        self.assertEqual(result["source_verifier_provenance"],"PR849_PHYSICS_ONLY")
        self.assertTrue(result["shipboard_signoff_in_order"])
        self.assertTrue(result["flyer_read_explicitly_accepted"])
        self.assertGreaterEqual(result["direct_preflotation_stable_s"],2)
        self.assertGreaterEqual(result["direct_postflotation_stable_s"],2)
        for key in ("native_player_flight_verified", "actual_hull_ship_mesh_approved",
                    "lyra_recruitment_verified","human_keyboard_playthrough",
                    "cinematic_visual_approved","disk_restart_verified"):
            self.assertFalse(result[key])

    def test_source_signatures_match_creator_route(self):
        self.assertIn(FLYER_READ,SOURCE)
        self.assertIn(FLYER_ACCEPT,SOURCE)
        for key in E_TARGETS[2:]:
            self.assertIn(key.split("TSTSS_ENGINEROOM_REVIEW_")[1], SOURCE)
        self.assertIn("StageEarnedEngineRoomReview(",SOURCE)
        self.assertIn("FirstWakeState->AdvanceTo(ETSTSSFirstWakeBeat::FlyerDiscovered)",SOURCE)
        self.assertIn("TEXT(\"VS02_AureateInteriors\")",SOURCE)

    def test_read_must_be_followed_by_explicit_accept(self):
        raw=fixture()
        with self.assertRaises(ValueError):
            analyze(raw.replace(FLYER_ACCEPT,"NO_QUEST_AUTHORIZED",1))
        with self.assertRaisesRegex(ValueError,"chronology"):
            analyze(raw.replace(FLYER_READ+"\n"+FLYER_ACCEPT,
                                FLYER_ACCEPT+"\n"+FLYER_READ,1))

    def test_old_dockside_seven_E_sequence_is_rejected(self):
        raw=fixture().replace(E_TARGETS[2],
            "TSTSS_PRELUDE_REVIEW_LiftStation",1)
        with self.assertRaisesRegex(ValueError,"new route requires"):
            analyze(raw)
        raw=fixture().replace(E_TARGETS[5],
            "TSTSS_PRELUDE_REVIEW_EngineeringApproval",1)
        with self.assertRaisesRegex(ValueError,"new route requires"):
            analyze(raw)

    def test_old_coastal_fuel_shanty_not_immediate_canon(self):
        raw=fixture()+"TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination=/Game/TSTSS/Review/VerticalSlice/VS05_DenithFuelShanty\n"
        with self.assertRaisesRegex(ValueError,"legacy coastal shanty"):
            analyze(raw)

    def test_early_shipboard_action_blocked(self):
        raw=fixture()
        action=next(line for line in raw.splitlines()
                    if "TSTSS_PIE_REVIEW_E_ACCEPT target="+E_TARGETS[2] in line)
        boarding="LogLoad: LoadMap: "+MAPS[0]
        self.assertIn(boarding+"\n"+action, raw)
        with self.assertRaisesRegex(ValueError,"chronology"):
            analyze(raw.replace(boarding+"\n"+action,
                                action+"\n"+boarding,1))

    def test_missing_pie_or_trace_fails(self):
        raw=fixture()
        with self.assertRaises(ValueError):
            analyze(raw.replace("PIE: Server logged in","No player login",1))
        with self.assertRaises(ValueError):
            analyze(raw.replace(TRACE_CVAR,'tstss.FirstWake.WaterTrace = "0"',1))

    def test_stable_sea_physics_is_required(self):
        raw=fixture()
        boundary=next(x for x in raw.splitlines()
                      if "beat_before=5 beat_after=6" in x)
        with self.assertRaises(ValueError):
            analyze(raw.replace(boundary,boundary.replace("immersed=1","immersed=0"),1))
        with self.assertRaises(ValueError):
            analyze(raw.replace(boundary,boundary.replace("stable_sec=2.2000","stable_sec=0.1000"),1))
        with self.assertRaisesRegex(ValueError,"postflotation"):
            analyze(fixture(post_frames=5))

    def test_early_lyra_grant_rejected(self):
        with self.assertRaisesRegex(ValueError,"premature Lyra"):
            analyze(fixture()+"TSTSS_LYRA_RECRUITED\n")

if __name__=="__main__":
    unittest.main()
