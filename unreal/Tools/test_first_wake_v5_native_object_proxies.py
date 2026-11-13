"""Contract tests for noncolliding, asset-backed V5 review interaction props.

No native Unreal compilation or gameplay approval is inferred from these tests.
"""
from pathlib import Path
import re
import unittest

UNREAL = Path(__file__).resolve().parents[1]
CPP = (UNREAL / "Source/ToSailTheStarrySky/Private/TSTSSMilestoneActor.cpp"
       ).read_text(encoding="utf-8")
HEADER = (UNREAL / "Source/ToSailTheStarrySky/Public/TSTSSMilestoneActor.h"
          ).read_text(encoding="utf-8")
AUTHORITATIVE = CPP.split("bool ATSTSSMilestoneActor::TryActivate(", 1)[1]

REVIEW_OBJECTS = (
    "FlyerPodium",
    "CaptainDesk",
    "GangwayAnchor",
    "LiftResonator",
    "PressureRegulator",
    "ReserveTank",
    "SignoffPlinth",
)


class FirstWakeV5ObjectProxySourceTest(unittest.TestCase):
    def test_exact_seven_assets_are_already_in_authorized_review_content(self):
        for name in REVIEW_OBJECTS:
            path = (
                UNREAL / "Content/TSTSS/Review/MultipathV1/ObjectImports"
                / name / name / "StaticMeshes" / f"{name}.uasset"
            )
            self.assertTrue(path.is_file(), name)
            self.assertIn(f'TEXT("{name}")', CPP)
        asset_names = re.findall(r'AssetName = TEXT\("([^"]+)"\)', CPP)
        self.assertEqual(set(asset_names), set(REVIEW_OBJECTS))
        self.assertEqual(len(asset_names), 7)

    def test_strict_v5_world_and_existing_milestone_label_gate(self):
        section = CPP.split("void ATSTSSMilestoneActor::EnsureV5ReviewObjectProxy()", 1)[1].split(
            "void ATSTSSMilestoneActor::UpdateReviewBeacon(", 1
        )[0]
        self.assertIn("IsAuthorizedReviewMilestoneWorld(World, GetActorLabel())", section)
        self.assertIn('TEXT("FirstWake_PreludeInteraction_V5_VisualReview")', section)
        self.assertIn("bReviewProxyInitialized", section)
        self.assertIn("bReviewProxyReady = true;", section)
        self.assertIn("TSTSS_V5_OBJECT_PROXY_HOLD", section)
        self.assertIn("GetBounds()", section)
        self.assertIn("bFrontFacingReviewProp", section)
        self.assertIn("ProxyRotation.RotateVector(Bounds.Origin * TargetScale)", section)
        self.assertIn("FRotator(0.f, 90.f, 0.f).Quaternion()", section)
        self.assertIn("Extents.ContainsNaN()", section)
        self.assertIn("constexpr float MaxHalfXY = 80.f;", section)
        self.assertIn("constexpr float MaxHalfZ = 108.f;", section)

    def test_proxy_is_independent_from_authoritative_e_ray_and_story(self):
        self.assertIn("ReviewObjectProxy = CreateDefaultSubobject<UStaticMeshComponent>", CPP)
        self.assertIn("ReviewObjectProxy->SetupAttachment(InteractionMesh)", CPP)
        self.assertIn("ReviewObjectProxy->SetCollisionEnabled(ECollisionEnabled::NoCollision)", CPP)
        self.assertIn("ReviewObjectProxy->SetCollisionResponseToAllChannels(ECR_Ignore)", CPP)
        self.assertIn("ReviewObjectProxy->SetGenerateOverlapEvents(false)", CPP)
        self.assertIn("InteractionMesh->SetVisibility(!bConsumed && !bReviewProxyReady, false)", CPP)
        self.assertIn("ReviewObjectProxy->SetVisibility(!bConsumed, false)", CPP)
        self.assertIn("InteractionMesh->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block)", CPP)
        self.assertIn("TObjectPtr<class UStaticMeshComponent> ReviewObjectProxy;", HEADER)
        self.assertIn("#if WITH_EDITORONLY_DATA", HEADER)
        self.assertIn("bReviewProxyInitialized = false;", HEADER)
        self.assertIn("bReviewProxyReady = false;", HEADER)
        # Purely visual helper must not own gameplay transitions or physics authority.
        section = CPP.split("void ATSTSSMilestoneActor::EnsureV5ReviewObjectProxy()", 1)[1].split(
            "void ATSTSSMilestoneActor::UpdateReviewBeacon(", 1
        )[0]
        for forbidden in (
            "AdvanceTo(", "InspectStation(", "SaveGameToSlot(",
            "OpenLevel(", "QueueShore(", "AdvanceWaterBeat(",
            "SetActorEnableCollision(true)", "SetCollisionResponseToChannel(ECC_Visibility",
            "SetActorLocation(",
        ):
            self.assertNotIn(forbidden, section)
        self.assertIn("Milestone == ETSTSSFirstWakeBeat::SeaContact", AUTHORITATIVE)
        self.assertIn("Milestone == ETSTSSFirstWakeBeat::FlotationConfirmed", AUTHORITATIVE)

    def test_proxy_does_not_pretend_to_be_approved_character(self):
        section = CPP.split("void ATSTSSMilestoneActor::EnsureV5ReviewObjectProxy()", 1)[1].split(
            "void ATSTSSMilestoneActor::UpdateReviewBeacon(", 1
        )[0]
        self.assertIn("review props, not representations of approved cast", section)
        self.assertNotIn("Genesis9", section)
        self.assertNotIn("EnderSliceReviewBody", section)
        self.assertNotIn("L_VS06_Shore", section)


if __name__ == "__main__":
    unittest.main()
