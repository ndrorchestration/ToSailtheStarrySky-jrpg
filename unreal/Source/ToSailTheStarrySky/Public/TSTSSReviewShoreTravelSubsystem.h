#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSReviewShoreTravelSubsystem.generated.h"

class UWorld;

// One-use, memory-only First Wake route across native *review* maps.
// No save, item, spell, recruitment, or canonical progression authority.
UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSReviewShoreTravelSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    static const TCHAR* ShorePackage();
    static FString NextReviewMap(const UTSTSSFirstWakeState* State, const FString& SourceMap);
    static bool IsEligible(const UTSTSSFirstWakeState* State, const FString& SourceMap);
    bool QueueShore(UWorld* World, UTSTSSFirstWakeState* State);
    bool ConsumeShoreArrival(const UWorld* World, UTSTSSFirstWakeState* State);
    const FString& GetPendingMapPackage() const { return PendingMapPackage; }

private:
    bool bPending = false;
    FString PendingMapPackage;
    ETSTSSFirstWakeBeat PendingBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    uint8 PendingInspectionMask = 0;
};
