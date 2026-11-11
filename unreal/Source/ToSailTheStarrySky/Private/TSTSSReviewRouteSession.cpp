#include "TSTSSReviewRouteSession.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

FString UTSTSSReviewRouteSession::GetReviewLevelName(const ETSTSSReviewMap Stage)
{
    // Exact package basenames, not suffix/prefix matching. Never admit
    // a production map or a similarly named user map into review travel.
    switch (Stage)
    {
    case ETSTSSReviewMap::DenithHarbor: return TEXT("VS01_DenithHarbor_TraversalReviewV1");
    case ETSTSSReviewMap::AureateInteriors: return TEXT("VS02_AureateInteriors_TraversalReviewV1");
    case ETSTSSReviewMap::FirstWakeSky: return TEXT("VS03_FirstWakeSky_TraversalReviewV1");
    case ETSTSSReviewMap::SplashdownSea: return TEXT("VS04_SplashdownSea_TraversalReviewV1");
    case ETSTSSReviewMap::DenithFuelShanty: return TEXT("VS05_DenithFuelShanty_TraversalReviewV1");
    case ETSTSSReviewMap::SplashdownShore: return TEXT("VS06_SplashdownShore_TraversalReviewV1");
    default: return FString();
    }
}

bool UTSTSSReviewRouteSession::IsEligible(
    const ETSTSSReviewMap Departure, const UTSTSSFirstWakeState* Story)
{
    if (!IsValid(Story) || !Story->HasStarted()) return false;
    const ETSTSSFirstWakeBeat Beat = Story->GetCurrentBeat();
    const uint8 Mask = Story->GetInspectionMask();
    if ((Mask & ~0x07u) != 0) return false;

    switch (Departure)
    {
    case ETSTSSReviewMap::DenithHarbor:
        // Boarding is the minimum; the seven-stop parent may also have
        // completed its inspections before Ender chose to board visually.
        return Beat == ETSTSSFirstWakeBeat::BoardedAureateWake ||
               (Beat == ETSTSSFirstWakeBeat::EngineeringChecked && Mask == 0x07u);
    case ETSTSSReviewMap::AureateInteriors:
        // Never infer launch from three inspections or boarding alone.
        return Beat == ETSTSSFirstWakeBeat::Launched && Mask == 0x07u;
    case ETSTSSReviewMap::FirstWakeSky:
        // Travel to the actual water lab is NOT sea contact itself.
        return Beat == ETSTSSFirstWakeBeat::Launched && Mask == 0x07u;
    case ETSTSSReviewMap::SplashdownSea:
        // Only the existing physical water gate can issue this beat.
        return Beat == ETSTSSFirstWakeBeat::FlotationConfirmed && Mask == 0x07u;
    case ETSTSSReviewMap::DenithFuelShanty:
        // An actual post-flotation reserve investigation is needed.
        return Beat == ETSTSSFirstWakeBeat::EmptyReserveInspected && Mask == 0x07u;
    case ETSTSSReviewMap::SplashdownShore:
    default:
        return false;
    }
}

bool UTSTSSReviewRouteSession::ArmNextStage(
    const UWorld* World, const ETSTSSReviewMap Departure,
    const UTSTSSFirstWakeState* Story, FString& OutTargetLevel)
{
    OutTargetLevel.Empty();
#if WITH_EDITOR
    if (bPending || !World || World->WorldType != EWorldType::PIE ||
        !IsEligible(Departure, Story)) return false;

    const FString FromName = GetReviewLevelName(Departure);
    const uint8 Index = static_cast<uint8>(Departure);
    if (FromName.IsEmpty() ||
        UGameplayStatics::GetCurrentLevelName(World, true) != FromName ||
        Index >= static_cast<uint8>(ETSTSSReviewMap::SplashdownShore))
    {
        return false;
    }
    const ETSTSSReviewMap Next = static_cast<ETSTSSReviewMap>(Index + 1u);
    const FString NextLevel = GetReviewLevelName(Next);
    if (NextLevel.IsEmpty()) return false;

    bPending = true;
    ExpectedArrival = Next;
    SnapshotBeat = Story->GetCurrentBeat();
    SnapshotInspectionMask = Story->GetInspectionMask();
    OutTargetLevel = NextLevel;
    return true;
#else
    (void)World;
    (void)Departure;
    (void)Story;
    return false;
#endif
}

bool UTSTSSReviewRouteSession::ConsumeArrival(
    const UWorld* World, UTSTSSFirstWakeState* Story)
{
    const bool bWasPending = bPending;
    const ETSTSSReviewMap Arrival = ExpectedArrival;
    const ETSTSSFirstWakeBeat Beat = SnapshotBeat;
    const uint8 Mask = SnapshotInspectionMask;
    // One-shot consumption precedes all validation and Restore() mutation.
    CancelPending();
#if WITH_EDITOR
    if (!bWasPending || !World || World->WorldType != EWorldType::PIE ||
        !IsValid(Story) ||
        UGameplayStatics::GetCurrentLevelName(World, true) != GetReviewLevelName(Arrival))
    {
        return false;
    }
    return Story->Restore(true, Beat, Mask);
#else
    (void)World;
    (void)Story;
    (void)bWasPending;
    (void)Arrival;
    (void)Beat;
    (void)Mask;
    return false;
#endif
}

void UTSTSSReviewRouteSession::CancelPending()
{
    bPending = false;
    ExpectedArrival = ETSTSSReviewMap::DenithHarbor;
    SnapshotBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    SnapshotInspectionMask = 0;
}
