#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "TSTSSLevelOneReviewAsset.generated.h"

// DRAFT level-one data for DESIGN REVIEW ONLY. Nothing here is a live combatant,
// a SaveGame field, a spell authorization, or creator-approved numerical balance.
USTRUCT(BlueprintType)
struct FTSTSSLevelOneDraftStats
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Level One Review")
    FName CharacterId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Level One Review")
    int32 Level = 1;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Level One Review")
    int32 MaxHealth = 0;

    // Independently named, because FTSTSSCombatant::Resource has NOT been
    // accepted as MP and cannot be silently reinterpreted.
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Level One Review")
    int32 ProposedMaxMP = 0;

    // This is only a review metric; no magical damage formula is authorized.
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Level One Review")
    int32 ProposedMAG = 0;
};

UCLASS(BlueprintType)
class TOSAILTHESTARRYSKY_API UTSTSSLevelOneReviewAsset : public UDataAsset
{
    GENERATED_BODY()

public:
    // Opt-in editor preview ONLY. It never means creator approval or gameplay admission.
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Level One Review")
    bool bEnableLocalReview = false;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Level One Review")
    TArray<FTSTSSLevelOneDraftStats> Entries;

    // Read-only, non-authorizing Blueprint preview gate; no save/stat mutation.
    UFUNCTION(BlueprintPure, Category="TSTSS|Level One Review")
    bool IsConsistentForReview() const;
};
