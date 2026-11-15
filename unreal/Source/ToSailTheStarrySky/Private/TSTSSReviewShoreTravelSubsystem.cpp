#include "TSTSSReviewShoreTravelSubsystem.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/PackageName.h"

namespace
{
constexpr const TCHAR* PreludeName = TEXT("FirstWake_PreludeInteraction_V2");
constexpr const TCHAR* VisualReviewPreludeName = TEXT("FirstWake_PreludeInteraction_V5_VisualReview");
inline bool IsPreludeScene(const FString& Name)
{
    return Name == PreludeName || Name == VisualReviewPreludeName;
}
constexpr const TCHAR* ShipName = TEXT("VS02_AureateInteriors");
// A separately built nonshipping optical-review scene. Entry must be explicit
// from the already-authorized ship interior; K launch still follows the sky.
constexpr const TCHAR* OpticalName = TEXT("M_EnginePresentationReview");
constexpr const TCHAR* OpticalPackage =
    TEXT("/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview");
constexpr const TCHAR* SkyName = TEXT("VS03_FirstWakeSky");
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
    // Always consume, even if the next level or pawn is wrong.
    bPending = false;
    PendingMapPackage.Reset();
#if WITH_EDITOR
    if (bHadTicket && World &&
        (World->WorldType == EWorldType::PIE || World->WorldType == EWorldType::Game) &&
        World->GetNetMode() == NM_Standalone && World->GetOutermost() &&
        World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")) &&
        Target.StartsWith(TEXT("/Game/TSTSS/Review/")) &&
        UGameplayStatics::GetCurrentLevelName(World, true) == FPackageName::GetShortName(Target) &&
        IsValid(State))
    {
        return State->Restore(true, Beat, Mask);
    }
#else
    (void)World;
    (void)State;
    (void)Target;
    (void)Beat;
    (void)Mask;
#endif
    return false;
}
