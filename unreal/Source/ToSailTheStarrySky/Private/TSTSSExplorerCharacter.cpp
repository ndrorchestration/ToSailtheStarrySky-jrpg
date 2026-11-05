#include "TSTSSExplorerCharacter.h"
#include "TSTSSMilestoneActor.h"
#include "TSTSSPersistence.h"
#include "TSTSSInteractionReach.h"
#include "TSTSSSaveGame.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/InputComponent.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Kismet/GameplayStatics.h"
#include "CollisionQueryParams.h"
#include "Components/PrimitiveComponent.h"
#include "HAL/IConsoleManager.h"

namespace
{
#if !UE_BUILD_SHIPPING
// Read-only, opt-in telemetry for one actual E press. Never alter reach,
// line-of-sight, story order, or shipping gameplay to diagnose a review map.
TAutoConsoleVariable<int32> CVarFirstWakeInteractionTrace(
    TEXT("tstss.FirstWake.InteractionTrace"), 0,
    TEXT("Enable First Wake review interaction ray/target diagnostics (default 0)."),
    ECVF_Default);
#endif

void TraceFirstWakeReviewInteraction(
    const TCHAR* Outcome, const FVector& Pawn, const FVector& Camera,
    const FVector& Forward, const FHitResult* Hit, const float Reach, const int32 BeatBefore,
    const UTSTSSFirstWakeState* State)
{
#if !UE_BUILD_SHIPPING
    if (CVarFirstWakeInteractionTrace.GetValueOnGameThread() == 0)
    {
        return;
    }
    const AActor* Target = Hit ? Hit->GetActor() : nullptr;
    const float PawnToHit = Hit ? FVector::Dist(Pawn, Hit->ImpactPoint) : -1.f;
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_FIRST_WAKE_INTERACTION_DIAG outcome=%s pawn=%s camera=%s forward=%s hit_actor=%s hit_component=%s impact=%s pawn_hit_cm=%.1f max_reach_cm=%.1f beat_before=%d beat_after=%d"),
        Outcome, *Pawn.ToCompactString(), *Camera.ToCompactString(),
        *Forward.ToCompactString(), *GetNameSafe(Target),
        *GetNameSafe(Hit ? Hit->GetComponent() : nullptr),
        *(Hit ? Hit->ImpactPoint.ToCompactString() : FString(TEXT("None"))),
        PawnToHit, Reach, BeatBefore,
        IsValid(State) ? static_cast<int32>(State->GetCurrentBeat()) : -1);
#else
    (void)Outcome;
    (void)Pawn;
    (void)Camera;
    (void)Forward;
    (void)Hit;
    (void)Reach;
    (void)BeatBefore;
    (void)State;
#endif
}

// This review slot captures story/inspection state, not pawn location.
void ShowFirstWakeReviewSaveLoadStatus(const bool bLoad, const bool bSucceeded)
{
#if !UE_BUILD_SHIPPING
    if (!GEngine) return;
    const TCHAR* Message = bLoad
        ? (bSucceeded
            ? TEXT("First Wake (review): story progress loaded; position unchanged")
            : TEXT("First Wake (review): load failed; no progress restored"))
        : (bSucceeded
            ? TEXT("First Wake (review): story progress saved; position not saved")
            : TEXT("First Wake (review): save failed; progress not confirmed"));
    GEngine->AddOnScreenDebugMessage(
        -1, 8.f, bSucceeded ? FColor::Green : FColor::Red, Message);
#else
    (void)bLoad;
    (void)bSucceeded;
#endif
}

// Rejected interactions show the current objective, without implying the
// engine determined why the milestone was refused (order, repetition, etc.).
void ShowFirstWakeReviewProtectedSlotWarning(const bool bLoad)
{
#if !UE_BUILD_SHIPPING
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 8.f, FColor::Red,
            bLoad
                ? TEXT("First Wake (review): no quicksave made in this PIE session")
                : TEXT("First Wake (review): existing PIE quicksave protected; refusing overwrite"));
    }
#else
    (void)bLoad;
#endif
}

void ShowFirstWakeReviewBlockedInteraction(const UTSTSSFirstWakeState* State)
{
#if !UE_BUILD_SHIPPING
    if (GEngine && IsValid(State))
    {
        GEngine->AddOnScreenDebugMessage(
            -1, 5.f, FColor::Yellow,
            FString::Printf(TEXT("First Wake (review): no progress; objective: %s"),
                            *State->GetReviewObjectiveText()));
    }
#else
    (void)State;
#endif
}

void ShowFirstWakeReviewObjective(const UTSTSSFirstWakeState* State)
{
#if !UE_BUILD_SHIPPING
    if (GEngine && IsValid(State))
    {
        GEngine->AddOnScreenDebugMessage(
            -1, 8.f, FColor::Cyan,
            FString::Printf(TEXT("First Wake (review): %s  [J to recall]"), *State->GetReviewObjectiveText()));
    }
#else
    (void)State;
#endif
}
}

ATSTSSExplorerCharacter::ATSTSSExplorerCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(GetRootComponent());
    CameraBoom->TargetArmLength = 360.f;
    CameraBoom->bUsePawnControlRotation = true;
    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;
    bUseControllerRotationYaw = false;
    GetCharacterMovement()->bOrientRotationToMovement = true;
}

void ATSTSSExplorerCharacter::BeginPlay()
{
    Super::BeginPlay();
    FirstWakeState = NewObject<UTSTSSFirstWakeState>(this);
    bPIEReviewQuickSlotOwned = false;
    ShowFirstWakeReviewObjective(FirstWakeState);
}

void ATSTSSExplorerCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    check(PlayerInputComponent);
    PlayerInputComponent->BindAxis(TEXT("MoveForward"), this, &ATSTSSExplorerCharacter::MoveForward);
    PlayerInputComponent->BindAxis(TEXT("MoveRight"), this, &ATSTSSExplorerCharacter::MoveRight);
    PlayerInputComponent->BindAxis(TEXT("Turn"), this, &ATSTSSExplorerCharacter::Turn);
    PlayerInputComponent->BindAxis(TEXT("LookUp"), this, &ATSTSSExplorerCharacter::LookUp);
    PlayerInputComponent->BindAction(TEXT("Interact"), IE_Pressed, this, &ATSTSSExplorerCharacter::Interact);
    PlayerInputComponent->BindAction(TEXT("QuickSave"), IE_Pressed, this, &ATSTSSExplorerCharacter::QuickSave);
    PlayerInputComponent->BindAction(TEXT("QuickLoad"), IE_Pressed, this, &ATSTSSExplorerCharacter::QuickLoad);
    PlayerInputComponent->BindAction(TEXT("ReviewObjective"), IE_Pressed, this, &ATSTSSExplorerCharacter::ShowObjectiveReview);
}

void ATSTSSExplorerCharacter::MoveForward(float Value)
{
    if (Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator Yaw(0.f, Controller->GetControlRotation().Yaw, 0.f);
        AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::X), Value);
    }
}
void ATSTSSExplorerCharacter::MoveRight(float Value)
{
    if (Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator Yaw(0.f, Controller->GetControlRotation().Yaw, 0.f);
        AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y), Value);
    }
}
void ATSTSSExplorerCharacter::Turn(float Value) { AddControllerYawInput(Value); }
void ATSTSSExplorerCharacter::LookUp(float Value) { AddControllerPitchInput(Value); }

void ATSTSSExplorerCharacter::Interact()
{
    if (!FirstWakeState || !FollowCamera || !GetWorld()) return;
    const FVector Start = FollowCamera->GetComponentLocation();
    const FVector PawnLocation = GetActorLocation();
    const int32 BeatBefore = static_cast<int32>(FirstWakeState->GetCurrentBeat());
    const FVector Forward = FollowCamera->GetForwardVector();
    const float CameraTraceLength =
        TSTSSInteractionReach::GetCameraTraceLength(Start, PawnLocation, InteractionDistance);
    if (CameraTraceLength <= 0.f)
    {
        TraceFirstWakeReviewInteraction(TEXT("trace_disabled"), PawnLocation, Start,
                                        Forward, nullptr, InteractionDistance, BeatBefore, FirstWakeState);
        return;
    }

    // Trace across the camera boom before applying the *separate* pawn
    // reach check. At a 360 cm boom and 300 cm interact range the old
    // camera-only 300 cm ray could end behind the player entirely.
    const FVector End = Start + Forward * CameraTraceLength;
    FHitResult Hit;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(TSTSSInteract), false, this);
    const bool bTraceHit =
        GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Query);
    const TCHAR* Outcome = TEXT("visibility_miss");
    if (bTraceHit)
    {
        Outcome = TEXT("visibility_hit_non_milestone");
        if (ATSTSSMilestoneActor* Milestone = Cast<ATSTSSMilestoneActor>(Hit.GetActor()))
        {
            Outcome = TEXT("outside_pawn_reach");
            // A longer camera ray never increases interaction reach.
            if (TSTSSInteractionReach::IsInsidePlayerReach(
                    PawnLocation, Hit.ImpactPoint, InteractionDistance))
            {
                if (Milestone->TryActivate(FirstWakeState))
                {
                    Outcome = TEXT("accepted");
                    ShowFirstWakeReviewObjective(FirstWakeState);
                }
                else
                {
                    // A valid, in-reach marker rejected the state transition.
                    // This does not grant progression or claim that E hit when
                    // the camera trace missed or the target was out of reach.
                    Outcome = TEXT("story_or_repeat_rejected");
                    ShowFirstWakeReviewBlockedInteraction(FirstWakeState);
                }
            }
        }
    }
    // One log line per E press, only when the default-off review CVar is enabled.
    // This reports observed ray/target/reach/state outcomes; it never
    // manufactures a hit, advances the beat, or changes collision.
    TraceFirstWakeReviewInteraction(Outcome, PawnLocation, Start, Forward,
                                    bTraceHit ? &Hit : nullptr,
                                    InteractionDistance, BeatBefore, FirstWakeState);
}

void ATSTSSExplorerCharacter::ShowObjectiveReview()
{
    // Read-only recall of the existing short-lived objective cue.
    ShowFirstWakeReviewObjective(FirstWakeState);
}

void ATSTSSExplorerCharacter::QuickSave()
{
    // PIE testing must not write the normal quicksave slot. Never adopt or
    // overwrite a leftover review save from another Editor session.
    const UWorld* World = GetWorld();
    const bool bPIE = World && World->WorldType == EWorldType::PIE;
    const FString Slot = bPIE ? TEXT("tstss_prelude_pie_quick") : TEXT("first_wake_quick");
    if (bPIE && !bPIEReviewQuickSlotOwned &&
        UGameplayStatics::DoesSaveGameExist(Slot, 0))
    {
        ShowFirstWakeReviewProtectedSlotWarning(false);
        return;
    }
    const bool bSaved = SaveFirstWake(Slot);
    if (bPIE && bSaved)
    {
        bPIEReviewQuickSlotOwned = true;
    }
    ShowFirstWakeReviewSaveLoadStatus(false, bSaved);
}

void ATSTSSExplorerCharacter::QuickLoad()
{
    const UWorld* World = GetWorld();
    const bool bPIE = World && World->WorldType == EWorldType::PIE;
    const FString Slot = bPIE ? TEXT("tstss_prelude_pie_quick") : TEXT("first_wake_quick");
    // No stale PIE save from an earlier test session can change this pawn.
    if (bPIE && !bPIEReviewQuickSlotOwned)
    {
        ShowFirstWakeReviewProtectedSlotWarning(true);
        return;
    }
    const bool bLoaded = LoadFirstWake(Slot);
    if (bLoaded)
    {
        ShowFirstWakeReviewObjective(FirstWakeState);
    }
    ShowFirstWakeReviewSaveLoadStatus(true, bLoaded);
}

bool ATSTSSExplorerCharacter::SaveFirstWake(const FString& Slot)
{
    if (!IsValid(FirstWakeState) || !UTSTSSPersistence::IsValidSlotName(Slot))
    {
        return false;
    }

    // This review actor does not own the combat party. An existing save may
    // contain a valid roster (or be corrupt/future-versioned). Never replace
    // such player data with an empty story-only payload. For a validated,
    // roster-free save, reuse its object to preserve other schema fields.
    UTSTSSSaveGame* Save = nullptr;
    if (UGameplayStatics::DoesSaveGameExist(Slot, 0))
    {
        Save = UTSTSSPersistence::LoadProgress(Slot);
        if (!IsValid(Save) || Save->PartyRoster.Num() != 0)
        {
            return false;
        }
    }
    else
    {
        Save = NewObject<UTSTSSSaveGame>(this);
    }
    if (!IsValid(Save))
    {
        return false;
    }

    Save->bFirstWakeStarted = FirstWakeState->HasStarted();
    Save->FirstWakeBeat = FirstWakeState->GetCurrentBeat();
    Save->InspectionMask = FirstWakeState->GetInspectionMask();
    return UTSTSSPersistence::SaveProgress(Slot, Save);
}

bool ATSTSSExplorerCharacter::LoadFirstWake(const FString& Slot)
{
    if (!IsValid(FirstWakeState)) return false;
    const UTSTSSSaveGame* Save = UTSTSSPersistence::LoadProgress(Slot);
    if (!Save) return false;
    return FirstWakeState->Restore(Save->bFirstWakeStarted, Save->FirstWakeBeat, Save->InspectionMask);
}
