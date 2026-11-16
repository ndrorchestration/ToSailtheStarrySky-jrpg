"""Synthetic parser mutations and source-wiring checks, NOT native PIE evidence."""
from __future__ import annotations
import datetime as dt
import math
import unittest
from pathlib import Path

from verify_engine_focus_reach_pie_log import verify,EXPECTED_E
from test_engine_focus_gameplay_preview import check_contract

ROOT=Path(__file__).resolve().parents[1]
CPP=(ROOT/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
HEADER=(ROOT/"Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf-8")
INPUT=(ROOT/"Config/DefaultInput.ini").read_text(encoding="utf-8")

def fixture():
    time=dt.datetime(2026,11,15,2,0,0)
    lines=[]
    def line(offset,msg):
        when=time+dt.timedelta(seconds=offset)
        stamp=when.strftime("%Y.%m.%d-%H.%M.%S")
        ms=when.microsecond//1000
        lines.append(f"[{stamp}:{ms:03d}][007]LogTemp: Display: {msg}")
    for i,name in enumerate(EXPECTED_E):
        line(i+1,f"TSTSS_PIE_REVIEW_E_ACCEPT target=TSTSS_PRELUDE_REVIEW_{name} pawn_hit_cm=220.0")
    line(9.0,"TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination=/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors")
    line(9.1,"TSTSS_FIRSTWAKE_REVIEW_SCENE_ARRIVAL_STORY_RESTORED_NO_RECRUITMENT beat=3")
    line(10.0,"TSTSS_FIRSTWAKE_OPTICAL_REVIEW_QUEUED_NO_STORY_ADVANCE destination=/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview")
    line(10.1,"TSTSS_FIRSTWAKE_REVIEW_SCENE_ARRIVAL_STORY_RESTORED_NO_RECRUITMENT beat=3")
    d=math.dist((-620.,-120.,95.),(-250.,-250.,270.))
    line(12.0,("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RANGE "
        "pawn_x=-620.0 pawn_y=-120.0 pawn_z=95.0 "
        "gauge_x=-250.0 gauge_y=-250.0 gauge_z=270.0 "
        f"distance_cm={d:.1f} limit_cm=450.0 gauge_count=1 sky_count=1"))
    focus=math.sqrt(380**2+650**2+260**2)
    line(12.1,(f"TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_ENTER focus_cm={focus:.1f} "
         f"gauge_distance_cm={d:.1f} preview_limit_s=4.0 "
         "move_ignored=1 look_ignored=1"))
    line(16.11,("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RESTORE_AUDIT "
         "elapsed_s=4.010 move_ignored=0 look_ignored=0 "
         "immediate_view_pawn=0 controller_valid=1"))
    line(16.12,"TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RESTORE")
    return "\n".join(lines)+"\n"

class FocusTelemetryReviewTests(unittest.TestCase):
    def test_valid_log_contract_descriptive_not_natively_proven(self):
        r=verify(fixture())
        self.assertEqual(r["status"],
            "PIE_LOG_CONTRACT_PASS_STILL_NEEDS_REAL_INPUT_AND_NATIVE_CUSTODY")
        self.assertEqual(r["seven_earned_interactions"],True)
        self.assertLess(r["distance_cm"],450.)
        self.assertFalse(r["view_target_blend_completed_after_0_3s"])
        self.assertFalse(r["actual_physical_wasd_independently_observed"])
        self.assertFalse(r["actual_gpu_bokeh_approved"])
        self.assertFalse(r["creator_visual_approved"])
        self.assertFalse(r["canonical_story_save_mutated"])

    def test_real_source_contract_remains_unchanged(self):
        check_contract(CPP,HEADER,INPUT)
        self.assertEqual(CPP.count("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RANGE"),1)
        self.assertEqual(CPP.count("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RESTORE_AUDIT"),1)
        section=CPP.split("void ATSTSSExplorerCharacter::ToggleEngineFocusPreview()",1)[1].split("void ATSTSSExplorerCharacter::VerifyEngineFocusPreview()",1)[0]
        self.assertLess(section.index("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RANGE"),
                        section.index("if (InstrumentCount != 1 || AtmosphereCount != 1"))
        self.assertLess(section.index("if (InstrumentCount != 1 || AtmosphereCount != 1"),
                        section.index("Coordinator->TryPublishMoment("))
        self.assertIn("FVector::Dist(GetActorLocation(), Instrument->GetActorLocation()) > 450.f",section)
        self.assertIn("World->WorldType != EWorldType::PIE",section)
        self.assertIn("denied=instrument_or_range",section)
        self.assertIn("denied=story_weather_access",section)
        self.assertIn("denied=cinematic_owner",section)
        self.assertIn("denied=controller_or_input_owner",section)
        self.assertNotIn("SetActorLocation(",section)
        self.assertNotIn("SaveFirstWake(",section)

    def test_negative_log_mutations_all_rejected(self):
        baseline=fixture()
        mutations={
          "wrong_E_objective":("TSTSS_PRELUDE_REVIEW_LiftStation","TSTSS_PRELUDE_REVIEW_SpareStation"),
          "wrong_story_beat":("ARRIVAL_STORY_RESTORED_NO_RECRUITMENT beat=3","ARRIVAL_STORY_RESTORED_NO_RECRUITMENT beat=2"),
          "wrong_early_map":("VS02_AureateInteriors","VS03_FirstWakeSky"),
          "wrong_optical_map":("M_EnginePresentationReview","VS02_AureateInteriors"),
          "no_gauge_owner":("gauge_count=1","gauge_count=0"),
          "two_atmosphere_owners":("sky_count=1","sky_count=2"),
          "moved_gauge":("gauge_x=-250.0","gauge_x=-100.0"),
          "far_player":("pawn_x=-620.0","pawn_x=-1080.0"),
          "spoofed_log_distance":("distance_cm=429.4","distance_cm=120.0"),
          "different_lens":("focus_cm=796.6","focus_cm=420.0"),
          "decreased_time_limit":("preview_limit_s=4.0","preview_limit_s=2.0"),
          "ignored_move_not_set":("move_ignored=1","move_ignored=0"),
          "ignored_look_not_set":("look_ignored=1","look_ignored=0"),
          "did_not_restore_move":("elapsed_s=4.010 move_ignored=0","elapsed_s=4.010 move_ignored=1"),
          "did_not_restore_look":("move_ignored=0 look_ignored=0","move_ignored=0 look_ignored=1"),
          "controller_lost":("controller_valid=1","controller_valid=0"),
          "elapsed_spoofed":("elapsed_s=4.010","elapsed_s=2.100"),
          "forged_fake_millis":("[2026.11.15-02.00.12:100]","[2026.11.15-02.00.99:100]"),
        }
        for name,(old,new) in mutations.items():
            with self.subTest(name=name):
                # Only apply if the exact synthetic field is present.
                self.assertIn(old,baseline)
                mutated=baseline.replace(old,new,1)
                with self.assertRaises(ValueError):
                    verify(mutated)

    def test_missing_duplicate_or_out_of_order_events_rejected(self):
        baseline=fixture()
        lines=baseline.splitlines()
        indices=[i for i,x in enumerate(lines) if
                 "TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_ENTER" in x]
        self.assertEqual(len(indices),1)
        scenarios={
            "missing_entry":"\n".join(x for x in lines if "TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_ENTER" not in x),
            "duplicate_entry":baseline+lines[indices[0]]+"\n",
            "duplicate_E":baseline+lines[0]+"\n",
            "missing_optical":baseline.replace(
                "TSTSS_FIRSTWAKE_OPTICAL_REVIEW_QUEUED_NO_STORY_ADVANCE",
                "UNKNOWN_REVIEW_TRAVEL",1),
            "entry_before_range":"\n".join(
                x.replace("02.00.12:100","02.00.11:000")
                if "TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_ENTER" in x else x
                for x in lines),
            "no_restore":baseline.replace("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RESTORE_AUDIT",
                                           "UNKNOWN_RESTORE",1),
        }
        for name,value in scenarios.items():
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    verify(value)

    def test_timestamp_wall_time_does_not_accept_premature_manual_cancel(self):
        baseline=fixture()
        self.assertIn("02.00.16:110",baseline)
        self.assertIn("02.00.16:120",baseline)
        fast=(baseline.replace("02.00.16:110","02.00.13:210")
                      .replace("02.00.16:120","02.00.13:220")
                      .replace("elapsed_s=4.010","elapsed_s=1.110"))
        with self.assertRaisesRegex(ValueError,"four-second auto return"):
            verify(fast)

if __name__=="__main__":
    unittest.main()
