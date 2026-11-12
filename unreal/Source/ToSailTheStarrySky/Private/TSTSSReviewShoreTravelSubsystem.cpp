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
    if (!IsValid(State) || !State->HasStarted() || !State->AreInspectionsComplete())
    {
        return FString();
    }
    const ETSTSSFirstWakeBeat Beat = State->GetCurrentBeat();
    if (IsPreludeScene(SourceMap) && Beat == ETSTSSFirstWakeBeat::EngineeringChecked)
    {
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
        World->GetNetMode() != NM_Standalone || bPending)
    {
        return false;
    }
    const FString SourceMap = UGameplayStatics::GetCurrentLevelName(World, true);
    const FString Destination = NextReviewMap(State, SourceMap);
    if (Destination.IsEmpty() || !FPackageName::DoesPackageExist(*Destination))
    {
        return false;
    }
    // Pressing K is the explicit launch action. Never manufacture sea contact
    // or flotation; only native water physics may authorize those beats.
    if (IsPreludeScene(SourceMap) && !State->AdvanceTo(ETSTSSFirstWakeBeat::Launched))
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
