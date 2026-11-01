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
    TestEqual(TEXT("Exactly two preview hydrofoil struts"), Ship->GetHydrofoilStrutCount(), 2);
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
        Ship->AuthoredWingMesh = TemporaryWing;
        Ship->bUseRootPivotedWingPose = true;
        Ship->RefreshWingMeshes();
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

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSAureateSixRouteSupportReviewTest,
    "TSTSS.Ship.ReviewSupportSixDirectedRoutes",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSAureateSixRouteSupportReviewTest::RunTest(const FString& Parameters)
{
    // Pure transient review. Exercise actual components in all six ordinary
    // directed routes, without importing art or touching gameplay/story state.
    UWorld* ReviewWorld = UWorld::CreateWorld(EWorldType::Game, false,
        FName(TEXT("TSTSSAureateSixRouteTransientWorld")));
    if (!TestNotNull(TEXT("Six-route transient world created"), ReviewWorld)) return false;

    AAureateWakePreviewActor* Ship = ReviewWorld->SpawnActor<AAureateWakePreviewActor>();
    if (!TestNotNull(TEXT("Six-route preview actor spawned"), Ship))
    {
        ReviewWorld->DestroyWorld(false);
        return false;
    }

    TArray<UStaticMeshComponent*> Components;
    Ship->GetComponents<UStaticMeshComponent>(Components);
    TMap<FName, UStaticMeshComponent*> ByName;
    for (UStaticMeshComponent* Component : Components)
    {
        if (Component) ByName.Add(Component->GetFName(), Component);
    }
    const auto Part = [&ByName](const TCHAR* Prefix, int32 Index) -> UStaticMeshComponent*
    {
        return ByName.FindRef(FName(*FString::Printf(TEXT("%s_%d"), Prefix, Index + 1)));
    };

    // All review supports should begin hidden when authored wings are not opted in.
    for (int32 I = 0; I < 4; ++I)
    {
        UStaticMeshComponent* Bracket = Part(TEXT("ReviewWingRootBracket"), I);
        if (TestNotNull(TEXT("Four root brackets exist"), Bracket))
        {
            TestFalse(TEXT("Legacy preview root bracket hidden"), Bracket->IsVisible());
            TestEqual(TEXT("Review root bracket has no collision"), Bracket->GetCollisionEnabled(),
                ECollisionEnabled::NoCollision);
        }
    }
    for (int32 I = 0; I < 2; ++I)
    {
        UStaticMeshComponent* Strut = Part(TEXT("ReviewHydrofoilStrut"), I);
        if (TestNotNull(TEXT("Two hydrofoil struts exist"), Strut))
        {
            TestFalse(TEXT("Legacy preview strut hidden"), Strut->IsVisible());
            TestEqual(TEXT("Review hydrofoil strut has no collision"), Strut->GetCollisionEnabled(),
                ECollisionEnabled::NoCollision);
        }
    }

    UStaticMesh* NoncanonicalMesh = LoadObject<UStaticMesh>(nullptr,
        TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (!TestNotNull(TEXT("Engine review placeholder available"), NoncanonicalMesh))
    {
        ReviewWorld->DestroyWorld(false);
        return false;
    }
    Ship->AuthoredWingMesh = NoncanonicalMesh;
    Ship->bUseRootPivotedWingPose = true;
    Ship->bAllowOrbiterPreview = true; // Must never defeat the authored-wing Orbiter hold.
    Ship->RefreshWingMeshes();

    const EAureateWakeForm OrdinaryForms[] = {
        EAureateWakeForm::Skyborne,
        EAureateWakeForm::Seaborne,
        EAureateWakeForm::Submersible
    };
    int32 RoutesCompleted = 0;
    for (const EAureateWakeForm Start : OrdinaryForms)
    {
        for (const EAureateWakeForm Target : OrdinaryForms)
        {
            if (Start == Target) continue;
            if (Ship->GetCurrentForm() != Start)
            {
                if (!TestTrue(TEXT("Route origin transition authorized"), Ship->RequestForm(Start))
                    || !TestTrue(TEXT("Route origin reached"), Ship->FinishOrdinaryPreviewTransitionForReview()))
                {
                    ReviewWorld->DestroyWorld(false);
                    return false;
                }
            }

            TestFalse(TEXT("Orbiter blocked at ordinary-form origin"),
                Ship->RequestForm(EAureateWakeForm::Orbiter));
            if (!TestTrue(TEXT("Ordinary route starts"), Ship->RequestForm(Target)))
            {
                ReviewWorld->DestroyWorld(false);
                return false;
            }
            Ship->Tick(Ship->TransitionSeconds * 0.5f);
            TestTrue(TEXT("Halfway transition remains active"), Ship->IsTransitioning());
            TestEqual(TEXT("Current form unchanged halfway"), Ship->GetCurrentForm(), Start);
            TestFalse(TEXT("Orbiter blocked while ordinary route runs"),
                Ship->RequestForm(EAureateWakeForm::Orbiter));

            // Support positions are recomputed from live component transforms.
            // The positive local X end of each temporary Cube support reaches
            // its designated wing/foil root (within floating-point tolerance).
            for (int32 I = 0; I < 4; ++I)
            {
                UStaticMeshComponent* Bracket = Part(TEXT("ReviewWingRootBracket"), I);
                UStaticMeshComponent* Wing = Part(TEXT("DragonflyWing"), I);
                if (!TestNotNull(TEXT("Moving bracket found"), Bracket)
                    || !TestNotNull(TEXT("Moving wing found"), Wing)) continue;
                TestTrue(TEXT("Root bracket visible during authored ordinary motion"),
                    Bracket->IsVisible());
                const FVector Tip = Bracket->GetRelativeLocation()
                    + Bracket->GetRelativeRotation().RotateVector(
                        FVector(Bracket->GetRelativeScale3D().X * 50.f, 0.f, 0.f));
                TestTrue(TEXT("Root bracket tip tracks wing pivot"),
                    Tip.Equals(Wing->GetRelativeLocation(), 0.5f));
            }
            for (int32 I = 0; I < 2; ++I)
            {
                UStaticMeshComponent* Strut = Part(TEXT("ReviewHydrofoilStrut"), I);
                UStaticMeshComponent* Foil = Part(TEXT("Hydrofoil"), I);
                if (!TestNotNull(TEXT("Moving strut found"), Strut)
                    || !TestNotNull(TEXT("Moving hydrofoil found"), Foil)) continue;
                TestTrue(TEXT("Hydrofoil strut visible during deployed-foil motion"),
                    Strut->IsVisible());
                const FVector Tip = Strut->GetRelativeLocation()
                    + Strut->GetRelativeRotation().RotateVector(
                        FVector(Strut->GetRelativeScale3D().X * 50.f, 0.f, 0.f));
                TestTrue(TEXT("Hydrofoil strut tip tracks foil pivot"),
                    Tip.Equals(Foil->GetRelativeLocation(), 0.5f));
            }

            if (!TestTrue(TEXT("Ordinary route completes"), Ship->FinishOrdinaryPreviewTransitionForReview()))
            {
                ReviewWorld->DestroyWorld(false);
                return false;
            }
            TestEqual(TEXT("Ordinary destination reached"), Ship->GetCurrentForm(), Target);
            TestFalse(TEXT("Ordinary route ends idle"), Ship->IsTransitioning());
            TestEqual(TEXT("Four wings retained"), Ship->GetWingCount(), 4);
            TestEqual(TEXT("Two foils retained"), Ship->GetHydrofoilCount(), 2);
            for (int32 I = 0; I < 2; ++I)
            {
                UStaticMeshComponent* Strut = Part(TEXT("ReviewHydrofoilStrut"), I);
                if (TestNotNull(TEXT("Terminal hydrofoil strut found"), Strut))
                {
                    TestEqual(TEXT("Strut visible only in terminal Seaborne"),
                        Strut->IsVisible(), Target == EAureateWakeForm::Seaborne);
                }
            }
            TestFalse(TEXT("Orbiter blocked at ordinary destination"),
                Ship->RequestForm(EAureateWakeForm::Orbiter));
            ++RoutesCompleted;
        }
    }
    TestEqual(TEXT("All six directed ordinary routes reviewed"), RoutesCompleted, 6);
    ReviewWorld->DestroyWorld(false);
    return true;
}

#endif
