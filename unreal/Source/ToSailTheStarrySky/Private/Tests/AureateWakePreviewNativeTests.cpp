#include "AureateWakePreviewActor.h"
#include "Engine/World.h"
#include "Engine/StaticMesh.h"
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
    TestEqual(TEXT("Defaults to Skyborne"), Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);
    TestFalse(TEXT("Orbiter preview is gated off by default"), Ship->bAllowOrbiterPreview);
    TestFalse(TEXT("Authored root pivot requires opt-in"), Ship->bUseRootPivotedWingPose);
    TestFalse(TEXT("Invalid form is rejected"), Ship->RequestForm(static_cast<EAureateWakeForm>(255)));
    TestFalse(TEXT("Orbiter request is rejected"), Ship->RequestForm(EAureateWakeForm::Orbiter));

    TestTrue(TEXT("Skyborne to Seaborne starts"), Ship->RequestForm(EAureateWakeForm::Seaborne));
    TestFalse(TEXT("Cannot interrupt a transition"), Ship->RequestForm(EAureateWakeForm::Submersible));
    Ship->Tick(Ship->TransitionSeconds + 0.2f);
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
#endif
