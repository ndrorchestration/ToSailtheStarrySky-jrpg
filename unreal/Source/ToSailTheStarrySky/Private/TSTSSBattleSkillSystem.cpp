#include "TSTSSBattleSkillSystem.h"

namespace
{
    constexpr int32 CenteringPercent = 15;
    constexpr int32 CenteringDuration = 3;

    // The established CombatRules remains responsible for actual damage math.
    // Do not change base defense in the roster: effects expire transparently.
    int32 EffectivePhysicalDefenseBonus(int32 BaseDefense, int32 Percent)
    {
        if (BaseDefense < 0 || Percent != CenteringPercent) return 0;
        const int64 Scaled = (static_cast<int64>(BaseDefense) * Percent + 99) / 100;
        const int64 Bonus = FMath::Max<int64>(1, Scaled);
        return static_cast<int32>(FMath::Min<int64>(
            Bonus,static_cast<int64>(MAX_int32)-BaseDefense));
    }
}


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
        (Row.bHealing && Row.Target == ETSTSSBattleSkillTarget::Enemy) ||
        Row.PhysicalDefenseBuffPercent < 0 || Row.BuffDurationRounds < 0 ||
        (!Row.bPartyPhysicalDefenseBuff &&
         (Row.PhysicalDefenseBuffPercent != 0 || Row.BuffDurationRounds != 0)) ||
        (Row.bPartyPhysicalDefenseBuff &&
         (SkillId != TEXT("Ender_Centering") || ActorId != TEXT("Ender") ||
          Row.Kind != ETSTSSBattleSkillKind::Spell ||
          Row.Target != ETSTSSBattleSkillTarget::Self ||
          Row.Power != 0 || Row.bHealing ||
          Row.RequiredSchool != TEXT("ResonanceHarmonic") ||
          Row.RequiredMasteryRank != 1 ||
          !Row.RequiredSecondarySchool.IsNone() ||
          Row.RequiredSecondaryRank != 0 ||
          Row.PhysicalDefenseBuffPercent != CenteringPercent ||
          Row.BuffDurationRounds != CenteringDuration)))
    {
        return false;
    }

    // Reject save/reentry state that bypassed the single authoritative action path.
    // Every accepted action must contribute exactly one actor-local turn.
    int64 AccountedTurns = 0;
    for (const TPair<FName, int32>& Entry : State.AcceptedTurnsByActor)
    {
        if (Entry.Key.IsNone() || !State.Combat.Order.Contains(Entry.Key) ||
            Entry.Value < 0 || Entry.Value > State.Combat.AcceptedActions)
        {
            return false;
        }
        AccountedTurns += Entry.Value;
    }
    if (AccountedTurns != State.Combat.AcceptedActions) return false;
    if (State.Combat.Round < 1 || State.Combat.Round > MAX_int32-8)
        return false;
    const FName* ActingFaction = Factions.Find(ActorId);
    if (Row.bPartyPhysicalDefenseBuff &&
        (!ActingFaction || *ActingFaction != PartyFaction ||
         PartyFaction.IsNone())) return false;
    // Reject malformed/foreign/expired status records. A review save cannot
    // conjure a cross-faction, oversized or permanent defensive aura.
    for (const auto& Pair : State.ActivePhysicalDefenseBuffs)
    {
        const FName* Side = Factions.Find(Pair.Key);
        if (Pair.Key.IsNone() || !Side || *Side != PartyFaction ||
            Pair.Value.Percent != CenteringPercent ||
            Pair.Value.ExpiresAtRound <= State.Combat.Round ||
            Pair.Value.ExpiresAtRound > State.Combat.Round + CenteringDuration)
            return false;
        const FTSTSSCombatant* Unit=State.Combat.Roster.FindByPredicate(
            [Id=Pair.Key](const FTSTSSCombatant& U){return U.CharacterId==Id;});
        if (!Unit || Unit->Health<=0) return false;
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
    Ability.bSupportOnly = Row.bPartyPhysicalDefenseBuff;
    // An ordinary attack/heal spell does not consume the physical-only aura.
    Ability.bPhysicalDamage = Row.Kind != ETSTSSBattleSkillKind::Spell &&
        !Row.bHealing;
    if (Ability.bPhysicalDamage)
    {
        const FTSTSSPhysicalDefenseBuff* Buff =
            State.ActivePhysicalDefenseBuffs.Find(TargetId);
        if (Buff)
        {
            const FTSTSSCombatant* Target = State.Combat.Roster.FindByPredicate(
                [TargetId](const FTSTSSCombatant& U) {
                    return U.CharacterId == TargetId;
                });
            if (!Target || Buff->ExpiresAtRound <= State.Combat.Round)
                return false;
            Ability.PhysicalDefenseBonus = EffectivePhysicalDefenseBonus(
                Target->Defense, Buff->Percent);
        }
    }
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
    // Expire on crossed round boundaries, not per actor or per second.
    for (auto It=Candidate.ActivePhysicalDefenseBuffs.CreateIterator();It;++It)
    {
        if (It.Value().ExpiresAtRound <= Candidate.Combat.Round ||
            !Candidate.Combat.Roster.ContainsByPredicate(
                [Id=It.Key()](const FTSTSSCombatant& U){
                    return U.CharacterId==Id && U.Health>0;
                }))
        {
            It.RemoveCurrent();
        }
    }
    if (Row.bPartyPhysicalDefenseBuff)
    {
        // Applied only after the normal authenticated, MP-paying turn succeeds.
        // All active living allies receive a refresh. Reserve/unrecruited crew
        // never exist in this encounter roster and cannot be buffed.
        for (const FTSTSSCombatant& Unit:Candidate.Combat.Roster)
        {
            if (Unit.Health <= 0) continue;
            const FName* Side=Factions.Find(Unit.CharacterId);
            if (Side && *Side == PartyFaction)
            {
                FTSTSSPhysicalDefenseBuff& Buff =
                    Candidate.ActivePhysicalDefenseBuffs.FindOrAdd(Unit.CharacterId);
                Buff.Percent = CenteringPercent;
                Buff.ExpiresAtRound = Candidate.Combat.Round + CenteringDuration;
            }
        }
    }
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
