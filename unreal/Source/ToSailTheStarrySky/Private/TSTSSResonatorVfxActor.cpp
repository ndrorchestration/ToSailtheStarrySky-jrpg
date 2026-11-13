#include "TSTSSResonatorVfxActor.h"

#include "Components/InstancedStaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
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
        {TEXT("Ender_Centering"), TEXT("VFX.Ender.Centering"), 9, FLinearColor(0.35f, 0.94f, 0.73f)},
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
    UMaterialInterface* Material = nullptr;
#if WITH_EDITOR
    // Presentation-only A/B override in two precisely named standalone
    // research scenes. Never promote the preview copy to a production
    // effect, mutate the immutable historical material, or grant a skill.
    const UWorld* ReviewWorld = GetWorld();
    if (ReviewWorld &&
        (ReviewWorld->WorldType == EWorldType::PIE ||
         ReviewWorld->WorldType == EWorldType::Game) &&
        ReviewWorld->GetNetMode() == NM_Standalone &&
        ReviewWorld->GetOutermost() &&
        ReviewWorld->GetOutermost()->GetName().StartsWith(
            TEXT("/Game/TSTSS/Review/")))
    {
        const FString Scene = UGameplayStatics::GetCurrentLevelName(
            ReviewWorld, true);
        if (Scene == TEXT("L_VS06_ShoreMagicEnemyGear_Review") ||
            Scene == TEXT("L_EnderResonatorFocusReview_V2"))
        {
            Material = LoadObject<UMaterialInterface>(
                nullptr,
                TEXT("/Game/TSTSS/Review/ResonatorMaterialV1/"
                     "M_ResonatorGlow_InstancedReview."
                     "M_ResonatorGlow_InstancedReview"));
            if (Material)
            {
                UE_LOG(LogTemp, Display,
                    TEXT("TSTSS_RESONATOR_REVIEW_INSTANCED_MATERIAL_APPLIED scene=%s story_unchanged=1"),
                    *Scene);
            }
            else
            {
                UE_LOG(LogTemp, Warning,
                    TEXT("TSTSS_RESONATOR_REVIEW_INSTANCED_MATERIAL_HOLD missing_copy scene=%s"),
                    *Scene);
            }
        }
    }
#endif
    if (!Material)
    {
        Material = LoadObject<UMaterialInterface>(
            nullptr, TEXT("/Game/TSTSS/Magic/M_ResonatorGlow.M_ResonatorGlow"));
    }
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
    Duration = Style == 9 ? 2.7f :
        (Style == 1 || Style == 7 || Style == 8) ? 2.45f : 2.15f;
    TargetOffset = RelativeTarget;
    bReviewInstance = bReview;
    bPlaying = true;
    if (UMaterialInstanceDynamic* Dynamic = Cast<UMaterialInstanceDynamic>(RingMeshes->GetMaterial(0)))
    {
        Dynamic->SetVectorParameterValue(TEXT("Tint"), CueTint);
        Dynamic->SetScalarParameterValue(TEXT("Glow"), 14.f);
    }
    CastLight->SetLightColor(CueTint);
    CastLight->SetAttenuationRadius(Style == 0
        ? static_cast<float>(FTSTSSBattleSkillSystem::ResonantPulseRadiusCm)
        : 540.f);
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
    const bool bAtOrigin = (Style == 0 || Style == 6 || Style == 9);
    const float TravelT = FMath::Clamp(T * 1.45f, 0.f, 1.f);
    const FVector Center = bAtOrigin ? FVector::ZeroVector :
        bAtTarget ? TargetOffset : FMath::Lerp(FVector::ZeroVector, TargetOffset, TravelT);
    const FVector CenterRaised = Center + FVector(0.f, 0.f, 95.f);
    const float Pulse = 0.5f + 0.5f * FMath::Sin(TimeSeconds * 16.f);

    if (Style == 0)
    {
        // Resonant Pulse is a TRUE 3D spherical expanding shockwave, never
        // three flat concentric rings. Distribute visible points across a
        // Fibonacci sphere; the mesh points are cosmetic and collision-free.
        // Mechanical target admission is separately owned by
        // FTSTSSBattleSkillSystem::TryUseResonantPulseArea.
        const float WaveT = FMath::Clamp(T * 1.28f, 0.f, 1.f);
        const float EaseOut = 1.f - FMath::Pow(1.f - WaveT, 3.f);
        const float RadiusCm = FMath::Lerp(25.f,
            static_cast<float>(FTSTSSBattleSkillSystem::ResonantPulseRadiusCm),
            EaseOut);
        constexpr float GoldenAngle = 2.3999632297286533f;
        for (int32 Index = 0; Index < 72; ++Index)
        {
            const float H = 1.f - 2.f * (static_cast<float>(Index) + .5f) / 72.f;
            const float Azimuth = GoldenAngle * static_cast<float>(Index);
            const float Planar = FMath::Sqrt(FMath::Max(0.f, 1.f - H * H));
            const FVector Unit(Planar * FMath::Cos(Azimuth),
                Planar * FMath::Sin(Azimuth), H);
            const FVector Point = Unit * RadiusCm;
            const float Size = (0.045f + 0.030f * Pulse) * Visibility;
            RingMeshes->UpdateInstanceTransform(Index,
                FTransform(FRotator::ZeroRotator, Point, FVector(Size)),
                false, Index == 71, true);
        }
        for (int32 Index = 0; Index < 32; ++Index)
        {
            const float H = 1.f - 2.f * (static_cast<float>(Index) + .5f) / 32.f;
            const float Azimuth = GoldenAngle * (static_cast<float>(Index) + 0.5f)
                + TimeSeconds * 1.4f;
            const float Planar = FMath::Sqrt(FMath::Max(0.f, 1.f - H * H));
            const FVector Unit(Planar * FMath::Cos(Azimuth),
                Planar * FMath::Sin(Azimuth), H);
            const FVector Trail = Unit * RadiusCm * (0.85f + .08f * Pulse);
            const float Size = (0.024f + .025f * Pulse) * Visibility;
            MoteMeshes->UpdateInstanceTransform(Index,
                FTransform(FRotator::ZeroRotator, Trail, FVector(Size)),
                false, Index == 31, true);
        }
        CoreMesh->UpdateInstanceTransform(0,
            FTransform(FRotator::ZeroRotator, FVector::ZeroVector,
                FVector((.10f + .06f * Pulse) * Visibility)),
            false, true, true);
        CastLight->SetRelativeLocation(FVector::ZeroVector);
        CastLight->SetIntensity(2500.f * Visibility * (1.f - .45f * WaveT));
        return;
    }

    for (int32 Ring = 0; Ring < 3; ++Ring)
    {
        const float Delay = static_cast<float>(Ring) * 0.16f;
        const float Phase = FMath::Clamp((T - Delay) / (1.f - Delay), 0.f, 1.f);
        const float Radius = Style == 9
            ? 70.f + 440.f * Phase :
            (Style == 0 || Style == 7 || Style == 8)
            ? 35.f + 240.f * Phase : 40.f + 70.f * Phase;
        const float Tilt = (Style == 3 || Style == 4) ? 0.6f * Ring : 0.0f;
        for (int32 Segment = 0; Segment < 24; ++Segment)
        {
            const float A = 2.f * PI * static_cast<float>(Segment) / 24.f +
                            2.5f * TimeSeconds * ((Ring % 2) ? -1.f : 1.f);
            const FVector Point = CenterRaised + Right * (Radius * FMath::Cos(A)) +
                Up * (Radius * FMath::Sin(A)) + Direction * (Tilt * Radius * FMath::Sin(A));
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
        const FVector Trail = CenterRaised + Right * (Spiral * FMath::Cos(A)) +
            Up * (Spiral * FMath::Sin(A)) + Direction * ((Seed - 0.5f) * 150.f);
        const float Size = (0.025f + 0.035f * (0.5f + 0.5f * FMath::Sin(A * 2.f))) * Visibility;
        MoteMeshes->UpdateInstanceTransform(i, FTransform(
            FRotator::ZeroRotator, Trail, FVector(Size)), false, i == 31, true);
    }
    const float CoreScale = (0.12f + 0.12f * Pulse) * Visibility;
    CoreMesh->UpdateInstanceTransform(0, FTransform(FRotator::ZeroRotator,
        CenterRaised, FVector(CoreScale)), false, true, true);
    CastLight->SetRelativeLocation(CenterRaised);
    CastLight->SetIntensity((Style == 9 ? 1050.f : 2200.f) *
        Visibility * (0.6f + 0.4f * Pulse));
}
