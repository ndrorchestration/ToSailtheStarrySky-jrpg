#include "TSTSSResonatorVfxActor.h"

#include "Components/InstancedStaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#if WITH_EDITOR
#include "Engine/Engine.h"
#include "GameFramework/PlayerController.h"
#include "Camera/CameraActor.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"
#endif
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "UObject/UObjectGlobals.h"

namespace
{
struct FCueDesign
{
    FName Skill;
    FName Visual;
    int32 Style;
    FLinearColor Color;
};

// Locked mapping of *presentation* names. This is not a skill unlock list.
// Styles: 0 pulse, 1 lance, 2 mend, 3 thread, 4 break, 5 psychic,
// 6 self-focus, 7 harmonic correspondence synergy, 8 thought synergy.
const FCueDesign* FindCue(FName CueId)
{
    static const FCueDesign Cues[] = {
        {TEXT("Ender_ResonantPulse"), TEXT("VFX.Ender.ResonantPulse"), 0, FLinearColor(0.03f, 0.68f, 1.0f)},
        {TEXT("Ender_TuningLance"), TEXT("VFX.Ender.TuningLance"), 1, FLinearColor(0.11f, 0.94f, 0.96f)},
        {TEXT("Ender_EchoMend"), TEXT("VFX.Ender.EchoMend"), 2, FLinearColor(0.12f, 1.0f, 0.58f)},
        {TEXT("Ender_CorrespondenceThread"), TEXT("VFX.Ender.CorrespondenceThread"), 3, FLinearColor(0.6f, 0.32f, 1.0f)},
        {TEXT("Ender_LatticeBreak"), TEXT("VFX.Ender.LatticeBreak"), 4, FLinearColor(0.85f, 0.28f, 1.0f)},
        {TEXT("Ender_MindRipple"), TEXT("VFX.Ender.MindRipple"), 5, FLinearColor(0.98f, 0.52f, 0.22f)},
        {TEXT("Ender_FocusHarmonic"), TEXT("VFX.Ender.FocusHarmonic"), 6, FLinearColor(1.0f, 0.76f, 0.24f)},
        {TEXT("Ender_ConcordanceBurst"), TEXT("VFX.Ender.ConcordanceBurst"), 7, FLinearColor(0.15f, 0.94f, 0.85f)},
        {TEXT("Ender_ThoughtChord"), TEXT("VFX.Ender.ThoughtChord"), 8, FLinearColor(1.0f, 0.4f, 0.68f)}
    };
    for (const FCueDesign& Cue : Cues)
    {
        if (Cue.Visual == CueId) return &Cue;
    }
    return nullptr;
}
} // namespace

ATSTSSResonatorVfxActor::ATSTSSResonatorVfxActor()
{
    PrimaryActorTick.bCanEverTick = true;
    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    RootComponent = SceneRoot;
    RingMeshes = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("HarmonicRings"));
    MoteMeshes = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("OrbitingMotes"));
    CoreMesh = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("SpellCore"));
    CastLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("SpellLight"));
    RingMeshes->SetupAttachment(SceneRoot);
    MoteMeshes->SetupAttachment(SceneRoot);
    CoreMesh->SetupAttachment(SceneRoot);
    CastLight->SetupAttachment(SceneRoot);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    if (Sphere.Succeeded())
    {
        RingMeshes->SetStaticMesh(Sphere.Object);
        MoteMeshes->SetStaticMesh(Sphere.Object);
        CoreMesh->SetStaticMesh(Sphere.Object);
    }
    for (UInstancedStaticMeshComponent* Part : {RingMeshes.Get(), MoteMeshes.Get(), CoreMesh.Get()})
    {
        Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Part->SetCastShadow(false);
        Part->SetMobility(EComponentMobility::Movable);
    }
    CastLight->SetIntensity(0.f);
    CastLight->SetAttenuationRadius(540.f);
    CastLight->SetCastShadows(false);
}

bool ATSTSSResonatorVfxActor::IsKnownCue(FName CueId)
{
    return FindCue(CueId) != nullptr;
}

bool ATSTSSResonatorVfxActor::IsAcceptedEnderCue(const FTSTSSBattleSkillCue& AcceptedCue)
{
    const FCueDesign* Def = FindCue(AcceptedCue.VfxCueId);
    return Def && AcceptedCue.ActorId == TEXT("Ender") &&
           !AcceptedCue.TargetId.IsNone() && AcceptedCue.SkillId == Def->Skill;
}

void ATSTSSResonatorVfxActor::BeginPlay()
{
    Super::BeginPlay();
    UMaterialInterface* Material = LoadObject<UMaterialInterface>(
        nullptr, TEXT("/Game/TSTSS/Magic/M_ResonatorGlow.M_ResonatorGlow"));
    if (!Material)
    {
        Material = LoadObject<UMaterialInterface>(
            nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    }
    if (Material)
    {
        UMaterialInstanceDynamic* Dynamic = UMaterialInstanceDynamic::Create(Material, this);
        RingMeshes->SetMaterial(0, Dynamic);
        MoteMeshes->SetMaterial(0, Dynamic);
        CoreMesh->SetMaterial(0, Dynamic);
    }
    for (int32 i = 0; i < 72; ++i) RingMeshes->AddInstance(FTransform::Identity);
    for (int32 i = 0; i < 32; ++i) MoteMeshes->AddInstance(FTransform::Identity);
    CoreMesh->AddInstance(FTransform::Identity);
    if (!PreviewCueId.IsNone() && GetWorld() && GetWorld()->IsGameWorld())
    {
        StartCue(PreviewCueId, PreviewTargetOffset, true);
    }
}

bool ATSTSSResonatorVfxActor::StartCue(FName CueId, const FVector& RelativeTarget, bool bReview)
{
    const FCueDesign* Def = FindCue(CueId);
    if (!Def || RelativeTarget.ContainsNaN()) return false;
    RunningCue = CueId;
    Style = Def->Style;
    CueTint = Def->Color;
    Age = 0.f;
    Duration = (Style == 1 || Style == 7 || Style == 8) ? 2.45f : 2.15f;
    TargetOffset = RelativeTarget;
    bReviewInstance = bReview;
    bPlaying = true;
    if (UMaterialInstanceDynamic* Dynamic = Cast<UMaterialInstanceDynamic>(RingMeshes->GetMaterial(0)))
    {
        Dynamic->SetVectorParameterValue(TEXT("Tint"), CueTint);
        Dynamic->SetScalarParameterValue(TEXT("Glow"), 14.f);
    }
    CastLight->SetLightColor(CueTint);
    UpdateVisuals(0.f);
    return true;
}

ATSTSSResonatorVfxActor* ATSTSSResonatorVfxActor::SpawnFromAcceptedCue(
    UWorld* World, const FTSTSSBattleSkillCue& AcceptedCue,
    const FVector& CasterWorld, const FVector& TargetWorld)
{
    // This renderer consumes an accepted combat result; it never grants access itself.
    if (!World || !World->IsGameWorld() || !IsAcceptedEnderCue(AcceptedCue) ||
        CasterWorld.ContainsNaN() || TargetWorld.ContainsNaN()) return nullptr;
    ATSTSSResonatorVfxActor* Effect = World->SpawnActor<ATSTSSResonatorVfxActor>(
        ATSTSSResonatorVfxActor::StaticClass(), FTransform(FRotator::ZeroRotator, CasterWorld));
    if (!Effect) return nullptr;
    if (!Effect->StartCue(AcceptedCue.VfxCueId, TargetWorld - CasterWorld, false))
    {
        Effect->Destroy();
        return nullptr;
    }
    return Effect;
}

void ATSTSSResonatorVfxActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!bPlaying) return;
#if WITH_EDITOR
    // Explicit opt-in diagnostic: never run in shipped builds or from combat casts.
    // Delaying the screenshot avoids startup-frame captures before renderer readiness.
    if (bReviewInstance && !bReviewCaptureRequested &&
        PreviewCueId == FName(TEXT("VFX.Ender.ResonantPulse")) &&
        FParse::Param(FCommandLine::Get(), TEXT("TSTSSResonatorCapture")))
    {
        ReviewCaptureElapsed += FMath::Max(0.f, DeltaSeconds);
        if (ReviewCaptureElapsed >= 3.f)
        {
            bReviewCaptureRequested = true;
            APlayerController* Controller = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr;
            const AActor* View = Controller ? Controller->GetViewTarget() : nullptr;
            UE_LOG(LogTemp, Display,
                TEXT("TSTSS_RESONATOR_REVIEW_CAPTURE camera=%s rings=%d motes=%d material=%s center=%s"),
                View ? *View->GetName() : TEXT("None"),
                RingMeshes->GetInstanceCount(), MoteMeshes->GetInstanceCount(),
                RingMeshes->GetMaterial(0) ? *RingMeshes->GetMaterial(0)->GetName() : TEXT("None"),
                *GetActorLocation().ToString());
            // FScreenshotRequest is queued for the next viewport frame; the
            // engine Exec console command did not create a delayed capture in
            // unattended standalone review. Never request in shipping builds.
            FScreenshotRequest::RequestScreenshot(false, true);
            UE_LOG(LogTemp, Display, TEXT("TSTSS_RESONATOR_SCREENSHOT_PENDING=%d"),
                FScreenshotRequest::IsScreenshotRequested() ? 1 : 0);
        }
    }
    // Explicit opt-in time-series proof; no ordinary combat or non-Editor effect.
    if (bReviewInstance && PreviewCueId == FName(TEXT("VFX.Ender.ResonantPulse")) &&
        FParse::Param(FCommandLine::Get(), TEXT("TSTSSResonatorCaptureSequence")) &&
        ReviewSequenceStage < 3)
    {
        ReviewSequenceElapsed += FMath::Max(0.f, DeltaSeconds);
        static constexpr float ReviewSampleSeconds[3] = {2.8f, 3.35f, 3.9f};
        if (ReviewSequenceElapsed >= ReviewSampleSeconds[ReviewSequenceStage] &&
            !FScreenshotRequest::IsScreenshotRequested())
        {
            UE_LOG(LogTemp, Display,
                TEXT("TSTSS_RESONATOR_SEQUENCE_CAPTURE stage=%d elapsed=%.3f cue_age=%.3f duration=%.3f"),
                ReviewSequenceStage, ReviewSequenceElapsed, Age, Duration);
            FScreenshotRequest::RequestScreenshot(false, true);
            ++ReviewSequenceStage;
        }
    }
    // Editor-only screenshot review: nine deterministic known cue actors,
    // no combat requests, saved map writes or skill/admission mutations.
    if (bReviewInstance && PreviewCueId == FName(TEXT("VFX.Ender.ResonantPulse")) &&
        FParse::Param(FCommandLine::Get(), TEXT("TSTSSResonatorCueSweep")) &&
        ReviewSweepIndex < 9)
    {
        static const FName ReviewCues[9] = {
            TEXT("VFX.Ender.ResonantPulse"), TEXT("VFX.Ender.TuningLance"),
            TEXT("VFX.Ender.EchoMend"), TEXT("VFX.Ender.CorrespondenceThread"),
            TEXT("VFX.Ender.LatticeBreak"), TEXT("VFX.Ender.MindRipple"),
            TEXT("VFX.Ender.FocusHarmonic"), TEXT("VFX.Ender.ConcordanceBurst"),
            TEXT("VFX.Ender.ThoughtChord")
        };
        ReviewSweepElapsed += FMath::Max(0.f, DeltaSeconds);
        const float StageStart = 2.7f + ReviewSweepIndex * 1.0f;
        if (ReviewSweepElapsed >= StageStart && !FScreenshotRequest::IsScreenshotRequested())
        {
            ATSTSSResonatorVfxActor* Selected = nullptr;
            for (TActorIterator<ATSTSSResonatorVfxActor> It(GetWorld()); It; ++It)
            {
                if (It->bReviewInstance && It->PreviewCueId == ReviewCues[ReviewSweepIndex])
                {
                    Selected = *It;
                    break;
                }
            }
            APlayerController* Controller = GetWorld()->GetFirstPlayerController();
            AActor* Camera = Controller ? Controller->GetViewTarget() : nullptr;
            if (Selected && Camera && Camera->IsA<ACameraActor>())
            {
                if (!bReviewSweepCameraMoved)
                {
                    // During opt-in capture, show only the selected review actor
                    // so distant grid neighbors cannot masquerade as its particles.
                    // HiddenInGame is transient, never saved to a map or asset.
                    for (TActorIterator<ATSTSSResonatorVfxActor> It(GetWorld()); It; ++It)
                    {
                        if (It->bReviewInstance)
                        {
                            It->SetActorHiddenInGame(It->PreviewCueId != ReviewCues[ReviewSweepIndex]);
                        }
                    }
                    // Center targeted/traveling visuals at their effect position,
                    // not the caster. Pulse and Focus Harmonic stay caster-centered.
                    const float CueT = FMath::Clamp(Selected->Age /
                        FMath::Max(Selected->Duration, 0.1f), 0.f, 1.f);
                    const bool bAtTarget = Selected->Style == 2 ||
                        Selected->Style == 4 || Selected->Style == 5;
                    const bool bAtCaster = Selected->Style == 0 || Selected->Style == 6;
                    const float TravelT = FMath::Clamp(CueT * 1.45f, 0.f, 1.f);
                    const FVector Offset = bAtCaster ? FVector::ZeroVector :
                        bAtTarget ? Selected->TargetOffset :
                        FMath::Lerp(FVector::ZeroVector, Selected->TargetOffset, TravelT);
                    const FVector Aim = Selected->GetActorLocation() + Offset +
                        FVector(0.f, 0.f, 95.f);
                    const FVector Location = Aim + FVector(0.f, -610.f, 175.f);
                    Camera->SetActorLocationAndRotation(Location, (Aim - Location).Rotation());
                    Controller->SetViewTarget(Camera);
                    bReviewSweepCameraMoved = true;
                    ReviewSweepCameraMovedAt = ReviewSweepElapsed;
                    UE_LOG(LogTemp, Display, TEXT("TSTSS_RESONATOR_SWEEP_FOCUS stage=%d cue=%s"),
                        ReviewSweepIndex, *ReviewCues[ReviewSweepIndex].ToString());
                }
                else if (ReviewSweepElapsed - ReviewSweepCameraMovedAt >= 0.24f)
                {
                    UE_LOG(LogTemp, Display, TEXT("TSTSS_RESONATOR_SWEEP_CAPTURE stage=%d cue=%s age=%.3f"),
                        ReviewSweepIndex, *ReviewCues[ReviewSweepIndex].ToString(), Selected->Age);
                    FScreenshotRequest::RequestScreenshot(false, true);
                    ++ReviewSweepIndex;
                    bReviewSweepCameraMoved = false;
                }
            }
            else if (!bReviewSweepBlockedLogged)
            {
                bReviewSweepBlockedLogged = true;
                UE_LOG(LogTemp, Error, TEXT("TSTSS_RESONATOR_SWEEP_BLOCKED missing cue or camera stage=%d"),
                    ReviewSweepIndex);
            }
        }
    }
#endif
    Age += FMath::Max(0.f, DeltaSeconds);
    if (Age >= Duration)
    {
        if (!bReviewInstance || !bLoopReview)
        {
            bPlaying = false;
            CastLight->SetIntensity(0.f);
            Destroy();
            return;
        }
        Age = FMath::Fmod(Age, Duration);
    }
    UpdateVisuals(Age);
}

void ATSTSSResonatorVfxActor::UpdateVisuals(float TimeSeconds)
{
    const float T = FMath::Clamp(TimeSeconds / FMath::Max(Duration, 0.1f), 0.f, 1.f);
    const float FadeIn = FMath::Min(1.f, T * 10.f);
    const float FadeOut = FMath::Min(1.f, (1.f - T) * 6.f);
    const float Visibility = FMath::Max(0.02f, FadeIn * FadeOut);
    FVector Direction = TargetOffset.GetSafeNormal();
    if (Direction.IsNearlyZero()) Direction = FVector::ForwardVector;
    FVector Right = FVector::CrossProduct(Direction, FVector::UpVector).GetSafeNormal();
    if (Right.IsNearlyZero()) Right = FVector::RightVector;
    const FVector Up = FVector::CrossProduct(Right, Direction).GetSafeNormal();
    const bool bAtTarget = (Style == 2 || Style == 4 || Style == 5);
    const bool bAtOrigin = (Style == 0 || Style == 6);
    const float TravelT = FMath::Clamp(T * 1.45f, 0.f, 1.f);
    const FVector Center = bAtOrigin ? FVector::ZeroVector :
        bAtTarget ? TargetOffset : FMath::Lerp(FVector::ZeroVector, TargetOffset, TravelT);
    const FVector CenterRaised = Center + FVector(0.f, 0.f, 95.f);
    const float Pulse = 0.5f + 0.5f * FMath::Sin(TimeSeconds * 16.f);

    for (int32 Ring = 0; Ring < 3; ++Ring)
    {
        const float Delay = static_cast<float>(Ring) * 0.16f;
        // A sphere needs the same expanding radius on all three orthogonal great circles.
        // Other cue styles retain their existing staggered ring timing.
        const float Phase = (Style == 0) ? T :
            FMath::Clamp((T - Delay) / (1.f - Delay), 0.f, 1.f);
        const float Radius = (Style == 0 || Style == 7 || Style == 8)
            ? 35.f + 240.f * Phase : 40.f + 70.f * Phase;
        const float Tilt = (Style == 3 || Style == 4) ? 0.6f * Ring : 0.0f;
        // Resonant Pulse: XY equator + XZ and YZ meridians, all on one
        // caster-centered expanding spherical shell (not stacked latitude hoops).
        for (int32 Segment = 0; Segment < 24; ++Segment)
        {
            const float A = 2.f * PI * static_cast<float>(Segment) / 24.f +
                            2.5f * TimeSeconds * ((Ring % 2) ? -1.f : 1.f);
            const float CosA = FMath::Cos(A);
            const float SinA = FMath::Sin(A);
            const FVector SphereUnit = Ring == 0 ? FVector(CosA, SinA, 0.f) :
                Ring == 1 ? FVector(CosA, 0.f, SinA) : FVector(0.f, CosA, SinA);
            const FVector Point = (Style == 0)
                ? CenterRaised + Radius * SphereUnit
                : CenterRaised + Right * (Radius * CosA) +
                    Up * (Radius * SinA) + Direction * (Tilt * Radius * SinA);
            const float Size = (0.045f + 0.035f * Pulse) * Visibility;
            RingMeshes->UpdateInstanceTransform(Ring * 24 + Segment,
                FTransform(FRotator::ZeroRotator, Point, FVector(Size)),
                false, Ring == 2 && Segment == 23, true);
        }
    }
    for (int32 i = 0; i < 32; ++i)
    {
        const float Seed = static_cast<float>(i) / 32.f;
        const float A = Seed * 2.f * PI + TimeSeconds * (2.8f + (Style % 3));
        const float Spiral = 65.f + Seed * 150.f + 22.f * FMath::Sin(12.f * T + Seed * 16.f);
        const float SphereZ = 1.f - 2.f * (Seed + 0.5f / 32.f);
        const float SphereXY = FMath::Sqrt(FMath::Max(0.f, 1.f - SphereZ * SphereZ));
        const float SphereRadius = 35.f + 240.f * T;
        const FVector Trail = (Style == 0)
            ? CenterRaised + SphereRadius * FVector(SphereXY * FMath::Cos(A),
                SphereXY * FMath::Sin(A), SphereZ)
            : CenterRaised + Right * (Spiral * FMath::Cos(A)) +
                Up * (Spiral * FMath::Sin(A)) + Direction * ((Seed - 0.5f) * 150.f);
        const float Size = (0.025f + 0.035f * (0.5f + 0.5f * FMath::Sin(A * 2.f))) * Visibility;
        MoteMeshes->UpdateInstanceTransform(i, FTransform(
            FRotator::ZeroRotator, Trail, FVector(Size)), false, i == 31, true);
    }
    const float CoreScale = (0.12f + 0.12f * Pulse) * Visibility;
    CoreMesh->UpdateInstanceTransform(0, FTransform(FRotator::ZeroRotator,
        CenterRaised, FVector(CoreScale)), false, true, true);
    CastLight->SetRelativeLocation(CenterRaised);
    CastLight->SetIntensity(2200.f * Visibility * (0.6f + 0.4f * Pulse));
}
