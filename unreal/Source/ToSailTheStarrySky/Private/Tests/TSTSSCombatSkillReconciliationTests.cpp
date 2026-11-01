#include "Misc/AutomationTest.h"
#include "TSTSSCombatSkillReconciliation.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSCrossAgentSkillBridgeTest,
    "TSTSS.CombatData.NonExecutableSkillReconciliation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSCrossAgentSkillBridgeTest::RunTest(const FString& Parameters)
{
    FTSTSSActionDefRow Spell;
    Spell.ActionId = TEXT("ReviewLumen");
    Spell.Category = ETSTSSActionCategory::Spell;
    Spell.Target = ETSTSSActionTarget::Enemy;
    Spell.Power = 4;
    Spell.Cost = 2;
    Spell.UnlockLevel = 2;
    Spell.Learners = {TEXT("Ender")};
    Spell.Approval = ETSTSSApproval::CreatorApproved; // Test only, not an approval of this ability.
    Spell.Affinity = ETSTSSLight::Spirit; // A narrative tag; NOT the Lumen school.

    FTSTSSActionDefRow Technique = Spell;
    Technique.ActionId = TEXT("ReviewStaffMove");
    Technique.Category = ETSTSSActionCategory::WeaponTechnique;
    Technique.Target = ETSTSSActionTarget::Self;
    Technique.Power = 1;
    Technique.Cost = 0;
    Technique.Approval = ETSTSSApproval::Placeholder;

    TMap<FName, FTSTSSBattleSkillRow> Out;
    if (!TestTrue(TEXT("compatible action rows export"),
        FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {Spell, Technique}, Out))) return false;
    TestEqual(TEXT("both rows preserved"), Out.Num(), 2);
    const FTSTSSBattleSkillRow* S = Out.Find(Spell.ActionId);
    if (!TestNotNull(TEXT("spell row exists"), S)) return false;
    TestEqual(TEXT("spell power copied"), S->Power, 4);
    TestEqual(TEXT("spell cost copied"), S->ResourceCost, 2);
    TestTrue(TEXT("approval alone does not admit executable magic"),
             S->Admission == ETSTSSBattleSkillAdmission::DesignOnly);
    TestTrue(TEXT("school NOT guessed from Spirit story affinity"),
             S->RequiredSchool.IsNone());
    TestEqual(TEXT("rank never auto-granted"), S->RequiredMasteryRank, 0);
    TestTrue(TEXT("Unreal school access remains ungranted"),
             S->RequiredSecondarySchool.IsNone());
    const FTSTSSBattleSkillRow* T = Out.Find(Technique.ActionId);
    if (!TestNotNull(TEXT("technique row exists"), T)) return false;
    TestTrue(TEXT("weapon not guessed"), T->RequiredWeaponClass.IsNone());
    TestTrue(TEXT("technique not executable"), T->Admission == ETSTSSBattleSkillAdmission::DesignOnly);
    TestTrue(TEXT("target transferred"), T->Target == ETSTSSBattleSkillTarget::Self);

    // A design-only conversion must be denied by the REAL executor even if
    // a test actor has learned the skill and a fabricated mastery rank.
    // This checks the admission boundary behavior, not just a data flag.
    FTSTSSCombatant Ender;
    Ender.CharacterId = TEXT("Ender");
    Ender.Health = Ender.MaxHealth = 20;
    Ender.Resource = Ender.MaxResource = 10;
    Ender.Attack = 2;
    FTSTSSCombatant Foe = Ender;
    Foe.CharacterId = TEXT("ReviewFoe");
    FTSTSSBattleSkillState Battle;
    if (!TestTrue(TEXT("review encounter initialized"),
        FTSTSSCombatTurns::TryBegin(
            {Ender, Foe}, {FName(TEXT("Ender")), FName(TEXT("ReviewFoe"))},
            Battle.Combat))) return false;
    FTSTSSBattleSkillKnowledge Knowledge;
    Knowledge.LearnedByActor.FindOrAdd(FName(TEXT("Ender"))).Add(Spell.ActionId);
    Knowledge.MasteryByActor.FindOrAdd(FName(TEXT("Ender"))).Add(TEXT("Lumen"), 5);
    FTSTSSBattleSkillRow BypassedSchool = *S;
    BypassedSchool.RequiredSchool = TEXT("Lumen");
    BypassedSchool.RequiredMasteryRank = 1;
    TMap<FName, FName> Factions;
    Factions.Add(TEXT("Ender"), TEXT("Crew"));
    Factions.Add(TEXT("ReviewFoe"), TEXT("Opponents"));
    FTSTSSBattleSkillState Rejected;
    Rejected.Combat.AcceptedActions = 41;
    FTSTSSBattleSkillCue RejectedCue;
    RejectedCue.SkillId = TEXT("UntouchedCue");
    TestFalse(TEXT("review admission is denied by actual executor"),
        FTSTSSBattleSkillSystem::TryUseRow(
            Battle, Knowledge, Factions, TEXT("Crew"), TEXT("Opponents"),
            TEXT("Ender"), TEXT("ReviewFoe"), Spell.ActionId,
            BypassedSchool, Rejected, RejectedCue));
    TestEqual(TEXT("executor denial leaves output state intact"),
              Rejected.Combat.AcceptedActions, 41);
    TestEqual(TEXT("executor denial leaves output cue intact"),
              RejectedCue.SkillId, FName(TEXT("UntouchedCue")));
    TestEqual(TEXT("executor denial leaves encounter untouched"),
              Battle.Combat.Roster[1].Health, 20);

    const int32 OldSize = Out.Num();
    FTSTSSActionDefRow GenericAttack = Spell;
    GenericAttack.ActionId = TEXT("GenericAttack");
    GenericAttack.Category = ETSTSSActionCategory::Attack;
    TestFalse(TEXT("generic attacks cannot be mislabeled JobArts"),
              FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
                  {Spell, GenericAttack}, Out));
    TestEqual(TEXT("failed conversion preserves output count"), Out.Num(), OldSize);
    TestTrue(TEXT("failed conversion preserves existing spell"),
             Out.Contains(Spell.ActionId));
    FTSTSSActionDefRow Duplicate = Spell;
    TestFalse(TEXT("duplicate IDs fail closed"),
              FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
                  {Spell, Duplicate}, Out));
    TestEqual(TEXT("duplicate rejection is atomic"), Out.Num(), OldSize);

    FTSTSSActionDefRow Invalid = Spell;
    Invalid.ActionId = TEXT("ReviewInvalid");
    Invalid.bHealing = true;
    Invalid.Target = ETSTSSActionTarget::Enemy;
    TestFalse(TEXT("enemy healing rejected by source validator"),
              FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
                  {Invalid}, Out));
    TestTrue(TEXT("rejection keeps prior row"), Out.Contains(Technique.ActionId));
    return true;
}
#endif
