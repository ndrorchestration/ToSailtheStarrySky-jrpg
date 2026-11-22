#include "TSTSSReviewShoreTravelSubsystem.h"
#include "TSTSSExplorerCharacter.h"
#include "UObject/Package.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/PackageName.h"
#if WITH_EDITOR
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#endif

namespace
{
constexpr const TCHAR* PreludeName = TEXT("FirstWake_PreludeInteraction_V2");
constexpr const TCHAR* VisualReviewPreludeName = TEXT("FirstWake_PreludeInteraction_V5_VisualReview");
inline bool IsPreludeScene(const FString& Name)
{
    return Name == PreludeName || Name == VisualReviewPreludeName;
}
constexpr const TCHAR* ShipName = TEXT("VS02_AureateInteriors");
// Only locally licensed editor-staged Ender; never a public content dependency.
constexpr const TCHAR* PrivateEnderPawnClassPath = TEXT(
    "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/"
    "BP_EnderLocomotionPreview_NONCANONICAL."
    "BP_EnderLocomotionPreview_NONCANONICAL_C");
constexpr const TCHAR* ShipPackage =
    TEXT("/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors");
#if WITH_EDITOR
constexpr const TCHAR* PrivatePreludePackage =
    TEXT("/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/FirstWake_PreludeInteraction_V5_VisualReview");
bool IsPrivateEnderStandaloneWorld(const UWorld* World, const TCHAR* ExpectedPackage)
{
    return World && ExpectedPackage &&
        World->WorldType == EWorldType::Game &&
        World->GetNetMode() == NM_Standalone &&
        FParse::Param(FCommandLine::Get(), TEXT("TSTSSPrivateEnderLowMemReview")) &&
        World->GetOutermost() &&
        World->GetOutermost()->GetName() == ExpectedPackage;
}
#endif
// A separately built nonshipping optical-review scene. Entry must be explicit
// from the already-authorized ship interior; K launch still follows the sky.
constexpr const TCHAR* OpticalName = TEXT("M_EnginePresentationReview");
constexpr const TCHAR* OpticalPackage =
    TEXT("/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview");
constexpr const TCHAR* SkyName = TEXT("VS03_FirstWakeSky");
constexpr const TCHAR* SkyPackage = TEXT("/Game/TSTSS/Review/VerticalSlice/VS03_FirstWakeSky");
constexpr const TCHAR* SeaName = TEXT("VS04_SplashdownSea");
constexpr const TCHAR* FuelName = TEXT("VS05_DenithFuelShanty");
constexpr const TCHAR* ShoreMap = TEXT("/Game/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review");
}

const TCHAR* UTSTSSReviewShoreTravelSubsystem::ShorePackage()
{
    return ShoreMap;
}

FString UTSTSSReviewShoreTravelSubsystem::NextReviewMap(
    const UTSTSSFirstWakeState* State, const FString& SourceMap)
{
    if (!IsValid(State) || !State->HasStarted())
    {
        return FString();
    }
    const ETSTSSFirstWakeBeat Beat = State->GetCurrentBeat();
    // Creator-directed engine-room reboard: V5 boards BEFORE inspecting.
    // Older partially inspected V5 saves retain their genuine bitmask on
    // arrival; no travel automatically grants any missing inspection.
    if (SourceMap == VisualReviewPreludeName &&
        (Beat == ETSTSSFirstWakeBeat::BoardedAureateWake ||
         (Beat == ETSTSSFirstWakeBeat::EngineeringChecked &&
          State->AreInspectionsComplete())))
    {
        return TEXT("/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors");
    }
    // The V2 regression scene retains its original signoff-before-sky route.
    // Once in VS02, sky launch still requires all three inspections.
    if (!State->AreInspectionsComplete())
    {
        return FString();
    }
    if (SourceMap == PreludeName && Beat == ETSTSSFirstWakeBeat::EngineeringChecked)
    {
        return TEXT("/Game/TSTSS/Review/VerticalSlice/VS03_FirstWakeSky");
    }
    if (SourceMap == ShipName && Beat == ETSTSSFirstWakeBeat::EngineeringChecked)
    {
        // No sky/sea claim until the player explicitly requests departure.
        return TEXT("/Game/TSTSS/Review/VerticalSlice/VS03_FirstWakeSky");
    }
    if (SourceMap == OpticalName && Beat == ETSTSSFirstWakeBeat::EngineeringChecked)
    {
        // An opt-in camera study is NOT a launch, splashdown or story advance.
        return TEXT("/Game/TSTSS/Review/VerticalSlice/VS03_FirstWakeSky");
    }
    if (SourceMap == SkyName && Beat == ETSTSSFirstWakeBeat::Launched)
    {
        return TEXT("/Game/TSTSS/Review/VerticalSlice/VS04_SplashdownSea");
    }
    if (SourceMap == SeaName && Beat == ETSTSSFirstWakeBeat::FlotationConfirmed)
    {
        return TEXT("/Game/TSTSS/Review/VerticalSlice/VS05_DenithFuelShanty");
    }
    if (SourceMap == FuelName && Beat == ETSTSSFirstWakeBeat::EmptyReserveInspected)
    {
        return ShoreMap;
    }
    return FString();
}

bool UTSTSSReviewShoreTravelSubsystem::IsEligible(
    const UTSTSSFirstWakeState* State, const FString& SourceMap)
{
    return !NextReviewMap(State, SourceMap).IsEmpty();
}

bool UTSTSSReviewShoreTravelSubsystem::QueueShore(
    UWorld* World, UTSTSSFirstWakeState* State)
{
#if WITH_EDITOR
    // Dedicated source/beat pair, local PIE or Editor standalone, existing
    // native target package, and no duplicate outstanding handoff.
    if (!World ||
        (World->WorldType != EWorldType::PIE && World->WorldType != EWorldType::Game) ||
        World->GetNetMode() != NM_Standalone ||
        !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")) ||
        bPending)
    {
        return false;
    }
    const FString SourceMap = UGameplayStatics::GetCurrentLevelName(World, true);
    const FString Destination = NextReviewMap(State, SourceMap);
    if (Destination.IsEmpty() || !FPackageName::DoesPackageExist(*Destination))
    {
        return false;
    }
    // K explicitly requests travel; only the ship/legacy V2 departure
    // counts as launch. Water beats require physical observation.
    // V5 -> engine room preserves BoardedAureateWake AND all inspection bits.
    // Sky launch remains locked until shipboard signoff is genuinely earned.
    // No level travel may synthesize SeaContact or FlotationConfirmed.
    if (((IsPreludeScene(SourceMap) && SourceMap != VisualReviewPreludeName) ||
         SourceMap == ShipName || SourceMap == OpticalName) &&
        !State->AdvanceTo(ETSTSSFirstWakeBeat::Launched))
    {
        return false;
    }
    // Record only an *already possessed*, exact private Ender pawn on the
    // V5->VS02 boarding ticket. No asset path loading, arbitrary Blueprint,
    // production scene, save slot or authoring-map mutation.
    PendingPrivateEnderClass = nullptr;
    bPrivateEnderArrivalReady = false;
    bPrivateEnderSkyArrivalReady = false;
    if ((World->WorldType == EWorldType::PIE ||
         IsPrivateEnderStandaloneWorld(World, PrivatePreludePackage)) &&
        SourceMap == VisualReviewPreludeName && Destination == ShipPackage)
    {
        APlayerController* PC = UGameplayStatics::GetPlayerController(World, 0);
        ATSTSSExplorerCharacter* SourcePawn = PC
            ? Cast<ATSTSSExplorerCharacter>(PC->GetPawn()) : nullptr;
        if (IsValid(SourcePawn) && SourcePawn->IsPlayerControlled() &&
            SourcePawn->GetClass()->GetPathName() == PrivateEnderPawnClassPath)
        {
            PendingPrivateEnderClass = SourcePawn->GetClass();
            UE_LOG(LogTemp, Display,
                TEXT("TSTSS_PRIVATE_ENDER_REVIEW_BOARDING_CLASS_CUSTODY staged=1 private_only=1"));
        }
    }
    // A separate editor-only experiment may carry the already possessed
    // exact private Ender study body from earned engineering signoff to
    // the sky observer map. Without the explicit flag, existing behavior
    // stays untouched. Never load a licensed class by name here.
    if (FParse::Param(FCommandLine::Get(), TEXT("TSTSSPrivateEnderSkyContinuityReview")) &&
        World->WorldType == EWorldType::PIE &&
        World->GetNetMode() == NM_Standalone &&
        World->GetOutermost() &&
        World->GetOutermost()->GetName().StartsWith(
            TEXT("/Game/TSTSS/Review/VerticalSlice/UEDPIE_")) &&
        SourceMap == ShipName && Destination == SkyPackage &&
        State->GetCurrentBeat() == ETSTSSFirstWakeBeat::Launched &&
        State->AreInspectionsComplete())
    {
        APlayerController* PC = UGameplayStatics::GetPlayerController(World, 0);
        const ATSTSSExplorerCharacter* SourcePawn = PC
            ? Cast<ATSTSSExplorerCharacter>(PC->GetPawn()) : nullptr;
        if (IsValid(SourcePawn) && PC->GetPawn() == SourcePawn &&
            SourcePawn->GetClass()->GetPathName().Equals(
                PrivateEnderPawnClassPath, ESearchCase::CaseSensitive))
        {
            PendingPrivateEnderClass = SourcePawn->GetClass();
            UE_LOG(LogTemp, Display,
                TEXT("TSTSS_PRIVATE_ENDER_SKY_CLASS_CUSTODY staged=1 earned_signoff=1 opted_in=1 review_only=1"));
        }
    }
    PendingBeat = State->GetCurrentBeat();
    PendingInspectionMask = State->GetInspectionMask();
    PendingMapPackage = Destination;
    bPending = true;
    return true;
#else
    (void)World;
    (void)State;
    return false;
#endif
}

bool UTSTSSReviewShoreTravelSubsystem::QueueOpticalInspection(
    UWorld* World, UTSTSSFirstWakeState* State)
{
#if WITH_EDITOR
    // A distinct, explicit O-key review handoff. Does NOT replace the normal
    // K route, alter story beats or load arbitrary maps. Exact PIE-only ship
    // source and earned engineering signoff are both necessary.
    if (!World || World->WorldType != EWorldType::PIE ||
        World->GetNetMode() != NM_Standalone || bPending ||
        !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")) ||
        UGameplayStatics::GetCurrentLevelName(World, true) != ShipName ||
        !IsValid(State) || !State->HasStarted() ||
        State->GetCurrentBeat() != ETSTSSFirstWakeBeat::EngineeringChecked ||
        !State->AreInspectionsComplete() ||
        State->IsSeabourneRecoveryLocked() ||
        !FPackageName::DoesPackageExist(OpticalPackage))
    {
        return false;
    }
    // Same one-use in-memory ticket that restores REAL earned story state on
    // arrival. No synthetic progression and no save-slot write.
    PendingPrivateEnderClass = nullptr;
    bPrivateEnderArrivalReady = false;
    PendingBeat = State->GetCurrentBeat();
    PendingInspectionMask = State->GetInspectionMask();
    PendingMapPackage = OpticalPackage;
    bPending = true;
    return true;
#else
    (void)World;
    (void)State;
    return false;
#endif
}

bool UTSTSSReviewShoreTravelSubsystem::ConsumeShoreArrival(
    const UWorld* World, UTSTSSFirstWakeState* State)
{
    const bool bHadTicket = bPending;
    const FString Target = PendingMapPackage;
    const ETSTSSFirstWakeBeat Beat = PendingBeat;
    const uint8 Mask = PendingInspectionMask;
    // Always consume the travel ticket, including an invalid destination.
    bPending = false;
    PendingMapPackage.Reset();
    bPrivateEnderArrivalReady = false;
    bPrivateEnderSkyArrivalReady = false;
#if WITH_EDITOR
    if (bHadTicket && World &&
        (World->WorldType == EWorldType::PIE || World->WorldType == EWorldType::Game) &&
        World->GetNetMode() == NM_Standalone && World->GetOutermost() &&
        World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")) &&
        Target.StartsWith(TEXT("/Game/TSTSS/Review/")) &&
        UGameplayStatics::GetCurrentLevelName(World, true) == FPackageName::GetShortName(Target) &&
        IsValid(State))
    {
        const bool bRestored = State->Restore(true, Beat, Mask);
        bPrivateEnderArrivalReady =
            bRestored && (World->WorldType == EWorldType::PIE ||
                IsPrivateEnderStandaloneWorld(World, ShipPackage)) &&
            Target == ShipPackage && IsValid(PendingPrivateEnderClass.Get()) &&
            PendingPrivateEnderClass.Get()->GetPathName() == PrivateEnderPawnClassPath;
        bPrivateEnderSkyArrivalReady =
            bRestored && World->WorldType == EWorldType::PIE &&
            Target == SkyPackage &&
            World->GetOutermost()->GetName().StartsWith(
                TEXT("/Game/TSTSS/Review/VerticalSlice/UEDPIE_")) &&
            World->GetOutermost()->GetName().EndsWith(
                TEXT("_VS03_FirstWakeSky")) &&
            State->GetCurrentBeat() == ETSTSSFirstWakeBeat::Launched &&
            State->AreInspectionsComplete() &&
            IsValid(PendingPrivateEnderClass.Get()) &&
            PendingPrivateEnderClass.Get()->GetPathName() == PrivateEnderPawnClassPath;
        if (!bPrivateEnderArrivalReady && !bPrivateEnderSkyArrivalReady)
        {
            PendingPrivateEnderClass = nullptr;
        }
        return bRestored;
    }
    PendingPrivateEnderClass = nullptr;
#else
    (void)World;
    (void)State;
    (void)Target;
    (void)Beat;
    (void)Mask;
#endif
    return false;
}

bool UTSTSSReviewShoreTravelSubsystem::TryResumePrivateEnderInShipRoom(
    ATSTSSExplorerCharacter* DefaultPawn)
{
#if WITH_EDITOR
    if (!bPrivateEnderArrivalReady)
    {
        return false;
    }
    // Consume the one-use class ticket BEFORE spawn, preventing reentrant
    // BeginPlay, a failed resume, or a second player from replaying it.
    UClass* PrivateClass = PendingPrivateEnderClass.Get();
    bPrivateEnderArrivalReady = false;
    PendingPrivateEnderClass = nullptr;
    UWorld* World = IsValid(DefaultPawn) ? DefaultPawn->GetWorld() : nullptr;
    APlayerController* PC = World ? UGameplayStatics::GetPlayerController(World, 0) : nullptr;
    UTSTSSFirstWakeState* State = IsValid(DefaultPawn)
        ? DefaultPawn->GetFirstWakeState() : nullptr;
    if (!World || (World->WorldType != EWorldType::PIE &&
        !IsPrivateEnderStandaloneWorld(World, ShipPackage)) ||
        World->GetNetMode() != NM_Standalone ||
        !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(
            TEXT("/Game/TSTSS/Review/VerticalSlice/")) ||
        UGameplayStatics::GetCurrentLevelName(World, true) != ShipName ||
        !IsValid(PC) || PC->GetPawn() != DefaultPawn ||
        DefaultPawn->GetClass() != ATSTSSExplorerCharacter::StaticClass() ||
        !IsValid(State) || !State->HasStarted() ||
        (State->GetCurrentBeat() != ETSTSSFirstWakeBeat::BoardedAureateWake &&
         State->GetCurrentBeat() != ETSTSSFirstWakeBeat::EngineeringChecked) ||
        !PrivateClass || PrivateClass->GetPathName() != PrivateEnderPawnClassPath ||
        !PrivateClass->IsChildOf(ATSTSSExplorerCharacter::StaticClass()))
    {
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_PRIVATE_ENDER_VS02_REBIND_HOLD scope_or_source_state"));
        return false;
    }
    // The existing map spawned its ordinary pawn and already restored story
    // and staged real E targets. Replace ONLY that transient PIE pawn; keep
    // GameMode, level assets, script authority, and the original map unchanged.
    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    // BeginPlay binds a private body only during this synchronous spawn.
    // The ticket was already consumed, so no other spawn can reuse it.
    bPrivateEnderShipSpawnInProgress = true;
    ATSTSSExplorerCharacter* Ender = World->SpawnActor<ATSTSSExplorerCharacter>(
        PrivateClass, DefaultPawn->GetActorTransform(), Params);
    bPrivateEnderShipSpawnInProgress = false;
    if (!IsValid(Ender) || Ender->GetClass() != PrivateClass ||
        !IsValid(Ender->GetFirstWakeState()) ||
        !Ender->GetFirstWakeState()->Restore(
            true, State->GetCurrentBeat(), State->GetInspectionMask()))
    {
        if (IsValid(Ender)) Ender->Destroy();
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_PRIVATE_ENDER_VS02_REBIND_HOLD spawn_or_story_restore"));
        return false;
    }
    PC->Possess(Ender);
    if (PC->GetPawn() != Ender)
    {
        PC->Possess(DefaultPawn);
        Ender->Destroy();
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_PRIVATE_ENDER_VS02_REBIND_HOLD possess"));
        return false;
    }
    DefaultPawn->Destroy();
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_PRIVATE_ENDER_VS02_REBIND_OK possessed=1 class_exact=1 beat=%d mask=%u save_mutation=0 map_unchanged=1 art_NOT_APPROVED"),
        static_cast<int32>(Ender->GetFirstWakeState()->GetCurrentBeat()),
        Ender->GetFirstWakeState()->GetInspectionMask());
    return true;
#else
    (void)DefaultPawn;
    return false;
#endif
}

bool UTSTSSReviewShoreTravelSubsystem::TryResumePrivateEnderInSkyReview(
    ATSTSSExplorerCharacter* DefaultPawn)
{
#if WITH_EDITOR
    if (!bPrivateEnderSkyArrivalReady)
    {
        return false;
    }
    // The arrival ticket is single-use even if the private asset is missing.
    UClass* PrivateClass = PendingPrivateEnderClass.Get();
    bPrivateEnderSkyArrivalReady = false;
    PendingPrivateEnderClass = nullptr;
    UWorld* World = IsValid(DefaultPawn) ? DefaultPawn->GetWorld() : nullptr;
    APlayerController* PC = World ? UGameplayStatics::GetPlayerController(World, 0) : nullptr;
    UTSTSSFirstWakeState* State = IsValid(DefaultPawn)
        ? DefaultPawn->GetFirstWakeState() : nullptr;
    if (!World || World->WorldType != EWorldType::PIE ||
        World->GetNetMode() != NM_Standalone || !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(
            TEXT("/Game/TSTSS/Review/VerticalSlice/UEDPIE_")) ||
        !World->GetOutermost()->GetName().EndsWith(TEXT("_VS03_FirstWakeSky")) ||
        !FParse::Param(FCommandLine::Get(), TEXT("TSTSSPrivateEnderSkyContinuityReview")) ||
        UGameplayStatics::GetCurrentLevelName(World, true) != SkyName ||
        !IsValid(PC) || PC->GetPawn() != DefaultPawn ||
        DefaultPawn->GetClass() != ATSTSSExplorerCharacter::StaticClass() ||
        !IsValid(State) || State->GetCurrentBeat() != ETSTSSFirstWakeBeat::Launched ||
        !State->AreInspectionsComplete() ||
        !PrivateClass || !PrivateClass->GetPathName().Equals(
            PrivateEnderPawnClassPath, ESearchCase::CaseSensitive) ||
        !PrivateClass->IsChildOf(ATSTSSExplorerCharacter::StaticClass()))
    {
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_PRIVATE_ENDER_SKY_REBIND_HOLD scope_or_earned_state"));
        return false;
    }
    // The original VS03 is an observer scene with NO walkable deck. Reuse its
    // camera start and flying observation mode; this is NOT ship piloting.
    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    ATSTSSExplorerCharacter* Ender = World->SpawnActor<ATSTSSExplorerCharacter>(
        PrivateClass, DefaultPawn->GetActorTransform(), Params);
    if (!IsValid(Ender) || Ender->GetClass() != PrivateClass ||
        !IsValid(Ender->GetFirstWakeState()) ||
        !Ender->GetFirstWakeState()->Restore(
            true, State->GetCurrentBeat(), State->GetInspectionMask()) ||
        !IsValid(Ender->GetCharacterMovement()))
    {
        if (IsValid(Ender)) Ender->Destroy();
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_PRIVATE_ENDER_SKY_REBIND_HOLD spawn_or_story_restore"));
        return false;
    }
    Ender->GetCharacterMovement()->SetMovementMode(MOVE_Flying);
    PC->Possess(Ender);
    if (PC->GetPawn() != Ender)
    {
        PC->Possess(DefaultPawn);
        Ender->Destroy();
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_PRIVATE_ENDER_SKY_REBIND_HOLD possess"));
        return false;
    }
    DefaultPawn->Destroy();
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_PRIVATE_ENDER_SKY_REBIND_OK possessed=1 class_exact=1 beat=%d mask=%u movement=observer_flying no_piloting=1 art_NOT_APPROVED"),
        static_cast<int32>(Ender->GetFirstWakeState()->GetCurrentBeat()),
        Ender->GetFirstWakeState()->GetInspectionMask());
    return true;
#else
    (void)DefaultPawn;
    return false;
#endif
}
