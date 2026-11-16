#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "TSTSSJRPGReviewRewards.generated.h"

USTRUCT(BlueprintType)
struct FTSTSSJRPGReviewLootLine
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Review Rewards")
    FName ItemId=NAME_None;
    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Review Rewards")
    FString DisplayName;
    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Review Rewards")
    int32 Quantity=0;
};

USTRUCT(BlueprintType)
struct FTSTSSJRPGReviewReward
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Review Rewards")
    int32 TicketSerial=0;
    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Review Rewards")
    FName SourceWave=NAME_None;
    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Review Rewards")
    int32 GoldEarned=0;
    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Review Rewards")
    int32 XpEachPartyMember=0;
    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Review Rewards")
    TArray<FName> AwardedPartyIds;
    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Review Rewards")
    TArray<FTSTSSJRPGReviewLootLine> Items;
    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Review Rewards")
    bool bReviewOnly=true;
};

// This is a REAL in-session transaction ledger with cumulative balances,
// but NOT a SaveGame/inventory/progression integration. Only a verified
// victory transition in the review flow is permitted to call TryAwardOnce.
UCLASS(BlueprintType)
class TOSAILTHESTARRYSKY_API UTSTSSJRPGReviewRewards : public UObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="TSTSS|Review Rewards")
    bool TryAwardOnce(int32 TicketSerial, FName WavePreset,
                      const TArray<FName>& ActiveParty,
                      FTSTSSJRPGReviewReward& OutReward);

    UFUNCTION(BlueprintPure, Category="TSTSS|Review Rewards")
    int32 GetGoldBalance() const {return GoldBalance;}

    UFUNCTION(BlueprintPure, Category="TSTSS|Review Rewards")
    int32 GetExperienceTotal(FName PartyId) const;

    UFUNCTION(BlueprintPure, Category="TSTSS|Review Rewards")
    int32 GetItemCount(FName ItemId) const;

    UFUNCTION(BlueprintPure, Category="TSTSS|Review Rewards")
    bool WasTicketAwarded(int32 TicketSerial) const
    {return AwardedTickets.Contains(TicketSerial);}

private:
    UPROPERTY(Transient)
    int32 GoldBalance=0;
    UPROPERTY(Transient)
    TMap<FName,int32> XpBalances;
    UPROPERTY(Transient)
    TMap<FName,int32> Inventory;
    UPROPERTY(Transient)
    TSet<int32> AwardedTickets;

    static bool IsExactReviewParty(const TArray<FName>& Party);
    static bool TryMakeReward(FName Wave, FTSTSSJRPGReviewReward& Out);
};
