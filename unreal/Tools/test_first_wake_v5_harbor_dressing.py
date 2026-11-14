"""Engine-free exact-source scope/geometry contracts for V5-only dock dressing.

Actual native Unreal compile and screenshot review are separate acceptance gates.
"""
from pathlib import Path
import re
import unittest

PROJECT = Path(__file__).resolve().parents[1]
CPP = (PROJECT / "Source/ToSailTheStarrySky/Private/TSTSSV5HarborReviewDressing.cpp"
       ).read_text(encoding="utf-8")
HEADER = (PROJECT / "Source/ToSailTheStarrySky/Private/TSTSSV5HarborReviewDressing.h"
          ).read_text(encoding="utf-8")
PAWN = (PROJECT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp"
        ).read_text(encoding="utf-8")
BASE = (PROJECT / "Tools/build_first_wake_prelude_interaction.py"
        ).read_text(encoding="utf-8")


class V5HarborDressingContract(unittest.TestCase):
    def test_runtime_only_map_gate_nonnetwork_review_world(self):
        for token in (
            "World->WorldType != EWorldType::PIE",
            "World->WorldType != EWorldType::Game",
            "World->GetNetMode() != NM_Standalone",
            'StartsWith(TEXT("/Game/TSTSS/Review/"))',
            'TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',
            "GetActorLabel() == DressingLabel",
        ):
            self.assertIn(token, CPP)
        self.assertIn("#if WITH_EDITOR", CPP)
        self.assertIn("No duplicate dressing", CPP)
        self.assertIn("Apply(UWorld* World", HEADER)

    def test_original_seven_interactions_remain_on_uncovered_center_line(self):
        # Material dressing cannot be treated as new collision authority.
        self.assertIn("constexpr int32 BoardColumns = 70;", CPP)
        self.assertIn("constexpr int32 BoardRows = 5;", CPP)
        self.assertIn("const float Y = -370.f + 185.f * Lane;", CPP)
        self.assertIn("const float X = -3000.f + 65.f * Column", CPP)
        self.assertIn("++DeckPlanks", CPP)
        self.assertIn('deck_planks=%d rail_posts=%d props=%d lights=%d', CPP)
        self.assertIn("FLOOR_LOCATION = (-600.0, 0.0, -100.0)", BASE)
        self.assertIn("FLOOR_SCALE = (63.0, 14.0, 2.0)", BASE)
        self.assertIn('ReviewStop("FlyerDiscovery", -2200, 0', BASE)
        self.assertIn('ReviewStop("EngineeringApproval", 1175, 0', BASE)
        self.assertIn("Side * 545.f", CPP)
        self.assertIn("Side * 525.f", CPP)
        self.assertNotIn('Owner->SetActorEnableCollision(true)', CPP)
        self.assertIn("Owner->SetActorEnableCollision(false)", CPP)
        self.assertIn("Component->SetCollisionEnabled(ECollisionEnabled::NoCollision)", CPP)
        self.assertIn("Component->SetCollisionResponseToAllChannels(ECR_Ignore)", CPP)
        self.assertIn("Component->SetGenerateOverlapEvents(false)", CPP)
        # Noninteractive dressing assets cannot hide E rays or block player.
        for forbidden in ("ECC_Visibility", "ECC_Pawn", "BlockAll",
                          "SetCollisionProfileName", "TryActivate(", "AdvanceTo(",
                          "InspectStation(", "TeleportTo(", "OpenLevel(",
                          "SaveGameToSlot(", "SaveCurrentLevel(", "save_map("):
            self.assertNotIn(forbidden, CPP)

    def test_reuses_true_native_materials_and_instancing_not_faux_textures(self):
        self.assertIn("UInstancedStaticMeshComponent", CPP)
        self.assertIn("Component->AddInstance(FTransform(", CPP)
        self.assertIn('TEXT("/Engine/BasicShapes/Cube.Cube")', CPP)
        self.assertIn('TEXT("/Engine/BasicShapes/Cylinder.Cylinder")', CPP)
        self.assertIn("DockDeckTimber", CPP)
        self.assertIn("QuayStoneEdges", CPP)
        self.assertIn("MooringBrassAndRails", CPP)
        self.assertIn("MerchantAwnings", CPP)
        self.assertIn("UPointLightComponent", CPP)
        self.assertIn("Light->SetIntensity(700.f)", CPP)
        self.assertIn("PracticalLights", CPP)
        self.assertIn("source_map_unchanged=1", CPP)
        self.assertIn("TSTSSV5HarborReviewDressing::Apply(", PAWN)
        self.assertRegex(PAWN, r"if \(bCompletePBRPack\)\s*\{\s*const bool bDockReady = TSTSSV5HarborReviewDressing::Apply")
        self.assertRegex(PAWN, r"if \(bDockReady\)\s*\{\s*UMaterialInterface\* Canopy")
        self.assertIn("PBRLoaded[0], PBRLoaded[2], PBRLoaded[3], PBRLoaded[4]", PAWN)

    def test_has_storehouse_pier_cargo_and_lamp_silhouettes(self):
        for token in (
            "(-3200, 650, 350)",
            "Mooring hardware, cargo",
            "MerchantAwnings",
            "ReviewLantern_%d",
            "Storehouse volume exists",
            "DeckPlanks",
            "RailPosts",
            "Props",
        ):
            self.assertIn(token, CPP)
        # All created visual actors share one owner; no actor per plank.
        self.assertEqual(CPP.count("World->SpawnActor<AActor>("), 1)
        self.assertEqual(CPP.count("++PracticalLights"), 1)


if __name__ == "__main__":
    unittest.main()
