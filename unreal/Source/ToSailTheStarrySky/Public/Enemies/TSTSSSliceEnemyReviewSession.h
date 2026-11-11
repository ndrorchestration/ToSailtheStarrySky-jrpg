#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "Combat/TSS_CombatTurnManager.h"
#include "Enemies/TSTSSSliceEnemyCatalog.h"
#include "TSTSSSliceEnemyReviewSession.generated.h"

// The explicit options represent what may exist in a review-only battle.
// These do not advance, infer or persist the actual First Wake story.
UENUM(BlueprintType)
enum class ETSTSSSliceReviewPartyStage : uint8
{
    EnderOnly,
    IoniaRecruited,
    AfterSplashdown
};

// Pure review battle controller using the EXISTING authoritative turn manager.
// No new combat math, save slot, quest flag, editor world or spawning authority.
// All entry points are denied outright in shipping builds.
UCLASS(BlueprintType)
class TOSAILTHESTARRYSKY_API UTSTSSSliceEnemyReviewSession : public UObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="TSTSS|Enemy Review")
    bool TryStart(FName ReviewWavePreset, ETSTSSSliceReviewPartyStage PartyStage);

    // Two explicit enemy slots, never the player or a bystander.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Enemy Review")
    bool TryPlayerStrike(int32 EnemySlot);

    // The existing review AI submits commands through UTSS_CombatTurnManager.
    // Fail closed if enemy identity, learned skills or authority do not match.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Enemy Review")
    bool TryAdvanceEnemyTurns();

    UFUNCTION(BlueprintPure, Category="TSTSS|Enemy Review")
    FString GetReviewStatus() const;

    UFUNCTION(BlueprintPure, Category="TSTSS|Enemy Review")
    UTSS_CombatTurnManager* GetReviewManager() const { return Manager.Get(); }

    UFUNCTION(BlueprintPure, Category="TSTSS|Enemy Review")
    TArray<FName> GetReviewActivePartyIds() const { return ActivePartyIds; }

    UFUNCTION(BlueprintPure, Category="TSTSS|Enemy Review")
    TArray<FName> GetReviewEnemyIds() const { return EnemyIds; }

private:
    UPROPERTY(Transient)
    TObjectPtr<UTSS_CombatTurnManager> Manager;

    UPROPERTY(Transient)
    TObjectPtr<UDataTable> ReviewSkillTable;

    UPROPERTY(Transient)
    TArray<FName> ActivePartyIds;

    UPROPERTY(Transient)
    TArray<FName> EnemyIds;

    TMap<FName, ETSTSSSliceEnemyKind> EnemyKinds;
};
