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

    // Exercise all six ordered ordinary form routes in the *actual* native
    // actor, rather than relying on engine-free proxy arithmetic. Sample
    // 20 intermediate phases per route, plus the completed endpoint.
    // This intentionally does NOT simulate swept geometry or fluid loads.
    const EAureateWakeForm OrdinaryForms[3] = {
        EAureateWakeForm::Skyborne,
        EAureateWakeForm::Seaborne,
        EAureateWakeForm::Submersible
    };
    int32 VerifiedSupportPoses = 0;
    int32 VisibleSupportObservations = 0;
    int32 HiddenSupportObservations = 0;
    for (int32 FromIndex = 0; FromIndex < 3; ++FromIndex)
    {
        for (int32 ToIndex = 0; ToIndex < 3; ++ToIndex)
        {
            if (FromIndex == ToIndex) continue;
            const EAureateWakeForm Start = OrdinaryForms[FromIndex];
            const EAureateWakeForm Finish = OrdinaryForms[ToIndex];
            if (Ship->GetCurrentForm() != Start)
            {
                if (!TestTrue(TEXT("Prepare ordinary route start"), Ship->RequestForm(Start)) ||
                    !TestTrue(TEXT("Finish ordinary route preparation"),
                        Ship->FinishOrdinaryPreviewTransitionForReview()))
                {
                    World->DestroyWorld(false);
                    return false;
                }
            }
            if (!TestTrue(TEXT("Six-route native transition starts"), Ship->RequestForm(Finish)))
            {
                World->DestroyWorld(false);
                return false;
            }
            const bool bRouteUsesHydrofoils =
                Start == EAureateWakeForm::Seaborne || Finish == EAureateWakeForm::Seaborne;
            const float StartZ = Start == EAureateWakeForm::Seaborne ? -140.f : -45.f;
            const float FinishZ = Finish == EAureateWakeForm::Seaborne ? -140.f : -45.f;
            const float StepSeconds = FMath::Max(.1f, Ship->TransitionSeconds) / 20.f;
            for (int32 Step = 0; Step < 20; ++Step)
            {
                Ship->Tick(Step == 0 ? 0.f : StepSeconds);
                const float Alpha = static_cast<float>(Step) / 20.f;
                const float Smooth = Alpha * Alpha * (3.f - 2.f * Alpha);
                const float ExpectedZ = FMath::Lerp(StartZ, FinishZ, Smooth);
                for (int32 Index = 0; Index < 2; ++Index)
                {
                    const float Side = Index == 0 ? -1.f : 1.f;
                    const FVector Anchor(0.f, Side * 60.f, -30.f);
                    const FVector ExpectedFoil(0.f, Side * 80.f, ExpectedZ);
                    const FVector ExpectedMid = (Anchor + ExpectedFoil) * .5f;
                    const FVector Span = ExpectedFoil - Anchor;
                    const FTransform Proxy = Struts[Index]->GetRelativeTransform();
                    const FString Prefix = FString::Printf(
                        TEXT("Ordinary route %d to %d step %d side %d: "),
                        FromIndex, ToIndex, Step, Index);
                    TestEqual(*(Prefix + TEXT("foil visibility matches route")),
                        Foils[Index]->IsVisible(), bRouteUsesHydrofoils);
                    TestEqual(*(Prefix + TEXT("strut visibility matches route")),
                        Struts[Index]->IsVisible(), bRouteUsesHydrofoils);
                    TestTrue(*(Prefix + TEXT("actual foil center matches eased path")),
                        FVector::Dist(Foils[Index]->GetRelativeLocation(), ExpectedFoil) < 0.2f);
                    if (bRouteUsesHydrofoils)
                    {
                        TestTrue(*(Prefix + TEXT("actual support center matches proxy span")),
                            FVector::Dist(Struts[Index]->GetRelativeLocation(), ExpectedMid) < 0.2f);
                        TestTrue(*(Prefix + TEXT("support length matches moving endpoints")),
                            FMath::Abs(Struts[Index]->GetRelativeScale3D().X - Span.Size()/100.f) < 0.005f);
                        TestTrue(*(Prefix + TEXT("inboard cube end contacts proxy anchor")),
                            FVector::Dist(Proxy.TransformPosition(FVector(-50.f,0.f,0.f)), Anchor) < 0.3f);
                        TestTrue(*(Prefix + TEXT("outboard cube end contacts foil center")),
                            FVector::Dist(Proxy.TransformPosition(FVector(50.f,0.f,0.f)), ExpectedFoil) < 0.3f);
                        ++VisibleSupportObservations;
                    }
                    else
                    {
                        // Hidden support transforms need not track the invisible
                        // foil. Only visibility and foil pose are authoritative here.
                        ++HiddenSupportObservations;
                    }
                    ++VerifiedSupportPoses;
                }
            }
            if (!TestTrue(TEXT("Complete sampled ordinary transition"),
                Ship->FinishOrdinaryPreviewTransitionForReview()))
            {
                World->DestroyWorld(false);
                return false;
            }
            TestEqual(TEXT("Correct end form of sampled route"), Ship->GetCurrentForm(), Finish);
            for (int32 Index = 0; Index < 2; ++Index)
            {
                const bool bDeployed = Finish == EAureateWakeForm::Seaborne;
                TestEqual(TEXT("Completed foil visibility matches destination"),
                    Foils[Index]->IsVisible(), bDeployed);
                TestEqual(TEXT("Completed support visibility matches destination"),
                    Struts[Index]->IsVisible(), bDeployed);
                if (bDeployed) ++VisibleSupportObservations;
                else ++HiddenSupportObservations;
                ++VerifiedSupportPoses;
            }
            TestFalse(TEXT("Orbiter remains unavailable after ordinary route"),
                Ship->RequestForm(EAureateWakeForm::Orbiter));
        }
    }
    TestEqual(TEXT("Six routes x 21 phases x two supports"), VerifiedSupportPoses, 252);
    TestEqual(TEXT("Visible support observations on Seaborne routes"), VisibleSupportObservations, 164);
    TestEqual(TEXT("Hidden support observations on non-Seaborne routes"), HiddenSupportObservations, 88);

    World->DestroyWorld(false);
    return true;
}
#endif
