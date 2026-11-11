#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSReviewShoreTravelSubsystem.generated.h"

class UWorld;

// Transient review-only story handoff: no save slot, equipment, spells,
// enemies, party recruitment, or production map authority is modified.
UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSReviewShoreTravelSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    static const TCHAR* ShorePackage();
    static bool IsEligible(const UTSTSSFirstWakeState* State, const FString& SourceMap);
    bool QueueShore(UWorld* World, const UTSTSSFirstWakeState* State);
    bool ConsumeShoreArrival(const UWorld* World, UTSTSSFirstWakeState* State);

private:
    bool bPending = false;
    ETSTSSFirstWakeBeat PendingBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    uint8 PendingInspectionMask = 0;
};
