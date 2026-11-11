#include "TSTSSReviewShoreTravelSubsystem.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/PackageName.h"

namespace
{
constexpr const TCHAR* PreludeName = TEXT("FirstWake_PreludeInteraction_V2");
constexpr const TCHAR* ShoreName = TEXT("L_VS06_ShoreMagicEnemyGear_Review");
constexpr const TCHAR* ShoreMap = TEXT("/Game/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review");
}

const TCHAR* UTSTSSReviewShoreTravelSubsystem::ShorePackage()
{
    return ShoreMap;
}

bool UTSTSSReviewShoreTravelSubsystem::IsEligible(
    const UTSTSSFirstWakeState* State, const FString& SourceMap)
{
    return IsValid(State) && State->HasStarted() &&
        SourceMap == PreludeName &&
        State->AreInspectionsComplete() &&
        static_cast<uint8>(State->GetCurrentBeat()) >=
            static_cast<uint8>(ETSTSSFirstWakeBeat::EmptyReserveInspected) &&
        static_cast<uint8>(State->GetCurrentBeat()) <=
            static_cast<uint8>(ETSTSSFirstWakeBeat::ReturnedToBerth);
}

bool UTSTSSReviewShoreTravelSubsystem::QueueShore(
    UWorld* World, const UTSTSSFirstWakeState* State)
{
#if WITH_EDITOR
    // Only the explicit editor review pathway may traverse to this unapproved
    // stage. An arbitrary level load or premature milestone is never enough.
    if (!World ||
        (World->WorldType != EWorldType::PIE &&
         World->WorldType != EWorldType::Game) ||
        World->GetNetMode() != NM_Standalone || bPending ||
        !IsEligible(State, UGameplayStatics::GetCurrentLevelName(World, true)) ||
        !FPackageName::DoesPackageExist(ShoreMap))
    {
        return false;
    }
    PendingBeat = State->GetCurrentBeat();
    PendingInspectionMask = State->GetInspectionMask();
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
    // One-use, fail-closed even if arrival map or state is wrong.
    bPending = false;
#if WITH_EDITOR
    if (bHadTicket && World &&
        (World->WorldType == EWorldType::PIE ||
         World->WorldType == EWorldType::Game) &&
        UGameplayStatics::GetCurrentLevelName(World, true) == ShoreName &&
        IsValid(State))
    {
        return State->Restore(true, PendingBeat, PendingInspectionMask);
    }
#else
    (void)World;
    (void)State;
#endif
    return false;
}
