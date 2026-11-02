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
    OriginalCubeWingMesh = Shape;

    Hull = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Hull"));
    Hull->SetupAttachment(VesselRoot);
    SetupPreviewMesh(Hull, Shape);
    Hull->SetRelativeScale3D(FVector(8.0, 1.5, 0.65));

    // Coupled review-only pivot: identity at baseline, so the original static
    // forward bridge remains in precisely the same position until opted in.
    BridgeHabitationPivot = CreateDefaultSubobject<USceneComponent>(TEXT("BridgeHabitationPivot"));
    BridgeHabitationPivot->SetupAttachment(VesselRoot);

    ForwardBridge = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ForwardBridge"));
    ForwardBridge->SetupAttachment(BridgeHabitationPivot);
    SetupPreviewMesh(ForwardBridge, Shape);
    ForwardBridge->SetRelativeLocation(FVector(240, 0, 95));
    ForwardBridge->SetRelativeScale3D(FVector(2.1, 1.1, 1.1));

    LivingQuartersEnvelope = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LivingQuartersEnvelope"));
    LivingQuartersEnvelope->SetupAttachment(BridgeHabitationPivot);
    SetupPreviewMesh(LivingQuartersEnvelope, Shape);
    LivingQuartersEnvelope->SetRelativeLocation(FVector(0, 0, -25));
    LivingQuartersEnvelope->SetRelativeScale3D(FVector(2.2, 1.15, .35));
    LivingQuartersEnvelope->SetVisibility(false); // No added default art or habitation geometry.

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

    // Four removable visual brackets: only visible with explicitly opted-in
    // authored wings, not a claim of physical or pressure-rated mount design.
    for (int32 Index = 0; Index < 4; ++Index)
    {
        const FName Name(*FString::Printf(TEXT("ReviewWingRootBracket_%d"), Index + 1));
        UStaticMeshComponent* Bracket = CreateDefaultSubobject<UStaticMeshComponent>(Name);
        Bracket->SetupAttachment(VesselRoot);
        SetupPreviewMesh(Bracket, Shape);
        Bracket->SetVisibility(false);
        WingRootMounts.Add(Bracket);
    }
    for (int32 Index = 0; Index < 2; ++Index)
    {
        const FName Name(*FString::Printf(TEXT("ReviewHydrofoilStrut_%d"), Index + 1));
        UStaticMeshComponent* Strut = CreateDefaultSubobject<UStaticMeshComponent>(Name);
        Strut->SetupAttachment(VesselRoot);
        SetupPreviewMesh(Strut, Shape);
        Strut->SetVisibility(false);
        HydrofoilStruts.Add(Strut);
    }
    SnapToForm(EAureateWakeForm::Skyborne);
}

void AAureateWakePreviewActor::BeginPlay()
{
    Super::BeginPlay();
    RefreshWingMeshes();
    RefreshWingMaterials();
    RefreshCentralBridgeHabitationReview();
}

FQuat AAureateWakePreviewActor::HabitationReviewRotationForForm(EAureateWakeForm Form) const
{
    // Artist-editable review poses; ZeroRotator defaults avoid inventing canon.
    switch (Form)
    {
    case EAureateWakeForm::Skyborne:
        return SkyborneHabitationReviewRotation.Quaternion();
    case EAureateWakeForm::Seaborne:
        return SeaborneHabitationReviewRotation.Quaternion();
    case EAureateWakeForm::Submersible:
        return SubmersibleHabitationReviewRotation.Quaternion();
    default:
        return FQuat::Identity; // Orbiter/Starbourne remains independently gated.
    }
}

bool AAureateWakePreviewActor::RefreshCentralBridgeHabitationReview()
{
    if (bTransitioning || CurrentForm == EAureateWakeForm::Orbiter ||
        !BridgeHabitationPivot || !ForwardBridge || !LivingQuartersEnvelope)
    {
        return false;
    }

    if (bPreviewCentralBridgeHabitation)
    {
        // Provisional position only: central shared pivot, dome above quarters.
        // Real pressure seals, access corridors and vessel clearance are HOLD.
        BridgeHabitationPivot->SetRelativeLocation(FVector(0, 0, 50));
        ForwardBridge->SetRelativeLocation(FVector(0, 0, 80));
        LivingQuartersEnvelope->SetVisibility(true);
        BridgeHabitationPivot->SetRelativeRotation(HabitationReviewRotationForForm(CurrentForm));
    }
    else
    {
        // Exact original default silhouette: static bridge at (240,0,95).
        BridgeHabitationPivot->SetRelativeLocation(FVector::ZeroVector);
        BridgeHabitationPivot->SetRelativeRotation(FQuat::Identity);
        ForwardBridge->SetRelativeLocation(FVector(240, 0, 95));
        LivingQuartersEnvelope->SetVisibility(false);
    }
    return true;
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

void AAureateWakePreviewActor::UpdateWingRootMounts()
{
    const bool bReviewMountsVisible = bUseRootPivotedWingPose && AuthoredWingMesh &&
        CurrentForm != EAureateWakeForm::Orbiter && TargetForm != EAureateWakeForm::Orbiter;
    for (int32 Index = 0; Index < WingRootMounts.Num(); ++Index)
    {
        UStaticMeshComponent* Bracket = WingRootMounts[Index];
        if (!Bracket) continue;
        Bracket->SetVisibility(bReviewMountsVisible);
        if (!bReviewMountsVisible || !Wings.IsValidIndex(Index) || !Wings[Index]) continue;
        const FVector WingPivot = Wings[Index]->GetRelativeLocation();
        const float Side = Index % 2 == 0 ? -1.f : 1.f;
        // Provisional 150cm-wide hull uses +/-75cm half-width. Clamp the
        // inboard endpoint to the current proxy hull top; no load calculations.
        const FVector HullAnchor(WingPivot.X, Side * 72.f,
            FMath::Clamp(WingPivot.Z, -28.f, 28.f));
        const FVector Span = WingPivot - HullAnchor;
        const float Length = Span.Size();
        if (Length <= KINDA_SMALL_NUMBER)
        {
            Bracket->SetVisibility(false);
            continue;
        }
        Bracket->SetRelativeLocation((WingPivot + HullAnchor) * .5f);
        Bracket->SetRelativeRotation(Span.ToOrientationQuat());
        Bracket->SetRelativeScale3D(FVector(Length / 100.f, .09f, .09f));
    }
}

void AAureateWakePreviewActor::UpdateHydrofoilStruts()
{
    for (int32 Index = 0; Index < HydrofoilStruts.Num(); ++Index)
    {
        UStaticMeshComponent* Strut = HydrofoilStruts[Index];
        if (!Strut) continue;
        if (!Hydrofoils.IsValidIndex(Index) || !Hydrofoils[Index] || !Hydrofoils[Index]->IsVisible())
        {
            Strut->SetVisibility(false);
            continue;
        }
        const FVector FoilPosition = Hydrofoils[Index]->GetRelativeLocation();
        const float Side = Index == 0 ? -1.f : 1.f;
        const FVector HullAnchor(0.f, Side * 60.f, -30.f);
        const FVector Span = FoilPosition - HullAnchor;
        const float Length = Span.Size();
        Strut->SetVisibility(Length > KINDA_SMALL_NUMBER);
        if (Length <= KINDA_SMALL_NUMBER) continue;
        Strut->SetRelativeLocation((HullAnchor + FoilPosition) * .5f);
        Strut->SetRelativeRotation(Span.ToOrientationQuat());
        Strut->SetRelativeScale3D(FVector(Length / 100.f, .12f, .12f));
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
    CurrentForm = Form;
    TargetForm = Form;
    bTransitioning = false;
    bHabitationReviewLatchedForTransition = false;
    // Apply opt-in or restore the original forward bridge unconditionally.
    // Editing the exposed review flag during animation must not leave a
    // half-rotated dome stranded after the wing motion completes.
    RefreshCentralBridgeHabitationReview();
    UpdateWingRootMounts();
    UpdateHydrofoilStruts();
}

bool AAureateWakePreviewActor::RequestForm(EAureateWakeForm RequestedForm)
{
    if (!FMath::IsWithinInclusive(static_cast<int32>(RequestedForm), 0, 3) ||
        Wings.Num() != 4 || Hydrofoils.Num() != 2 ||
        (bUseRootPivotedWingPose && !AuthoredWingMesh) ||
        // Root-pivoted authored GLB crosses provisional hull/bridge during
        // direct Orbiter interpolation. Do not attempt until a safe route exists.
        (bUseRootPivotedWingPose && (RequestedForm == EAureateWakeForm::Orbiter || CurrentForm == EAureateWakeForm::Orbiter)) ||
        // The rotating habitation envelope has not cleared Orbiter's sail
        // and hull geometry. The independent visual preview flag never
        // authorizes this additional moving assembly in Orbiter.
        (bPreviewCentralBridgeHabitation &&
            (RequestedForm == EAureateWakeForm::Orbiter || CurrentForm == EAureateWakeForm::Orbiter)) ||
        bTransitioning || RequestedForm == CurrentForm ||
        (RequestedForm == EAureateWakeForm::Orbiter && !bAllowOrbiterPreview))
    {
        return false;
    }

    // Reconcile any idle inspector/Blueprint toggle before sampling the pose.
    // The snapshot below is then stable even if properties change mid-flight.
    if (!RefreshCentralBridgeHabitationReview()) return false;
    bHabitationReviewLatchedForTransition = bPreviewCentralBridgeHabitation;
    TargetForm = RequestedForm;
    StartHabitationReviewRotation = BridgeHabitationPivot
        ? BridgeHabitationPivot->GetRelativeRotation().Quaternion() : FQuat::Identity;
    TargetHabitationReviewRotation = bHabitationReviewLatchedForTransition
        ? HabitationReviewRotationForForm(RequestedForm) : FQuat::Identity;
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
    // Foils are deployed in Seaborne only. Keep them hidden for direct
    // Skyborne <-> Submersible travel; show during entry/exit from Seaborne
    // so the temporary folding animation remains visible.
    const bool bReviewFoilsInMotion =
        CurrentForm == EAureateWakeForm::Seaborne ||
        RequestedForm == EAureateWakeForm::Seaborne;
    for (int32 Index = 0; Index < Hydrofoils.Num(); ++Index)
    {
        StartFoilTransforms.Add(Hydrofoils[Index]->GetRelativeTransform());
        TargetFoilTransforms.Add(FoilPose(RequestedForm, Index));
        Hydrofoils[Index]->SetVisibility(bReviewFoilsInMotion);
    }
    bTransitioning = true;
    // Synchronize temporary mounts and hydrofoil struts immediately with
    // the requested transition; no one-frame visibility pop before Tick.
    // These remain collision-free, noncanonical review proxies.
    UpdateWingRootMounts();
    UpdateHydrofoilStruts();
    return true;
}

bool AAureateWakePreviewActor::FinishOrdinaryPreviewTransitionForReview()
{
    if (!bTransitioning || CurrentForm == EAureateWakeForm::Orbiter ||
        TargetForm == EAureateWakeForm::Orbiter) return false;
    Tick(FMath::Max(.1f, TransitionSeconds) + .2f);
    return !bTransitioning;
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
    if (bHabitationReviewLatchedForTransition && BridgeHabitationPivot)
    {
        BridgeHabitationPivot->SetRelativeRotation(FQuat::Slerp(
            StartHabitationReviewRotation, TargetHabitationReviewRotation, Smooth).GetNormalized());
    }
    for (int32 Index = 0; Index < Wings.Num(); ++Index)
    {
        Wings[Index]->SetRelativeTransform(Interpolate(StartWingTransforms[Index], TargetWingTransforms[Index], Smooth));
    }
    for (int32 Index = 0; Index < Hydrofoils.Num(); ++Index)
    {
        Hydrofoils[Index]->SetRelativeTransform(Interpolate(StartFoilTransforms[Index], TargetFoilTransforms[Index], Smooth));
    }
    UpdateWingRootMounts();
    UpdateHydrofoilStruts();
    if (T >= 1.f)
    {
        SnapToForm(TargetForm);
    }
}
