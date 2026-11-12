#include "Review/TSTSSReviewFocusReceiver.h"

#include "CineCameraActor.h"
#include "CineCameraComponent.h"
#include "TSTSSExplorerCharacter.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"

ATSTSSReviewFocusReceiver::ATSTSSReviewFocusReceiver()
{
    PrimaryActorTick.bCanEverTick = false;
    SetActorEnableCollision(false);
}

bool ATSTSSReviewFocusReceiver::IsFocusCueApplicable(
    const FTSTSSPresentationIntent& Intent,
    ETSTSSPresentationMoment Moment,
    bool bExplicitlyEnabled, bool bPIE)
{
    if (!bPIE || !bExplicitlyEnabled || !Intent.bEligible
        || !Intent.bAllowCinematicFocus || !Intent.bAllowFocusRack
        || Intent.bRequireDeepFocus)
    {
        return false;
    }
    if (Moment == ETSTSSPresentationMoment::EngineInspection)
    {
        return Intent.ShotId == FName(TEXT("FW03_Engine_Inspection"));
    }
    if (Moment == ETSTSSPresentationMoment::EngineAwakening)
    {
        return Intent.ShotId == FName(TEXT("FW04_Engine_Awakening"));
    }
    return false;
}

void ATSTSSReviewFocusReceiver::BeginPlay()
{
    Super::BeginPlay();
#if WITH_EDITOR
    UWorld* World = GetWorld();
    if (!bExplicitReviewOptIn || !World || World->WorldType != EWorldType::PIE)
    {
        return;
    }
    UTSTSSPresentationCoordinatorSubsystem* Coordinator =
        World->GetSubsystem<UTSTSSPresentationCoordinatorSubsystem>();
    if (IsValid(Coordinator))
    {
        BoundCoordinator = Coordinator;
        Coordinator->OnReviewIntentChanged.AddDynamic(
            this, &ATSTSSReviewFocusReceiver::ReceivePresentationIntent);
    }
#endif
}

void ATSTSSReviewFocusReceiver::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    RestoreReviewCamera();
    if (UTSTSSPresentationCoordinatorSubsystem* Coordinator =
            BoundCoordinator.Get())
    {
        Coordinator->OnReviewIntentChanged.RemoveDynamic(
            this, &ATSTSSReviewFocusReceiver::ReceivePresentationIntent);
    }
    BoundCoordinator.Reset();
    Super::EndPlay(EndPlayReason);
}

bool ATSTSSReviewFocusReceiver::IsAuthenticReviewCamera() const
{
#if WITH_EDITOR
    const UWorld* World = GetWorld();
    if (!bExplicitReviewOptIn || !World || World->WorldType != EWorldType::PIE
        || !IsValid(StagedReviewCamera) || !IsValid(AuthoredEngineFocusAnchor)
        || StagedReviewCamera->GetWorld() != World
        || AuthoredEngineFocusAnchor->GetWorld() != World
        || !StagedReviewCamera->GetActorLabel().StartsWith(
            TEXT("TSTSS_BOKEH_ENGINE_REVIEW_"))
        || !AuthoredEngineFocusAnchor->GetActorLabel().StartsWith(
            TEXT("TSTSS_VS_REVIEW_")))
    {
        return false;
    }
    // An authored optical preview is not permission to change the active
    // player camera. Editor viewport piloting remains a separate operator act.
    const APlayerController* Player = UGameplayStatics::GetPlayerController(World, 0);
    if (IsValid(Player) && Player->GetViewTarget() == StagedReviewCamera)
    {
        return false;
    }
    const float FocusCm = FVector::Dist(
        StagedReviewCamera->GetActorLocation(),
        AuthoredEngineFocusAnchor->GetActorLocation());
    return FMath::IsFinite(FocusCm) && FocusCm >= 65.f && FocusCm <= 12000.f
        && IsValid(StagedReviewCamera->GetCineCameraComponent());
#else
    return false;
#endif
}

bool ATSTSSReviewFocusReceiver::ApplyBoundedLens(
    const FTSTSSPresentationIntent& Intent)
{
#if WITH_EDITOR
    if (!IsAuthenticReviewCamera()) return false;
    const bool bInspection =
        Intent.ShotId == FName(TEXT("FW03_Engine_Inspection"));
    const ETSTSSPresentationMoment Moment = bInspection
        ? ETSTSSPresentationMoment::EngineInspection
        : ETSTSSPresentationMoment::EngineAwakening;
    if (!IsFocusCueApplicable(Intent, Moment, bExplicitReviewOptIn, true))
    {
        return false;
    }
    UCineCameraComponent* Cine = StagedReviewCamera->GetCineCameraComponent();
    if (!IsValid(Cine)) return false;
    const float FocusCm = FVector::Dist(
        StagedReviewCamera->GetActorLocation(),
        AuthoredEngineFocusAnchor->GetActorLocation());
    if (!FMath::IsFinite(FocusCm) || FocusCm < 65.f || FocusCm > 12000.f)
    {
        return false;
    }

    if (!bHasSavedLens)
    {
        OriginalFocus = Cine->FocusSettings;
        OriginalFocalLength = Cine->CurrentFocalLength;
        OriginalAperture = Cine->CurrentAperture;
        bHasSavedLens = true;
    }

    // The sole property writes in this feature target the explicitly
    // assigned, non-player, isolated CineCameraComponent. No global PPV.
    Cine->SetCurrentFocalLength(bInspection ? 65.f : 50.f);
    Cine->SetCurrentAperture(bInspection ? 2.8f : 4.0f);
    FCameraFocusSettings Settings = Cine->FocusSettings;
    Settings.FocusMethod = ECameraFocusMethod::Manual;
    Settings.ManualFocusDistance = FocusCm;
    Settings.bSmoothFocusChanges = true;
    Settings.FocusSmoothingInterpSpeed = bInspection ? 2.0f : 1.5f;
#if WITH_EDITORONLY_DATA
    Settings.bDrawDebugFocusPlane = false;
#endif
    Cine->SetFocusSettings(Settings);

    // Only while a cue is applied, run a low-rate expiry guard; story state
    // mutations are already invalidated immediately via the native delegate.
    GetWorldTimerManager().SetTimer(
        FocusGuardTimer, this, &ATSTSSReviewFocusReceiver::VerifyActiveSource,
        0.25f, true);
    return true;
#else
    return false;
#endif
}

void ATSTSSReviewFocusReceiver::ReceivePresentationIntent(
    const FTSTSSPresentationIntent& Intent)
{
#if WITH_EDITOR
    UTSTSSPresentationCoordinatorSubsystem* Coordinator = BoundCoordinator.Get();
    if (!IsValid(Coordinator) || !IsAuthenticReviewCamera())
    {
        RestoreReviewCamera();
        return;
    }
    const FTSTSSPresentationIntent Current = Coordinator->GetCurrentIntent();
    if (!Current.bEligible || Current.ShotId != Intent.ShotId
        || Current.bAllowCinematicFocus != Intent.bAllowCinematicFocus)
    {
        RestoreReviewCamera();
        return;
    }
    if (!ApplyBoundedLens(Current))
    {
        RestoreReviewCamera();
    }
#else
    (void)Intent;
#endif
}

bool ATSTSSReviewFocusReceiver::RequestAuthoredEngineFocus(
    ETSTSSPresentationMoment Moment)
{
#if WITH_EDITOR
    if (Moment != ETSTSSPresentationMoment::EngineInspection
        && Moment != ETSTSSPresentationMoment::EngineAwakening)
    {
        return false;
    }
    if (!IsAuthenticReviewCamera()) return false;
    UWorld* World = GetWorld();
    UTSTSSPresentationCoordinatorSubsystem* Coordinator = BoundCoordinator.Get();
    if (!IsValid(Coordinator) || !Coordinator->IsReviewEnabled()) return false;

    const ATSTSSExplorerCharacter* Player = Cast<ATSTSSExplorerCharacter>(
        UGameplayStatics::GetPlayerPawn(World, 0));
    if (!IsValid(Player) || !IsValid(Player->GetFirstWakeState())) return false;

    // Only one owned atmosphere director may supply a weather snapshot.
    ATSTSSAtmosphereDirector* Atmosphere = nullptr;
    int32 AtmosphereCount = 0;
    for (TActorIterator<ATSTSSAtmosphereDirector> It(World); It; ++It)
    {
        ++AtmosphereCount;
        Atmosphere = *It;
        if (AtmosphereCount > 1) return false;
    }
    if (AtmosphereCount != 1 || !IsValid(Atmosphere)) return false;

    // This explicitly authored review call requests focus, but cannot
    // trigger a camera cut, advance narrative state or suppress player input.
    const FTSTSSPresentationIntent Intent = Coordinator->TryPublishMoment(
        Player->GetFirstWakeState(), Atmosphere, Moment, false, false);
    return Intent.bEligible && bHasSavedLens;
#else
    (void)Moment;
    return false;
#endif
}

void ATSTSSReviewFocusReceiver::VerifyActiveSource()
{
#if WITH_EDITOR
    UTSTSSPresentationCoordinatorSubsystem* Coordinator = BoundCoordinator.Get();
    if (!IsValid(Coordinator) || !IsAuthenticReviewCamera()
        || !Coordinator->GetCurrentIntent().bEligible
        || !Coordinator->GetCurrentIntent().bAllowCinematicFocus)
    {
        RestoreReviewCamera();
    }
#endif
}

void ATSTSSReviewFocusReceiver::RestoreReviewCamera()
{
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(FocusGuardTimer);
    }
    if (bHasSavedLens && IsValid(StagedReviewCamera))
    {
        UCineCameraComponent* Cine = StagedReviewCamera->GetCineCameraComponent();
        if (IsValid(Cine))
        {
            Cine->SetFocusSettings(OriginalFocus);
            Cine->SetCurrentFocalLength(OriginalFocalLength);
            Cine->SetCurrentAperture(OriginalAperture);
        }
    }
    bHasSavedLens = false;
}
