#include "TSTSSExplorerCharacter.h"
#include "TSTSSMilestoneActor.h"
#include "TSTSSPersistence.h"
#include "TSTSSInteractionReach.h"
#include "TSTSSSaveGame.h"
#include "TSTSSPartyGearMenuReviewWidget.h"
#include "Blueprint/UserWidget.h"
#include "GameFramework/HUD.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Components/InputComponent.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Kismet/GameplayStatics.h"
#include "CollisionQueryParams.h"
#if WITH_EDITOR
#include "EngineUtils.h"
#endif

namespace
{
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
    // Editor shortcuts may consume or strip modifier state before the game
    // receives the key. Never bind the PIE save action to F5 at all:
    // Shift+F5 must not accidentally trigger a gameplay save.
    // Outside PIE, preserve the existing normal-game F5 action.
    const UWorld* InputWorld = GetWorld();
    if (InputWorld && InputWorld->WorldType == EWorldType::PIE)
    {
        PlayerInputComponent->BindAction(TEXT("PIEReviewQuickSave"), IE_Pressed, this, &ATSTSSExplorerCharacter::QuickSave);
    }
    else if (InputWorld && InputWorld->WorldType == EWorldType::Game)
    {
        PlayerInputComponent->BindAction(TEXT("QuickSave"), IE_Pressed, this, &ATSTSSExplorerCharacter::QuickSave);
    }
    PlayerInputComponent->BindAction(TEXT("QuickLoad"), IE_Pressed, this, &ATSTSSExplorerCharacter::QuickLoad);
    PlayerInputComponent->BindAction(TEXT("ReviewObjective"), IE_Pressed, this, &ATSTSSExplorerCharacter::ShowObjectiveReview);
#if !UE_BUILD_SHIPPING
    // No equipment-review action outside an actual PIE/game world.
    if (InputWorld && (InputWorld->WorldType == EWorldType::PIE ||
                       InputWorld->WorldType == EWorldType::Game))
    {
        PlayerInputComponent->BindAction(
            TEXT("ReviewEquipment"), IE_Pressed, this,
            &ATSTSSExplorerCharacter::ToggleEquipmentReview);
        PlayerInputComponent->BindAction(
            TEXT("ReviewRPGMenu"), IE_Pressed, this,
            &ATSTSSExplorerCharacter::TogglePartyMenuReview);
    }
#endif
}

void ATSTSSExplorerCharacter::MoveForward(float Value)
{
    if (EquipmentReviewMenu && EquipmentReviewMenu->IsInViewport()) return;
    if (Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator Yaw(0.f, Controller->GetControlRotation().Yaw, 0.f);
        AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::X), Value);
    }
}
void ATSTSSExplorerCharacter::MoveRight(float Value)
{
    if (EquipmentReviewMenu && EquipmentReviewMenu->IsInViewport()) return;
    if (Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator Yaw(0.f, Controller->GetControlRotation().Yaw, 0.f);
        AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y), Value);
    }
}
void ATSTSSExplorerCharacter::Turn(float Value)
{
    if (!EquipmentReviewMenu || !EquipmentReviewMenu->IsInViewport())
        AddControllerYawInput(Value);
}
void ATSTSSExplorerCharacter::LookUp(float Value)
{
    if (!EquipmentReviewMenu || !EquipmentReviewMenu->IsInViewport())
        AddControllerPitchInput(Value);
}

void ATSTSSExplorerCharacter::Interact()
{
    if (EquipmentReviewMenu && EquipmentReviewMenu->IsInViewport()) return;
    if (!FirstWakeState || !FollowCamera || !GetWorld()) return;
    const FVector Start = FollowCamera->GetComponentLocation();
    const FVector PawnLocation = GetActorLocation();
    const float CameraTraceLength =
        TSTSSInteractionReach::GetCameraTraceLength(Start, PawnLocation, InteractionDistance);
    if (CameraTraceLength <= 0.f)
    {
        return;
    }

    // Trace across the camera boom before applying the *separate* pawn
    // reach check. At a 360 cm boom and 300 cm interact range the old
    // camera-only 300 cm ray could end behind the player entirely.
    const FVector End = Start + FollowCamera->GetForwardVector() * CameraTraceLength;
    FHitResult Hit;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(TSTSSInteract), false, this);
    const bool bTraceHit = GetWorld()->LineTraceSingleByChannel(
        Hit, Start, End, ECC_Visibility, Query);
#if WITH_EDITOR
    if (GetWorld()->WorldType == EWorldType::PIE && !bTraceHit)
    {
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_PIE_REVIEW_E_MISS pawn=%s camera=%s forward=%s trace_cm=%.1f objective=%s"),
            *PawnLocation.ToCompactString(), *Start.ToCompactString(),
            *FollowCamera->GetForwardVector().ToCompactString(), CameraTraceLength,
            *FirstWakeState->GetReviewObjectiveText());
    }
#endif
    if (bTraceHit)
    {
        if (ATSTSSMilestoneActor* Milestone = Cast<ATSTSSMilestoneActor>(Hit.GetActor()))
        {
            // A longer camera ray never increases interaction reach.
            if (TSTSSInteractionReach::IsInsidePlayerReach(
                    PawnLocation, Hit.ImpactPoint, InteractionDistance))
            {
                if (Milestone->TryActivate(FirstWakeState))
                {
#if WITH_EDITOR
                    if (GetWorld()->WorldType == EWorldType::PIE)
                    {
                        UE_LOG(LogTemp, Display,
                            TEXT("TSTSS_PIE_REVIEW_E_ACCEPT target=%s pawn_hit_cm=%.1f objective_after=%s"),
                            *Milestone->GetActorLabel(),
                            FVector::Dist(PawnLocation, Hit.ImpactPoint),
                            *FirstWakeState->GetReviewObjectiveText());
                    }
#endif
                    ShowFirstWakeReviewObjective(FirstWakeState);
                }
                else
                {
                    // A valid, in-reach marker rejected the state transition.
                    // This does not grant progression or claim that E hit when
                    // the camera trace missed or the target was out of reach.
#if WITH_EDITOR
                    if (GetWorld()->WorldType == EWorldType::PIE)
                    {
                        UE_LOG(LogTemp, Display,
                            TEXT("TSTSS_PIE_REVIEW_E_DENIED target=%s pawn_hit_cm=%.1f objective=%s"),
                            *Milestone->GetActorLabel(),
                            FVector::Dist(PawnLocation, Hit.ImpactPoint),
                            *FirstWakeState->GetReviewObjectiveText());
                    }
#endif
                    ShowFirstWakeReviewBlockedInteraction(FirstWakeState);
                }
            }
            else
            {
#if WITH_EDITOR
                if (GetWorld()->WorldType == EWorldType::PIE)
                {
                    UE_LOG(LogTemp, Display,
                        TEXT("TSTSS_PIE_REVIEW_E_OUT_OF_REACH target=%s pawn=%s pawn_hit_cm=%.1f limit_cm=%.1f objective=%s"),
                        *Milestone->GetActorLabel(), *PawnLocation.ToCompactString(),
                        FVector::Dist(PawnLocation, Hit.ImpactPoint),
                        InteractionDistance, *FirstWakeState->GetReviewObjectiveText());
                }
#endif
            }
        }
        else
        {
#if WITH_EDITOR
            if (GetWorld()->WorldType == EWorldType::PIE)
            {
                const AActor* OtherActor = Hit.GetActor();
                UE_LOG(LogTemp, Display,
                    TEXT("TSTSS_PIE_REVIEW_E_OTHER target=%s pawn=%s pawn_hit_cm=%.1f objective=%s"),
                    OtherActor ? *OtherActor->GetActorNameOrLabel() : TEXT("None"),
                    *PawnLocation.ToCompactString(),
                    FVector::Dist(PawnLocation, Hit.ImpactPoint),
                    *FirstWakeState->GetReviewObjectiveText());
            }
#endif
        }
    }
}

void ATSTSSExplorerCharacter::ShowObjectiveReview()
{
    // Read-only recall of the existing short-lived objective cue.
    ShowFirstWakeReviewObjective(FirstWakeState);
}

void ATSTSSExplorerCharacter::QuickSave()
{
    if (EquipmentReviewMenu && EquipmentReviewMenu->IsInViewport()) return;
    // UE's Shift+F5 is Stop Play-In-Editor. The F5 action may also be
    // dispatched to this pawn before PIE shuts down; that must never
    // create a new review SaveGame as a side effect of stopping play.
    // Fail closed for unpossessed PIE pawns as well.
    const UWorld* World = GetWorld();
    const bool bPIE = World && World->WorldType == EWorldType::PIE;
    if (bPIE)
    {
        const APlayerController* PC = Cast<APlayerController>(GetController());
        if (!PC || PC->IsInputKeyDown(EKeys::LeftShift) ||
            PC->IsInputKeyDown(EKeys::RightShift))
        {
            return;
        }
    }
    // PIE testing must not write the normal quicksave slot. Never adopt or
    // overwrite a leftover review save from another Editor session.
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
    if (EquipmentReviewMenu && EquipmentReviewMenu->IsInViewport()) return;
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
    const bool bRestored = FirstWakeState->Restore(
        Save->bFirstWakeStarted, Save->FirstWakeBeat, Save->InspectionMask);
#if WITH_EDITOR
    // Previously accepted review cubes have been made transparent to rays
    // and pawn movement. Restoring an earlier story beat must reactivate
    // only the markers which are now incomplete; keep saved-complete ones
    // transparent. Do not touch non-PIE or production-world actors.
    UWorld* World = GetWorld();
    if (bRestored && World && World->WorldType == EWorldType::PIE)
    {
        int32 ReconciledCount = 0;
        for (TActorIterator<ATSTSSMilestoneActor> It(World); It; ++It)
        {
            if (IsValid(*It))
            {
                It->ReconcileReviewCollisionAfterRestore(FirstWakeState);
                ++ReconciledCount;
            }
        }
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_PIE_REVIEW_LOAD_REBOUND beat=%d inspection_mask=%u generation=%llu actors_considered=%d"),
            static_cast<int32>(FirstWakeState->GetCurrentBeat()),
            static_cast<uint32>(FirstWakeState->GetInspectionMask()),
            static_cast<unsigned long long>(FirstWakeState->GetRestoreGeneration()),
            ReconciledCount);
    }
#endif
    return bRestored;
}

void ATSTSSExplorerCharacter::ToggleEquipmentReview()
{
#if !UE_BUILD_SHIPPING
    if (!IsValid(FirstWakeState)) return;
    APlayerController* PC = Cast<APlayerController>(Controller);
    if (!IsValid(PC) || !IsLocallyControlled()) return;
    if (AHUD* CurrentHUD = PC->GetHUD(); CurrentHUD && !CurrentHUD->bShowHUD)
    {
        // Never overlap the opening movie/title screen.
        return;
    }

    if (EquipmentReviewMenu && EquipmentReviewMenu->IsInViewport())
    {
        EquipmentReviewMenu->CloseReview();
        return;
    }
    if (!IsValid(EquipmentReviewMenu))
    {
        UTSTSSPartyGearMenuReviewWidget* Candidate =
            CreateWidget<UTSTSSPartyGearMenuReviewWidget>(
                PC, UTSTSSPartyGearMenuReviewWidget::StaticClass());
        if (!IsValid(Candidate)) return;

        // Current First Wake save schema contains no Lyra recruitment receipt.
        // Even after splashdown, Lyra MUST remain locked in this runtime UI.
        const auto Stage = FirstWakeState->IsChapterOneActOne()
            ? ETSTSSPartySliceReviewStage::AfterSplashdown
            : ETSTSSPartySliceReviewStage::FirstWake;
        if (!Candidate->TryBeginEquipmentReview(Stage) ||
            !Candidate->TryBindFirstWakeStoryForReview(FirstWakeState))
            return;
        EquipmentReviewMenu = Candidate;
    }

    const auto CurrentStage = FirstWakeState->IsChapterOneActOne()
        ? ETSTSSPartySliceReviewStage::AfterSplashdown
        : ETSTSSPartySliceReviewStage::FirstWake;
    if (!EquipmentReviewMenu->TryRefreshStoryStageReview(CurrentStage))
        return;

    EquipmentReviewMenu->AddToViewport(30);
    PC->bShowMouseCursor = true;
    FInputModeGameAndUI Mode;
    Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
    Mode.SetHideCursorDuringCapture(false);
    PC->SetInputMode(Mode);
#endif
}

void ATSTSSExplorerCharacter::TogglePartyMenuReview()
{
#if !UE_BUILD_SHIPPING
    if (EquipmentReviewMenu && EquipmentReviewMenu->IsInViewport())
    {
        EquipmentReviewMenu->CloseReview();
        return;
    }
    ToggleEquipmentReview();
    if (EquipmentReviewMenu && EquipmentReviewMenu->IsInViewport())
        EquipmentReviewMenu->OpenPageForReview(ETSTSSReviewMenuPage::Status);
#endif
}
