#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSReviewRouteSession.generated.h"

// Nonshipping vertical-slice map handoff. This is not campaign persistence.
UENUM(BlueprintType)
enum class ETSTSSReviewMap : uint8
{
    DenithHarbor,
    AureateInteriors,
    FirstWakeSky,
    SplashdownSea,
    DenithFuelShanty,
    SplashdownShore
};

UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSReviewRouteSession : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    static FString GetReviewLevelName(ETSTSSReviewMap Stage);
    static bool IsEligible(ETSTSSReviewMap Departure, const UTSTSSFirstWakeState* Story);

    // Arms only the immediate next stage while in an exact matching PIE map.
    // Rejected requests never alter state. No disk save or gameplay reward.
    bool ArmNextStage(const class UWorld* World, ETSTSSReviewMap Departure,
                      const UTSTSSFirstWakeState* Story, FString& OutTargetLevel);

    // One-shot, destination-bound restore. Clears the pending handoff first,
    // even when the map is wrong, so stale requests cannot be replayed.
    bool ConsumeArrival(const class UWorld* World, UTSTSSFirstWakeState* Story);
    bool HasPendingTravel() const { return bPending; }
    void CancelPending();

private:
    UPROPERTY(Transient)
    bool bPending = false;

    UPROPERTY(Transient)
    ETSTSSReviewMap ExpectedArrival = ETSTSSReviewMap::DenithHarbor;

    UPROPERTY(Transient)
    ETSTSSFirstWakeBeat SnapshotBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;

    UPROPERTY(Transient)
    uint8 SnapshotInspectionMask = 0;
};
