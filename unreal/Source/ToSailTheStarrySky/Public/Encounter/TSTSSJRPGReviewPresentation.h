#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "TSTSSJRPGReviewPresentation.generated.h"

UENUM(BlueprintType)
enum class ETSTSSJRPGReviewSequencePhase : uint8
{
    Exploration,
    EncounterFlash,
    BattleReveal,
    Combat,
    VictoryFanfare,
    Celebration,
    Rewards,
    Defeat,
    ReturnFlash,
    ReturnReady
};

// Deterministic stage machine. Audio and visuals are side effects of a
// separately-authorized game-world adapter. No reward or battle completion
// is inferred merely from elapsed time.
UCLASS(BlueprintType)
class TOSAILTHESTARRYSKY_API UTSTSSJRPGReviewPresentation : public UObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="TSTSS|Review Sequence")
    bool TryBegin(int32 TicketSerial);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Review Sequence")
    bool Advance(float DeltaSeconds);

    // Roll back an encounter if map/battle admission is denied before combat.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Review Sequence")
    bool TryAbortBeforeCombat(int32 TicketSerial);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Review Sequence")
    bool TryEnterCombat(int32 TicketSerial);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Review Sequence")
    bool TryResolveVictory(int32 TicketSerial);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Review Sequence")
    bool TryResolveDefeat(int32 TicketSerial);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Review Sequence")
    bool TryFlee(int32 TicketSerial);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Review Sequence")
    bool TryDismissResult(int32 TicketSerial);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Review Sequence")
    bool TryFinishReturn(int32 TicketSerial);

    UFUNCTION(BlueprintPure, Category="TSTSS|Review Sequence")
    ETSTSSJRPGReviewSequencePhase GetPhase() const {return Phase;}

    UFUNCTION(BlueprintPure, Category="TSTSS|Review Sequence")
    int32 GetTicketSerial() const {return ActiveTicket;}

    UFUNCTION(BlueprintPure, Category="TSTSS|Review Sequence")
    float GetPhaseProgress() const;

    UFUNCTION(BlueprintPure, Category="TSTSS|Review Sequence")
    bool IsAwaitingBattleStart() const
    {return Phase==ETSTSSJRPGReviewSequencePhase::BattleReveal && Elapsed>=.36f;}

private:
    UPROPERTY(Transient)
    ETSTSSJRPGReviewSequencePhase Phase=
        ETSTSSJRPGReviewSequencePhase::Exploration;
    UPROPERTY(Transient)
    int32 ActiveTicket=0;
    float Elapsed=0.f;
    void SetPhase(ETSTSSJRPGReviewSequencePhase Next)
    {Phase=Next;Elapsed=0.f;}
    static float Duration(ETSTSSJRPGReviewSequencePhase Phase);
};
