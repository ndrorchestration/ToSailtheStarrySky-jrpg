#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSReviewShoreTravelSubsystem.generated.h"

class UWorld;
class ATSTSSExplorerCharacter;

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
    bool QueueOpticalInspection(UWorld* World, UTSTSSFirstWakeState* State);
    bool ConsumeShoreArrival(const UWorld* World, UTSTSSFirstWakeState* State);
    // One-shot private pawn continuity for a REAL V5 -> VS02 PIE boarding ticket.
    // Never authorizes travel, story beats, save writes, or production assets.
    bool TryResumePrivateEnderInShipRoom(ATSTSSExplorerCharacter* DefaultPawn);
#if WITH_EDITOR
    // True only during the synchronous spawn after an earned one-use ticket.
    bool IsPrivateEnderShipSpawnInProgress() const { return bPrivateEnderShipSpawnInProgress; }
#endif
    const FString& GetPendingMapPackage() const { return PendingMapPackage; }

private:
    // Strong transient class reference survives OpenLevel, never serializes.
    // Only the exact private Ender class from an already-possessed V5 pawn
    // may be carried; no dynamic class selection or arbitrary content load.
    UPROPERTY(Transient)
    TSubclassOf<ATSTSSExplorerCharacter> PendingPrivateEnderClass;
    bool bPrivateEnderArrivalReady = false;
#if WITH_EDITOR
    bool bPrivateEnderShipSpawnInProgress = false;
#endif
    bool bPending = false;
    FString PendingMapPackage;
    ETSTSSFirstWakeBeat PendingBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    uint8 PendingInspectionMask = 0;
};
