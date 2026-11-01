#pragma once

#include "CoreMinimal.h"

// Source-only, review-stage Level 1 stat profile; NOT a SaveGame/Blueprint schema.
// These numeric fields are acceptance inputs, not creator-approved game values.
// In particular, MaxMagicPoints is NOT implicitly FTSTSSCombatant::MaxResource.
struct FTSTSSLevelOneRankCandidate
{
    FName CharacterId = NAME_None;
    int32 Level = 1;
    int32 MaxHealth = 0;
    int32 MaxMagicPoints = 0;
    int32 MagicPower = 0;
};

// Immutable approval-order check used by the UE C++ review test and future
// authored-data preflight. It grants no spells, stat formula, or party entry.
class FTSTSSLevelOneRankContract
{
public:
    static bool Validate(const TArray<FTSTSSLevelOneRankCandidate>& Candidates)
    {
        if (Candidates.Num() != 5)
        {
            return false;
        }

        TMap<FName, const FTSTSSLevelOneRankCandidate*> ById;
        for (const FTSTSSLevelOneRankCandidate& Character : Candidates)
        {
            if (!IsKnownCharacter(Character.CharacterId)
                || Character.Level != 1
                || Character.MaxHealth < 1 || Character.MaxHealth > MaxReviewStat
                || Character.MaxMagicPoints < 0 || Character.MaxMagicPoints > MaxReviewStat
                || Character.MagicPower < 0 || Character.MagicPower > MaxReviewStat
                || ById.Contains(Character.CharacterId))
            {
                return false;
            }
            ById.Add(Character.CharacterId, &Character);
        }

        const FTSTSSLevelOneRankCandidate* Ender = ById.FindRef(FName(TEXT("Ender")));
        const FTSTSSLevelOneRankCandidate* Lyra = ById.FindRef(FName(TEXT("Lyra")));
        if (!Ender || !Lyra
            || !(Ender->MagicPower > Lyra->MagicPower)
            || !(Ender->MaxMagicPoints > Lyra->MaxMagicPoints)
            || !(Lyra->MaxHealth < Ender->MaxHealth))
        {
            return false;
        }

        const FName Others[] = {
            FName(TEXT("Ionia")), FName(TEXT("Reson")), FName(TEXT("Aepex"))
        };
        for (const FName& Id : Others)
        {
            const FTSTSSLevelOneRankCandidate* Other = ById.FindRef(Id);
            if (!Other
                || !(Lyra->MagicPower > Other->MagicPower)
                || !(Lyra->MaxMagicPoints > Other->MaxMagicPoints)
                || !(Ender->MaxHealth < Other->MaxHealth))
            {
                return false;
            }
        }
        return true;
    }

private:
    static constexpr int32 MaxReviewStat = 999999;

    static bool IsKnownCharacter(FName Id)
    {
        return Id == FName(TEXT("Ender"))
            || Id == FName(TEXT("Ionia"))
            || Id == FName(TEXT("Lyra"))
            || Id == FName(TEXT("Reson"))
            || Id == FName(TEXT("Aepex"));
    }
};
