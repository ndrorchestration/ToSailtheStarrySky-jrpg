#include "AureateWakePreviewActor.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
    void SetupPreviewMesh(UStaticMeshComponent* Component, UStaticMesh* Shape)
    {
        Component->SetStaticMesh(Shape);
        Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Component->SetCastShadow(true);
    }
}

AAureateWakePreviewActor::AAureateWakePreviewActor()
{
    PrimaryActorTick.bCanEverTick = true;
    VesselRoot = CreateDefaultSubobject<USceneComponent>(TEXT("VesselRoot"));
    RootComponent = VesselRoot;

    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    UStaticMesh* Shape = Cube.Succeeded() ? Cube.Object : nullptr;

    Hull = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Hull"));
    Hull->SetupAttachment(VesselRoot);
    SetupPreviewMesh(Hull, Shape);
    Hull->SetRelativeScale3D(FVector(8.0, 1.5, 0.65));

    ForwardBridge = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ForwardBridge"));
    ForwardBridge->SetupAttachment(VesselRoot);
    SetupPreviewMesh(ForwardBridge, Shape);
    ForwardBridge->SetRelativeLocation(FVector(240, 0, 95));
    ForwardBridge->SetRelativeScale3D(FVector(2.1, 1.1, 1.1));

    // Exactly four persistent, independently articulated, dragonfly-derived wings.
    for (int32 Index = 0; Index < 4; ++Index)
    {
        const FName Name(*FString::Printf(TEXT("DragonflyWing_%d"), Index + 1));
        UStaticMeshComponent* Wing = CreateDefaultSubobject<UStaticMeshComponent>(Name);
        Wing->SetupAttachment(VesselRoot);
        SetupPreviewMesh(Wing, Shape);
        Wings.Add(Wing);
    }

    for (int32 Index = 0; Index < 2; ++Index)
    {
        const FName Name(*FString::Printf(TEXT("Hydrofoil_%d"), Index + 1));
        UStaticMeshComponent* Foil = CreateDefaultSubobject<UStaticMeshComponent>(Name);
        Foil->SetupAttachment(VesselRoot);
        SetupPreviewMesh(Foil, Shape);
        Hydrofoils.Add(Foil);
    }
    SnapToForm(EAureateWakeForm::Skyborne);
}

void AAureateWakePreviewActor::BeginPlay()
{
    Super::BeginPlay();
    RefreshWingMeshes();
    RefreshWingMaterials();
}

void AAureateWakePreviewActor::RefreshWingMeshes()
{
    if (!AuthoredWingMesh)
    {
        return; // Preserve intentionally temporary cubes until a reviewed mesh is provided.
    }
    for (UStaticMeshComponent* Wing : Wings)
    {
        if (Wing) Wing->SetStaticMesh(AuthoredWingMesh);
    }
}

FTransform AAureateWakePreviewActor::WingPose(EAureateWakeForm Form, int32 WingIndex)
{
    // The mesh origin is the HINGE at local X=0; its long axis extends to +X.
    // Rotations swing the SAME four wings away from their fixed hull mounts.
    const bool bForwardWing = WingIndex < 2;
    const float Side = (WingIndex % 2 == 0) ? -1.f : 1.f;
    FVector Position = FVector::ZeroVector;
    FRotator Rotation = FRotator::ZeroRotator;
    FVector Scale = FVector::OneVector;

    switch (Form)
    {
    case EAureateWakeForm::Skyborne:
        Position = FVector(bForwardWing ? 155.f : -165.f, Side * 72.f, 45.f);
        Rotation = FRotator(6.f, Side * (bForwardWing ? 84.f : 112.f), Side * 8.f);
        Scale = FVector(3.25f, 1.05f, 1.f);
        break;
    case EAureateWakeForm::Seaborne:
        Position = FVector(bForwardWing ? 155.f : -165.f, Side * 72.f, 40.f);
        Rotation = FRotator(28.f, Side * (bForwardWing ? 70.f : 110.f), Side * 36.f);
        Scale = FVector(2.25f, 0.85f, 1.f);
        break;
    case EAureateWakeForm::Submersible:
        // Distinct front/back hinge orientations tuck membranes lengthwise on hull.
        Position = FVector(bForwardWing ? 150.f : -155.f, Side * 73.f, 25.f);
        Rotation = FRotator(0.f, Side * (bForwardWing ? 12.f : 168.f), Side * 78.f);
        Scale = FVector(bForwardWing ? 1.65f : 1.55f, 0.42f, 1.f);
        break;
    case EAureateWakeForm::Orbiter:
        // Same physical root-tip mesh for all four EQUAL sails.
        // Fixed hull-facing mounts, +X bow undisturbed.
        Position = WingIndex == 0 ? FVector(0, 0, 50) :
                   WingIndex == 1 ? FVector(0, 0, -50) :
                   WingIndex == 2 ? FVector(0, -78, 0) : FVector(0, 78, 0);
        Rotation = WingIndex == 0 ? FRotator(90.f, 0.f, 0.f) :
                   WingIndex == 1 ? FRotator(-90.f, 0.f, 0.f) :
                   WingIndex == 2 ? FRotator(0.f, -90.f, 0.f) :
                                    FRotator(0.f, 90.f, 0.f);
        Scale = FVector(3.6f, 1.15f, 1.f);
        break;
    default:
        // Public caller validates the enum; fall back to a neutral pose.
        break;
    }
    return FTransform(Rotation, Position, Scale);
}

FTransform AAureateWakePreviewActor::FoilPose(EAureateWakeForm Form, int32 FoilIndex)
{
    const float Side = FoilIndex == 0 ? -1.f : 1.f;
    const bool bDeployed = Form == EAureateWakeForm::Seaborne;
    return FTransform(FRotator(0, 0, bDeployed ? 0.f : 80.f),
        FVector(0, Side * 80.f, bDeployed ? -140.f : -45.f),
        FVector(2.1f, 0.75f, 0.10f));
}

FTransform AAureateWakePreviewActor::Interpolate(const FTransform& Start, const FTransform& End, float Alpha)
{
    return FTransform(FQuat::Slerp(Start.GetRotation(), End.GetRotation(), Alpha).GetNormalized(),
        FMath::Lerp(Start.GetLocation(), End.GetLocation(), Alpha),
        FMath::Lerp(Start.GetScale3D(), End.GetScale3D(), Alpha));
}

void AAureateWakePreviewActor::RefreshWingMaterials()
{
    DynamicWingMaterials.Reset();
    if (!WingMaterial)
    {
        return;
    }
    for (UStaticMeshComponent* Wing : Wings)
    {
        UMaterialInstanceDynamic* Dynamic = UMaterialInstanceDynamic::Create(WingMaterial, this);
        Wing->SetMaterial(0, Dynamic);
        Dynamic->SetScalarParameterValue(TEXT("OrbiterSailBlend"), OrbiterSailBlend);
        DynamicWingMaterials.Add(Dynamic);
    }
}

void AAureateWakePreviewActor::SnapToForm(EAureateWakeForm Form)
{
    for (int32 Index = 0; Index < Wings.Num(); ++Index)
    {
        Wings[Index]->SetRelativeTransform(WingPose(Form, Index));
    }
    for (int32 Index = 0; Index < Hydrofoils.Num(); ++Index)
    {
        Hydrofoils[Index]->SetRelativeTransform(FoilPose(Form, Index));
        Hydrofoils[Index]->SetVisibility(Form == EAureateWakeForm::Seaborne);
    }
    OrbiterSailBlend = Form == EAureateWakeForm::Orbiter ? 1.f : 0.f;
    for (UMaterialInstanceDynamic* Dynamic : DynamicWingMaterials)
    {
        if (Dynamic) Dynamic->SetScalarParameterValue(TEXT("OrbiterSailBlend"), OrbiterSailBlend);
    }
    CurrentForm = Form;
    TargetForm = Form;
    bTransitioning = false;
}

bool AAureateWakePreviewActor::RequestForm(EAureateWakeForm RequestedForm)
{
    if (!FMath::IsWithinInclusive(static_cast<int32>(RequestedForm), 0, 3) ||
        Wings.Num() != 4 || Hydrofoils.Num() != 2 ||
        bTransitioning || RequestedForm == CurrentForm ||
        (RequestedForm == EAureateWakeForm::Orbiter && !bAllowOrbiterPreview))
    {
        return false;
    }

    TargetForm = RequestedForm;
    StartSailBlend = OrbiterSailBlend;
    TargetSailBlend = RequestedForm == EAureateWakeForm::Orbiter ? 1.f : 0.f;
    TransitionElapsed = 0.f;
    StartWingTransforms.Reset();
    TargetWingTransforms.Reset();
    StartFoilTransforms.Reset();
    TargetFoilTransforms.Reset();

    for (int32 Index = 0; Index < Wings.Num(); ++Index)
    {
        StartWingTransforms.Add(Wings[Index]->GetRelativeTransform());
        TargetWingTransforms.Add(WingPose(RequestedForm, Index));
    }
    for (int32 Index = 0; Index < Hydrofoils.Num(); ++Index)
    {
        StartFoilTransforms.Add(Hydrofoils[Index]->GetRelativeTransform());
        TargetFoilTransforms.Add(FoilPose(RequestedForm, Index));
        Hydrofoils[Index]->SetVisibility(true);
    }
    bTransitioning = true;
    return true;
}

void AAureateWakePreviewActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!bTransitioning)
    {
        return;
    }

    TransitionElapsed += FMath::Max(0.f, DeltaSeconds);
    const float T = FMath::Clamp(TransitionElapsed / FMath::Max(0.1f, TransitionSeconds), 0.f, 1.f);
    const float Smooth = T * T * (3.f - 2.f * T);
    OrbiterSailBlend = FMath::Lerp(StartSailBlend, TargetSailBlend, Smooth);
    for (UMaterialInstanceDynamic* Dynamic : DynamicWingMaterials)
    {
        if (Dynamic) Dynamic->SetScalarParameterValue(TEXT("OrbiterSailBlend"), OrbiterSailBlend);
    }
    for (int32 Index = 0; Index < Wings.Num(); ++Index)
    {
        Wings[Index]->SetRelativeTransform(Interpolate(StartWingTransforms[Index], TargetWingTransforms[Index], Smooth));
    }
    for (int32 Index = 0; Index < Hydrofoils.Num(); ++Index)
    {
        Hydrofoils[Index]->SetRelativeTransform(Interpolate(StartFoilTransforms[Index], TargetFoilTransforms[Index], Smooth));
    }
    if (T >= 1.f)
    {
        SnapToForm(TargetForm);
    }
}
