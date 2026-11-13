#include "TSTSSExplorerCharacter.h"
#include "TSTSSMilestoneActor.h"
#include "TSTSSPersistence.h"
#include "TSTSSInteractionReach.h"
#include "TSTSSSaveGame.h"
#include "TSTSSReviewShoreTravelSubsystem.h"
#include "Engine/GameInstance.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/TextRenderActor.h"
#include "Components/TextRenderComponent.h"
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
#include "Review/TSTSSPresentationCoordinatorSubsystem.h"
#include "TSTSSAtmosphereDirector.h"
#include "EngineUtils.h"
#include "CineCameraActor.h"
#include "CineCameraComponent.h"
#include "HAL/PlatformTime.h"
#include "TSTSSReviewContinueManifest.h"
#include "IO/IoHash.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Misc/PackageName.h"
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
            ? TEXT("First Wake (review): story saved; F9 does not move pawn; F7 Continue can restore position")
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

#if WITH_EDITOR
constexpr const TCHAR* ReviewPrimarySlot = TEXT("tstss_prelude_pie_quick");
constexpr const TCHAR* ReviewManifestSlot = TEXT("tstss_prelude_pie_manifest_v1");

FString BoundReviewMapPackage(const UWorld* World)
{
    if (!World || !World->GetOutermost()) return FString();
    return FPackageName::GetLongPackagePath(World->GetOutermost()->GetName()) +
        TEXT("/") + UGameplayStatics::GetCurrentLevelName(World, true);
}

FString BoundReviewProjectRoot()
{
    return FPaths::ConvertRelativePathToFull(FPaths::ProjectDir());
}

// BLAKE3 truncated to 160 bits is an integrity binding between two
// SaveGame files, not an authentication signature or source-commit proof.
bool DigestExactReviewPrimary(const FString& Slot, FString& OutDigest)
{
    OutDigest.Reset();
    if (Slot != ReviewPrimarySlot) return false;
    const FString Path = FPaths::Combine(
        FPaths::ProjectSavedDir(), TEXT("SaveGames"), Slot + TEXT(".sav"));
    TArray<uint8> Bytes;
    if (!FFileHelper::LoadFileToArray(Bytes, *Path) ||
        Bytes.IsEmpty() || Bytes.Num() > 262144)
    {
        return false;
    }
    OutDigest = LexToString(FIoHash::HashBuffer(Bytes.GetData(),
        static_cast<uint64>(Bytes.Num())));
    return OutDigest.Len() == 40;
}

bool LoadBoundReviewContinueCandidate(const UWorld* World, const FString& Slot,
    UTSTSSSaveGame*& OutSave, UTSTSSReviewContinueManifest*& OutManifest,
    FString& OutDigest)
{
    OutSave = nullptr;
    OutManifest = nullptr;
    OutDigest.Reset();
    if (!World || World->WorldType != EWorldType::PIE ||
        Slot != ReviewPrimarySlot ||
        !UGameplayStatics::DoesSaveGameExist(Slot, 0) ||
        !UGameplayStatics::DoesSaveGameExist(ReviewManifestSlot, 0) ||
        !DigestExactReviewPrimary(Slot, OutDigest))
    {
        return false;
    }
    UTSTSSSaveGame* Save = UTSTSSPersistence::LoadProgress(Slot);
    UTSTSSReviewContinueManifest* Manifest =
        Cast<UTSTSSReviewContinueManifest>(
            UGameplayStatics::LoadGameFromSlot(ReviewManifestSlot, 0));
    if (!IsValid(Save) || !IsValid(Manifest) ||
        !Manifest->IsBoundFor(Save, Slot, BoundReviewProjectRoot(),
            BoundReviewMapPackage(World), OutDigest))
    {
        return false;
    }
    OutSave = Save;
    OutManifest = Manifest;
    return true;
}
#endif
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
#if WITH_EDITOR
    if (UWorld* World = GetWorld())
    {
        if (UGameInstance* GameInstance = World->GetGameInstance())
        {
            if (UTSTSSReviewShoreTravelSubsystem* Travel =
                    GameInstance->GetSubsystem<UTSTSSReviewShoreTravelSubsystem>())
            {
                if (Travel->ConsumeShoreArrival(World, FirstWakeState))
                {
                    UE_LOG(LogTemp, Display,
                        TEXT("TSTSS_FIRSTWAKE_REVIEW_SCENE_ARRIVAL_STORY_RESTORED_NO_RECRUITMENT beat=%d"),
                        static_cast<int32>(FirstWakeState->GetCurrentBeat()));
                    const FString Scene = UGameplayStatics::GetCurrentLevelName(World, true);
                    if (Scene == TEXT("VS03_FirstWakeSky") ||
                        Scene == TEXT("VS04_SplashdownSea"))
                    {
                        // Both scene-review levels have no PlayerStart or walkable
                        // route. Use a temporary observer pawn, not canonical flight.
                        GetCharacterMovement()->SetMovementMode(MOVE_Flying);
                        SetActorLocation(Scene == TEXT("VS03_FirstWakeSky")
                            ? FVector(-1600.f, -2300.f, 1000.f)
                            : FVector(-1800.f, -2800.f, 950.f));
                        if (Controller)
                        {
                            Controller->SetControlRotation(FRotator(-12.f, 55.f, 0.f));
                        }
                    }
                    else if (Scene == TEXT("VS05_DenithFuelShanty") &&
                        FirstWakeState->GetCurrentBeat() ==
                            ETSTSSFirstWakeBeat::FlotationConfirmed)
                    {
                        // The native fuel-shanty map is scenery only. Add one
                        // review interaction at the player's spawn, requiring E
                        // before K may advance to the published shoreline.
                        ATSTSSMilestoneActor* Reserve =
                            World->SpawnActor<ATSTSSMilestoneActor>(
                                FVector(-1430.f, -140.f, 180.f),
                                FRotator::ZeroRotator);
                        UStaticMesh* ReviewCube = LoadObject<UStaticMesh>(
                            nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
                        if (IsValid(Reserve) && IsValid(ReviewCube))
                        {
                            Reserve->SetActorLabel(
                                TEXT("TSTSS_SPLASHDOWN_GREYBOX_EmptyReserveMarker"));
                            Reserve->Milestone = ETSTSSFirstWakeBeat::EmptyReserveInspected;
                            UStaticMeshComponent* Shape =
                                Reserve->FindComponentByClass<UStaticMeshComponent>();
                            if (IsValid(Shape))
                            {
                                Shape->SetStaticMesh(ReviewCube);
                                Shape->SetWorldScale3D(FVector(1.2f));
                            }
                            if (ATextRenderActor* Sign = World->SpawnActor<ATextRenderActor>(
                                    FVector(-1490.f, -230.f, 330.f),
                                    FRotator::ZeroRotator))
                            {
                                Sign->SetActorLabel(TEXT("TSTSS_REVIEW_ReserveCheckNotice"));
                                Sign->GetTextRender()->SetText(
                                    FText::FromString(TEXT("EMPTY RESERVES  |  Inspect [E]")));
                            }
                        }
                        else if (IsValid(Reserve))
                        {
                            Reserve->Destroy();
                        }
                    }
                }
            }
        }
    }
#endif
    bPIEReviewQuickSlotOwned = false;
#if WITH_EDITOR
    bPendingReviewContinue = false;
#endif
    ShowObjectiveReview();
}

void ATSTSSExplorerCharacter::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
#if WITH_EDITOR
    RestoreEngineFocusPreview();
#endif
    Super::EndPlay(EndPlayReason);
}

#if WITH_EDITOR
void ATSTSSExplorerCharacter::ToggleEngineFocusPreview()
{
    // Explicit review-only camera cut; never an E-interaction consequence.
    // The production explorer and its camera are unchanged unless the player presses C.
    UWorld* World = GetWorld();
    if (!World || World->WorldType != EWorldType::PIE || !IsValid(FirstWakeState))
    {
        return;
    }
    if (EngineFocusPreviewCamera.IsValid())
    {
        RestoreEngineFocusPreview();
        return;
    }

    const auto Warn = [](const TCHAR* Message)
    {
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 4.f, FColor::Yellow, Message);
        }
    };

    APlayerController* PC = Cast<APlayerController>(Controller);
    if (!IsValid(PC) || PC != UGameplayStatics::GetPlayerController(World, 0)
        || PC->GetViewTarget() != this || PC->IsMoveInputIgnored()
        || PC->IsLookInputIgnored())
    {
        Warn(TEXT("Engine view unavailable: player camera is already owned"));
        return;
    }

    // The actual VS02 gauge is the only acceptable focus target.
    // No runtime duplication of story markers or fabrication of first-wake state.
    AActor* Instrument = nullptr;
    int32 InstrumentCount = 0;
    ATSTSSAtmosphereDirector* Atmosphere = nullptr;
    int32 AtmosphereCount = 0;
    for (TActorIterator<AActor> It(World); It; ++It)
    {
        AActor* Actor = *It;
        if (!IsValid(Actor)) continue;
        if (Actor->GetActorLabel() ==
            TEXT("TSTSS_VS_REVIEW_InstrumentCore_LIFT"))
        {
            Instrument = Actor;
            ++InstrumentCount;
        }
        if (ATSTSSAtmosphereDirector* Director =
                Cast<ATSTSSAtmosphereDirector>(Actor))
        {
            Atmosphere = Director;
            ++AtmosphereCount;
        }
    }
    if (InstrumentCount != 1 || AtmosphereCount != 1
        || !IsValid(Instrument) || !IsValid(Atmosphere)
        || FVector::Dist(GetActorLocation(), Instrument->GetActorLocation()) > 450.f)
    {
        Warn(TEXT("Engine view: stand near the LIFT instrument in the ship"));
        return;
    }
    UTSTSSPresentationCoordinatorSubsystem* Coordinator =
        World->GetSubsystem<UTSTSSPresentationCoordinatorSubsystem>();
    if (!IsValid(Coordinator))
    {
        Warn(TEXT("Engine view unavailable: no presentation coordinator"));
        return;
    }
    const bool bWasEnabled = Coordinator->IsReviewEnabled();
    if (!bWasEnabled)
    {
        Coordinator->SetReviewEnabled(true);
    }
    const FTSTSSPresentationIntent Intent = Coordinator->TryPublishMoment(
        FirstWakeState, Atmosphere, ETSTSSPresentationMoment::EngineInspection,
        /*bReducedMotion=*/false, /*bGameplayClarityOverride=*/false);
    if (!Intent.bEligible || !Intent.bAllowCinematicFocus
        || !Intent.bAllowFocusRack || Intent.bRequireDeepFocus
        || Intent.ShotId != FName(TEXT("FW03_Engine_Inspection")))
    {
        if (!bWasEnabled) Coordinator->SetReviewEnabled(false);
        Warn(TEXT("Engine view held: first-wake story/weather/access gate"));
        return;
    }

    // Same approved 65 mm f/2.8 optical recipe as the native A/B review.
    // A higher camera elevation clears more of the foreground railing.
    const FVector Target = Instrument->GetActorLocation();
    const FVector Location = Target + FVector(-350.f, -610.f, 265.f);
    const float FocusCm = FVector::Dist(Location, Target);
    if (!FMath::IsFinite(FocusCm) || FocusCm < 65.f || FocusCm > 12000.f)
    {
        if (!bWasEnabled) Coordinator->SetReviewEnabled(false);
        return;
    }
    FActorSpawnParameters Spawn;
    Spawn.SpawnCollisionHandlingOverride =
        ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    ACineCameraActor* Camera = World->SpawnActor<ACineCameraActor>(
        Location, (Target - Location).Rotation(), Spawn);
    if (!IsValid(Camera) || !IsValid(Camera->GetCineCameraComponent()))
    {
        if (IsValid(Camera)) Camera->Destroy();
        if (!bWasEnabled) Coordinator->SetReviewEnabled(false);
        Warn(TEXT("Engine view unavailable: no native Cine Camera"));
        return;
    }
    Camera->SetActorLabel(TEXT("TSTSS_GAMEPLAY_ENGINE_FOCUS_PREVIEW_ONLY"));
    UCineCameraComponent* Cine = Camera->GetCineCameraComponent();
    Cine->SetCurrentFocalLength(65.f);
    Cine->SetCurrentAperture(2.8f);
    FCameraFocusSettings Settings = Cine->FocusSettings;
    Settings.FocusMethod = ECameraFocusMethod::Manual;
    Settings.ManualFocusDistance = FocusCm;
    Settings.bSmoothFocusChanges = true;
    Settings.FocusSmoothingInterpSpeed = 2.f;
#if WITH_EDITORONLY_DATA
    Settings.bDrawDebugFocusPlane = false;
#endif
    Cine->SetFocusSettings(Settings);

    // Explicit, reversible 4 s preview. The player pawn stays at its
    // original location, and existing movement/look ignore values are
    // refused above rather than overwritten.
    EngineFocusPreviewCamera = Camera;
    EngineFocusPreviewController = PC;
    bEngineFocusPreviewOwnsCoordinatorEnable = !bWasEnabled;
    EngineFocusPreviewIgnoredMove = true;
    EngineFocusPreviewIgnoredLook = true;
    EngineFocusPreviewStartedSeconds = FPlatformTime::Seconds();
    EngineFocusPreviewDeadlineSeconds = EngineFocusPreviewStartedSeconds + 4.0;
    PC->SetIgnoreMoveInput(true);
    PC->SetIgnoreLookInput(true);
    PC->SetViewTargetWithBlend(Camera, 0.35f, VTBlend_EaseInOut, 2.f);
    GetWorldTimerManager().SetTimer(EngineFocusPreviewGuardTimer, this,
        &ATSTSSExplorerCharacter::VerifyEngineFocusPreview, 0.2f, true);
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 4.f, FColor::Cyan,
            TEXT("LIFT inspection view - press C to return (auto return 4s)"));
    }
    UE_LOG(LogTemp, Display, TEXT("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_ENTER focus_cm=%.1f"),
        FocusCm);
}

void ATSTSSExplorerCharacter::VerifyEngineFocusPreview()
{
    const UWorld* World = GetWorld();
    APlayerController* PC = EngineFocusPreviewController.Get();
    ACineCameraActor* Camera = EngineFocusPreviewCamera.Get();
    UTSTSSPresentationCoordinatorSubsystem* Coordinator = World
        ? World->GetSubsystem<UTSTSSPresentationCoordinatorSubsystem>() : nullptr;
    if (!World || World->WorldType != EWorldType::PIE
        || !IsValid(PC) || !IsValid(Camera)
        // A blend can still report the pawn as view target momentarily.
        // Do not destroy the camera midway through its entry transition.
        || (FPlatformTime::Seconds() - EngineFocusPreviewStartedSeconds > 0.75
            && PC->GetViewTarget() != Camera)
        || FPlatformTime::Seconds() >= EngineFocusPreviewDeadlineSeconds
        || !IsValid(Coordinator)
        || !Coordinator->GetCurrentIntent().bEligible
        || !Coordinator->GetCurrentIntent().bAllowCinematicFocus
        || Coordinator->GetCurrentIntent().ShotId !=
            FName(TEXT("FW03_Engine_Inspection")))
    {
        RestoreEngineFocusPreview();
    }
}

void ATSTSSExplorerCharacter::RestoreEngineFocusPreview()
{
    const bool bHadPreview = EngineFocusPreviewCamera.IsValid()
        || bEngineFocusPreviewIgnoredMove || bEngineFocusPreviewIgnoredLook;
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(EngineFocusPreviewGuardTimer);
    }
    APlayerController* PC = EngineFocusPreviewController.Get();
    ACineCameraActor* Camera = EngineFocusPreviewCamera.Get();
    // Do not override any new externally-owned view target.
    if (IsValid(PC))
    {
        if (IsValid(Camera) && PC->GetViewTarget() == Camera)
        {
            PC->SetViewTargetWithBlend(this, 0.3f, VTBlend_EaseInOut, 2.f);
        }
        if (bEngineFocusPreviewIgnoredMove) PC->SetIgnoreMoveInput(false);
        if (bEngineFocusPreviewIgnoredLook) PC->SetIgnoreLookInput(false);
    }
    if (IsValid(Camera))
    {
        // Retain the temporary camera until the return blend finishes.
        Camera->SetLifeSpan(0.6f);
    }
    if (bEngineFocusPreviewOwnsCoordinatorEnable)
    {
        if (UWorld* World = GetWorld())
        {
            if (UTSTSSPresentationCoordinatorSubsystem* Coordinator =
                    World->GetSubsystem<UTSTSSPresentationCoordinatorSubsystem>())
            {
                // Never shut off another presentation source's eligible
                // shot if it superseded our inspection while the preview ran.
                const FTSTSSPresentationIntent Current =
                    Coordinator->GetCurrentIntent();
                if (!Current.bEligible
                    || Current.ShotId == FName(TEXT("FW03_Engine_Inspection")))
                {
                    Coordinator->SetReviewEnabled(false);
                }
            }
        }
    }
    else if (bHadPreview)
    {
        if (UWorld* World = GetWorld())
        {
            if (UTSTSSPresentationCoordinatorSubsystem* Coordinator =
                    World->GetSubsystem<UTSTSSPresentationCoordinatorSubsystem>())
            {
                if (Coordinator->GetCurrentIntent().ShotId ==
                        FName(TEXT("FW03_Engine_Inspection")))
                {
                    // A pre-enabled coordinator remains enabled but the expired
                    // inspection must not leak after the player returns.
                    Coordinator->ResetReviewIntent();
                }
            }
        }
    }
    EngineFocusPreviewCamera.Reset();
    EngineFocusPreviewController.Reset();
    bEngineFocusPreviewOwnsCoordinatorEnable = false;
    bEngineFocusPreviewIgnoredMove = false;
    bEngineFocusPreviewIgnoredLook = false;
    EngineFocusPreviewStartedSeconds = 0.;
    EngineFocusPreviewDeadlineSeconds = 0.;
    if (bHadPreview)
    {
        UE_LOG(LogTemp, Display, TEXT("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RESTORE"));
    }
}
#endif // WITH_EDITOR

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
#if WITH_EDITOR
    if (InputWorld && InputWorld->WorldType == EWorldType::PIE)
    {
        PlayerInputComponent->BindAction(TEXT("ReviewContinue"), IE_Pressed, this, &ATSTSSExplorerCharacter::ReviewContinue);
        // Explicit C-only opt-in: never automatic on E inspection or ordinary exploration.
        PlayerInputComponent->BindAction(TEXT("EngineFocusPreview"), IE_Pressed,
            this, &ATSTSSExplorerCharacter::ToggleEngineFocusPreview);
    }
#endif
    PlayerInputComponent->BindAction(TEXT("ReviewObjective"), IE_Pressed, this, &ATSTSSExplorerCharacter::ShowObjectiveReview);
#if WITH_EDITOR
    if (InputWorld && (InputWorld->WorldType == EWorldType::PIE ||
                       InputWorld->WorldType == EWorldType::Game))
    {
        PlayerInputComponent->BindAction(TEXT("ReviewShoreTravel"), IE_Pressed,
            this, &ATSTSSExplorerCharacter::ReviewShoreTravel);
    }
#endif
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
                        // Optional visual-intent bridge AFTER the genuine
                        // interaction accepted the milestone/inspection.
                        // No input changes, camera cuts, audio playback or
                        // world progression are caused by this adapter.
                        if (UTSTSSPresentationCoordinatorSubsystem* Review =
                                GetWorld()->GetSubsystem<
                                    UTSTSSPresentationCoordinatorSubsystem>())
                        {
                            if (Review->IsReviewEnabled())
                            {
                                ETSTSSPresentationMoment Moment =
                                    ETSTSSPresentationMoment::None;
                                if (Milestone->bIsInspectionStation)
                                {
                                    Moment = ETSTSSPresentationMoment::EngineInspection;
                                }
                                else if (Milestone->Milestone ==
                                         ETSTSSFirstWakeBeat::IoniaHired)
                                {
                                    Moment = ETSTSSPresentationMoment::IoniaConversation;
                                }
                                if (Moment != ETSTSSPresentationMoment::None)
                                {
                                    const ATSTSSAtmosphereDirector* Atmosphere =
                                        Cast<ATSTSSAtmosphereDirector>(
                                            UGameplayStatics::GetActorOfClass(
                                                GetWorld(),
                                                ATSTSSAtmosphereDirector::StaticClass()));
                                    // No cinematic focus while the pawn retains
                                    // gameplay control. Reduced-motion-safe
                                    // until the real accessibility source binds.
                                    Review->TryPublishMoment(
                                        FirstWakeState, Atmosphere, Moment,
                                        true, true);
                                }
                            }
                        }

                        UE_LOG(LogTemp, Display,
                            TEXT("TSTSS_PIE_REVIEW_E_ACCEPT target=%s pawn_hit_cm=%.1f objective_after=%s"),
                            *Milestone->GetActorLabel(),
                            FVector::Dist(PawnLocation, Hit.ImpactPoint),
                            *FirstWakeState->GetReviewObjectiveText());
                    }
#endif
                    ShowFirstWakeReviewObjective(FirstWakeState);
#if WITH_EDITOR
                    if (GetWorld()->WorldType == EWorldType::PIE
                        && Milestone->bIsInspectionStation && GEngine)
                    {
                        // A discoverable OPTIONAL view, never an automatic
                        // camera cut during the normal E inspection.
                        GEngine->AddOnScreenDebugMessage(-1, 6.f, FColor::Cyan,
                            TEXT("Engine inspection: press C near the LIFT instrument for a 4s focus view"));
                    }
#endif
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
#if WITH_EDITOR
    UWorld* World = GetWorld();
    if (World && (World->WorldType == EWorldType::PIE ||
                  World->WorldType == EWorldType::Game) &&
        UTSTSSReviewShoreTravelSubsystem::IsEligible(
            FirstWakeState, UGameplayStatics::GetCurrentLevelName(World, true)) && GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 7.f, FColor::Cyan,
            TEXT("First Wake (review): K = next 3D scene (review only; no visual/gameplay approval)"));
    }
#endif
}

#if WITH_EDITOR
void ATSTSSExplorerCharacter::ReviewShoreTravel()
{
    UWorld* World = GetWorld();
    UGameInstance* GameInstance = World ? World->GetGameInstance() : nullptr;
    UTSTSSReviewShoreTravelSubsystem* Travel = GameInstance
        ? GameInstance->GetSubsystem<UTSTSSReviewShoreTravelSubsystem>() : nullptr;
    if (!Travel || !Travel->QueueShore(World, FirstWakeState))
    {
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 6.f, FColor::Yellow,
                TEXT("First Wake (review): next scene locked until the current milestone is complete"));
        }
        return;
    }
    const FString Destination = Travel->GetPendingMapPackage();
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination=%s"),
        *Destination);
    UGameplayStatics::OpenLevel(this, FName(*Destination));
}
#endif

void ATSTSSExplorerCharacter::QuickSave()
{
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
        (UGameplayStatics::DoesSaveGameExist(Slot, 0) ||
         UGameplayStatics::DoesSaveGameExist(
             TEXT("tstss_prelude_pie_manifest_v1"), 0)))
    {
        ShowFirstWakeReviewProtectedSlotWarning(false);
        return;
    }
#if WITH_EDITOR
    bPendingReviewContinue = false;
#endif
    const bool bSavedStory = SaveFirstWake(Slot);
    bool bSaved = bSavedStory;
#if WITH_EDITOR
    if (bPIE && bSavedStory)
    {
        bSaved = SaveReviewContinueBinding(Slot);
    }
#endif
    if (bPIE && bSaved)
    {
        bPIEReviewQuickSlotOwned = true;
    }
    ShowFirstWakeReviewSaveLoadStatus(false, bSaved);
}

void ATSTSSExplorerCharacter::QuickLoad()
{
#if WITH_EDITOR
    bPendingReviewContinue = false;
#endif
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

#if WITH_EDITOR
bool ATSTSSExplorerCharacter::SaveReviewContinueBinding(const FString& Slot)
{
    const UWorld* World = GetWorld();
    if (Slot != ReviewPrimarySlot || !World ||
        World->WorldType != EWorldType::PIE || !IsValid(FirstWakeState))
    {
        return false;
    }
    FString Digest;
    if (!DigestExactReviewPrimary(Slot, Digest)) return false;

    UTSTSSReviewContinueManifest* Manifest =
        NewObject<UTSTSSReviewContinueManifest>(this);
    if (!IsValid(Manifest)) return false;

    Manifest->PrimarySlot = Slot;
    Manifest->ProjectRoot = BoundReviewProjectRoot();
    Manifest->ReviewMapPackage = BoundReviewMapPackage(World);
    Manifest->PrimaryBlake3_160 = Digest;
    Manifest->PrimarySchemaVersion = UTSTSSSaveGame::CurrentVersion;
    Manifest->bSavedStoryStarted = FirstWakeState->HasStarted();
    Manifest->SavedBeat = FirstWakeState->GetCurrentBeat();
    Manifest->SavedInspectionMask = FirstWakeState->GetInspectionMask();
    Manifest->SavedPawnLocation = GetActorLocation();
    Manifest->SavedPawnRotation = GetActorRotation();
    Manifest->SavedControlRotation = Controller
        ? Controller->GetControlRotation() : GetActorRotation();

    // Existing manifest can only be updated after this PIE session owns the
    // primary slot; QuickSave checks ownership before writing the primary.
    const bool bStored = UGameplayStatics::SaveGameToSlot(
        Manifest, ReviewManifestSlot, 0);
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_PIE_REVIEW_CONTINUE_BINDING saved=%d beat=%d slot=%s"),
        bStored ? 1 : 0, static_cast<int32>(Manifest->SavedBeat), *Slot);
    return bStored;
}

void ATSTSSExplorerCharacter::ReviewContinue()
{
    UWorld* World = GetWorld();
    auto Reject = [this](const TCHAR* Reason)
    {
        bPendingReviewContinue = false;
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_PIE_REVIEW_CONTINUE_REJECT reason=%s"), Reason);
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(
                -1, 8.f, FColor::Red,
                FString::Printf(TEXT("Review Continue refused: %s"), Reason));
        }
    };

    if (!World || World->WorldType != EWorldType::PIE ||
        !IsValid(FirstWakeState))
    {
        Reject(TEXT("review_PIE_only"));
        return;
    }
    // F9 remains session-scoped. F7 is a separate explicit action and cannot
    // silently adopt any save after a fresh Editor process starts.
    if (bPIEReviewQuickSlotOwned)
    {
        Reject(TEXT("session_already_owns_quicksave_use_F9"));
        return;
    }

    UTSTSSSaveGame* Saved = nullptr;
    UTSTSSReviewContinueManifest* Manifest = nullptr;
    FString Digest;
    if (!LoadBoundReviewContinueCandidate(
            World, ReviewPrimarySlot, Saved, Manifest, Digest))
    {
        Reject(TEXT("missing_corrupt_foreign_or_flight_save"));
        return;
    }

    // A second F7 is effective only for the unchanged state, exact files,
    // project/world, and same current PIE generation within 30 seconds.
    const bool bConfirm = bPendingReviewContinue &&
        World->GetTimeSeconds() <= PendingReviewContinueExpireWorldSeconds &&
        PendingReviewContinueDigest == Digest &&
        FirstWakeState->GetRestoreGeneration() ==
            PendingReviewContinueRestoreGeneration &&
        FirstWakeState->HasStarted() == bPendingReviewContinueStarted &&
        FirstWakeState->GetCurrentBeat() == PendingReviewContinueBeat &&
        FirstWakeState->GetInspectionMask() ==
            PendingReviewContinueInspectionMask;

    if (!bConfirm)
    {
        bPendingReviewContinue = true;
        PendingReviewContinueDigest = Digest;
        PendingReviewContinueExpireWorldSeconds =
            World->GetTimeSeconds() + 30.f;
        PendingReviewContinueRestoreGeneration =
            FirstWakeState->GetRestoreGeneration();
        bPendingReviewContinueStarted = FirstWakeState->HasStarted();
        PendingReviewContinueBeat = FirstWakeState->GetCurrentBeat();
        PendingReviewContinueInspectionMask =
            FirstWakeState->GetInspectionMask();

        const FString BeatName = StaticEnum<ETSTSSFirstWakeBeat>()->
            GetNameStringByValue(static_cast<int64>(Saved->FirstWakeBeat));
        const FString Summary = FString::Printf(
            TEXT("Continue preview: %s, inspections %u, Ender (%.0f,%.0f,%.0f). Press F7 AGAIN within 30s to confirm."),
            *BeatName, static_cast<uint32>(Saved->InspectionMask),
            Manifest->SavedPawnLocation.X, Manifest->SavedPawnLocation.Y,
            Manifest->SavedPawnLocation.Z);
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_PIE_REVIEW_CONTINUE_PREVIEW beat=%d inspections=%u position=%s confirmation_required=1"),
            static_cast<int32>(Saved->FirstWakeBeat),
            static_cast<uint32>(Saved->InspectionMask),
            *Manifest->SavedPawnLocation.ToCompactString());
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(
                -1, 30.f, FColor::Cyan, Summary);
        }
        return;
    }

    bPendingReviewContinue = false;
    // Validate the story restore in an isolated UObject first; no mutations
    // to the current gameplay state or actor collision on rejected saves.
    UTSTSSFirstWakeState* Trial =
        NewObject<UTSTSSFirstWakeState>(this);
    if (!IsValid(Trial) || !Trial->Restore(
            Saved->bFirstWakeStarted, Saved->FirstWakeBeat,
            Saved->InspectionMask))
    {
        Reject(TEXT("invalid_story_state"));
        return;
    }

    FVector TargetLocation = Manifest->SavedPawnLocation;
    const FRotator TargetRotation = Manifest->SavedPawnRotation;
    // Fail closed if the saved pawn would be embedded in collision or moved
    // far from the position that the player explicitly previewed.
    if (!World->FindTeleportSpot(this, TargetLocation, TargetRotation) ||
        FVector::Dist(TargetLocation, Manifest->SavedPawnLocation) > 50.f)
    {
        Reject(TEXT("unsafe_saved_player_location"));
        return;
    }

    const FVector OriginalLocation = GetActorLocation();
    const FRotator OriginalRotation = GetActorRotation();
    if (!TeleportTo(TargetLocation, TargetRotation, false, false))
    {
        Reject(TEXT("player_teleport_not_safe"));
        return;
    }
    // Use the same validated story load and review collision reconciliation
    // as the already tested in-session F9. If it fails, undo the pawn move.
    if (!LoadFirstWake(ReviewPrimarySlot))
    {
        SetActorLocationAndRotation(OriginalLocation, OriginalRotation,
            false, nullptr, ETeleportType::TeleportPhysics);
        Reject(TEXT("story_restore_failed"));
        return;
    }

    if (Controller)
    {
        Controller->SetControlRotation(Manifest->SavedControlRotation);
    }
    bPIEReviewQuickSlotOwned = true;
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_PIE_REVIEW_CONTINUE_ACCEPT beat=%d mask=%u location=%s generation=%llu"),
        static_cast<int32>(FirstWakeState->GetCurrentBeat()),
        static_cast<uint32>(FirstWakeState->GetInspectionMask()),
        *GetActorLocation().ToCompactString(),
        static_cast<unsigned long long>(
            FirstWakeState->GetRestoreGeneration()));
    ShowFirstWakeReviewObjective(FirstWakeState);
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(
            -1, 8.f, FColor::Green,
            TEXT("First Wake review Continue accepted. F9 now uses this session's adopted slot."));
    }
}
#endif
