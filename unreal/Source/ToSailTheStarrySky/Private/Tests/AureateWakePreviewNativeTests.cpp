#include "AureateWakePreviewActor.h"
#include "Engine/World.h"
#include "Engine/StaticMesh.h"
#include "Components/StaticMeshComponent.h"
#include "Misc/AutomationTest.h"
#include "UObject/UObjectGlobals.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSAureatePreviewFormTest,
    "TSTSS.Ship.PreviewFormsAndOrbiterHold",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSAureatePreviewFormTest::RunTest(const FString& Parameters)
{
    // Transient native world: no authored level, save, story, or canon mutation.
    // CreateWorld already initializes the level and its unique WorldSettings.
    UWorld* ReviewWorld = UWorld::CreateWorld(EWorldType::Game, false,
        FName(TEXT("TSTSSAureatePreviewTransientWorld")));
    if (!TestNotNull(TEXT("Transient review world created"), ReviewWorld)) return false;

    AAureateWakePreviewActor* Ship = ReviewWorld->SpawnActor<AAureateWakePreviewActor>();
    if (!TestNotNull(TEXT("Preview actor spawned"), Ship))
    {
        ReviewWorld->DestroyWorld(false);
        return false;
    }

    TestEqual(TEXT("Exactly four persistent wings"), Ship->GetWingCount(), 4);
    TestEqual(TEXT("Exactly two hydrofoils"), Ship->GetHydrofoilCount(), 2);
    TestEqual(TEXT("Exactly four removable preview mounts"), Ship->GetWingRootMountCount(), 4);
    TestNull(TEXT("Authored root support must remain opt-in"),
        Ship->AuthoredRootSupportMesh.Get());
    TestEqual(TEXT("Exactly two preview hydrofoil struts"), Ship->GetHydrofoilStrutCount(), 2);
    TestEqual(TEXT("Four opt-in curved hull/foredeck sections"),
        Ship->GetHullSilhouetteSectionCount(), 4);
    TestEqual(TEXT("Forty triangulated canopy frame elements"),
        Ship->GetCanopyFramePieceCount(), 40);
    TestFalse(TEXT("Curved hull review is disabled by default"),
        Ship->bUseHullSilhouetteReview);
    TestFalse(TEXT("No silhouette when no study is requested"),
        AAureateWakePreviewActor::ShouldShowPrimitiveHullStudy(false, false));
    TestTrue(TEXT("Primitive study shows only when requested and no body applied"),
        AAureateWakePreviewActor::ShouldShowPrimitiveHullStudy(true, false));
    TestFalse(TEXT("Applied authored body overrides conflicting primitive request"),
        AAureateWakePreviewActor::ShouldShowPrimitiveHullStudy(true, true));
    TestFalse(TEXT("Applied authored body remains exclusive when study is off"),
        AAureateWakePreviewActor::ShouldShowPrimitiveHullStudy(false, true));
    TestFalse(TEXT("Approved-reference body candidate defaults off"),
        Ship->bUseAuthoredBodyReview);
    TestFalse(TEXT("Approved-reference body is not applied"),
        Ship->IsAuthoredBodyReviewApplied());
    TestNull(TEXT("No hull review mesh selected"), Ship->AuthoredHullReviewMesh.Get());
    TestNull(TEXT("No bridge review mesh selected"), Ship->AuthoredBridgeDomeReviewMesh.Get());
    TestTrue(TEXT("Default body refresh restores stock proxies"),
        Ship->RefreshBodyReviewMeshes());
    Ship->bUseHullSilhouetteReview = true;
    Ship->RefreshHullSilhouetteReview();
    TestEqual(TEXT("Hull review does not add extra wings"), Ship->GetWingCount(), 4);
    TestFalse(TEXT("Hull review does not authorize Orbiter"),
        Ship->RequestForm(EAureateWakeForm::Orbiter));
    Ship->bUseHullSilhouetteReview = false;
    Ship->RefreshHullSilhouetteReview();
    TestFalse(TEXT("Cannot finish a transition that has not started"),
        Ship->FinishOrdinaryPreviewTransitionForReview());
    TestEqual(TEXT("Defaults to Skyborne"), Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);
    TestFalse(TEXT("Orbiter preview is gated off by default"), Ship->bAllowOrbiterPreview);
    TestFalse(TEXT("Authored root pivot requires opt-in"), Ship->bUseRootPivotedWingPose);
    TestFalse(TEXT("Invalid form is rejected"), Ship->RequestForm(static_cast<EAureateWakeForm>(255)));
    TestFalse(TEXT("Orbiter request is rejected"), Ship->RequestForm(EAureateWakeForm::Orbiter));

    TestTrue(TEXT("Skyborne to Seaborne starts"), Ship->RequestForm(EAureateWakeForm::Seaborne));
    TestFalse(TEXT("Cannot interrupt a transition"), Ship->RequestForm(EAureateWakeForm::Submersible));
    TestTrue(TEXT("Editor-only ordinary review completion is permitted"),
        Ship->FinishOrdinaryPreviewTransitionForReview());
    TestEqual(TEXT("Seaborne reached"), Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);
    TestFalse(TEXT("Transition finished"), Ship->IsTransitioning());
    TestTrue(TEXT("Seaborne to Submersible starts"), Ship->RequestForm(EAureateWakeForm::Submersible));
    Ship->Tick(Ship->TransitionSeconds + 0.2f);
    TestEqual(TEXT("Submersible reached"), Ship->GetCurrentForm(), EAureateWakeForm::Submersible);
    TestTrue(TEXT("Submersible to Skyborne starts"), Ship->RequestForm(EAureateWakeForm::Skyborne));
    Ship->Tick(Ship->TransitionSeconds + 0.2f);
    TestEqual(TEXT("Skyborne restored"), Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);

    // The engine Cube is an intentionally noncanonical stand-in: exercise the
    // authored-pose gate without depending on imported, unapproved review assets.
    UStaticMesh* TemporaryWing = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (TestNotNull(TEXT("Engine test mesh available"), TemporaryWing))
    {
        // Verify review-only body validation without importing or accepting art.
        // The stock engine Cube is intentionally outside both allowed folders.
        TArray<UStaticMeshComponent*> MeshComponents;
        Ship->GetComponents<UStaticMeshComponent>(MeshComponents);
        UStaticMeshComponent* HullComponent = nullptr;
        UStaticMeshComponent* BridgeComponent = nullptr;
        for (UStaticMeshComponent* Component : MeshComponents)
        {
            if (Component->GetFName() == FName(TEXT("Hull"))) HullComponent = Component;
            if (Component->GetFName() == FName(TEXT("ForwardBridge"))) BridgeComponent = Component;
        }
        if (TestNotNull(TEXT("Preview hull exists"), HullComponent) &&
            TestNotNull(TEXT("Preview bridge exists"), BridgeComponent))
        {
            UStaticMesh* OriginalHull = HullComponent->GetStaticMesh().Get();
            UStaticMesh* OriginalBridge = BridgeComponent->GetStaticMesh().Get();
            Ship->bUseAuthoredBodyReview = true;
            Ship->AuthoredHullReviewMesh = TemporaryWing;
            TestFalse(TEXT("Missing bridge fails body intake atomically"),
                Ship->RefreshBodyReviewMeshes());
            TestFalse(TEXT("Missing bridge cannot apply body"),
                Ship->IsAuthoredBodyReviewApplied());
            Ship->AuthoredBridgeDomeReviewMesh = TemporaryWing;
            TestFalse(TEXT("Non-allowlisted engine cubes rejected"),
                Ship->RefreshBodyReviewMeshes());
            TestEqual(TEXT("Rejected body leaves hull mesh untouched"),
                HullComponent->GetStaticMesh().Get(), OriginalHull);
            TestEqual(TEXT("Rejected body leaves bridge mesh untouched"),
                BridgeComponent->GetStaticMesh().Get(), OriginalBridge);
            Ship->bUseHullSilhouetteReview = true;
            TestFalse(TEXT("Conflicting review modes refused"),
                Ship->RefreshBodyReviewMeshes());
            Ship->bUseHullSilhouetteReview = false;
            Ship->bAllowOrbiterPreview = true;
            TestFalse(TEXT("Body intent refuses Orbiter even with preview toggle"),
                Ship->RequestForm(EAureateWakeForm::Orbiter));
            Ship->bUseAuthoredBodyReview = false;
            TestTrue(TEXT("Disabling review restores original mesh poses"),
                Ship->RefreshBodyReviewMeshes());
            TestFalse(TEXT("Disabling review clears applied state"),
                Ship->IsAuthoredBodyReviewApplied());
            TestEqual(TEXT("Restored hull source mesh"), HullComponent->GetStaticMesh().Get(), OriginalHull);
            TestEqual(TEXT("Restored bridge source mesh"), BridgeComponent->GetStaticMesh().Get(), OriginalBridge);
            Ship->bAllowOrbiterPreview = false;
        }

        Ship->AuthoredWingMesh = TemporaryWing;
        Ship->bUseRootPivotedWingPose = true;
        Ship->RefreshWingMeshes();
        Ship->AuthoredRootSupportMesh = TemporaryWing; // review-only stand-in, not the GLB.
        Ship->RefreshRootSupportReview();
        TestEqual(TEXT("Assigning authored support adds no wing components"),
            Ship->GetWingCount(), 4);
        TestEqual(TEXT("Assigning authored support reuses four existing mounts"),
            Ship->GetWingRootMountCount(), 4);
        Ship->bAllowOrbiterPreview = true; // Review toggle must NOT override motion safety hold.
        TestFalse(TEXT("Authored-wing Orbiter hold survives preview opt-in"),
            Ship->RequestForm(EAureateWakeForm::Orbiter));
        TestTrue(TEXT("Authored-wing ordinary Seaborne route remains available"),
            Ship->RequestForm(EAureateWakeForm::Seaborne));
        Ship->Tick(Ship->TransitionSeconds + 0.2f);
        TestEqual(TEXT("Authored ordinary route reaches Seaborne"),
            Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);
    }
    ReviewWorld->DestroyWorld(false);
    return true;
}
#endif
