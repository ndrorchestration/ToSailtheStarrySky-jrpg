#include "Combat/TSS_CombatTurnManager.h"
#include "TSTSSEncounterGate.h"

namespace
{
    const FName CrewFaction(TEXT("TSTSSParty"));
    const FName EnemyFaction(TEXT("TSTSSOpponent"));

    // Stable tie-breaking means original roster order cannot bias simultaneous initiative.
    bool HigherInitiative(const FTSS_CombatParticipant& Left,
                          const FTSS_CombatParticipant& Right)
    {
        if (Left.Agility != Right.Agility) return Left.Agility > Right.Agility;
        return Left.ParticipantId.ToString().Compare(
            Right.ParticipantId.ToString(), ESearchCase::CaseSensitive) < 0;
    }
}

UTSS_CombatTurnManager::UTSS_CombatTurnManager()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UTSS_CombatTurnManager::IsCanonicalPlayer(FName ParticipantId)
{
    return ParticipantId == FName(TEXT("Ender")) ||
           ParticipantId == FName(TEXT("Ionia")) ||
           ParticipantId == FName(TEXT("Lyra")) ||
           ParticipantId == FName(TEXT("Reson")) ||
           ParticipantId == FName(TEXT("Aepex"));
}

bool UTSS_CombatTurnManager::ValidateParticipant(
    const FTSS_CombatParticipant& Participant, bool bExpectedPlayer)
{
    const FTSTSSCombatant& Stats = Participant.Stats;
    if (Participant.ParticipantId.IsNone() ||
        Stats.CharacterId != Participant.ParticipantId ||
        Participant.bIsPlayerParty != bExpectedPlayer ||
        Participant.Agility < 0 || Participant.Agility > 1000 ||
        Stats.MaxHealth <= 0 || Stats.Health < 0 ||
        Stats.Health > Stats.MaxHealth ||
        Stats.MaxResource < 0 || Stats.Resource < 0 ||
        Stats.Resource > Stats.MaxResource ||
        Stats.Attack < 0 || Stats.Defense < 0 ||
        (bExpectedPlayer && !IsCanonicalPlayer(Participant.ParticipantId)) ||
        (!bExpectedPlayer && Stats.Health <= 0))
    {
        return false;
    }

    TSet<FName> SeenSkills;
    for (FName Skill : Participant.LearnedSkills)
    {
        if (Skill.IsNone() || SeenSkills.Contains(Skill)) return false;
        SeenSkills.Add(Skill);
    }
    for (const TPair<FName, int32>& School : Participant.MasteryRanks)
    {
        if (School.Key.IsNone() || School.Value < 0 || School.Value > 5) return false;
    }
    return true;
}

bool UTSS_CombatTurnManager::InitializeEncounter(
    const TArray<FTSS_CombatParticipant>& PlayerRoster,
    const TArray<FName>& ActivePlayerIds,
    const TArray<FTSS_CombatParticipant>& Enemies)
{
    if (CurrentPhase != ETSS_CombatPhase::NotStarted ||
        PlayerRoster.IsEmpty() || PlayerRoster.Num() > 5 ||
        ActivePlayerIds.IsEmpty() || ActivePlayerIds.Num() > 3 ||
        Enemies.IsEmpty() || Enemies.Num() > 32)
    {
        return false;
    }

    TMap<FName, const FTSS_CombatParticipant*> Players;
    TSet<FName> AllNames;
    for (const FTSS_CombatParticipant& Member : PlayerRoster)
    {
        if (!ValidateParticipant(Member, true) ||
            AllNames.Contains(Member.ParticipantId)) return false;
        AllNames.Add(Member.ParticipantId);
        Players.Add(Member.ParticipantId, &Member);
    }

    TSet<FName> ActiveIds;
    TArray<FTSS_CombatParticipant> Participants;
    for (const FName Id : ActivePlayerIds)
    {
        const FTSS_CombatParticipant* const* Member = Players.Find(Id);
        if (Id.IsNone() || ActiveIds.Contains(Id) || !Member ||
            (*Member)->Stats.Health <= 0) return false;
        ActiveIds.Add(Id);
        Participants.Add(**Member);
    }

    for (const FTSS_CombatParticipant& Enemy : Enemies)
    {
        if (!ValidateParticipant(Enemy, false) ||
            AllNames.Contains(Enemy.ParticipantId)) return false;
        AllNames.Add(Enemy.ParticipantId);
        Participants.Add(Enemy);
    }

    Participants.Sort(HigherInitiative);
    TArray<FTSTSSCombatant> Roster;
    TArray<FName> TurnOrder;
    FTSTSSBattleSkillKnowledge CandidateKnowledge;
    TMap<FName, FName> CandidateFactions;
    for (const FTSS_CombatParticipant& Participant : Participants)
    {
        Roster.Add(Participant.Stats);
        TurnOrder.Add(Participant.ParticipantId);
        CandidateFactions.Add(Participant.ParticipantId,
            Participant.bIsPlayerParty ? CrewFaction : EnemyFaction);

        TSet<FName> Learned;
        for (const FName SkillId : Participant.LearnedSkills) Learned.Add(SkillId);
        CandidateKnowledge.LearnedByActor.Add(Participant.ParticipantId, MoveTemp(Learned));
        CandidateKnowledge.MasteryByActor.Add(
            Participant.ParticipantId, Participant.MasteryRanks);
        if (!Participant.EquippedWeaponClass.IsNone())
        {
            CandidateKnowledge.WeaponClassByActor.Add(
                Participant.ParticipantId, Participant.EquippedWeaponClass);
        }
    }

    FTSTSSBattleSkillState Candidate;
    if (!FTSTSSCombatTurns::TryBegin(Roster, TurnOrder, Candidate.Combat) ||
        FTSTSSEncounterGate::Evaluate(
            Candidate.Combat, CandidateFactions, CrewFaction, EnemyFaction) !=
                ETSTSSEncounterOutcome::Ongoing)
    {
        return false;
    }

    TArray<FName> CandidateReserve;
    for (const FTSS_CombatParticipant& Member : PlayerRoster)
    {
        if (!ActiveIds.Contains(Member.ParticipantId))
        {
            CandidateReserve.Add(Member.ParticipantId);
        }
    }

    // Commit only after a fully checked, live encounter. Failed initialization
    // cannot partially replace the current game state or broadcast events.
    BattleState = MoveTemp(Candidate);
    Knowledge = MoveTemp(CandidateKnowledge);
    Factions = MoveTemp(CandidateFactions);
    ReservePartyIds = MoveTemp(CandidateReserve);
    CurrentPhase = ETSS_CombatPhase::TurnSelection;
    OnPhaseChanged.Broadcast(CurrentPhase);
    OnTurnStarted.Broadcast(GetActiveParticipantId());
    return true;
}

FName UTSS_CombatTurnManager::GetActiveParticipantId() const
{
    if (CurrentPhase == ETSS_CombatPhase::NotStarted ||
        CurrentPhase == ETSS_CombatPhase::Victory ||
        CurrentPhase == ETSS_CombatPhase::Defeat ||
        CurrentPhase == ETSS_CombatPhase::Draw) return NAME_None;
    return FTSTSSCombatTurns::CurrentActor(BattleState.Combat);
}

int32 UTSS_CombatTurnManager::GetCenteringRoundsRemaining(FName PartyMember) const
{
    if (CurrentPhase == ETSS_CombatPhase::NotStarted ||
        CurrentPhase == ETSS_CombatPhase::Victory ||
        CurrentPhase == ETSS_CombatPhase::Defeat ||
        CurrentPhase == ETSS_CombatPhase::Draw) return 0;
    const FTSTSSPhysicalDefenseBuff* Status =
        BattleState.ActivePhysicalDefenseBuffs.Find(PartyMember);
    return Status && Status->Percent == 15
        ? FMath::Max(0, Status->ExpiresAtRound-BattleState.Combat.Round) : 0;
}

int32 UTSS_CombatTurnManager::GetCenteringEffectiveDefense(FName PartyMember) const
{
    const FTSTSSCombatant* Unit=BattleState.Combat.Roster.FindByPredicate(
        [PartyMember](const FTSTSSCombatant& X){return X.CharacterId==PartyMember;});
    if (!Unit) return 0;
    if (GetCenteringRoundsRemaining(PartyMember)==0) return Unit->Defense;
    const int64 Bonus=FMath::Max<int64>(
        1,(static_cast<int64>(Unit->Defense)*15+99)/100);
    return static_cast<int32>(FMath::Min<int64>(MAX_int32,
        static_cast<int64>(Unit->Defense)+Bonus));
}

bool UTSS_CombatTurnManager::SubmitCommand(const FTSS_CombatCommand& Command)
{
    if (CurrentPhase != ETSS_CombatPhase::TurnSelection ||
        Command.SourceParticipantId.IsNone() ||
        Command.TargetParticipantId.IsNone() || Command.SkillId.IsNone() ||
        Command.SourceParticipantId != GetActiveParticipantId() ||
        Command.SkillId == TEXT("Ender_ResonantPulse"))
    {
        return false;
    }

    FTSTSSBattleSkillState Candidate;
    FTSTSSBattleSkillCue CandidateCue;
    if (!FTSTSSBattleSkillSystem::TryUseDataTable(
        BattleState, Knowledge, Factions, CrewFaction, EnemyFaction,
        Command.SourceParticipantId, Command.TargetParticipantId, Command.SkillId,
        SkillTable.Get(), Candidate, CandidateCue))
    {
        return false;
    }

    return CommitAcceptedAction(MoveTemp(Candidate), CandidateCue);
}

bool UTSS_CombatTurnManager::SubmitResonantPulseArea(
    const FTSS_CombatCommand& Command,
    const TMap<FName, FVector>& ParticipantWorldPositions)
{
    // No arbitrary single-enemy target choice: caster is the center.
    if (CurrentPhase != ETSS_CombatPhase::TurnSelection ||
        Command.SourceParticipantId != TEXT("Ender") ||
        Command.SkillId != TEXT("Ender_ResonantPulse") ||
        Command.TargetParticipantId != Command.SourceParticipantId ||
        Command.SourceParticipantId != GetActiveParticipantId() ||
        !IsValid(SkillTable.Get()) ||
        SkillTable->GetRowStruct() != FTSTSSBattleSkillRow::StaticStruct())
        return false;

    const FTSTSSBattleSkillRow* Pulse =
        SkillTable->FindRow<FTSTSSBattleSkillRow>(
            Command.SkillId, TEXT("Ender spatial Pulse"), false);
    if (!Pulse) return false;

    FTSTSSBattleSkillState Candidate;
    FTSTSSBattleSkillCue CandidateCue;
    TArray<FName> AffectedEnemyIds;
    if (!FTSTSSBattleSkillSystem::TryUseResonantPulseArea(
        BattleState, Knowledge, Factions, CrewFaction, EnemyFaction,
        Command.SourceParticipantId, *Pulse, ParticipantWorldPositions,
        Candidate, CandidateCue, AffectedEnemyIds))
        return false;

    // Only the area executor is allowed to generate an accepted Pulse cue.
    // This broadcasts ONCE regardless of the number of enemies struck.
    return CommitAcceptedAction(MoveTemp(Candidate), CandidateCue);
}

bool UTSS_CombatTurnManager::CommitAcceptedAction(
    FTSTSSBattleSkillState&& Candidate,
    const FTSTSSBattleSkillCue& CandidateCue)
{
    CurrentPhase = ETSS_CombatPhase::ResolvingAction;
    OnPhaseChanged.Broadcast(CurrentPhase);
    BattleState = MoveTemp(Candidate);
    OnSkillAccepted.Broadcast(
        CandidateCue.SkillId, CandidateCue.ActorId, CandidateCue.TargetId,
        CandidateCue.VfxCueId, CandidateCue.AnimationCueId);
    CurrentPhase = ETSS_CombatPhase::TurnComplete;
    OnPhaseChanged.Broadcast(CurrentPhase);

    switch (FTSTSSEncounterGate::Evaluate(
        BattleState.Combat, Factions, CrewFaction, EnemyFaction))
    {
    case ETSTSSEncounterOutcome::Victory:
        CurrentPhase = ETSS_CombatPhase::Victory; break;
    case ETSTSSEncounterOutcome::Defeat:
        CurrentPhase = ETSS_CombatPhase::Defeat; break;
    case ETSTSSEncounterOutcome::Draw:
        CurrentPhase = ETSS_CombatPhase::Draw; break;
    case ETSTSSEncounterOutcome::Ongoing:
        CurrentPhase = ETSS_CombatPhase::TurnSelection; break;
    default:
        // Should be unreachable after prior validation, but fail closed.
        CurrentPhase = ETSS_CombatPhase::Draw; break;
    }
    OnPhaseChanged.Broadcast(CurrentPhase);
    if (CurrentPhase == ETSS_CombatPhase::TurnSelection)
    {
        OnTurnStarted.Broadcast(GetActiveParticipantId());
    }
    return true;
}
