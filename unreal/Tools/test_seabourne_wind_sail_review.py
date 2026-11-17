"""Engine-free source-contract regression for opt-in Seabourne wind-sail study.

Source tests are not Unreal UHT/UBT, native actor execution, actual kinematic
clearance, physics, wind response, native render, save persistence or art approval.
"""
import re
import unittest
from pathlib import Path

SRC=Path(__file__).resolve().parents[1] / "Source" / "ToSailTheStarrySky"
HEADER=SRC/"Public"/"AureateWakePreviewActor.h"
CPP=SRC/"Private"/"AureateWakePreviewActor.cpp"
NATIVE=SRC/"Private"/"Tests"/"AureateWakeSeabourneStoryGateTests.cpp"

def require_contract(text, labels):
    missing=[label for label in labels if label not in text]
    if missing:
        raise ValueError("WIND_SAIL_SOURCE_HOLD: "+", ".join(missing))

class SeabourneWindSailSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.header=HEADER.read_text(encoding="utf-8")
        cls.cpp=CPP.read_text(encoding="utf-8")
        cls.native=NATIVE.read_text(encoding="utf-8")

    def test_opt_in_and_story_authority_not_normal_gameplay(self):
        require_contract(self.header,(
            "bool bUseSeabourneWindSailReview = false;",
            "SetSeabourneWindTrimDegrees(int32 WingNumber, float Degrees);",
            "GetSeabourneWindTrimDegrees(int32 WingNumber) const;",
            "float SeabourneWindTrimDegrees[4] = { 0.f, 0.f, 0.f, 0.f };",
        ))
        require_contract(self.cpp,(
            "!bUseSeabourneWindSailReview || bTransitioning",
            "CurrentForm != EAureateWakeForm::Seaborne",
            "!IsValid(BoundReviewStory.Get())",
            "!BoundReviewStory->IsReviewShipModeAuthorized(FName(TEXT(\"Seabourne\")))",
            "Wings.Num() != 4 || Hydrofoils.Num() != 2",
        ))
        self.assertNotIn("UPROPERTY(SaveGame)",self.header)
        self.assertIn("bool bAllowOrbiterPreview = false;",self.header)
        self.assertIn("RequestedForm == EAureateWakeForm::Orbiter",self.cpp)

    def test_same_four_blades_upright_order_and_aft_rake(self):
        require_contract(self.cpp,(
            "static constexpr float StationsX[4] = { 300.f, 105.f, -90.f, -285.f };",
            "return FTransform(FRotator(98.f, TrimDegrees, 0.f),",
            "FVector(StationsX[WingIndex], 0.f, Z), Scale);",
            "const float Z = bAuthoredRootPivot ? 228.f : 365.f;",
            "FVector(2.8f, 1.25f, 0.05f)",
            "Form == EAureateWakeForm::Seaborne && bUseSeabourneWindSailReview",
            "return SeabourneWindSailPose(WingIndex, SeabourneWindTrimDegrees[WingIndex]",
        ))
        match=re.search(r"StationsX\[4\]\s*=\s*\{\s*(.*?)\s*\}",self.cpp)
        self.assertIsNotNone(match)
        stations=[float(x.strip().removesuffix("f")) for x in match.group(1).split(",")]
        self.assertEqual(len(stations),4)
        self.assertTrue(all(stations[i] > stations[i+1] for i in range(3)))
        self.assertEqual(stations,[300.0,105.0,-90.0,-285.0])
        self.assertIn("const bool bForwardWing = WingIndex < 2;",self.cpp)
        self.assertIn("Side * 175.f",self.cpp)  # old OFF-by-default Seabourne pose preserved

    def test_per_sail_trim_is_bounded_and_never_actuates_ship(self):
        require_contract(self.cpp,(
            "WingNumber < 1 || WingNumber > 4",
            "!FMath::IsFinite(Degrees) || FMath::Abs(Degrees) > 35.f",
            "SeabourneWindTrimDegrees[WingNumber - 1] = Degrees;",
            "Wings[WingNumber - 1].Get()",
            "Wings[Index]->SetRelativeTransform(WingPoseForMesh(",
            "UpdateRootSupportTransforms();",
        ))
        setter=self.cpp.split("bool AAureateWakePreviewActor::SetSeabourneWindTrimDegrees",1)[1].split(
            "\nbool AAureateWakePreviewActor::HasReviewStory",1)[0]
        self.assertNotIn("RequestForm(",setter)
        self.assertNotIn("SetPhysics",setter)
        self.assertNotIn("AddForce",setter)
        self.assertNotIn("AddTorque",setter)
        self.assertNotIn("SaveGame",setter)

    def test_load_and_revocation_never_restore_stale_trim(self):
        snap=self.cpp.split("void AAureateWakePreviewActor::SnapToForm",1)[1].split(
            "\nbool AAureateWakePreviewActor::HasReviewStory",1)[0]
        require_contract(snap,(
            "for (float& Degrees : SeabourneWindTrimDegrees)",
            "Degrees = 0.f;",
            "WingPoseForMesh(Form, Index)",
        ))
        self.assertLess(snap.index("Degrees = 0.f;"),snap.index("WingPoseForMesh(Form, Index)"))

    def test_existing_native_registry_stable_and_negative_assertions_present(self):
        require_contract(self.native,(
            "TSTSS.AureateWake.Review.SeabourneStoryGate",
            "Ship->bUseSeabourneWindSailReview = true;",
            "Ship->SetSeabourneWindTrimDegrees(1, 22.5f)",
            "Ship->SetSeabourneWindTrimDegrees(4, -14.f)",
            "Ship->SetSeabourneWindTrimDegrees(0, 4.f)",
            "Ship->SetSeabourneWindTrimDegrees(5, 4.f)",
            "Ship->SetSeabourneWindTrimDegrees(3, 36.f)",
            "std::numeric_limits<float>::quiet_NaN()",
            "Ship->GetWingCount(), 4",
            "Ship->GetHydrofoilCount(), 2",
            "Ship->BindReviewStory(Story)",
        ))
        self.assertEqual(self.native.count("IMPLEMENT_SIMPLE_AUTOMATION_TEST("),1)

    def test_live_opt_out_restores_legacy_pose_without_story_progress(self):
        require_contract(self.header,(
            "bool bSeabourneWindSailPoseActive = false;",
        ))
        snap=self.cpp.split("void AAureateWakePreviewActor::SnapToForm",1)[1].split(
            "\nfloat AAureateWakePreviewActor::GetSeabourneWindTrimDegrees",1)[0]
        require_contract(snap,(
            "bSeabourneWindSailPoseActive =",
            "bUseSeabourneWindSailReview && Form == EAureateWakeForm::Seaborne;",
            "RefreshRootSupports();",
        ))
        tick=self.cpp.split("void AAureateWakePreviewActor::Tick",1)[1]
        require_contract(tick,(
            "bSeabourneWindSailPoseActive && !bUseSeabourneWindSailReview",
            "SnapToForm(CurrentForm);",
            "(bUseSeabourneWindSailReview || bSeabourneWindSailPoseActive)",
        ))
        require_contract(self.native,(
            "Ship->SetSeabourneWindTrimDegrees(2, 15.f)",
            "Ship->bUseSeabourneWindSailReview = false;",
            "Ship->Tick(0.1f);",
            "Live opt-out clears stale yaw",
            "Same-frame opt-out plus revocation denies Seabourne presentation",
        ))
        self.assertNotIn("SetReviewShipMode",tick)
        self.assertNotIn("SaveGame",snap)

    def test_old_lateral_struts_hidden_when_dorsal_route_is_active(self):
        support=self.cpp.split("void AAureateWakePreviewActor::RefreshRootSupports",1)[1].split(
            "\nFTransform AAureateWakePreviewActor::WingPose",1)[0]
        require_contract(support,(
            "const bool bDorsalRoute = bUseSeabourneWindSailReview &&",
            "!bDorsalRoute;",
            "(bTransitioning && TargetForm == EAureateWakeForm::Seaborne)",
            "if (bUseSeabourneWindSailReview &&",
            "if (Support) Support->SetVisibility(false);",
            "return;",
        ))
        # Unmodified old side-anchor transform would otherwise draw across
        # the vessel's bridge if used on a dorsal-mounted wing.
        self.assertIn("const FVector HullAnchor(Root.X, Side * 73.f, 18.f);",support)
        # The suppression is explicitly above that old side-anchor path.
        self.assertLess(support.index("if (Support) Support->SetVisibility(false);"),
                        support.index("const FVector HullAnchor("))
        self.assertIn("RefreshRootSupports();",self.cpp.split(
            "void AAureateWakePreviewActor::SnapToForm",1)[1].split(
            "\nfloat AAureateWakePreviewActor::GetSeabourneWindTrimDegrees",1)[0])

    def test_negative_mutations_guard_live_optout_and_mount_suppression(self):
        original="bSeabourneWindSailPoseActive && !bUseSeabourneWindSailReview"
        self.assertIn(original,self.cpp)
        mutated=self.cpp.replace(original,"false /* unsafe disabled opt-out */",1)
        with self.assertRaisesRegex(ValueError,"WIND_SAIL_SOURCE_HOLD"):
            require_contract(mutated,(original,))
        original="if (Support) Support->SetVisibility(false);"
        self.assertIn(original,self.cpp)
        mutated=self.cpp.replace(original,"/* unsafe support left visible */",1)
        with self.assertRaisesRegex(ValueError,"WIND_SAIL_SOURCE_HOLD"):
            require_contract(mutated,(original,))
        self.assertIn("Same-frame opt-out plus revocation",self.native)

    def test_four_inert_dorsal_support_pairs_are_new_and_noncolliding(self):
        require_contract(self.header,(
            "GetDorsalMastCount() const { return DorsalMasts.Num(); }",
            "GetDorsalSwivelCount() const { return DorsalSwivels.Num(); }",
            "TArray<TObjectPtr<UStaticMeshComponent>> DorsalMasts;",
            "TArray<TObjectPtr<UStaticMeshComponent>> DorsalSwivels;",
            "void UpdateDorsalMountTransforms();",
        ))
        ctor=self.cpp.split("AAureateWakePreviewActor::AAureateWakePreviewActor()",1)[1].split(
            "\nvoid AAureateWakePreviewActor::OnConstruction",1)[0]
        require_contract(ctor,(
            'TEXT("DorsalMast_%d")',
            'TEXT("DorsalSwivel_%d")',
            "Mast->SetupAttachment(VesselRoot);",
            "Swivel->SetupAttachment(VesselRoot);",
            "SetupPreviewMesh(Mast, Shape);",
            "SetupPreviewMesh(Swivel, Shape);",
            "Mast->SetVisibility(false);",
            "Swivel->SetVisibility(false);",
            "DorsalMasts.Add(Mast);",
            "DorsalSwivels.Add(Swivel);",
        ))
        self.assertGreaterEqual(
            ctor.count("for (int32 Index = 0; Index < 4; ++Index)"),3)
        self.assertEqual(ctor.count("DorsalMasts.Add(Mast);"),1)
        self.assertEqual(ctor.count("DorsalSwivels.Add(Swivel);"),1)
        self.assertIn("Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);",self.cpp)

    def test_settled_mount_geometry_attaches_to_sail_base_without_bridge_intrusion(self):
        mount=self.cpp.split("void AAureateWakePreviewActor::UpdateDorsalMountTransforms()",1)[1].split(
            "\nvoid AAureateWakePreviewActor::UpdateRootSupportTransforms()",1)[0]
        require_contract(mount,(
            "CurrentForm == EAureateWakeForm::Seaborne && !bTransitioning",
            "Wings.Num() == 4 && Hydrofoils.Num() == 2 &&",
            "DorsalMasts.Num() == 4 && DorsalSwivels.Num() == 4;",
            "Mast->SetVisibility(false);",
            "Swivel->SetVisibility(false);",
            "if (!bReady || !IsValid(Wings[Index].Get())) continue;",
            "FMath::Abs(WingRoot.Y) > 1.f",
            "const float LowerEdge = bRootPivot ? WingRoot.Z :",
            "WingRoot.Z - 140.f * FMath::Abs(",
            "const float BaseZ = Index == 0 ? 150.f : 32.5f;",
            "const float Height = LowerEdge - BaseZ;",
            "if (!FMath::IsFinite(Height) || Height < 15.f) continue;",
            "FVector(WingRoot.X, 0.f, BaseZ + 0.5f * Height)",
            "FVector(0.20f, 0.20f, Height / 100.f)",
            "FVector(WingRoot.X, 0.f, LowerEdge)",
            "FVector(0.48f, 0.32f, 0.12f)",
            "Mast->SetVisibility(true);",
            "Swivel->SetVisibility(true);",
        ))
        # Proxy-only check, not real mesh clearance. First mast is over the
        # cube bridge roof at z=150; other 3 touch the hull top at z=32.5.
        import math
        sail_base=365.0-140.0*abs(math.sin(math.radians(98.0)))
        self.assertTrue(220.0 < sail_base < 230.0)
        self.assertTrue(sail_base-150.0 > 15.0)
        self.assertTrue(sail_base-32.5 > 15.0)
        self.assertLess(mount.index("Mast->SetVisibility(false);"),
                        mount.index("Mast->SetVisibility(true);"))
        # No physics or wing-array replacement inside supports.
        for forbidden in ("AddForce", "SetSimulatePhysics", "Wings.Add(", "SaveGame"):
            self.assertNotIn(forbidden,mount)

    def test_dorsal_mast_visibility_updates_and_native_failure_paths(self):
        support=self.cpp.split("void AAureateWakePreviewActor::RefreshRootSupports()",1)[1].split(
            "\nvoid AAureateWakePreviewActor::UpdateDorsalMountTransforms()",1)[0]
        self.assertIn("UpdateDorsalMountTransforms();",support)
        transition=self.cpp.split("bool AAureateWakePreviewActor::RequestForm",1)[1].split(
            "\nvoid AAureateWakePreviewActor::Tick",1)[0]
        require_contract(transition,(
            "bTransitioning = true;",
            "RefreshRootSupports();",
        ))
        require_contract(self.native,(
            "Ship->GetDorsalMastCount(), 4",
            "Ship->GetDorsalSwivelCount(), 4",
            "DorsalMasts[Index]->IsVisible()",
            "DorsalSwivels[Index]->IsVisible()",
            "Mast physically touches its hinge collar at sail bottom",
            "First dorsal hinge independently tracks sail 1 trim",
            "Fourth dorsal swivel tracks independent opposing trim",
            "Live opt-out hides former dorsal mast",
            "Story revocation hides every dorsal mast",
            "ECollisionEnabled::NoCollision",
        ))
        self.assertEqual(self.native.count("IMPLEMENT_SIMPLE_AUTOMATION_TEST("),1)

    def test_dorsal_mount_negative_mutation_checks(self):
        mount=self.cpp.split("void AAureateWakePreviewActor::UpdateDorsalMountTransforms()",1)[1].split(
            "\nvoid AAureateWakePreviewActor::UpdateRootSupportTransforms()",1)[0]
        originals=(
            "CurrentForm == EAureateWakeForm::Seaborne && !bTransitioning",
            "DorsalMasts.Num() == 4 && DorsalSwivels.Num() == 4;",
            "const float BaseZ = Index == 0 ? 150.f : 32.5f;",
            "Mast->SetVisibility(false);",
            "Swivel->SetVisibility(false);",
        )
        for original in originals:
            with self.subTest(original=original):
                self.assertIn(original,mount)
                changed=mount.replace(original,"/* UNSAFE DORSAL MUTATION */",1)
                with self.assertRaisesRegex(ValueError,"WIND_SAIL_SOURCE_HOLD"):
                    require_contract(changed,(original,))

    def test_negative_mutations_detect_unsafe_permission_and_geometry(self):
        originals=(
            "!bUseSeabourneWindSailReview || bTransitioning",
            "!IsValid(BoundReviewStory.Get())",
            "!FMath::IsFinite(Degrees) || FMath::Abs(Degrees) > 35.f",
            "Wings.Num() != 4 || Hydrofoils.Num() != 2",
        )
        # Mutation must target the setter BODY. The authorization predicate
        # intentionally also occurs in the guarded getter, so mutating the
        # first whole-file match could leave the setter unaffected.
        setter=self.cpp.split("bool AAureateWakePreviewActor::SetSeabourneWindTrimDegrees",1)[1].split(
            "\nbool AAureateWakePreviewActor::HasReviewStory",1)[0]
        for item in originals:
            self.assertIn(item,setter)
            mutated=setter.replace(item,"/* REDACTED UNSAFE */",1)
            with self.assertRaisesRegex(ValueError,"WIND_SAIL_SOURCE_HOLD"):
                require_contract(mutated,(item,))
        station="300.f, 105.f, -90.f, -285.f"
        wrong=self.cpp.replace(station,"300.f, 105.f, 105.f, -285.f",1)
        with self.assertRaisesRegex(ValueError,"WIND_SAIL_SOURCE_HOLD"):
            require_contract(wrong,(station,))

if __name__ == "__main__":
    unittest.main()
