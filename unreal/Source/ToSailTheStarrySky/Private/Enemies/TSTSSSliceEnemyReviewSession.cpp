#include "Enemies/TSTSSSliceEnemyReviewSession.h"
#include "Enemies/TSTSSSliceEnemyReviewAI.h"
#include "Engine/DataTable.h"

namespace
{
    const FName ReviewStrikeId(TEXT("SliceReview_PlayerStrike"));

    FTSS_CombatParticipant MakeReviewPartyMember(
        const TCHAR* Id, int32 HP, int32 Attack, int32 Defense, int32 Agility)
    {
        FTSS_CombatParticipant Member;
        Member.ParticipantId = FName(Id);
        Member.Stats.CharacterId = Member.ParticipantId;
        Member.Stats.Health = HP;
        Member.Stats.MaxHealth = HP;
        Member.Stats.Resource = 10;
        Member.Stats.MaxResource = 10;
        Member.Stats.Attack = Attack;
        Member.Stats.Defense = Defense;
        Member.Agility = Agility;
        Member.bIsPlayerParty = true;
        // A temporary sandbox move, not a Five Lights or canonical skill grant.
        Member.LearnedSkills.Add(ReviewStrikeId);
        return Member;
    }

    bool ResolveReviewKind(const FTSS_CombatParticipant& Participant,
                           ETSTSSSliceEnemyKind& OutKind)
    {
        if (Participant.bIsPlayerParty ||
            Participant.LearnedSkills.Num() != 2) return false;
        bool bFound = false;
        ETSTSSSliceEnemyKind Found = ETSTSSSliceEnemyKind::HarmonicShear;
        // Catalog enum order is append-only; this scans the fifteen known
        // review archetypes and verifies every identifying data dimension.
        for (uint8 I = 0;
             I <= static_cast<uint8>(ETSTSSSliceEnemyKind::NightGlider); ++I)
        {
            const ETSTSSSliceEnemyKind Kind = static_cast<ETSTSSSliceEnemyKind>(I);
            FTSTSSSliceEnemyDescriptor Descriptor;
            if (!FTSTSSSliceEnemyCatalog::TryDescribe(Kind, Descriptor)) return false;
            if (Descriptor.AbilityIds != Participant.LearnedSkills ||
                Descriptor.MaxHP != Participant.Stats.MaxHealth ||
                Descriptor.MaxResource != Participant.Stats.MaxResource ||
                Descriptor.Attack != Participant.Stats.Attack ||
                Descriptor.Defense != Participant.Stats.Defense ||
                Descriptor.Agility != Participant.Agility) continue;
            if (bFound) return false;
            bFound = true;
            Found = Kind;
        }
        if (!bFound) return false;
        OutKind = Found;
        return true;
    }
}

bool UTSTSSSliceEnemyReviewSession::TryStart(
    FName ReviewWavePreset, ETSTSSSliceReviewPartyStage PartyStage)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (Manager || ReviewWavePreset.IsNone()) return false;
    const uint8 StageIndex = static_cast<uint8>(PartyStage);
    if (StageIndex > static_cast<uint8>(
        ETSTSSSliceReviewPartyStage::AfterSplashdown)) return false;

    TArray<FTSS_CombatParticipant> Wave;
    if (!FTSTSSSliceEnemyCatalog::TryMakeReviewWave(ReviewWavePreset, Wave) ||
        Wave.Num() != 2) return false;

    TMap<FName, ETSTSSSliceEnemyKind> CandidateKinds;
    TArray<FName> CandidateEnemyIds;
    TArray<ETSTSSSliceEnemyKind> CandidateSlotKinds;
    for (const FTSS_CombatParticipant& Enemy : Wave)
    {
        ETSTSSSliceEnemyKind Kind;
        if (!ResolveReviewKind(Enemy, Kind) ||
            Enemy.ParticipantId.IsNone() ||
            CandidateKinds.Contains(Enemy.ParticipantId)) return false;
        CandidateKinds.Add(Enemy.ParticipantId, Kind);
        CandidateEnemyIds.Add(Enemy.ParticipantId);
        CandidateSlotKinds.Add(Kind);
    }

    // The party is authored explicitly, in canonical narrative recruitment
    // order. The stage is chosen by the REVIEWER and does not mutate the game.
    TArray<FTSS_CombatParticipant> Crew;
    TArray<FName> CandidatePartyIds;
    Crew.Add(MakeReviewPartyMember(TEXT("Ender"), 46, 7, 3, 11));
    CandidatePartyIds.Add(TEXT("Ender"));
    if (StageIndex >= static_cast<uint8>(
        ETSTSSSliceReviewPartyStage::IoniaRecruited))
    {
        Crew.Add(MakeReviewPartyMember(TEXT("Ionia"), 52, 6, 4, 9));
        CandidatePartyIds.Add(TEXT("Ionia"));
    }
    if (StageIndex == static_cast<uint8>(
        ETSTSSSliceReviewPartyStage::AfterSplashdown))
    {
        Crew.Add(MakeReviewPartyMember(TEXT("Lyra"), 38, 5, 2, 13));
        CandidatePartyIds.Add(TEXT("Lyra"));
    }

    UDataTable* Table = FTSTSSSliceEnemyCatalog::MakeReviewSkillTable(this, true);
    if (!IsValid(Table) || Table->GetRowMap().Contains(ReviewStrikeId)) return false;
    FTSTSSBattleSkillRow Strike;
    Strike.SkillId = ReviewStrikeId;
    Strike.Kind = ETSTSSBattleSkillKind::JobArt;
    Strike.Admission = ETSTSSBattleSkillAdmission::ReviewExecutable;
    Strike.Target = ETSTSSBattleSkillTarget::Enemy;
    Strike.Power = 7;
    Strike.ResourceCost = 0;
    Strike.CooldownActorTurns = 0;
    Strike.VfxCueId = TEXT("VFX_ReviewSwordHit");
    Strike.AnimationCueId = TEXT("ANIM_ReviewStrike");
    Table->AddRow(ReviewStrikeId, Strike);

    UTSS_CombatTurnManager* Next = NewObject<UTSS_CombatTurnManager>(this);
    if (!IsValid(Next)) return false;
    Next->SkillTable = Table;
    if (!Next->InitializeEncounter(Crew, CandidatePartyIds, Wave)) return false;

    ReviewSkillTable = Table;
    Manager = Next;
    EnemyKinds = MoveTemp(CandidateKinds);
    ActivePartyIds = MoveTemp(CandidatePartyIds);
    EnemyIds = MoveTemp(CandidateEnemyIds);
    EnemySlotKinds = MoveTemp(CandidateSlotKinds);
    TryAdvanceEnemyTurns();
    return true;
#endif
}

bool UTSTSSSliceEnemyReviewSession::TryGetReviewEnemyKind(
    int32 EnemySlot, ETSTSSSliceEnemyKind& OutKind) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!IsValid(Manager.Get()) || !EnemySlotKinds.IsValidIndex(EnemySlot) ||
        !EnemyIds.IsValidIndex(EnemySlot)) return false;
    OutKind = EnemySlotKinds[EnemySlot];
    return true;
#endif
}

bool UTSTSSSliceEnemyReviewSession::TryPlayerStrike(int32 EnemySlot)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!IsValid(Manager.Get()) || !EnemyIds.IsValidIndex(EnemySlot) ||
        Manager->GetCurrentPhase() != ETSS_CombatPhase::TurnSelection ||
        !ActivePartyIds.Contains(Manager->GetActiveParticipantId())) return false;

    FTSS_CombatCommand Action;
    Action.SourceParticipantId = Manager->GetActiveParticipantId();
    Action.TargetParticipantId = EnemyIds[EnemySlot];
    Action.SkillId = ReviewStrikeId;
    if (!Manager->SubmitCommand(Action)) return false;
    TryAdvanceEnemyTurns();
    return true;
#endif
}

bool UTSTSSSliceEnemyReviewSession::TryAdvanceEnemyTurns()
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!IsValid(Manager.Get())) return false;
    bool bAny = false;
    for (int32 Step = 0; Step < 4; ++Step)
    {
        if (Manager->GetCurrentPhase() != ETSS_CombatPhase::TurnSelection) return bAny;
        const FName Active = Manager->GetActiveParticipantId();
        if (ActivePartyIds.Contains(Active)) return bAny;
        const ETSTSSSliceEnemyKind* Kind = EnemyKinds.Find(Active);
        if (!Kind || !UTSTSSSliceEnemyReviewAI::TryActReviewEnemy(
                Manager.Get(), *Kind, Active)) return false;
        bAny = true;
    }
    // Four actions without returning control/ending is unexpected: do not
    // guess a fifth action or bypass the authoritative turn state.
    return false;
#endif
}

FString UTSTSSSliceEnemyReviewSession::GetReviewStatus() const
{
    if (!IsValid(Manager.Get()))
    {
        return TEXT("UNSTARTED / REVIEW ONLY\nF7 Ender | F8 +Ionia | F9 after splashdown\nJ/K strike enemy slot 1/2");
    }
    const ETSS_CombatPhase Phase = Manager->GetCurrentPhase();
    FString Text = FString::Printf(
        TEXT("REVIEW ONLY | phase %d | turn: %s\nJ/K strike enemy slot 1/2\n"),
        static_cast<int32>(Phase), *Manager->GetActiveParticipantId().ToString());
    for (const FTSTSSCombatant& Member : Manager->GetCombatantSnapshot())
    {
        Text += FString::Printf(TEXT("%s  HP %d/%d  RP %d/%d\n"),
            *Member.CharacterId.ToString(), Member.Health, Member.MaxHealth,
            Member.Resource, Member.MaxResource);
    }
    return Text;
}
