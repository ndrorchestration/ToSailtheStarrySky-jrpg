"""Source-level contract for bounded, opt-in native PIE water telemetry.

This does not generate actual engine physics readings. The separate D3D11
native test must collect and independently validate log samples at this SHA.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/"Source/ToSailTheStarrySky/Private/TSTSSWaterContactAdapter.cpp").read_text(encoding="utf-8")
HEADER=(ROOT/"Source/ToSailTheStarrySky/Public/TSTSSWaterContactAdapter.h").read_text(encoding="utf-8")
GATE=(ROOT/"Source/ToSailTheStarrySky/Public/TSTSSWaterLandingGate.h").read_text(encoding="utf-8")

class WaterFrameTelemetryContract(unittest.TestCase):
    def test_default_off_console_gate_excludes_non_editor(self):
        self.assertIn("#if WITH_EDITOR\n#include \"HAL/IConsoleManager.h\"", SOURCE)
        self.assertIn('TEXT("tstss.FirstWake.WaterTrace"), 0,', SOURCE)
        self.assertEqual(SOURCE.count("CVarTstssWaterReviewTrace.GetValueOnGameThread() != 0"),2)
        self.assertIn("TraceWorld->WorldType == EWorldType::PIE", SOURCE)
        self.assertEqual(SOURCE.count("bArmPrototypePhysicsOnLaunch"),3)

    def test_prelaunch_dry_snapshots_are_bounded_and_after_reset(self):
        self.assertIn("TSTSS_WATER_REVIEW_SAMPLE phase=DRY", SOURCE)
        self.assertIn("DryReviewTraceSamples < 30", SOURCE)
        self.assertIn("Now - LastDryReviewTraceWorldSeconds >= 1.f", SOURCE)
        dry=SOURCE.split('if (!bAfterLaunch)\n            {',1)[1]
        self.assertLess(dry.index('Gate->GetStableContactSeconds()'), dry.index('return;'))
        self.assertIn("sim=%d hull_z_cm=%.3f stable_sec=%.4f", dry)

    def test_actual_frame_observations_follow_unchanged_physics_gate(self):
        self.assertEqual(SOURCE.count(
            "Gate->Observe(DeltaSeconds, bActualImmersion, VerticalSpeed, Story);"),1)
        self.assertLess(SOURCE.index(
            "Gate->Observe(DeltaSeconds, bActualImmersion, VerticalSpeed, Story);"),
            SOURCE.index("TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS"))
        for token in ("world_sec=%.4f", "dt=%.4f", "hull_z_cm=%.3f",
                      "water_surface_z_cm=%.3f","tagged_overlap=%d",
                      "immersed=%d","submersion=%.5f",
                      "vertical_speed_cm_s=%.3f","stable_sec=%.4f",
                      "beat_before=%d","beat_after=%d",
                      "restore_gen=%llu"):
            with self.subTest(token=token):
                self.assertIn(token,SOURCE)
        self.assertIn("PhysicalReviewTraceSamples < 6000",SOURCE)
        self.assertIn("GetStableContactSeconds()",GATE)

    def test_no_story_or_save_or_collision_mutations_in_logger(self):
        suffix=SOURCE.split("TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS",1)[1]
        for forbidden in ("AdvanceTo(", "AdvanceWaterBeat(", "SaveGameToSlot(",
                          "SetCollisionEnabled(", "SetSimulatePhysics(", "SetWorldTransform("):
            self.assertNotIn(forbidden,suffix)
        self.assertIn("#if WITH_EDITOR", HEADER)
        self.assertIn("PhysicalReviewTraceSamples = 0",HEADER)

if __name__=="__main__":
    unittest.main()
