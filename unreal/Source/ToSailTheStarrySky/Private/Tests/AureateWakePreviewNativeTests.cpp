#include "AureateWakePreviewActor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "Engine/StaticMesh.h"
#include "Misc/AutomationTest.h"
#include "UObject/UObjectGlobals.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSAureatePreviewFormTest,
    "TSTSS.Ship.PreviewFormsAndOrbiterHold",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

namespace
{
    bool RunAureateWakePreviewScenario(FAutomationTestBase& Test)
    {
        // Transient native world: no authored level, save, story, or canon mutation.
        // CreateWorld already initializes the level and its unique WorldSettings.
        UWorld* ReviewWorld = UWorld::CreateWorld(EWorldType::Game, false,
            FName(TEXT("TSTSSAureatePreviewTransientWorld")));
        if (!Test.TestNotNull(TEXT("Transient review world created"), ReviewWorld)) return false;

        AAureateWakePreviewActor* Ship = ReviewWorld->SpawnActor<AAureateWakePreviewActor>();
        if (!Test.TestNotNull(TEXT("Preview actor spawned"), Ship))
        {
            ReviewWorld->DestroyWorld(false);
            return false;
        }

        const TArray<FName> ExpectedWingNames = {
            FName(TEXT("DragonflyWing_1")), FName(TEXT("DragonflyWing_2")),
            FName(TEXT("DragonflyWing_3")), FName(TEXT("DragonflyWing_4"))
        };
        TMap<FName, UStaticMeshComponent*> OriginalWingInstances;
        auto CheckKinematicWingInvariant = [&](const FString& Stage)
        {
            TArray<UStaticMeshComponent*> Components;
            Ship->GetComponents<UStaticMeshComponent>(Components);
            TMap<FName, UStaticMeshComponent*> FoundWings;
            int32 NamedWingComponentCount = 0;
            for (UStaticMeshComponent* Component : Components)
            {
                if (!Component) continue;
                const FString ComponentName = Component->GetFName().ToString();
                if (ComponentName.StartsWith(TEXT("DragonflyWing_")))
                {
                    ++NamedWingComponentCount;
                    FoundWings.Add(Component->GetFName(), Component);
                }
            }

            Test.TestEqual(Stage + TEXT(": exactly four named wing components"),
                NamedWingComponentCount, 4);
            Test.TestEqual(Stage + TEXT(": exactly four distinct wing components"),
                FoundWings.Num(), 4);
            if (OriginalWingInstances.Num() == 0 && FoundWings.Num() == 4)
            {
                OriginalWingInstances = FoundWings;
            }
            for (const FName& ExpectedName : ExpectedWingNames)
            {
                const FString Label = Stage + TEXT(": ") + ExpectedName.ToString();
                UStaticMeshComponent* const* Found = FoundWings.Find(ExpectedName);
                Test.TestTrue(Label + TEXT(" remains present"), Found != nullptr && *Found != nullptr);
                if (!Found || !*Found) continue;
                UStaticMeshComponent* const* Original = OriginalWingInstances.Find(ExpectedName);
                Test.TestTrue(Label + TEXT(" retains its original component identity"),
                    Original != nullptr && *Original == *Found);
                Test.TestTrue(Label + TEXT(" has collision disabled"),
                    (*Found)->GetCollisionEnabled() == ECollisionEnabled::NoCollision);
                Test.TestFalse(Label + TEXT(" is not simulating physics"),
                    (*Found)->IsSimulatingPhysics());
            }
        };

        Test.TestEqual(TEXT("Exactly four persistent wings"), Ship->GetWingCount(), 4);
        Test.TestEqual(TEXT("Exactly two hydrofoils"), Ship->GetHydrofoilCount(), 2);
        Test.TestEqual(TEXT("Exactly four removable preview mounts"), Ship->GetWingRootMountCount(), 4);
        Test.TestEqual(TEXT("Exactly two preview hydrofoil struts"), Ship->GetHydrofoilStrutCount(), 2);
        Test.TestFalse(TEXT("Cannot finish a transition that has not started"),
            Ship->FinishOrdinaryPreviewTransitionForReview());
        Test.TestEqual(TEXT("Defaults to Skyborne"), Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);
        Test.TestFalse(TEXT("Orbiter preview is gated off by default"), Ship->bAllowOrbiterPreview);
        Test.TestFalse(TEXT("Authored root pivot requires opt-in"), Ship->bUseRootPivotedWingPose);
        Test.TestFalse(TEXT("Invalid form is rejected"), Ship->RequestForm(static_cast<EAureateWakeForm>(255)));
        Test.TestFalse(TEXT("Orbiter request is rejected"), Ship->RequestForm(EAureateWakeForm::Orbiter));
        CheckKinematicWingInvariant(TEXT("Initial Skyborne pose"));

        // First route also preserves the existing review-only completion action.
        Test.TestTrue(TEXT("Skyborne to Seaborne starts"), Ship->RequestForm(EAureateWakeForm::Seaborne));
        CheckKinematicWingInvariant(TEXT("Skyborne to Seaborne transition start"));
        Ship->Tick(Ship->TransitionSeconds * 0.5f);
        Test.TestTrue(TEXT("First ordinary transition remains active at midpoint"), Ship->IsTransitioning());
        CheckKinematicWingInvariant(TEXT("Skyborne to Seaborne transition midpoint"));
        Test.TestTrue(TEXT("Editor-only ordinary review completion is permitted"),
            Ship->FinishOrdinaryPreviewTransitionForReview());
        Test.TestEqual(TEXT("Seaborne reached"), Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);
        Test.TestFalse(TEXT("Transition finished"), Ship->IsTransitioning());
        CheckKinematicWingInvariant(TEXT("Seaborne endpoint"));

        // Exercise all six directed ordinary routes among the three existing forms.
        // These are visual-preview transitions only; no new mode or physics authority is added.
        auto RunOrdinaryRoute = [&](EAureateWakeForm From, EAureateWakeForm To,
            const TCHAR* RouteName)
        {
            const FString Route(RouteName);
            Test.TestEqual(Route + TEXT(": expected source form"), Ship->GetCurrentForm(), From);
            Test.TestTrue(Route + TEXT(": request accepted"), Ship->RequestForm(To));
            Test.TestTrue(Route + TEXT(": transition entered"), Ship->IsTransitioning());
            CheckKinematicWingInvariant(Route + TEXT(" start"));
            Ship->Tick(Ship->TransitionSeconds * 0.5f);
            Test.TestTrue(Route + TEXT(": transition remains active at midpoint"), Ship->IsTransitioning());
            CheckKinematicWingInvariant(Route + TEXT(" midpoint"));
            Ship->Tick(Ship->TransitionSeconds + 0.2f);
            Test.TestFalse(Route + TEXT(": transition completed"), Ship->IsTransitioning());
            Test.TestEqual(Route + TEXT(": target form reached"), Ship->GetCurrentForm(), To);
            CheckKinematicWingInvariant(Route + TEXT(" endpoint"));
        };

        RunOrdinaryRoute(EAureateWakeForm::Seaborne, EAureateWakeForm::Submersible,
            TEXT("Seaborne to Submersible"));
        RunOrdinaryRoute(EAureateWakeForm::Submersible, EAureateWakeForm::Skyborne,
            TEXT("Submersible to Skyborne"));
        RunOrdinaryRoute(EAureateWakeForm::Skyborne, EAureateWakeForm::Submersible,
            TEXT("Skyborne to Submersible"));
        RunOrdinaryRoute(EAureateWakeForm::Submersible, EAureateWakeForm::Seaborne,
            TEXT("Submersible to Seaborne"));
        RunOrdinaryRoute(EAureateWakeForm::Seaborne, EAureateWakeForm::Skyborne,
            TEXT("Seaborne to Skyborne"));

        // The engine Cube is an intentionally noncanonical stand-in: exercise the
        // authored-pose gate without depending on imported, unapproved review assets.
        UStaticMesh* TemporaryWing = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
        if (Test.TestNotNull(TEXT("Engine test mesh available"), TemporaryWing))
        {
            Ship->AuthoredWingMesh = TemporaryWing;
            Ship->bUseRootPivotedWingPose = true;
            Ship->RefreshWingMeshes();
            CheckKinematicWingInvariant(TEXT("Authored-wing Skyborne pose"));
            Ship->bAllowOrbiterPreview = true; // Review toggle must NOT override motion safety hold.
            Test.TestFalse(TEXT("Authored-wing Orbiter hold survives preview opt-in"),
                Ship->RequestForm(EAureateWakeForm::Orbiter));
            Test.TestTrue(TEXT("Authored-wing ordinary Seaborne route remains available"),
                Ship->RequestForm(EAureateWakeForm::Seaborne));
            CheckKinematicWingInvariant(TEXT("Authored-wing transition start"));
            Ship->Tick(Ship->TransitionSeconds * 0.5f);
            CheckKinematicWingInvariant(TEXT("Authored-wing transition midpoint"));
            Ship->Tick(Ship->TransitionSeconds + 0.2f);
            Test.TestEqual(TEXT("Authored ordinary route reaches Seaborne"),
                Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);
            CheckKinematicWingInvariant(TEXT("Authored-wing transition endpoint"));
        }
        ReviewWorld->DestroyWorld(false);
        return true;
    }
}

bool FTSTSSAureatePreviewFormTest::RunTest(const FString& Parameters)
{
    return RunAureateWakePreviewScenario(*this);
}
#endif
