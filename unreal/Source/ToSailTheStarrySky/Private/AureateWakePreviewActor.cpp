#include "AureateWakePreviewActor.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "Math/RotationMatrix.h"

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
    OriginalCubeWingMesh = Shape;

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
    // Structural struts stay invisible until a reviewed mesh and authored pose are both selected.
    for (int32 Index = 0; Index < 4; ++Index)
    {
        const FName Name(*FString::Printf(TEXT("WingRootSupport_%d"), Index + 1));
        UStaticMeshComponent* Support = CreateDefaultSubobject<UStaticMeshComponent>(Name);
        Support->SetupAttachment(VesselRoot);
        Support->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Support->SetCastShadow(true);
        Support->SetVisibility(false);
        WingRootSupports.Add(Support);
    }
    SnapToForm(EAureateWakeForm::Skyborne);
}

void AAureateWakePreviewActor::BeginPlay()
{
    Super::BeginPlay();
    RefreshWingMeshes();
    RefreshWingMaterials();
    RefreshRootSupports();
}

void AAureateWakePreviewActor::RefreshWingMeshes()
{
    // Orbiter authored-wing interpolation has not cleared the hull/bridge envelope.
    // Keep the currently displayed cube preview rather than switching mid-Orbiter.
    if (bUseRootPivotedWingPose && CurrentForm == EAureateWakeForm::Orbiter)
    {
        return;
    }

    // Selecting an authored GLB without opting into its root-pivot poses must
    // NOT stretch it through transforms calibrated for the old 100cm cubes.
    UStaticMesh* MeshToDisplay = bUseRootPivotedWingPose
        ? AuthoredWingMesh.Get() : OriginalCubeWingMesh.Get();
    if (!MeshToDisplay)
    {
        return;
    }
    for (UStaticMeshComponent* Wing : Wings)
    {
        if (Wing) Wing->SetStaticMesh(MeshToDisplay);
    }
    if (!bTransitioning)
    {
        SnapToForm(CurrentForm); // Recompose the same preview form without story events.
    }
    RefreshRootSupports();
}

void AAureateWakePreviewActor::RefreshRootSupports()
{
    const bool bVisible = bUseRootPivotedWingPose && AuthoredWingMesh &&
        AuthoredRootSupportMesh && CurrentForm != EAureateWakeForm::Orbiter;
    for (UStaticMeshComponent* Support : WingRootSupports)
    {
        if (!Support) continue;
        Support->SetStaticMesh(bVisible ? AuthoredRootSupportMesh.Get() : nullptr);
        Support->SetVisibility(bVisible);
    }
    UpdateRootSupportTransforms();
}

void AAureateWakePreviewActor::UpdateRootSupportTransforms()
{
    // The authored 100-cm +X strut starts at the hull flank and extends to
    // the moving wing-root location. It is purely a visual telescoping member.
    if (!bUseRootPivotedWingPose || !AuthoredWingMesh ||
        WingRootSupports.Num() != 4 || Wings.Num() != 4) return;
    for (int32 Index = 0; Index < 4; ++Index)
    {
        UStaticMeshComponent* Support = WingRootSupports[Index];
        UStaticMeshComponent* Wing = Wings[Index];
        if (!Support || !Wing) continue;
        const float Side = (Index % 2 == 0) ? -1.f : 1.f;
        const FVector Root = Wing->GetRelativeLocation();
        const FVector HullAnchor(Root.X, Side * 73.f, 18.f);
        const FVector Link = Root - HullAnchor;
        const float Length = Link.Size();
        if (!FMath::IsFinite(Length) || Length < 1.f)
        {
            Support->SetVisibility(false);
            continue;
        }
        // No shared actor/physics state; strut follows the existing wing root.
        const FQuat Direction = FRotationMatrix::MakeFromX(Link).ToQuat();
        Support->SetRelativeTransform(FTransform(Direction, HullAnchor,
            FVector(Length / 100.f, 1.f, 1.f)));
    }
}

FTransform AAureateWakePreviewActor::WingPose(EAureateWakeForm Form, int32 WingIndex)
{
    const bool bForwardWing = WingIndex < 2;
    const float Side = (WingIndex % 2 == 0) ? -1.f : 1.f;
    FVector Position;
    FRotator Rotation;
    FVector Scale(3.1f, 0.04f, 1.05f); // Placeholder panels; NOT approved membrane geometry.

    switch (Form)
    {
    case EAureateWakeForm::Skyborne:
        Position = FVector(bForwardWing ? 150.f : -190.f, Side * 235.f, 35.f);
        Rotation = FRotator(0.f, Side * (bForwardWing ? 26.f : -24.f), Side * 8.f);
        Scale = FVector(2.9f, 2.3f, 0.05f);
        break;
    case EAureateWakeForm::Seaborne:
        Position = FVector(bForwardWing ? 145.f : -185.f, Side * 175.f, 95.f);
        Rotation = FRotator(0.f, Side * 18.f, Side * 36.f);
        Scale = FVector(2.7f, 1.35f, 0.05f);
        break;
    case EAureateWakeForm::Submersible:
        Position = FVector(bForwardWing ? 145.f : -180.f, Side * 105.f, 15.f);
        Rotation = FRotator(0.f, Side * 12.f, Side * 75.f);
        Scale = FVector(2.5f, 0.58f, 0.05f); // Remain visibly tucked, never disappear.
        break;
    case EAureateWakeForm::Orbiter:
        // Forward remains +X. Four equal sails form +Z, -Z, -Y, +Y cross.
        Position = WingIndex == 0 ? FVector(0, 0, 315) :
                   WingIndex == 1 ? FVector(0, 0, -315) :
                   WingIndex == 2 ? FVector(0, -315, 0) : FVector(0, 315, 0);
        // Local X axis is the blade length: pitch for vertical blades, yaw for port/starboard blades.
        Rotation = WingIndex < 2 ? FRotator(90.f, 0.f, 0.f) : FRotator(0.f, 90.f, 0.f);
        Scale = FVector(2.5f, 1.7f, 0.055f); // Same scale for all four sails.
        break;
    }
    return FTransform(Rotation, Position, Scale);
}

FTransform AAureateWakePreviewActor::RootPivotedWingPose(EAureateWakeForm Form, int32 WingIndex)
{
    // Review-only geometry: authored 280cm span extends from the root along local +X.
    // Do not use the centered 100cm cube transforms for this mesh.
    const bool bForward = WingIndex < 2;
    const float Side = WingIndex % 2 == 0 ? -1.f : 1.f;
    const float RootX = bForward ? 155.f : -180.f;
    const float RootY = Side * 112.f;
    FVector Position(RootX, RootY, 48.f);
    FRotator Rotation;
    FVector Scale(1.f, 1.f, 1.f);

    switch (Form)
    {
    case EAureateWakeForm::Skyborne:
        // Outboard dragonfly span with modest fore/aft sweep and dihedral.
        Rotation = FRotator(0.f, Side * (bForward ? 80.f : 100.f), Side * 7.f);
        break;
    case EAureateWakeForm::Seaborne:
        // Fold upward above the sea while leaving all four wing components present.
        Position.Z = 82.f;
        Rotation = FRotator(32.f, Side * (bForward ? 75.f : 105.f), Side * 50.f);
        Scale = FVector(.94f, .82f, 1.f);
        break;
    case EAureateWakeForm::Submersible:
        // Tuck wings lengthwise along the hull, visibly retained, never hidden.
        Position.Z = 16.f;
        Rotation = FRotator(0.f, Side * (bForward ? 23.f : 157.f), Side * 72.f);
        Scale = FVector(.78f, .38f, .95f);
        break;
    case EAureateWakeForm::Orbiter:
        // Opt-in review ONLY. Four equal root-pivoted sails in cardinal directions.
        // Hull orientation remains +X, separate from any story/unlock authority.
        Scale = FVector(1.f, 1.f, 1.f);
        if (WingIndex == 0)
        {
            Position = FVector(0.f, 0.f, 130.f);
            Rotation = FRotator(90.f, 0.f, 0.f);
        }
        else if (WingIndex == 1)
        {
            Position = FVector(0.f, 0.f, -130.f);
            Rotation = FRotator(-90.f, 0.f, 0.f);
        }
        else if (WingIndex == 2)
        {
            Position = FVector(0.f, -130.f, 0.f);
            Rotation = FRotator(0.f, -90.f, 0.f);
        }
        else
        {
            Position = FVector(0.f, 130.f, 0.f);
            Rotation = FRotator(0.f, 90.f, 0.f);
        }
        break;
    }
    return FTransform(Rotation, Position, Scale);
}

FTransform AAureateWakePreviewActor::WingPoseForMesh(EAureateWakeForm Form, int32 WingIndex) const
{
    return bUseRootPivotedWingPose && AuthoredWingMesh
        ? RootPivotedWingPose(Form, WingIndex)
        : WingPose(Form, WingIndex);
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
        Wings[Index]->SetRelativeTransform(WingPoseForMesh(Form, Index));
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
    UpdateRootSupportTransforms();
    CurrentForm = Form;
    TargetForm = Form;
    bTransitioning = false;
}

bool AAureateWakePreviewActor::RequestForm(EAureateWakeForm RequestedForm)
{
    if (!FMath::IsWithinInclusive(static_cast<int32>(RequestedForm), 0, 3) ||
        Wings.Num() != 4 || Hydrofoils.Num() != 2 ||
        (bUseRootPivotedWingPose && !AuthoredWingMesh) ||
        // Root-pivoted authored GLB crosses provisional hull/bridge during
        // direct Orbiter interpolation. Do not attempt until a safe route exists.
        (bUseRootPivotedWingPose && (RequestedForm == EAureateWakeForm::Orbiter || CurrentForm == EAureateWakeForm::Orbiter)) ||
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
        TargetWingTransforms.Add(WingPoseForMesh(RequestedForm, Index));
    }
    for (int32 Index = 0; Index < Hydrofoils.Num(); ++Index)
    {
        StartFoilTransforms.Add(Hydrofoils[Index]->GetRelativeTransform());
        TargetFoilTransforms.Add(FoilPose(RequestedForm, Index));
        // Keep deployment/retraction visible only on routes involving the sea form.
        Hydrofoils[Index]->SetVisibility(CurrentForm == EAureateWakeForm::Seaborne ||
            RequestedForm == EAureateWakeForm::Seaborne);
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
    UpdateRootSupportTransforms();
    if (T >= 1.f)
    {
        SnapToForm(TargetForm);
    }
}
