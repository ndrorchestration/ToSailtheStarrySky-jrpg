#include "Misc/AutomationTest.h"
#include "AureateWakePreviewActor.h"
#include "TSTSSFirstWakeState.h"
#include "Engine/World.h"
#include "Components/StaticMeshComponent.h"

#if WITH_DEV_AUTOMATION_TESTS
// Real native AActor geometry/policy test in an isolated transient world.
// Does not approve model art, prove buoyancy, or write any user SaveGame.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSAureateSeabourneStoryGate,
    "TSTSS.AureateWake.Review.SeabourneStoryGate",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSAureateSeabourneStoryGate::RunTest(const FString& Parameters)
{
    UWorld* World = UWorld::CreateWorld(
        EWorldType::Game, false, FName(TEXT("TSTSSAureateShipStoryGateTransient")));
    if (!TestNotNull(TEXT("Transient ship review world"), World)) return false;

    AAureateWakePreviewActor* Ship = World->SpawnActor<AAureateWakePreviewActor>();
    UTSTSSFirstWakeState* Story = NewObject<UTSTSSFirstWakeState>(GetTransientPackage());
    if (!TestNotNull(TEXT("Real review ship actor spawned"), Ship) ||
        !TestNotNull(TEXT("Authoritative story object exists"), Story))
    {
        World->DestroyWorld(false);
        return false;
    }

    UStaticMeshComponent* FirstWing = nullptr;
    UStaticMeshComponent* FirstFoil = nullptr;
    TArray<UStaticMeshComponent*> Meshes;
    Ship->GetComponents<UStaticMeshComponent>(Meshes);
    for (UStaticMeshComponent* Mesh : Meshes)
    {
        if (Mesh->GetFName() == FName(TEXT("DragonflyWing_1"))) FirstWing = Mesh;
        if (Mesh->GetFName() == FName(TEXT("Hydrofoil_1"))) FirstFoil = Mesh;
    }
    if (!TestNotNull(TEXT("First physical wing component"), FirstWing) ||
        !TestNotNull(TEXT("First hydrofoil component"), FirstFoil))
    {
        World->DestroyWorld(false);
        return false;
    }
    // A generic or production-world ship cannot impersonate the exact
    // runtime docked proxy or silently select a sea pose without authority.
    TestFalse(TEXT("Unscoped transient world refuses docked visual staging"),
        Ship->StageDockedSeabourneReviewPose());
    TestEqual(TEXT("Rejected visual staging keeps original geometry"),
        Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);

    const FVector SkyWingRoot = FirstWing->GetRelativeLocation();
    TestFalse(TEXT("Skybourne hydrofoil initially stowed"), FirstFoil->IsVisible());
    // Editor presentation may start folded for a disposable coastal review
    // but does not grant any runtime configuration authorization.
    Ship->EditorReviewPose = EAureateWakeForm::Seaborne;
    Ship->OnConstruction(FTransform::Identity);
    TestEqual(TEXT("Editor can preview folded Seabourne geometry"),
        Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);
    TestFalse(TEXT("Runtime world cannot invoke authoring pose"), Ship->ApplyEditorReviewPose());
    TestFalse(TEXT("Unbound editor pose grants no flight"),
        Ship->RequestForm(EAureateWakeForm::Skyborne));
    Ship->EditorReviewPose = EAureateWakeForm::Skyborne;
    Ship->OnConstruction(FTransform::Identity);
    TestEqual(TEXT("Preview pose restored before story binding"),
        Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);

    TestEqual(TEXT("Exactly four persistent wings"), Ship->GetWingCount(), 4);
    TestEqual(TEXT("Two hydrofoils available"), Ship->GetHydrofoilCount(), 2);
    TestFalse(TEXT("Unbound ship cannot request Seabourne"),
        Ship->RequestForm(EAureateWakeForm::Seaborne));
    Ship->bAllowOrbiterPreview = true;
    TestFalse(TEXT("Legacy Orbiter preview flag cannot bypass missing story"),
        Ship->RequestForm(EAureateWakeForm::Orbiter));

    // Creator-corrected sequence: the docked ship and preflight interior
    // remain Seabourne. Only the earned launch beat permits transformation.
    TestEqual(TEXT("Unstarted story has no authorized ship form"),
        Story->GetReviewShipMode(), NAME_None);
    TestFalse(TEXT("Unstarted story cannot authorize Skybourne"),
        Story->IsReviewShipModeAuthorized(FName(TEXT("Skybourne"))));
    TestTrue(TEXT("Restore earned engineering signoff"), Story->Restore(
        true, ETSTSSFirstWakeBeat::EngineeringChecked, 0x07));
    TestEqual(TEXT("Signed-off but docked ship remains Seabourne"),
        Story->GetReviewShipMode(), FName(TEXT("Seabourne")));
    TestTrue(TEXT("Prelaunch sea form is authorized"),
        Story->IsReviewShipModeAuthorized(FName(TEXT("Seabourne"))));
    TestFalse(TEXT("Signoff does not grant flight"),
        Story->IsReviewShipModeAuthorized(FName(TEXT("Skybourne"))));
    TestTrue(TEXT("Bind ship before captain's launch command"),
        Ship->BindReviewStory(Story));
    TestEqual(TEXT("Bound prelaunch ship shows deployed sea form"),
        Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);
    TestFalse(TEXT("Prelaunch ship cannot request Skybourne"),
        Ship->RequestForm(EAureateWakeForm::Skyborne));
    TestTrue(TEXT("Earned launch changes story authority"), Story->Restore(
        true, ETSTSSFirstWakeBeat::Launched, 0x07));
    TestEqual(TEXT("Launched story now authorizes Skybourne"),
        Story->GetReviewShipMode(), FName(TEXT("Skybourne")));
    Ship->Tick(0.1f);
    TestTrue(TEXT("Actual launch begins wing transformation"), Ship->IsTransitioning());

    // A story reset revokes flight during an active transition. The ship
    // must never visibly remain Skybourne while the story is unstarted.
    Story->Reset();
    Ship->Tick(0.1f);
    TestFalse(TEXT("Story reset cancels pending ascent"), Ship->IsTransitioning());
    TestEqual(TEXT("Reset mid-ascent returns docked Seabourne pose"),
        Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);
    TestTrue(TEXT("Reset mid-ascent deploys sea hydrofoil"), FirstFoil->IsVisible());
    TestFalse(TEXT("Reset story denies another flight request"),
        Ship->RequestForm(EAureateWakeForm::Skyborne));
    TestTrue(TEXT("Restore earned launch after reset"), Story->Restore(
        true, ETSTSSFirstWakeBeat::Launched, 0x07));
    Ship->Tick(0.1f);
    TestTrue(TEXT("Restored launch starts ascent anew"), Ship->IsTransitioning());
    Ship->Tick(5.f);
    TestEqual(TEXT("Launched review ship completes Skybourne form"),
        Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);

    // Reset after flight completes must also remove the now-unauthorized
    // airborne form. This is distinct from the in-transition reset above.
    Story->Reset();
    Ship->Tick(0.1f);
    TestFalse(TEXT("Reset completed flight leaves no pending transition"),
        Ship->IsTransitioning());
    TestEqual(TEXT("Reset after completed ascent returns docked Seabourne"),
        Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);
    TestTrue(TEXT("Reset after completed ascent shows hydrofoil"), FirstFoil->IsVisible());
    TestTrue(TEXT("Restore launch for subsequent splashdown assertions"), Story->Restore(
        true, ETSTSSFirstWakeBeat::Launched, 0x07));
    Ship->Tick(0.1f);
    Ship->Tick(5.f);
    TestEqual(TEXT("Restored launch returns Skybourne before sea contact"),
        Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);
    TestTrue(TEXT("Restore sea contact before stable flotation"), Story->Restore(
        true, ETSTSSFirstWakeBeat::SeaContact, 0x07));
    TestEqual(TEXT("Sea contact alone does not forge stable recovery"),
        Story->GetReviewShipMode(), FName(TEXT("Skybourne")));

    TestTrue(TEXT("Restore launched Prelude"), Story->Restore(
        true, ETSTSSFirstWakeBeat::Launched, 0x07));
    TestTrue(TEXT("Bind live pre-splashdown story"), Ship->BindReviewStory(Story));
    TestTrue(TEXT("Bound story registered"), Ship->HasReviewStory());
    TestEqual(TEXT("Prelude has Skybourne geometry"),
        Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);
    TestFalse(TEXT("Cannot deploy hydrofoils prematurely"),
        Ship->RequestForm(EAureateWakeForm::Seaborne));
    TestFalse(TEXT("Submersible denied in Prelude"),
        Ship->RequestForm(EAureateWakeForm::Submersible));

    TestTrue(TEXT("Restore measured flotation boundary"), Story->Restore(
        true, ETSTSSFirstWakeBeat::FlotationConfirmed, 0x07));
    // Running review scene animates the fold. Save/level restoration snaps
    // to the authorized form without an unauthorized Skybourne frame.
    Ship->Tick(0.1f);
    TestTrue(TEXT("Observed flotation starts Seabourne fold"), Ship->IsTransitioning());
    TestTrue(TEXT("Restoring pre-splashdown beat revokes pending fold"),
        Story->Restore(true, ETSTSSFirstWakeBeat::Launched, 0x07));
    Ship->Tick(0.1f);
    TestFalse(TEXT("Revoked transition cancels"), Ship->IsTransitioning());
    TestEqual(TEXT("Revocation restores Skybourne pose"),
        Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);

    TestTrue(TEXT("Float recovery boundary again"), Story->Restore(
        true, ETSTSSFirstWakeBeat::FlotationConfirmed, 0x07));
    Ship->Tick(0.1f);
    TestTrue(TEXT("Fold reinitiates under restored flotation"), Ship->IsTransitioning());
    Ship->Tick(5.f);
    TestFalse(TEXT("Seabourne fold finishes"), Ship->IsTransitioning());
    TestEqual(TEXT("Native form reaches Seabourne"),
        Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);
    TestTrue(TEXT("Wing articulates from Skybourne"),
        !FirstWing->GetRelativeLocation().Equals(SkyWingRoot, 0.1f));
    TestTrue(TEXT("Hydrofoil visibly deployed"), FirstFoil->IsVisible());

    TestTrue(TEXT("Rebind after travel/save restoration"), Ship->BindReviewStory(Story));
    TestEqual(TEXT("Restore snaps physical preview to Seabourne"),
        Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);
    TestFalse(TEXT("Skybourne flight blocked after splashdown"),
        Ship->RequestForm(EAureateWakeForm::Skyborne));
    TestFalse(TEXT("Submersible locked after splashdown"),
        Ship->RequestForm(EAureateWakeForm::Submersible));
    TestFalse(TEXT("Starbourne locked even if old debug flag is enabled"),
        Ship->RequestForm(EAureateWakeForm::Orbiter));
    TestFalse(TEXT("Unknown form rejected"),
        Ship->RequestForm(static_cast<EAureateWakeForm>(255)));
    TestFalse(TEXT("Duplicate active form does not transition"),
        Ship->RequestForm(EAureateWakeForm::Seaborne));
    TestFalse(TEXT("Denied requests leave no pending transition"),
        Ship->IsTransitioning());

    TestTrue(TEXT("Later recovery beat restored"), Story->Restore(
        true, ETSTSSFirstWakeBeat::EmptyReserveInspected, 0x07));
    TestTrue(TEXT("Rebind later Seabourne recovery"), Ship->BindReviewStory(Story));
    TestEqual(TEXT("Seabourne restriction persists beyond first shore"),
        Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);

    Story->Reset();
    TestFalse(TEXT("Reset story denies mode changes"),
        Ship->RequestForm(EAureateWakeForm::Skyborne));
    TestTrue(TEXT("Restore pre-splashdown story again"), Story->Restore(
        true, ETSTSSFirstWakeBeat::Launched, 0x07));
    TestTrue(TEXT("Rebind previous story snapshot"), Ship->BindReviewStory(Story));
    TestEqual(TEXT("Earlier story snapshot returns preview Skybourne"),
        Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);

    World->DestroyWorld(false);
    return !HasAnyErrors();
}
#endif