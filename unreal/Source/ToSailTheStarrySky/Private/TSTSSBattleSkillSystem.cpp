#include "TSTSSBattleSkillSystem.h"

bool FTSTSSBattleSkillSystem::TryUseRow(
    const FTSTSSBattleSkillState& State,
    const FTSTSSBattleSkillKnowledge& Knowledge,
    const TMap<FName, FName>& Factions,
    FName PartyFaction, FName OpponentFaction,
    FName ActorId, FName TargetId, FName SkillId,
    const FTSTSSBattleSkillRow& Row,
    FTSTSSBattleSkillState& OutState,
    FTSTSSBattleSkillCue& OutCue)
{
    if (SkillId.IsNone() || Row.SkillId != SkillId ||
        Row.Admission != ETSTSSBattleSkillAdmission::ReviewExecutable ||
        Row.Power < 0 || Row.ResourceCost < 0 || Row.CooldownActorTurns < 0 ||
        Row.CooldownActorTurns > 100 || Row.RequiredMasteryRank < 0 ||
        Row.RequiredMasteryRank > 5 ||
        Row.RequiredSecondaryRank < 0 || Row.RequiredSecondaryRank > 5 ||
        (Row.bHealing && Row.Target == ETSTSSBattleSkillTarget::Enemy))
    {
        return false;
    }

    const TSet<FName>* Learned = Knowledge.LearnedByActor.Find(ActorId);
    if (!Learned || !Learned->Contains(SkillId)) return false;

    // A spell is NEVER enabled by affinity, recruitment or its appearance in the catalog.
    if (Row.Kind == ETSTSSBattleSkillKind::Spell)
    {
        if (Row.RequiredSchool.IsNone() || Row.RequiredMasteryRank < 1 ||
            !Row.RequiredWeaponClass.IsNone()) return false;
    }
    else if (Row.Kind == ETSTSSBattleSkillKind::WeaponTechnique)
    {
        if (Row.RequiredWeaponClass.IsNone()) return false;
    }
    else if (Row.Kind != ETSTSSBattleSkillKind::JobArt)
    {
        return false;
    }

    if (!Row.RequiredSchool.IsNone())
    {
        if (Row.RequiredMasteryRank < 1) return false;
        const TMap<FName, int32>* Mastery = Knowledge.MasteryByActor.Find(ActorId);
        const int32* Rank = Mastery ? Mastery->Find(Row.RequiredSchool) : nullptr;
        if (!Rank || *Rank < Row.RequiredMasteryRank || *Rank > 5) return false;
    }
    else if (Row.RequiredMasteryRank != 0)
    {
        return false;
    }

    if (!Row.RequiredSecondarySchool.IsNone())
    {
        if (Row.RequiredSecondarySchool == Row.RequiredSchool ||
            Row.RequiredSecondaryRank < 1) return false;
        const TMap<FName, int32>* Mastery = Knowledge.MasteryByActor.Find(ActorId);
        const int32* Rank = Mastery ? Mastery->Find(Row.RequiredSecondarySchool) : nullptr;
        if (!Rank || *Rank < Row.RequiredSecondaryRank || *Rank > 5) return false;
    }
    else if (Row.RequiredSecondaryRank != 0)
    {
        return false;
    }

    if (!Row.RequiredWeaponClass.IsNone())
    {
        const FName* Equipped = Knowledge.WeaponClassByActor.Find(ActorId);
        if (!Equipped || *Equipped != Row.RequiredWeaponClass) return false;
    }

    // Healing a knocked-out target would create a resurrection mechanic by accident.
    if (Row.bHealing)
    {
        const FTSTSSCombatant* Target = State.Combat.Roster.FindByPredicate(
            [TargetId](const FTSTSSCombatant& Unit) { return Unit.CharacterId == TargetId; });
        if (!Target || Target->Health <= 0) return false;
    }

    const int32 Uses = State.AcceptedTurnsByActor.FindRef(ActorId);
    if (Uses < 0 || Uses > MAX_int32 - Row.CooldownActorTurns - 1) return false;
    const TMap<FName, int32>* ActorCooldowns = State.NextAllowedTurnByActorAndSkill.Find(ActorId);
    const int32* NextAllowed = ActorCooldowns ? ActorCooldowns->Find(SkillId) : nullptr;
    if (NextAllowed && (*NextAllowed < 0 || Uses < *NextAllowed)) return false;

    FTSTSSAbilitySpec Ability;
    Ability.AbilityId = SkillId;
    Ability.Power = Row.Power;
    Ability.Cost = Row.ResourceCost;
    Ability.bHealing = Row.bHealing;
    switch (Row.Target)
    {
    case ETSTSSBattleSkillTarget::Self: Ability.Target = FTSTSSAbilitySpec::ETarget::Self; break;
    case ETSTSSBattleSkillTarget::Ally: Ability.Target = FTSTSSAbilitySpec::ETarget::Ally; break;
    case ETSTSSBattleSkillTarget::Enemy: Ability.Target = FTSTSSAbilitySpec::ETarget::Enemy; break;
    default: return false;
    }

    TMap<FName, FTSTSSAbilitySpec> Catalog;
    Catalog.Add(SkillId, Ability);
    FTSTSSCombatTurnState NextCombat;
    if (!FTSTSSCombatAbilities::TryUse(
        State.Combat, ActorId, TargetId, SkillId, Catalog,
        Knowledge.LearnedByActor, Factions, PartyFaction, OpponentFaction,
        NextCombat))
    {
        return false;
    }

    // Commit all state and cues only after every permission and combat check passes.
    FTSTSSBattleSkillState Candidate = State;
    Candidate.Combat = MoveTemp(NextCombat);
    Candidate.AcceptedTurnsByActor.Add(ActorId, Uses + 1);
    Candidate.NextAllowedTurnByActorAndSkill.FindOrAdd(ActorId).Add(
        SkillId, Uses + 1 + Row.CooldownActorTurns);

    FTSTSSBattleSkillCue CandidateCue;
    CandidateCue.SkillId = SkillId;
    CandidateCue.ActorId = ActorId;
    CandidateCue.TargetId = TargetId;
    CandidateCue.VfxCueId = Row.VfxCueId;
    CandidateCue.AnimationCueId = Row.AnimationCueId;
    OutState = MoveTemp(Candidate);
    OutCue = CandidateCue;
    return true;
}

bool FTSTSSBattleSkillSystem::TryUseDataTable(
    const FTSTSSBattleSkillState& State,
    const FTSTSSBattleSkillKnowledge& Knowledge,
    const TMap<FName, FName>& Factions,
    FName PartyFaction, FName OpponentFaction,
    FName ActorId, FName TargetId, FName SkillId,
    const UDataTable* Skills,
    FTSTSSBattleSkillState& OutState,
    FTSTSSBattleSkillCue& OutCue)
{
    if (!Skills || Skills->GetRowStruct() != FTSTSSBattleSkillRow::StaticStruct() ||
        SkillId.IsNone()) return false;
    const FTSTSSBattleSkillRow* Row = Skills->FindRow<FTSTSSBattleSkillRow>(
        SkillId, TEXT("TSTSS skill execution"), false);
    if (!Row) return false;
    return TryUseRow(State, Knowledge, Factions, PartyFaction, OpponentFaction,
                     ActorId, TargetId, SkillId, *Row, OutState, OutCue);
}
