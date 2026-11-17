#include "Misc/AutomationTest.h"
#include "AureateWakePreviewActor.h"
#include "TSTSSFirstWakeState.h"
#include "Engine/World.h"
#include "Components/StaticMeshComponent.h"
#include <limits>

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

    // Creator-directed four upright, aft-raked Seabourne wind-sail study.
    // This opt-in test is REAL actor-component geometry, not a visual approval,
    // aerodynamics, physical swept clearance, real wind or ship navigation.
    TestFalse(TEXT("Wind sail study stays OFF unless explicitly selected"),
        Ship->bUseSeabourneWindSailReview);
    TestFalse(TEXT("Disabled wind trim refuses input"),
        Ship->SetSeabourneWindTrimDegrees(1, 20.f));
    Ship->bUseSeabourneWindSailReview = true;
    TestTrue(TEXT("Rebinding opt-in docked study remains story scoped"),
        Ship->BindReviewStory(Story));

    UStaticMeshComponent* FourSails[4] = { nullptr, nullptr, nullptr, nullptr };
    for (UStaticMeshComponent* Mesh : Meshes)
    {
        for (int32 Index = 0; Index < 4; ++Index)
        {
            if (Mesh->GetFName() ==
                FName(*FString::Printf(TEXT("DragonflyWing_%d"), Index + 1)))
            {
                FourSails[Index] = Mesh;
            }
        }
    }
    bool bHaveFourDistinctSails = true;
    for (int32 Index = 0; Index < 4; ++Index)
    {
        bHaveFourDistinctSails &= TestNotNull(
            *FString::Printf(TEXT("Persistent Seabourne sail %d"), Index + 1),
            FourSails[Index]);
    }
    if (!bHaveFourDistinctSails)
    {
        World->DestroyWorld(false);
        return false;
    }
    for (int32 Index = 0; Index < 4; ++Index)
    {
        const FVector Root = FourSails[Index]->GetRelativeLocation();
        const FVector Blade = FourSails[Index]->GetRelativeRotation().Vector();
        TestTrue(TEXT("Each original sail moves to dorsal centerline"),
            FMath::Abs(Root.Y) < 0.1f && Root.Z > 200.f);
        TestTrue(TEXT("Each sail rises near vertical, gently aft-raked"),
            Blade.Z > 0.94f && Blade.X < 0.f);
        TestEqual(TEXT("Sail starts untrimmed"), Ship->GetSeabourneWindTrimDegrees(Index + 1), 0.f);
        if (Index > 0)
        {
            TestTrue(TEXT("Dorsal row has distinct stations from fore to aft"),
                FourSails[Index - 1]->GetRelativeLocation().X > Root.X);
        }
    }
    const FRotator SecondBefore = FourSails[1]->GetRelativeRotation();
    TestTrue(TEXT("Trim first sail independently"),
        Ship->SetSeabourneWindTrimDegrees(1, 22.5f));
    TestEqual(TEXT("Only sail 1 trim changed"), Ship->GetSeabourneWindTrimDegrees(1), 22.5f);
    TestEqual(TEXT("Sail 2 unchanged"), Ship->GetSeabourneWindTrimDegrees(2), 0.f);
    TestTrue(TEXT("Other sail yaw remains unchanged"),
        FourSails[1]->GetRelativeRotation().Equals(SecondBefore, 0.01f));
    TestTrue(TEXT("Trim fourth sail independently opposite direction"),
        Ship->SetSeabourneWindTrimDegrees(4, -14.f));
    TestEqual(TEXT("Fourth changed without overwriting first"),
        Ship->GetSeabourneWindTrimDegrees(1), 22.5f);
    TestEqual(TEXT("Fourth stored trim"), Ship->GetSeabourneWindTrimDegrees(4), -14.f);
    TestFalse(TEXT("Invalid sail index zero denied"), Ship->SetSeabourneWindTrimDegrees(0, 4.f));
    TestFalse(TEXT("Invalid fifth sail denied"), Ship->SetSeabourneWindTrimDegrees(5, 4.f));
    TestFalse(TEXT("Beyond provisional visual yaw denied"), Ship->SetSeabourneWindTrimDegrees(3, 36.f));
    TestFalse(TEXT("Non-finite wind yaw denied"), Ship->SetSeabourneWindTrimDegrees(
        2, std::numeric_limits<float>::quiet_NaN()));
    TestEqual(TEXT("Bad trim never changed second sail"),
        Ship->GetSeabourneWindTrimDegrees(2), 0.f);
    TestEqual(TEXT("Still four wings, never added sails"), Ship->GetWingCount(), 4);
    TestEqual(TEXT("Still two hydrofoils"), Ship->GetHydrofoilCount(), 2);
    TestTrue(TEXT("Restore authorized Seabourne resets ephemeral trim"),
        Ship->BindReviewStory(Story));
    TestEqual(TEXT("After story bind no stale sail 1 trim"),
        Ship->GetSeabourneWindTrimDegrees(1), 0.f);
    TestTrue(TEXT("Run separate test trim before live opt-out"),
        Ship->SetSeabourneWindTrimDegrees(2, 15.f));
    Ship->bUseSeabourneWindSailReview = false;
    Ship->Tick(0.1f);
    TestEqual(TEXT("Disabled live preview rolls back to legacy lateral wing"),
        FourSails[1]->GetRelativeLocation().Y, 175.f);
    TestEqual(TEXT("Live opt-out clears stale yaw"), Ship->GetSeabourneWindTrimDegrees(2), 0.f);
    TestEqual(TEXT("Live opt-out retains authorized Seabourne form"),
        Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);
    TestTrue(TEXT("Restore original noncanonical default pose"),
        Ship->BindReviewStory(Story));
    TestFalse(TEXT("Disabled study refuses another trim"),
        Ship->SetSeabourneWindTrimDegrees(1, 10.f));

    TestTrue(TEXT("Later recovery beat restored"), Story->Restore(
        true, ETSTSSFirstWakeBeat::EmptyReserveInspected, 0x07));
    TestTrue(TEXT("Rebind later Seabourne recovery"), Ship->BindReviewStory(Story));
    TestEqual(TEXT("Seabourne restriction persists beyond first shore"),
        Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);

    Ship->bUseSeabourneWindSailReview = true;
    TestTrue(TEXT("Study yaw before story revocation"),
        Ship->SetSeabourneWindTrimDegrees(3, 12.f));
    Story->Reset();
    TestFalse(TEXT("Reset story immediately blocks wind trim"),
        Ship->SetSeabourneWindTrimDegrees(3, 5.f));
    TestEqual(TEXT("Unapproved stale trim not exposed after reset"),
        Ship->GetSeabourneWindTrimDegrees(3), 0.f);
    Ship->Tick(0.1f);
    TestEqual(TEXT("Revocation snaps visual ship from study to Skybourne"),
        Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);
    TestEqual(TEXT("Revocation clears ephemeral trim storage"),
        Ship->GetSeabourneWindTrimDegrees(3), 0.f);

    // Additional adversarial ordering: disable the feature and reset the
    // story in the same frame; revocation still has precedence over opt-out.
    TestTrue(TEXT("Recreate authorized Seabourne for simultaneous opt-out test"),
        Story->Restore(true, ETSTSSFirstWakeBeat::FlotationConfirmed, 0x07));
    TestTrue(TEXT("Rebind legal Seabourne before simultaneous opt-out test"),
        Ship->BindReviewStory(Story));
    TestTrue(TEXT("Trim sail 4 before simultaneous opt-out and story reset"),
        Ship->SetSeabourneWindTrimDegrees(4, 10.f));
    Ship->bUseSeabourneWindSailReview = false;
    Story->Reset();
    Ship->Tick(0.1f);
    TestEqual(TEXT("Same-frame opt-out plus revocation denies Seabourne presentation"),
        Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);
    TestEqual(TEXT("Same-frame opt-out plus revocation masks stale sail trim"),
        Ship->GetSeabourneWindTrimDegrees(4), 0.f);
    TestFalse(TEXT("Reset story denies mode changes"),
        Ship->RequestForm(EAureateWakeForm::Skyborne));
    Ship->bUseSeabourneWindSailReview = false;
    TestTrue(TEXT("Restore pre-splashdown story again"), Story->Restore(
        true, ETSTSSFirstWakeBeat::Launched, 0x07));
    TestTrue(TEXT("Rebind previous story snapshot"), Ship->BindReviewStory(Story));
    TestEqual(TEXT("Earlier story snapshot returns preview Skybourne"),
        Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);

    World->DestroyWorld(false);
    return !HasAnyErrors();
}
#endif