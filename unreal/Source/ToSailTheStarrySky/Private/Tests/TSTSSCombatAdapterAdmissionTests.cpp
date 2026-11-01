#include "Misc/AutomationTest.h"
#include "TSTSSCombatSkillReconciliation.h"

// NONCANONICAL test fixture: validates the real adapter output against the
// real guarded execution API; does not add or approve gameplay abilities.
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSCombatAdapterAdmissionGateTest,
    "TSTSS.CombatIntegration.AdapterRowsRemainDesignOnlyInExecutor",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSCombatAdapterAdmissionGateTest::RunTest(const FString& Parameters)
{
    const FName ActorId(TEXT("Ender"));
    const FName OpponentId(TEXT("FixtureEnemy"));
    const FName SpellId(TEXT("FixtureProposedSpell"));
    FTSTSSActionDefRow Proposal;
    Proposal.ActionId = SpellId;
    Proposal.Category = ETSTSSActionCategory::Spell;
    Proposal.Target = ETSTSSActionTarget::Enemy;
    Proposal.Power = 3;
    Proposal.Cost = 2;
    Proposal.UnlockLevel = 1;
    Proposal.Learners.Add(ActorId);
    Proposal.Approval = ETSTSSApproval::Proposed; // No creator approval.
    Proposal.Affinity = ETSTSSLight::Fire; // Narrative metadata only.

    TMap<FName, FTSTSSBattleSkillRow> DesignRows;
    if (!TestTrue(TEXT("Valid proposal can be exported for design review"),
        FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {Proposal}, DesignRows))) return false;
    const FTSTSSBattleSkillRow* Row = DesignRows.Find(SpellId);
    if (!TestNotNull(TEXT("Review export has the proposed row"), Row)) return false;
    TestTrue(TEXT("Adapter never grants execution admission"),
        Row->Admission == ETSTSSBattleSkillAdmission::DesignOnly);
    TestTrue(TEXT("Adapter does not infer school mastery from story affinity"),
        Row->RequiredSchool.IsNone());

    FTSTSSCombatant Ender;
    Ender.CharacterId = ActorId;
    Ender.Health = 12;
    Ender.MaxHealth = 20;
    Ender.Resource = 10;
    Ender.MaxResource = 10;
    Ender.Attack = 2;
    FTSTSSCombatant Foe = Ender;
    Foe.CharacterId = OpponentId;
    Foe.Health = 20;
    Foe.MaxHealth = 20;
    Foe.Defense = 1;

    FTSTSSBattleSkillState Before;
    if (!TestTrue(TEXT("Build deterministic review-only encounter"),
        FTSTSSCombatTurns::TryBegin({Ender, Foe}, {ActorId, OpponentId},
                                   Before.Combat))) return false;

    TMap<FName, FName> Factions;
    const FName Crew(TEXT("crew"));
    const FName Enemy(TEXT("enemy"));
    Factions.Add(ActorId, Crew);
    Factions.Add(OpponentId, Enemy);
    FTSTSSBattleSkillKnowledge Knowledge;
    // Deliberately grant unrelated positive gates to isolate DesignOnly denial:
    Knowledge.LearnedByActor.Add(ActorId, TSet<FName>{SpellId});
    Knowledge.MasteryByActor.FindOrAdd(ActorId).Add(FName(TEXT("Fire")), 5);
    Knowledge.WeaponClassByActor.Add(ActorId, FName(TEXT("Staff")));

    FTSTSSBattleSkillState UnchangedOutput;
    UnchangedOutput.Combat.AcceptedActions = 67;
    FTSTSSBattleSkillCue UnchangedCue;
    UnchangedCue.SkillId = FName(TEXT("PreviousCue"));
    TestFalse(TEXT("Actual gated executor rejects adapter's DesignOnly row"),
        FTSTSSBattleSkillSystem::TryUseRow(
            Before, Knowledge, Factions, Crew, Enemy, ActorId, OpponentId,
            SpellId, *Row, UnchangedOutput, UnchangedCue));
    TestEqual(TEXT("Denied adapter action cannot mutate output combat state"),
        UnchangedOutput.Combat.AcceptedActions, 67);
    TestEqual(TEXT("Denied adapter action cannot replace cue"),
        UnchangedCue.SkillId, FName(TEXT("PreviousCue")));
    TestEqual(TEXT("Original opponent still has full health"),
        Before.Combat.Roster[1].Health, 20);
    TestEqual(TEXT("Original actor resource remains unchanged"),
        Before.Combat.Roster[0].Resource, 10);
    return true;
}
#endif
