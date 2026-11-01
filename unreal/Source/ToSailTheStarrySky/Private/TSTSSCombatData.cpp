#include "TSTSSCombatData.h"

namespace
{
    void AddIssue(TArray<FTSTSSDataIssueEntry>& Out, ETSTSSDataIssue Code, FName Subject)
    {
        FTSTSSDataIssueEntry Entry;
        Entry.Code = Code;
        Entry.Subject = Subject;
        Out.Add(Entry);
    }

    bool InRange(int32 Value, int32 Min)
    {
        return Value >= Min && Value <= FTSTSSCombatData::MaxDataValue;
    }

    ETSTSSLight LightFromSlot(int32 Slot)
    {
        switch (Slot)
        {
        case 0: return ETSTSSLight::Spirit; // Ender
        case 1: return ETSTSSLight::Earth;  // Ionia
        case 2: return ETSTSSLight::Water;  // Lyra
        case 3: return ETSTSSLight::Fire;   // Reson
        case 4: return ETSTSSLight::Air;    // Aepex
        default: return ETSTSSLight::None;
        }
    }

    // Protagonist slots, matching FTSTSSCombatData::Protagonists() order.
    constexpr int32 SlotEnder = 0;
    constexpr int32 SlotLyra = 2;
}

const TArray<FName>& FTSTSSCombatData::Protagonists()
{
    static const TArray<FName> Ids = {
        FName(TEXT("Ender")), FName(TEXT("Ionia")), FName(TEXT("Lyra")),
        FName(TEXT("Reson")), FName(TEXT("Aepex"))};
    return Ids;
}

ETSTSSLight FTSTSSCombatData::ApprovedAffinity(FName CharacterId)
{
    return LightFromSlot(Protagonists().IndexOfByKey(CharacterId));
}

bool FTSTSSCombatData::ValidateBaselines(
    const TArray<FTSTSSCharacterBaselineRow>& Baselines, bool bShipping,
    TArray<FTSTSSDataIssueEntry>& OutIssues)
{
    const int32 Start = OutIssues.Num();
    // Row index per protagonist slot; INDEX_NONE until seen.
    int32 RowOfSlot[5] = {INDEX_NONE, INDEX_NONE, INDEX_NONE, INDEX_NONE, INDEX_NONE};

    for (int32 Index = 0; Index < Baselines.Num(); ++Index)
    {
        const FTSTSSCharacterBaselineRow& Row = Baselines[Index];
        const int32 Slot = Protagonists().IndexOfByKey(Row.CharacterId);
        if (Slot == INDEX_NONE)
        {
            AddIssue(OutIssues, ETSTSSDataIssue::UnknownCharacter, Row.CharacterId);
            continue;
        }
        if (RowOfSlot[Slot] != INDEX_NONE)
        {
            AddIssue(OutIssues, ETSTSSDataIssue::DuplicateCharacter, Row.CharacterId);
            continue;
        }
        RowOfSlot[Slot] = Index;
        if (Row.Affinity != LightFromSlot(Slot))
        {
            AddIssue(OutIssues, ETSTSSDataIssue::WrongAffinity, Row.CharacterId);
        }
        if (!InRange(Row.StartMaxHP, 1) || !InRange(Row.StartMaxMP, 0) ||
            !InRange(Row.StartMagic, 0))
        {
            AddIssue(OutIssues, ETSTSSDataIssue::ValueOutOfRange, Row.CharacterId);
        }
        if (bShipping && Row.Approval != ETSTSSApproval::CreatorApproved)
        {
            AddIssue(OutIssues, ETSTSSDataIssue::NotCreatorApproved, Row.CharacterId);
        }
    }

    bool bComplete = true;
    for (int32 Slot = 0; Slot < Protagonists().Num(); ++Slot)
    {
        if (RowOfSlot[Slot] == INDEX_NONE)
        {
            AddIssue(OutIssues, ETSTSSDataIssue::MissingProtagonist, Protagonists()[Slot]);
            bComplete = false;
        }
    }

    if (bComplete)
    {
        const FTSTSSCharacterBaselineRow& Ender = Baselines[RowOfSlot[SlotEnder]];
        const FTSTSSCharacterBaselineRow& Lyra = Baselines[RowOfSlot[SlotLyra]];
        if (!(Ender.StartMagic > Lyra.StartMagic))
            AddIssue(OutIssues, ETSTSSDataIssue::MagicOrderViolation, Ender.CharacterId);
        if (!(Ender.StartMaxMP > Lyra.StartMaxMP))
            AddIssue(OutIssues, ETSTSSDataIssue::MpOrderViolation, Ender.CharacterId);
        if (!(Lyra.StartMaxHP < Ender.StartMaxHP))
            AddIssue(OutIssues, ETSTSSDataIssue::HpOrderViolation, Lyra.CharacterId);

        for (int32 Slot = 0; Slot < Protagonists().Num(); ++Slot)
        {
            if (Slot == SlotEnder || Slot == SlotLyra) continue;
            const FTSTSSCharacterBaselineRow& Other = Baselines[RowOfSlot[Slot]];
            if (!(Lyra.StartMagic > Other.StartMagic))
                AddIssue(OutIssues, ETSTSSDataIssue::MagicOrderViolation, Lyra.CharacterId);
            if (!(Lyra.StartMaxMP > Other.StartMaxMP))
                AddIssue(OutIssues, ETSTSSDataIssue::MpOrderViolation, Lyra.CharacterId);
            if (!(Ender.StartMaxHP < Other.StartMaxHP))
                AddIssue(OutIssues, ETSTSSDataIssue::HpOrderViolation, Ender.CharacterId);
        }
    }
    return OutIssues.Num() == Start;
}

bool FTSTSSCombatData::ValidateActions(const TArray<FTSTSSActionDefRow>& Actions,
                                       bool bShipping,
                                       TArray<FTSTSSDataIssueEntry>& OutIssues)
{
    const int32 Start = OutIssues.Num();
    TSet<FName> SeenActions;
    for (const FTSTSSActionDefRow& Row : Actions)
    {
        if (Row.ActionId.IsNone())
        {
            AddIssue(OutIssues, ETSTSSDataIssue::InvalidActionId, NAME_None);
        }
        else if (SeenActions.Contains(Row.ActionId))
        {
            AddIssue(OutIssues, ETSTSSDataIssue::DuplicateAction, Row.ActionId);
        }
        else
        {
            SeenActions.Add(Row.ActionId);
        }
        // Deserialized/cast enum values outside the authored schema must never
        // receive a default combat meaning in the downstream catalog bridge.
        switch (Row.Category)
        {
        case ETSTSSActionCategory::Attack:
        case ETSTSSActionCategory::Spell:
        case ETSTSSActionCategory::WeaponTechnique:
        case ETSTSSActionCategory::Support:
            break;
        default:
            AddIssue(OutIssues, ETSTSSDataIssue::InvalidActionCategory, Row.ActionId);
            break;
        }
        switch (Row.Target)
        {
        case ETSTSSActionTarget::Self:
        case ETSTSSActionTarget::Ally:
        case ETSTSSActionTarget::Enemy:
            break;
        default:
            AddIssue(OutIssues, ETSTSSDataIssue::InvalidActionTarget, Row.ActionId);
            break;
        }
        if (!InRange(Row.Cost, 0) || !InRange(Row.Power, 0))
        {
            AddIssue(OutIssues, ETSTSSDataIssue::ValueOutOfRange, Row.ActionId);
        }
        if (!InRange(Row.UnlockLevel, 1))
        {
            AddIssue(OutIssues, ETSTSSDataIssue::InvalidUnlockLevel, Row.ActionId);
        }
        if (Row.bHealing && Row.Target == ETSTSSActionTarget::Enemy)
        {
            AddIssue(OutIssues, ETSTSSDataIssue::HealingTargetsEnemy, Row.ActionId);
        }
        if (Row.Learners.IsEmpty())
        {
            AddIssue(OutIssues, ETSTSSDataIssue::NoLearners, Row.ActionId);
        }
        TSet<FName> SeenLearners;
        for (const FName Learner : Row.Learners)
        {
            if (!Protagonists().Contains(Learner))
            {
                AddIssue(OutIssues, ETSTSSDataIssue::UnknownLearner, Learner);
            }
            else if (SeenLearners.Contains(Learner))
            {
                AddIssue(OutIssues, ETSTSSDataIssue::DuplicateLearner, Learner);
            }
            else
            {
                SeenLearners.Add(Learner);
            }
        }
        if (bShipping && Row.Approval != ETSTSSApproval::CreatorApproved)
        {
            AddIssue(OutIssues, ETSTSSDataIssue::NotCreatorApproved, Row.ActionId);
        }
    }
    return OutIssues.Num() == Start;
}

bool FTSTSSCombatData::ValidateActiveParty(const TArray<FName>& ActiveIds,
                                           TArray<FTSTSSDataIssueEntry>& OutIssues)
{
    const int32 Start = OutIssues.Num();
    if (ActiveIds.Num() != ActivePartySize)
    {
        AddIssue(OutIssues, ETSTSSDataIssue::InvalidActiveParty, NAME_None);
    }
    TSet<FName> Seen;
    for (const FName Id : ActiveIds)
    {
        if (!Protagonists().Contains(Id) || Seen.Contains(Id))
        {
            AddIssue(OutIssues, ETSTSSDataIssue::InvalidActiveParty, Id);
        }
        Seen.Add(Id);
    }
    return OutIssues.Num() == Start;
}

bool FTSTSSCombatData::TryBuildAbilityData(
    const TArray<FTSTSSCharacterBaselineRow>& Baselines,
    const TArray<FTSTSSActionDefRow>& Actions, const TMap<FName, int32>& Levels,
    bool bShipping, TMap<FName, FTSTSSAbilitySpec>& OutCatalog,
    TMap<FName, TSet<FName>>& OutLearned, TArray<FTSTSSDataIssueEntry>& OutIssues)
{
    TArray<FTSTSSDataIssueEntry> Local;
    ValidateBaselines(Baselines, bShipping, Local);
    ValidateActions(Actions, bShipping, Local);
    for (const FName Id : Protagonists())
    {
        const int32* Level = Levels.Find(Id);
        if (!Level)
        {
            AddIssue(Local, ETSTSSDataIssue::MissingLevel, Id);
        }
        else if (!InRange(*Level, 1))
        {
            AddIssue(Local, ETSTSSDataIssue::InvalidLevel, Id);
        }
    }
    for (const TPair<FName, int32>& Pair : Levels)
    {
        if (!Protagonists().Contains(Pair.Key))
        {
            AddIssue(Local, ETSTSSDataIssue::UnknownCharacter, Pair.Key);
        }
    }
    if (!Local.IsEmpty())
    {
        OutIssues.Append(Local);
        return false;
    }

    TMap<FName, FTSTSSAbilitySpec> Catalog;
    TMap<FName, TSet<FName>> Learned;
    for (const FName Id : Protagonists())
    {
        Learned.Add(Id, TSet<FName>());
    }
    for (const FTSTSSActionDefRow& Row : Actions)
    {
        FTSTSSAbilitySpec Spec;
        Spec.AbilityId = Row.ActionId;
        Spec.Power = Row.Power;
        Spec.Cost = Row.Cost;
        Spec.bHealing = Row.bHealing;
        switch (Row.Target)
        {
        case ETSTSSActionTarget::Self: Spec.Target = FTSTSSAbilitySpec::ETarget::Self; break;
        case ETSTSSActionTarget::Ally: Spec.Target = FTSTSSAbilitySpec::ETarget::Ally; break;
        case ETSTSSActionTarget::Enemy: Spec.Target = FTSTSSAbilitySpec::ETarget::Enemy; break;
        }
        Catalog.Add(Row.ActionId, Spec);
        for (const FName Learner : Row.Learners)
        {
            if (Levels.FindChecked(Learner) >= Row.UnlockLevel)
            {
                Learned.FindChecked(Learner).Add(Row.ActionId);
            }
        }
    }
    OutCatalog = MoveTemp(Catalog);
    OutLearned = MoveTemp(Learned);
    return true;
}
