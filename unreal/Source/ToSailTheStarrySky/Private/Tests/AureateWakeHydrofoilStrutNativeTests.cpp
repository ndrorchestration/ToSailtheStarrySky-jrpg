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
    UStaticMeshComponent* Foils[2] = {nullptr, nullptr};
    for (UStaticMeshComponent* Component : Meshes)
    {
        if (!Component) continue;
        if (Component->GetName() == TEXT("ReviewHydrofoilStrut_1")) Struts[0] = Component;
        if (Component->GetName() == TEXT("ReviewHydrofoilStrut_2")) Struts[1] = Component;
        if (Component->GetName() == TEXT("Hydrofoil_1")) Foils[0] = Component;
        if (Component->GetName() == TEXT("Hydrofoil_2")) Foils[1] = Component;
    }

    const bool bBothFoils = TestNotNull(TEXT("Port hydrofoil component exists"), Foils[0]) &&
        TestNotNull(TEXT("Starboard hydrofoil component exists"), Foils[1]);
    const bool bBothStruts = TestNotNull(TEXT("Port strut component exists"), Struts[0]) &&
        TestNotNull(TEXT("Starboard strut component exists"), Struts[1]);
    TestEqual(TEXT("Only two hydrofoil support slots"), Ship->GetHydrofoilStrutCount(), 2);
    if (!bBothStruts || !bBothFoils)
    {
        World->DestroyWorld(false);
        return false;
    }

    // Invisible, noncolliding preview pieces are not gameplay physics attachments.
    for (int32 Index = 0; Index < 2; ++Index)
    {
        const FString Label = FString::Printf(TEXT("Preview support %d"), Index);
        TestEqual(*(Label + TEXT(" has no collision")), Struts[Index]->GetCollisionEnabled(),
            ECollisionEnabled::NoCollision);
    }

    // Hidden hydrofoil support is mandatory outside of deployed review poses.
    for (int32 Index = 0; Index < 2; ++Index)
    {
        TestFalse(*FString::Printf(TEXT("Skyborne support %d hidden"), Index), Struts[Index]->IsVisible());
        TestFalse(*FString::Printf(TEXT("Skyborne hydrofoil %d hidden"), Index), Foils[Index]->IsVisible());
    }

    TestTrue(TEXT("Skyborne to Seaborne starts"), Ship->RequestForm(EAureateWakeForm::Seaborne));
    TestFalse(TEXT("Cannot interrupt transition"), Ship->RequestForm(EAureateWakeForm::Submersible));

    // Mid-transition refresh must keep each piece attached to the moving foil proxy.
    Ship->Tick(Ship->TransitionSeconds * 0.5f);
    for (int32 Index = 0; Index < 2; ++Index)
    {
        const float Side = Index == 0 ? -1.f : 1.f;
        const FVector HullAnchor(0.f, Side * 60.f, -30.f);
        const FVector ExpectedFoil(0.f, Side * 80.f, -92.5f);
        const FVector Midpoint = (HullAnchor + ExpectedFoil) * 0.5f;
        TestTrue(*FString::Printf(TEXT("Foil %d advances halfway to Seaborne"), Index),
            FVector::Dist(Foils[Index]->GetRelativeLocation(), ExpectedFoil) < 0.15f);
        TestTrue(*FString::Printf(TEXT("Support %d follows the actual moving foil"), Index),
            FVector::Dist(Struts[Index]->GetRelativeLocation(),
                (HullAnchor + Foils[Index]->GetRelativeLocation()) * 0.5f) < 0.15f);
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
        TestTrue(*(Label + TEXT(" hydrofoil really deployed")),
            FVector::Dist(Foils[Index]->GetRelativeLocation(), FoilCenter) < 0.15f);
        TestTrue(*(Label + TEXT(" remains visible")), Struts[Index]->IsVisible());
        TestTrue(*(Label + TEXT(" connects hull and foil centers")),
            FVector::Dist(Struts[Index]->GetRelativeLocation(), Midpoint) < 0.15f);
        TestTrue(*(Label + TEXT(" scales to endpoint span")),
            FMath::Abs(Struts[Index]->GetRelativeScale3D().X - Length / 100.f) < 0.005f);
        TestTrue(*(Label + TEXT(" aligns its cube X axis to span")),
            FVector::DotProduct(Struts[Index]->GetRelativeRotation().Vector(),
                Span.GetSafeNormal()) > 0.995f);
        const FTransform StrutTransform = Struts[Index]->GetRelativeTransform();
        // The temporary mesh is the engine's 100cm-centered BasicShapes cube.
        // Exact local endpoints +/-50cm must agree with both proxy attachment centers.
        TestTrue(*(Label + TEXT(" inboard tip reaches hull proxy")),
            FVector::Dist(StrutTransform.TransformPosition(FVector(-50.f, 0.f, 0.f)),
                HullAnchor) < 0.2f);
        TestTrue(*(Label + TEXT(" outboard tip reaches hydrofoil center")),
            FVector::Dist(StrutTransform.TransformPosition(FVector(50.f, 0.f, 0.f)),
                FoilCenter) < 0.2f);
    }

    TestFalse(TEXT("Orbiter request still refused"), Ship->RequestForm(EAureateWakeForm::Orbiter));
    TestTrue(TEXT("Seaborne to Submersible starts"), Ship->RequestForm(EAureateWakeForm::Submersible));
    Ship->Tick(Ship->TransitionSeconds * 0.5f);
    for (int32 Index = 0; Index < 2; ++Index)
    {
        TestTrue(*FString::Printf(TEXT("Support %d remains visible during fold"), Index),
            Struts[Index]->IsVisible());
    }
    Ship->Tick(Ship->TransitionSeconds + 0.2f);
    TestEqual(TEXT("Submersible reached"), Ship->GetCurrentForm(), EAureateWakeForm::Submersible);
    for (int32 Index = 0; Index < 2; ++Index)
    {
        TestFalse(*FString::Printf(TEXT("Submersible support %d hidden"), Index),
            Struts[Index]->IsVisible());
        TestFalse(*FString::Printf(TEXT("Submersible foil %d hidden"), Index),
            Foils[Index]->IsVisible());
    }
    TestFalse(TEXT("Cannot complete an inactive ordinary transition"),
        Ship->FinishOrdinaryPreviewTransitionForReview());

    // Exercise reverse deployment so stale hidden flags cannot survive re-entry.
    TestTrue(TEXT("Submersible to Seaborne starts"),
        Ship->RequestForm(EAureateWakeForm::Seaborne));
    Ship->Tick(Ship->TransitionSeconds + 0.2f);
    TestEqual(TEXT("Return to Seaborne"), Ship->GetCurrentForm(), EAureateWakeForm::Seaborne);
    for (int32 Index = 0; Index < 2; ++Index)
    {
        TestTrue(*FString::Printf(TEXT("Return support %d visible"), Index),
            Struts[Index]->IsVisible());
        TestTrue(*FString::Printf(TEXT("Return hydrofoil %d visible"), Index),
            Foils[Index]->IsVisible());
    }
    TestTrue(TEXT("Seaborne to Skyborne starts"), Ship->RequestForm(EAureateWakeForm::Skyborne));
    Ship->Tick(Ship->TransitionSeconds + 0.2f);
    TestEqual(TEXT("Skyborne restored"), Ship->GetCurrentForm(), EAureateWakeForm::Skyborne);
    for (int32 Index = 0; Index < 2; ++Index)
    {
        TestFalse(*FString::Printf(TEXT("Restored Skyborne support %d hidden"), Index),
            Struts[Index]->IsVisible());
        TestFalse(*FString::Printf(TEXT("Restored Skyborne hydrofoil %d hidden"), Index),
            Foils[Index]->IsVisible());
    }

    World->DestroyWorld(false);
    return true;
}
#endif
