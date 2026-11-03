// Review-only automation. Requires a real Unreal Editor build; not a render or physics test.
#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "AureateWakePreviewActor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAureateFourFormReview,
    "TSTSS.AureateWake.Review.FourFormMechanics",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FAureateFourFormReview::RunTest(const FString& Parameters)
{
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
    if (!TestNotNull(TEXT("Transient review world"), World)) return false;
    World->InitializeNewWorld(UWorld::InitializationValues()
        .AllowAudioPlayback(false).CreatePhysicsScene(false)
        .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false));
    // Independent expectations: removing the gate, prematurely committing state,
    // rebuilding components, hiding tucked wings, or moving the bridge must fail.
    auto Find = [](AAureateWakePreviewActor* Ship, const FString& Name)
    {
        TArray<UStaticMeshComponent*> Components;
        Ship->GetComponents<UStaticMeshComponent>(Components);
        for (auto* Component : Components)
            if (Component->GetName() == Name) return Component;
        return static_cast<UStaticMeshComponent*>(nullptr);
    };
    for (int32 From = 0; From < 4; ++From)
    for (int32 To = 0; To < 4; ++To)
    {
        if (From == To) continue;
        auto* Ship = World->SpawnActor<AAureateWakePreviewActor>();
        if (!TestNotNull(TEXT("Preview actor"), Ship)) continue;
        const FString Route = FString::Printf(TEXT("%d -> %d: "), From, To);
        TestFalse(Route + TEXT("Orbiter locked by default"), Ship->bAllowOrbiterPreview);
        TestFalse(Route + TEXT("Locked request rejected"), Ship->RequestForm(EAureateWakeForm::Orbiter));
        TestFalse(Route + TEXT("Invalid enum rejected"), Ship->RequestForm(static_cast<EAureateWakeForm>(255)));
        TestFalse(Route + TEXT("Same form rejected"), Ship->RequestForm(EAureateWakeForm::Skyborne));
        TestFalse(Route + TEXT("Rejection leaves actor idle"), Ship->IsTransitioning());
        Ship->bAllowOrbiterPreview = true; // Transient fixture only; never a progression unlock.
        Ship->TransitionSeconds = 1.f;
        if (From != 0)
        {
            TestTrue(Route + TEXT("Set up source"), Ship->RequestForm(static_cast<EAureateWakeForm>(From)));
            Ship->Tick(1.f);
        }
        TArray<UStaticMeshComponent*> Wings;
        TArray<FTransform> Starts;
        for (int32 Index = 1; Index <= 4; ++Index)
        {
            auto* Wing = Find(Ship, FString::Printf(TEXT("DragonflyWing_%d"), Index));
            TestNotNull(Route + TEXT("Persistent wing"), Wing);
            Wings.Add(Wing);
            Starts.Add(Wing ? Wing->GetRelativeTransform() : FTransform::Identity);
        }
        auto* Bridge = Find(Ship, TEXT("ForwardBridge"));
        const FTransform BridgeStart = Bridge ? Bridge->GetRelativeTransform() : FTransform::Identity;
        TestNotNull(Route + TEXT("Bridge"), Bridge);
        auto CheckTransitFoils = [&]()
        {
            for (int32 Index = 1; Index <= 2; ++Index)
            {
                auto* Foil = Find(Ship, FString::Printf(TEXT("Hydrofoil_%d"), Index));
                TestNotNull(Route + TEXT("Transit foil"), Foil);
                if (Foil) TestEqual(Route + TEXT("Only sea routes expose moving foils"),
                    Foil->IsVisible(), From == 1 || To == 1);
            }
        };
        TestTrue(Route + TEXT("Request accepted"), Ship->RequestForm(static_cast<EAureateWakeForm>(To)));
        CheckTransitFoils();
        TestFalse(Route + TEXT("Busy request rejected"), Ship->RequestForm(static_cast<EAureateWakeForm>(From)));
        Ship->Tick(-1.f);
        for (int32 Index = 0; Index < 4; ++Index)
            if (Wings[Index]) TestTrue(Route + TEXT("Negative time cannot advance"),
                Wings[Index]->GetRelativeTransform().Equals(Starts[Index]));
        Ship->Tick(0.5f);
        CheckTransitFoils();
        TestTrue(Route + TEXT("Midpoint still transitioning"), Ship->IsTransitioning());
        TestEqual(Route + TEXT("State commits only at completion"), static_cast<int32>(Ship->GetCurrentForm()), From);
        for (auto* Wing : Wings)
            if (Wing) TestFalse(Route + TEXT("Finite midpoint"), Wing->GetRelativeTransform().ContainsNaN());
        Ship->Tick(1.f); // Overshoot must settle at the destination.
        TestFalse(Route + TEXT("Finished"), Ship->IsTransitioning());
        TestEqual(Route + TEXT("Destination"), static_cast<int32>(Ship->GetCurrentForm()), To);
        TestEqual(Route + TEXT("Four wings"), Ship->GetWingCount(), 4);
        TestEqual(Route + TEXT("Two foils"), Ship->GetHydrofoilCount(), 2);
        for (int32 Index = 0; Index < 4; ++Index)
        {
            auto* Wing = Find(Ship, FString::Printf(TEXT("DragonflyWing_%d"), Index + 1));
            TestTrue(Route + TEXT("Wing identity retained"), Wing == Wings[Index]);
            if (!Wing) continue;
            TestTrue(Route + TEXT("Wing remains visible"), Wing->IsVisible());
            TestFalse(Route + TEXT("Finite endpoint"), Wing->GetRelativeTransform().ContainsNaN());
            TestTrue(Route + TEXT("Preview cannot provide collision"),
                Wing->GetCollisionEnabled() == ECollisionEnabled::NoCollision);
            if (To == 2)
                TestTrue(Route + TEXT("Submersible wings tuck near hull"),
                    FMath::Abs(Wing->GetRelativeLocation().Y) < FMath::Abs(Starts[Index].GetLocation().Y) || From == 3);
            if (To == 3)
            {
                const FVector Expected[] = { FVector(0,0,315), FVector(0,0,-315),
                    FVector(0,-315,0), FVector(0,315,0) };
                TestTrue(Route + TEXT("Cardinal sail"), Wing->GetRelativeLocation().Equals(Expected[Index], 0.01f));
                TestTrue(Route + TEXT("Equal sail scale"), Wing->GetRelativeScale3D().Equals(FVector(2.5f,1.7f,0.055f), 0.001f));
                const FVector Axis = Wing->GetRelativeRotation().RotateVector(FVector::ForwardVector);
                TestTrue(Route + TEXT("Radial long axis"), FMath::Abs(FVector::DotProduct(Axis, Expected[Index].GetSafeNormal())) > 0.999f);
            }
        }
        for (int32 Index = 1; Index <= 2; ++Index)
        {
            auto* Foil = Find(Ship, FString::Printf(TEXT("Hydrofoil_%d"), Index));
            TestNotNull(Route + TEXT("Foil"), Foil);
            if (Foil) TestEqual(Route + TEXT("Foils visible only at Sea endpoint"), Foil->IsVisible(), To == 1);
        }
        if (Bridge) TestTrue(Route + TEXT("Bridge fixed forward"), Bridge->GetRelativeTransform().Equals(BridgeStart));
        TestTrue(Route + TEXT("Sail material blend endpoint"),
            FMath::IsNearlyEqual(Ship->OrbiterSailBlend, To == 3 ? 1.f : 0.f));
        Ship->Destroy();
    }
    World->DestroyWorld(false);
    return !HasAnyErrors();
}
#endif
