#include "Enemies/TSTSSSliceEnemyReviewAI.h"
#include "Combat/TSS_CombatTurnManager.h"

namespace
{
    bool IsProtagonist(FName Id)
    {
        return Id == TEXT("Ender") || Id == TEXT("Ionia") ||
               Id == TEXT("Lyra") || Id == TEXT("Reson") || Id == TEXT("Aepex");
    }
}

bool UTSTSSSliceEnemyReviewAI::TryActReviewEnemy(
    UTSS_CombatTurnManager* Manager, ETSTSSSliceEnemyKind Kind, FName InstanceId)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!IsValid(Manager) || InstanceId.IsNone() || IsProtagonist(InstanceId) ||
        Manager->GetCurrentPhase() != ETSS_CombatPhase::TurnSelection ||
        Manager->GetActiveParticipantId() != InstanceId ||
        !IsValid(Manager->SkillTable.Get()))
    {
        return false;
    }

    FTSTSSSliceEnemyDescriptor Definition;
    if (!FTSTSSSliceEnemyCatalog::TryDescribe(Kind, Definition)) return false;
    const TArray<FTSTSSCombatant> Roster = Manager->GetCombatantSnapshot();
    const FTSTSSCombatant* Actor = Roster.FindByPredicate(
        [InstanceId](const FTSTSSCombatant& U) {
            return U.CharacterId == InstanceId;
        });
    // Reject mismatched archetype, dead participant and protagonist impersonation.
    if (!Actor || Actor->Health <= 0 ||
        Actor->MaxHealth != Definition.MaxHP ||
        Actor->MaxResource != Definition.MaxResource ||
        Actor->Attack != Definition.Attack ||
        Actor->Defense != Definition.Defense) return false;

    // Deterministically target the lowest-HP living protagonist.
    const FTSTSSCombatant* Target = nullptr;
    for (const FTSTSSCombatant& U : Roster)
    {
        if (!IsProtagonist(U.CharacterId) || U.Health <= 0) continue;
        if (!Target || U.Health < Target->Health ||
            (U.Health == Target->Health &&
             U.CharacterId.ToString().Compare(
                 Target->CharacterId.ToString(), ESearchCase::CaseSensitive) < 0))
        {
            Target = &U;
        }
    }
    if (!Target) return false;

    // Strong move first, basic attack on denial or insufficient resource.
    // Cooldowns, admission, target validity and the actual HP transition are
    // checked exclusively by the existing SubmitCommand authority.
    for (int32 I = Definition.AbilityIds.Num() - 1; I >= 0; --I)
    {
        const FName Skill = Definition.AbilityIds[I];
        const FTSTSSBattleSkillRow* Row =
            Manager->SkillTable->FindRow<FTSTSSBattleSkillRow>(
                Skill, TEXT("Slice enemy review AI"), false);
        if (!Row || Row->SkillId != Skill ||
            Row->ResourceCost > Actor->Resource ||
            Row->Target != ETSTSSBattleSkillTarget::Enemy) continue;

        FTSS_CombatCommand Command;
        Command.SourceParticipantId = InstanceId;
        Command.TargetParticipantId = Target->CharacterId;
        Command.SkillId = Skill;
        if (Manager->SubmitCommand(Command)) return true;
    }
    return false;
#endif
}
