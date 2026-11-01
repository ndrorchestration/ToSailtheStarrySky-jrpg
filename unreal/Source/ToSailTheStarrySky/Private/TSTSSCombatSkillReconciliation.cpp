#include "TSTSSCombatSkillReconciliation.h"

bool FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
    const TArray<FTSTSSActionDefRow>& Actions,
    TMap<FName, FTSTSSBattleSkillRow>& OutSkills)
{
    if (Actions.IsEmpty()) return false;
    TArray<FTSTSSDataIssueEntry> Issues;
    if (!FTSTSSCombatData::ValidateActions(Actions, false, Issues) || !Issues.IsEmpty())
    {
        return false;
    }

    TMap<FName, FTSTSSBattleSkillRow> Candidate;
    for (const FTSTSSActionDefRow& Action : Actions)
    {
        FTSTSSBattleSkillRow Skill;
        Skill.SkillId = Action.ActionId;
        Skill.Power = Action.Power;
        Skill.ResourceCost = Action.Cost;
        Skill.bHealing = Action.bHealing;
        Skill.Admission = ETSTSSBattleSkillAdmission::DesignOnly;

        switch (Action.Category)
        {
        case ETSTSSActionCategory::Spell:
            Skill.Kind = ETSTSSBattleSkillKind::Spell;
            break;
        case ETSTSSActionCategory::WeaponTechnique:
            Skill.Kind = ETSTSSBattleSkillKind::WeaponTechnique;
            break;
        default:
            // Generic Attack / Support must not be silently reclassified as a JobArt.
            return false;
        }

        switch (Action.Target)
        {
        case ETSTSSActionTarget::Self:
            Skill.Target = ETSTSSBattleSkillTarget::Self; break;
        case ETSTSSActionTarget::Ally:
            Skill.Target = ETSTSSBattleSkillTarget::Ally; break;
        case ETSTSSActionTarget::Enemy:
            Skill.Target = ETSTSSBattleSkillTarget::Enemy; break;
        default: return false;
        }

        // No magical school, rank, equipped weapon, cooldown or audiovisual cue
        // exists in the #665 source row. These MUST be authored separately.
        // Note: #665's level-derived LearnedByActor alone is not magic mastery.
        Candidate.Add(Action.ActionId, Skill);
    }
    OutSkills = MoveTemp(Candidate);
    return true;
}
