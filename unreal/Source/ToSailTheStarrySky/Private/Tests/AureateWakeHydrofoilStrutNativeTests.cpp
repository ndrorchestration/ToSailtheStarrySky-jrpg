#include "AureateWakePreviewActor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

// A bounded C++ runtime assertion on the provisional support pieces.
// This is not an authored-mesh, buoyancy, collision or cinematic art test.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FTSTSSHydrofoilStrutReviewTest,
    "TSTSS.Ship.HydrofoilStrutNativeReview",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSHydrofoilStrutReviewTest::RunTest(const FString& Parameters)
{
    UWorld* World = UWorld::CreateWorld(
        EWorldType::Game, false, FName(TEXT("TSTSSStrutNativeTransientWorld")));
    if (!TestNotNull(TEXT("Transient review world exists"), World))
    {
        return false;
    }

    AAureateWakePreviewActor* Ship = World->SpawnActor<AAureateWakePreviewActor>();
    if (!TestNotNull(TEXT("Native preview ship exists"), Ship))
    {
        World->DestroyWorld(false);
        return false;
    }

    // Assert actual runtime component instances, rather than a model-data declaration.
    TArray<UStaticMeshComponent*> Meshes;
    Ship->GetComponents<UStaticMeshComponent>(Meshes);
    UStaticMeshComponent* Struts[2] = {nullptr, nullptr};
    for (UStaticMeshComponent* Component : Meshes)
    {
        if (!Component) continue;
        if (Component->GetName() == TEXT("ReviewHydrofoilStrut_1")) Struts[0] = Component;
        if (Component->GetName() == TEXT("ReviewHydrofoilStrut_2")) Struts[1] = Component;
    }

    const bool bBothStruts = TestNotNull(TEXT("Port strut component exists"), Struts[0]) &&
        TestNotNull(TEXT("Starboard strut component exists"), Struts[1]);
    TestEqual(TEXT("Only two hydrofoil support slots"), Ship->GetHydrofoilStrutCount(), 2);
    if (!bBothStruts)
    {
        World->DestroyWorld(false);
        return false;
    }

    // Hidden hydrofoil support is mandatory outside of deployed review poses.
    for (int32 Index = 0; Index < 2; ++Index)
    {
        TestFalse(*FString::Printf(TEXT("Skyborne support %d hidden"), Index), Struts[Index]->IsVisible());
    }

    TestTrue(TEXT("Skyborne to Seaborne starts"), Ship->RequestForm(EAureateWakeForm::Seaborne));
    TestFalse(TEXT("Cannot interrupt transition"), Ship->RequestForm(EAureateWakeForm::Submersible));

    // Mid-transition refresh must keep each piece attached to the moving foil proxy.
    Ship->Tick(Ship->TransitionSeconds * 0.5f);
    for (int32 Index = 0; Index < 2; ++Index)
    {
        const float Side = Index == 0 ? -1.f : 1.f;
        const FVector Midpoint(0.f, Side * 70.f, -61.25f);
        TestTrue(*FString::Printf(TEXT("Support %d visible mid-transition"), Index),
            Struts[Index]->IsVisible());
        TestTrue(*FString::Printf(TEXT("Support %d follows moving foil midpoint"), Index),
            FVector::Dist(Struts[Index]->GetRelativeLocation(), Midpoint) < 0.15f);
    }

    TestTrue(TEXT("Review completion is available for ordinary forms"),
        Ship->FinishOrdinaryPreviewTransitionForReview());
    TestEqual(TEXT("Seaborne reached"), Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);

    for (int32 Index = 0; Index < 2; ++Index)
    {
        const float Side = Index == 0 ? -1.f : 1.f;
        const FVector HullAnchor(0.f, Side * 60.f, -30.f);
        const FVector FoilCenter(0.f, Side * 80.f, -140.f);
        const FVector Span = FoilCenter - HullAnchor;
        const FVector Midpoint = (FoilCenter + HullAnchor) * 0.5f;
        const float Length = Span.Size();
        const FString Label = FString::Printf(TEXT("Seaborne support %d"), Index);
        TestTrue(*(Label + TEXT(" remains visible")), Struts[Index]->IsVisible());
        TestTrue(*(Label + TEXT(" connects hull and foil centers")),
            FVector::Dist(Struts[Index]->GetRelativeLocation(), Midpoint) < 0.15f);
        TestTrue(*(Label + TEXT(" scales to endpoint span")),
            FMath::Abs(Struts[Index]->GetRelativeScale3D().X - Length / 100.f) < 0.005f);
        TestTrue(*(Label + TEXT(" aligns its cube X axis to span")),
            FVector::DotProduct(Struts[Index]->GetRelativeRotation().Vector(),
                Span.GetSafeNormal()) > 0.995f);
    }

    TestFalse(TEXT("Orbiter request still refused"), Ship->RequestForm(EAureateWakeForm::Orbiter));
    TestTrue(TEXT("Seaborne to Submersible starts"), Ship->RequestForm(EAureateWakeForm::Submersible));
    Ship->Tick(Ship->TransitionSeconds + 0.2f);
    TestEqual(TEXT("Submersible reached"), Ship->GetCurrentForm(), EAureateWakeForm::Submersible);
    for (int32 Index = 0; Index < 2; ++Index)
    {
        TestFalse(*FString::Printf(TEXT("Submersible support %d hidden"), Index),
            Struts[Index]->IsVisible());
    }
    TestFalse(TEXT("Cannot complete an inactive ordinary transition"),
        Ship->FinishOrdinaryPreviewTransitionForReview());

    World->DestroyWorld(false);
    return true;
}
#endif
