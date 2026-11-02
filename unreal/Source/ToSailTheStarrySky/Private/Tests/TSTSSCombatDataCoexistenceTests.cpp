#include "Misc/AutomationTest.h"
#include "TSTSSCombatData.h"
#include "TSTSSBattleSkillSystem.h"

// Isolated integration fixture for draft PRs #662, #665 and #666.
// Tests *coexistence of independent gates*, NOT a production catalog bridge.
// Nothing here authorizes actual game spells, techniques, stats or progression.
#if WITH_DEV_AUTOMATION_TESTS
namespace
{
    FTSTSSCharacterBaselineRow MakeReviewBaseline(
        const TCHAR* Id, ETSTSSLight Affinity, int32 HP, int32 MP, int32 Magic)
    {
        FTSTSSCharacterBaselineRow Row;
        Row.CharacterId = FName(Id);
        Row.Affinity = Affinity;
        Row.StartMaxHP = HP;
        Row.StartMaxMP = MP;
        Row.StartMagic = Magic;
        return Row;
    }

    TArray<FTSTSSCharacterBaselineRow> ReviewBaselines()
    {
        // Deliberately noncanonical test-only numbers.
        return {
            MakeReviewBaseline(TEXT("Ender"), ETSTSSLight::Spirit, 70, 50, 12),
            MakeReviewBaseline(TEXT("Ionia"), ETSTSSLight::Earth, 90, 10, 4),
            MakeReviewBaseline(TEXT("Lyra"), ETSTSSLight::Water, 60, 40, 9),
            MakeReviewBaseline(TEXT("Reson"), ETSTSSLight::Fire, 100, 10, 3),
            MakeReviewBaseline(TEXT("Aepex"), ETSTSSLight::Air, 80, 20, 5)
        };
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSCombatDataCoexistenceTest,
    "TSTSS.CombatIntegration.DataContractCannotAutoAuthorize",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSCombatDataCoexistenceTest::RunTest(const FString& Parameters)
{
    const FName SeedId(TEXT("NoncanonicalProposalSeed"));
    TArray<FTSTSSActionDefRow> SourceActions;
    FTSTSSActionDefRow Seed;
    Seed.ActionId = SeedId;
    Seed.Category = ETSTSSActionCategory::Spell;
    Seed.Target = ETSTSSActionTarget::Enemy;
    Seed.Cost = 2;
    Seed.Power = 3;
    Seed.Affinity = ETSTSSLight::Fire; // Narrative metadata, not a school entitlement.
    Seed.UnlockLevel = 1;
    Seed.Learners.Add(FName(TEXT("Ender")));
    Seed.Approval = ETSTSSApproval::Proposed;
    SourceActions.Add(Seed);

    TMap<FName, int32> Levels;
    for (const FName Id : FTSTSSCombatData::Protagonists())
    {
        Levels.Add(Id, 1);
    }

    TMap<FName, FTSTSSAbilitySpec> Catalog;
    TMap<FName, TSet<FName>> LevelEligible;
    TArray<FTSTSSDataIssueEntry> Issues;
    if (!TestTrue(TEXT("Non-shipping data may be inspected without approval"),
        FTSTSSCombatData::TryBuildAbilityData(
            ReviewBaselines(), SourceActions, Levels, false,
            Catalog, LevelEligible, Issues))) return false;
    TestTrue(TEXT("Proposed source entry may appear in a review catalog"),
        Catalog.Contains(SeedId));
    const TSet<FName>* EnderLevelEligible = LevelEligible.Find(FName(TEXT("Ender")));
    if (!TestNotNull(TEXT("Level eligibility was derived"), EnderLevelEligible)) return false;
    TestTrue(TEXT("Derived level knowledge is not an execution grant"),
        EnderLevelEligible->Contains(SeedId));

    // The shipping data admission gate must deny the proposed source data without
    // modifying any pre-existing catalog or learned-set outputs.
    TMap<FName, FTSTSSAbilitySpec> ShippingCatalog;
    FTSTSSAbilitySpec Existing;
    Existing.AbilityId = FName(TEXT("PreexistingFixture"));
    ShippingCatalog.Add(Existing.AbilityId, Existing);
    TMap<FName, TSet<FName>> ShippingLearned;
    ShippingLearned.Add(FName(TEXT("Ender")),
        TSet<FName>{FName(TEXT("PreexistingFixture"))});
    TArray<FTSTSSDataIssueEntry> ShippingIssues;
    TestFalse(TEXT("Proposed actions cannot pass shipping data validation"),
        FTSTSSCombatData::TryBuildAbilityData(
            ReviewBaselines(), SourceActions, Levels, true,
            ShippingCatalog, ShippingLearned, ShippingIssues));
    TestTrue(TEXT("Rejected catalog preserves prior data"),
        ShippingCatalog.Contains(FName(TEXT("PreexistingFixture"))) &&
        !ShippingCatalog.Contains(SeedId));
    const TSet<FName>* Preserved = ShippingLearned.Find(FName(TEXT("Ender")));
    if (!TestNotNull(TEXT("Previous learned set remains available"), Preserved)) return false;
    TestTrue(TEXT("Failed validation cannot change the learned output"),
        Preserved->Contains(FName(TEXT("PreexistingFixture"))) &&
        !Preserved->Contains(SeedId));

    FTSTSSCombatant Ender;
    Ender.CharacterId = FName(TEXT("Ender"));
    Ender.Health = 15;
    Ender.MaxHealth = 20;
    Ender.Resource = 12;
    Ender.MaxResource = 12;
    Ender.Attack = 2;
    FTSTSSCombatant Foe = Ender;
    Foe.CharacterId = FName(TEXT("FixtureFoe"));
    Foe.Health = 20;
    Foe.MaxHealth = 20;
    Foe.Defense = 1;

    FTSTSSBattleSkillState Turn;
    if (!TestTrue(TEXT("Start a separate deterministic review encounter"),
        FTSTSSCombatTurns::TryBegin(
            {Ender, Foe},
            {FName(TEXT("Ender")), FName(TEXT("FixtureFoe"))},
            Turn.Combat))) return false;

    TMap<FName, FName> Factions;
    Factions.Add(FName(TEXT("Ender")), FName(TEXT("Crew")));
    Factions.Add(FName(TEXT("FixtureFoe")), FName(TEXT("Foes")));

    FTSTSSBattleSkillKnowledge Knowledge;
    Knowledge.LearnedByActor = LevelEligible;
    Knowledge.MasteryByActor.FindOrAdd(FName(TEXT("Ender"))).Add(
        FName(TEXT("Fire")), 1);

    FTSTSSBattleSkillRow UnapprovedReviewRow;
    UnapprovedReviewRow.SkillId = SeedId;
    UnapprovedReviewRow.Kind = ETSTSSBattleSkillKind::Spell;
    UnapprovedReviewRow.Target = ETSTSSBattleSkillTarget::Enemy;
    UnapprovedReviewRow.Power = 3;
    UnapprovedReviewRow.ResourceCost = 2;
    UnapprovedReviewRow.RequiredSchool = FName(TEXT("Fire"));
    UnapprovedReviewRow.RequiredMasteryRank = 1;
    // The default admission is DesignOnly; NEVER infer ReviewExecutable
    // from SourceActions.Approval or from LevelEligible.
    FTSTSSBattleSkillState Denied;
    Denied.Combat.AcceptedActions = 77;
    FTSTSSBattleSkillCue DeniedCue;
    DeniedCue.SkillId = FName(TEXT("PreserveCue"));
    TestFalse(TEXT("Proposed/level-eligible seed cannot execute as DesignOnly"),
        FTSTSSBattleSkillSystem::TryUseRow(
            Turn, Knowledge, Factions, FName(TEXT("Crew")), FName(TEXT("Foes")),
            FName(TEXT("Ender")), FName(TEXT("FixtureFoe")), SeedId,
            UnapprovedReviewRow, Denied, DeniedCue));
    TestEqual(TEXT("Denied request leaves output state untouched"),
        Denied.Combat.AcceptedActions, 77);
    TestEqual(TEXT("Denied request leaves cue untouched"),
        DeniedCue.SkillId, FName(TEXT("PreserveCue")));

    // An INDEPENDENT test-only authored skill is manually admitted;
    // it must still be learned explicitly and satisfy mastery. It is not
    // an automatic conversion of the Proposed seed above.
    FTSTSSBattleSkillRow ExplicitFixture = UnapprovedReviewRow;
    ExplicitFixture.SkillId = FName(TEXT("SeparateApprovedReviewFixture"));
    ExplicitFixture.Admission = ETSTSSBattleSkillAdmission::ReviewExecutable;
    Knowledge.MasteryByActor.FindOrAdd(FName(TEXT("Ender"))).Remove(
        FName(TEXT("Fire")));
    TestFalse(TEXT("Review admission does not bypass missing learned knowledge"),
        FTSTSSBattleSkillSystem::TryUseRow(
            Turn, Knowledge, Factions, FName(TEXT("Crew")), FName(TEXT("Foes")),
            FName(TEXT("Ender")), FName(TEXT("FixtureFoe")),
            ExplicitFixture.SkillId, ExplicitFixture, Denied, DeniedCue));
    Knowledge.LearnedByActor.FindOrAdd(FName(TEXT("Ender"))).Add(
        ExplicitFixture.SkillId);
    TestFalse(TEXT("Explicit learning does not bypass school mastery"),
        FTSTSSBattleSkillSystem::TryUseRow(
            Turn, Knowledge, Factions, FName(TEXT("Crew")), FName(TEXT("Foes")),
            FName(TEXT("Ender")), FName(TEXT("FixtureFoe")),
            ExplicitFixture.SkillId, ExplicitFixture, Denied, DeniedCue));
    Knowledge.MasteryByActor.FindOrAdd(FName(TEXT("Ender"))).Add(
        FName(TEXT("Fire")), 1);
    FTSTSSBattleSkillState Accepted;
    FTSTSSBattleSkillCue AcceptedCue;
    if (!TestTrue(TEXT("Independently authored and explicitly permitted review fixture"),
        FTSTSSBattleSkillSystem::TryUseRow(
            Turn, Knowledge, Factions, FName(TEXT("Crew")), FName(TEXT("Foes")),
            FName(TEXT("Ender")), FName(TEXT("FixtureFoe")),
            ExplicitFixture.SkillId, ExplicitFixture, Accepted, AcceptedCue)))
        return false;
    TestEqual(TEXT("Target received expected deterministic review damage"),
        Accepted.Combat.Roster[1].Health, 16);
    TestEqual(TEXT("Actor spent exactly the authorized review cost"),
        Accepted.Combat.Roster[0].Resource, 10);
    TestEqual(TEXT("Accepted review path creates only its own cue"),
        AcceptedCue.SkillId, ExplicitFixture.SkillId);
    TestEqual(TEXT("Original encounter remains unchanged"),
        Turn.Combat.Roster[1].Health, 20);
    return true;
}
#endif // WITH_DEV_AUTOMATION_TESTS
