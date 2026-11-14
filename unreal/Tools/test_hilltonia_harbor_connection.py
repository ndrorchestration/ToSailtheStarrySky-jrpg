"""Hilltonia harbor-to-town spatial and authority contracts (engine-free).

These checks validate authoring intent and geometry only. They do not prove
Unreal collision, native movement, tree appearance, route accessibility,
winter biome transitions or creator visual acceptance.
"""
from pathlib import Path
import math
import re
import unittest

BASE = Path(__file__).resolve().parents[1]
CPP = (BASE / "Source/ToSailTheStarrySky/Private/TSTSSHilltoniaReviewExtension.cpp").read_text(
    encoding="utf-8")
HEADER = (BASE / "Source/ToSailTheStarrySky/Private/TSTSSHilltoniaReviewExtension.h").read_text(
    encoding="utf-8")
EXPLORER = (BASE / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(
    encoding="utf-8")
PRELUDE = (BASE / "Tools/build_first_wake_prelude_interaction.py").read_text(
    encoding="utf-8")

def const(name):
    value = re.search(
        rf"constexpr float {re.escape(name)} = (-?[\d.]+)f;", CPP)
    if not value:
        raise ValueError("Missing scoped float: " + name)
    return float(value.group(1))


class HilltoniaReviewContract(unittest.TestCase):
    def test_geography_named_and_mid_northern_biome(self):
        for token in (
            "TownLabel = TEXT(\"TSTSS_V5_REVIEW_HILLTONIA_TOWN\")",
            "world_north_latitude_provisional=1",
            "town=Hilltonia",
            "deciduous_trees=%d",
            "north-temperate woodland",
            "HILLTONIA  |  WOODLAND ROAD",
            "WOODLAND ROAD",
        ):
            self.assertIn(token, CPP)
        for prohibited in ("DenithFuelCache", "StarbourneUnlocked",
                           "AureateWakeUnlocked", "LyraRecruited"):
            self.assertNotIn(prohibited, CPP)

    def test_landward_continuous_collision_road_overlaps_only_dock_end(self):
        begin = const("RoadFirstX")
        end = const("RoadLastX")
        step = const("RoadStep")
        y = const("RoadCenterY")
        self.assertEqual((begin, end, step, y), (-3650, -9050, 600, -150))
        self.assertEqual(round((begin - end) / step), 9)
        self.assertEqual(round(begin - 310), -3960)
        self.assertGreater(begin + 310, -3750)  # original dock overlaps new road
        self.assertLess(begin + 310, -2200 - 300)  # cannot reach flyer E marker
        self.assertLessEqual(step, 620)  # 620cm sections touch/overlap
        self.assertLess(abs(y) + 35, 390)  # full capsule supported from dock
        self.assertIn("X >= RoadLastX; X -= RoadStep", CPP)
        self.assertIn("6.2f, 7.8f, .6f", CPP)
        self.assertIn("X, RoadCenterY, -30.f", CPP)
        self.assertIn("WorldStatic", CPP)
        self.assertIn("ECollisionEnabled::QueryAndPhysics", CPP)
        self.assertIn("SetCollisionResponseToAllChannels", CPP)
        self.assertIn("SetGenerateOverlapEvents(false)", CPP)
        self.assertIn("GetActorLabel() == TownLabel", CPP)

    def test_forest_turnoff_is_contiguous_and_keeps_tree_trunks_clear(self):
        self.assertIn("Step < 6", CPP)
        self.assertIn("-7350.f, -620.f - 500.f * Step", CPP)
        self.assertIn("3.6f, 5.2f, .6f", CPP)
        # Side lane centers 500 cm apart, width 520; the first overlaps road
        # extent Y[-540,240] by 180cm. Last ends at Y=-3380.
        self.assertLess(500, 520)
        self.assertGreater(-620 + 260, -540)
        self.assertEqual(-620 - 5 * 500 - 260, -3380)
        self.assertIn("FMath::Abs(X + 7350.f) < 420.f", CPP)
        self.assertIn("TreeTrunks", CPP)
        self.assertIn("TreeCrowns", CPP)
        self.assertIn("RollingHills", CPP)

    def test_town_is_on_connected_land_not_floating_over_harbor_ocean(self):
        self.assertIn('HilltoniaLandwardGround', CPP)
        self.assertIn('land_ground_sections=2', CPP)
        self.assertIn('Cube, Canopy, true', CPP)
        self.assertIn('Place(Ground, -7000.f, -1300.f, -90.f, 70.f, 58.f, 1.6f)', CPP)
        self.assertIn('Place(Ground, -7350.f, -4950.f, -140.f, 63.f, 20.f, 2.6f)', CPP)
        # Ground upper surfaces meet at -10 cm, 10 cm below the road top.
        for z, scale_z in ((-90, 1.6), (-140, 2.6)):
            self.assertAlmostEqual(z + scale_z * 50, -10)
        main_x_min, main_x_max = -7000 - 3500, -7000 + 3500
        main_y_min, main_y_max = -1300 - 2900, -1300 + 2900
        self.assertLess(main_x_min, const("RoadLastX") - 310)
        self.assertGreater(main_x_max, -3750)  # overlaps the original quay
        self.assertGreater(main_y_max, 900 + 270)  # houses on seaward side
        self.assertLess(main_y_min, -3120 - 260)  # covers woodland spur
        ridge_y_min, ridge_y_max = -4950 - 1000, -4950 + 1000
        self.assertLess(ridge_y_min, main_y_min)
        self.assertGreater(ridge_y_max, main_y_min)  # continuous ground

    def test_existing_seven_milestones_are_untouched(self):
        self.assertIn("ReviewStop(\"FlyerDiscovery\", -2200, 0", PRELUDE)
        self.assertIn("ReviewStop(\"EngineeringApproval\", 1175, 0", PRELUDE)
        self.assertIn('TEXT("FirstWake_PreludeInteraction_V5_VisualReview")', CPP)
        self.assertIn('StartsWith(TEXT("/Game/TSTSS/Review/"))', CPP)
        self.assertIn("World->GetNetMode() != NM_Standalone", CPP)
        self.assertIn("TSTSSHilltoniaReviewExtension::Apply(", EXPLORER)
        self.assertIn("if (bDockReady)", EXPLORER)
        for forbidden in ("AdvanceTo(", "TryActivate(", "SaveGameToSlot(",
                          "OpenLevel(", "SetActorLocation(", "TeleportTo(",
                          "SpawnActor<ATSTSSMilestoneActor>", "SetSimulatePhysics("):
            self.assertNotIn(forbidden, CPP)

    def test_real_map_and_foliage_palette_gate(self):
        self.assertIn('"/Engine/BasicShapes/Cube.Cube"', CPP)
        self.assertIn('"/Engine/BasicShapes/Cylinder.Cylinder"', CPP)
        self.assertIn('"/Engine/BasicShapes/Sphere.Sphere"', CPP)
        self.assertIn('M_VS_Green.M_VS_Green', EXPLORER)
        self.assertTrue((BASE / "Content/TSTSS/Review/VerticalSlice/M_VS_Green.uasset").is_file())
        self.assertIn('IsValid(Canopy)', EXPLORER)
        self.assertIn('World, PBRLoaded[0], PBRLoaded[2], PBRLoaded[3], Canopy', EXPLORER)
        self.assertIn("Apply(UWorld* World", HEADER)

    def test_review_safety_includes_no_map_save(self):
        self.assertIn("#if WITH_EDITOR", CPP)
        self.assertIn("Owner->SetActorLabel(TownLabel)", CPP)
        self.assertIn("SetCollisionEnabled(", CPP)
        self.assertIn("ECollisionEnabled::NoCollision", CPP)
        self.assertIn("saved_map_unchanged=1", CPP)
        for forbidden in ("EditorLoadingAndSavingUtils", "SavePackage",
                          "SaveCurrentLevel", "SaveGameToSlot", "git checkout",
                          "Starbourne", "FloatationConfirmed"):
            self.assertNotIn(forbidden, CPP)


if __name__ == "__main__":
    unittest.main()
