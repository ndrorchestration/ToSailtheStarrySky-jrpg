#include "Misc/AutomationTest.h"
#include "TSTSSCombatData.h"

#if WITH_DEV_AUTOMATION_TESTS
namespace
{
    // NONCANONICAL TEST FIXTURE. These numbers and action names exist only to satisfy the
    // approved ordering constraints so the validator can be exercised. They are not
    // proposed game data.
    FTSTSSCharacterBaselineRow MakeBaseline(const TCHAR* Id, ETSTSSLight Light,
                                            int32 HP, int32 MP, int32 Magic)
    {
        FTSTSSCharacterBaselineRow Row;
        Row.CharacterId = Id;
        Row.Affinity = Light;
        Row.StartMaxHP = HP;
        Row.StartMaxMP = MP;
        Row.StartMagic = Magic;
        return Row;
    }

    // Slots follow FTSTSSCombatData::Protagonists(): Ender, Ionia, Lyra, Reson, Aepex.
    TArray<FTSTSSCharacterBaselineRow> FixtureBaselines()
    {
        return {
            MakeBaseline(TEXT("Ender"), ETSTSSLight::Spirit, 70, 50, 12),
            MakeBaseline(TEXT("Ionia"), ETSTSSLight::Earth, 90, 10, 4),
            MakeBaseline(TEXT("Lyra"), ETSTSSLight::Water, 60, 40, 9),
            MakeBaseline(TEXT("Reson"), ETSTSSLight::Fire, 100, 10, 3),
            MakeBaseline(TEXT("Aepex"), ETSTSSLight::Air, 80, 20, 5)};
    }

    FTSTSSActionDefRow MakeAction(const TCHAR* Id, ETSTSSActionCategory Category,
                                  ETSTSSActionTarget Target, int32 Cost, int32 Power,
                                  bool bHealing, ETSTSSLight Light, int32 UnlockLevel,
                                  const TArray<FName>& Learners)
    {
        FTSTSSActionDefRow Row;
        Row.ActionId = Id;
        Row.Category = Category;
        Row.Target = Target;
        Row.Cost = Cost;
        Row.Power = Power;
        Row.bHealing = bHealing;
        Row.Affinity = Light;
        Row.UnlockLevel = UnlockLevel;
        Row.Learners = Learners;
        return Row;
    }

    TArray<FTSTSSActionDefRow> FixtureActions()
    {
        return {
            MakeAction(TEXT("TestStrike"), ETSTSSActionCategory::Attack,
                       ETSTSSActionTarget::Enemy, 2, 3, false, ETSTSSLight::None, 1,
                       {TEXT("Ender"), TEXT("Ionia"), TEXT("Reson")}),
            MakeAction(TEXT("TestMend"), ETSTSSActionCategory::Support,
                       ETSTSSActionTarget::Ally, 2, 4, true, ETSTSSLight::Water, 3,
                       {TEXT("Lyra")}),
            // Affinity tags are optional metadata: a Spirit character may learn a Fire action.
            MakeAction(TEXT("TestEmber"), ETSTSSActionCategory::Spell,
                       ETSTSSActionTarget::Enemy, 1, 2, false, ETSTSSLight::Fire, 1,
                       {TEXT("Ender")}),
            MakeAction(TEXT("TestTechnique"), ETSTSSActionCategory::WeaponTechnique,
                       ETSTSSActionTarget::Enemy, 3, 5, false, ETSTSSLight::None, 2,
                       {TEXT("Reson")})};
    }

    TMap<FName, int32> LevelsAll(int32 Level)
    {
        TMap<FName, int32> Levels;
        for (const FName Id : FTSTSSCombatData::Protagonists())
        {
            Levels.Add(Id, Level);
        }
        return Levels;
    }

    bool HasIssue(const TArray<FTSTSSDataIssueEntry>& Issues, ETSTSSDataIssue Code,
                  FName Subject = NAME_None)
    {
        for (const FTSTSSDataIssueEntry& Entry : Issues)
        {
            if (Entry.Code == Code && (Subject.IsNone() || Entry.Subject == Subject))
                return true;
        }
        return false;
    }

    void ExpectBaselineIssue(FAutomationTestBase& Test, const TCHAR* Label,
                             const TArray<FTSTSSCharacterBaselineRow>& Rows,
                             bool bShipping, ETSTSSDataIssue Code)
    {
        TArray<FTSTSSDataIssueEntry> Issues;
        Test.TestFalse(Label, FTSTSSCombatData::ValidateBaselines(Rows, bShipping, Issues));
        Test.TestTrue(Label, HasIssue(Issues, Code));
    }

    void ExpectActionIssue(FAutomationTestBase& Test, const TCHAR* Label,
                           const TArray<FTSTSSActionDefRow>& Rows, bool bShipping,
                           ETSTSSDataIssue Code)
    {
        TArray<FTSTSSDataIssueEntry> Issues;
        Test.TestFalse(Label, FTSTSSCombatData::ValidateActions(Rows, bShipping, Issues));
        Test.TestTrue(Label, HasIssue(Issues, Code));
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSCombatDataProtagonistsTest,
    "TSTSS.CombatData.ProtagonistContracts",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSCombatDataProtagonistsTest::RunTest(const FString& Parameters)
{
    TArray<FTSTSSDataIssueEntry> Issues;
    if (!TestTrue(TEXT("Fixture satisfies approved contract"),
                  FTSTSSCombatData::ValidateBaselines(FixtureBaselines(), false, Issues)))
        return false;
    TestEqual(TEXT("No issues on valid fixture"), Issues.Num(), 0);

    // Approved Five Lights mapping.
    TestTrue(TEXT("Ender Spirit"), FTSTSSCombatData::ApprovedAffinity(TEXT("Ender")) == ETSTSSLight::Spirit);
    TestTrue(TEXT("Ionia Earth"), FTSTSSCombatData::ApprovedAffinity(TEXT("Ionia")) == ETSTSSLight::Earth);
    TestTrue(TEXT("Lyra Water"), FTSTSSCombatData::ApprovedAffinity(TEXT("Lyra")) == ETSTSSLight::Water);
    TestTrue(TEXT("Reson Fire"), FTSTSSCombatData::ApprovedAffinity(TEXT("Reson")) == ETSTSSLight::Fire);
    TestTrue(TEXT("Aepex Air"), FTSTSSCombatData::ApprovedAffinity(TEXT("Aepex")) == ETSTSSLight::Air);
    TestTrue(TEXT("Non-protagonist has no affinity"),
             FTSTSSCombatData::ApprovedAffinity(TEXT("Talen")) == ETSTSSLight::None);

    // Ionia, Reson and Aepex may tie one another (Ionia and Reson tie on MP in the fixture).
    TestEqual(TEXT("Fixture exercises an allowed tie"),
              FixtureBaselines()[1].StartMaxMP, FixtureBaselines()[3].StartMaxMP);

    TArray<FTSTSSCharacterBaselineRow> Rows = FixtureBaselines();
    Rows[0].StartMagic = Rows[2].StartMagic;  // Ender ties Lyra
    ExpectBaselineIssue(*this, TEXT("Ender must exceed Lyra on magic"), Rows, false,
                        ETSTSSDataIssue::MagicOrderViolation);

    Rows = FixtureBaselines();
    Rows[1].StartMagic = Rows[2].StartMagic;  // Ionia ties Lyra
    ExpectBaselineIssue(*this, TEXT("Lyra must exceed the rest on magic"), Rows, false,
                        ETSTSSDataIssue::MagicOrderViolation);

    Rows = FixtureBaselines();
    Rows[2].StartMaxMP = Rows[0].StartMaxMP;  // Lyra ties Ender
    ExpectBaselineIssue(*this, TEXT("Ender must exceed Lyra on MP"), Rows, false,
                        ETSTSSDataIssue::MpOrderViolation);

    Rows = FixtureBaselines();
    Rows[4].StartMaxMP = Rows[2].StartMaxMP;  // Aepex ties Lyra
    ExpectBaselineIssue(*this, TEXT("Lyra must exceed the rest on MP"), Rows, false,
                        ETSTSSDataIssue::MpOrderViolation);

    Rows = FixtureBaselines();
    Rows[2].StartMaxHP = Rows[0].StartMaxHP;  // Lyra ties Ender
    ExpectBaselineIssue(*this, TEXT("Lyra must be lowest HP"), Rows, false,
                        ETSTSSDataIssue::HpOrderViolation);

    Rows = FixtureBaselines();
    Rows[3].StartMaxHP = Rows[0].StartMaxHP;  // Reson ties Ender
    ExpectBaselineIssue(*this, TEXT("Ender must be second lowest HP"), Rows, false,
                        ETSTSSDataIssue::HpOrderViolation);

    Rows = FixtureBaselines();
    Rows[0].Affinity = ETSTSSLight::Fire;
    ExpectBaselineIssue(*this, TEXT("Wrong affinity rejected"), Rows, false,
                        ETSTSSDataIssue::WrongAffinity);

    Rows = FixtureBaselines();
    Rows.RemoveAt(4);
    ExpectBaselineIssue(*this, TEXT("Missing protagonist rejected"), Rows, false,
                        ETSTSSDataIssue::MissingProtagonist);

    Rows = FixtureBaselines();
    const FTSTSSCharacterBaselineRow DuplicateLyra = Rows[2];  // copy: TArray::Add asserts on self-references
    Rows.Add(DuplicateLyra);
    ExpectBaselineIssue(*this, TEXT("Duplicate protagonist rejected"), Rows, false,
                        ETSTSSDataIssue::DuplicateCharacter);

    Rows = FixtureBaselines();
    Rows.Add(MakeBaseline(TEXT("Talen"), ETSTSSLight::None, 50, 5, 1));
    ExpectBaselineIssue(*this, TEXT("Non-protagonist rejected"), Rows, false,
                        ETSTSSDataIssue::UnknownCharacter);

    Rows = FixtureBaselines();
    Rows[1].StartMaxHP = 0;
    ExpectBaselineIssue(*this, TEXT("Zero max HP rejected"), Rows, false,
                        ETSTSSDataIssue::ValueOutOfRange);

    Rows = FixtureBaselines();
    Rows[1].StartMaxMP = FTSTSSCombatData::MaxDataValue + 1;
    ExpectBaselineIssue(*this, TEXT("Oversized MP rejected"), Rows, false,
                        ETSTSSDataIssue::ValueOutOfRange);

    // Shipping mode requires explicit creator approval on every row.
    ExpectBaselineIssue(*this, TEXT("Placeholder rows blocked from shipping"),
                        FixtureBaselines(), true, ETSTSSDataIssue::NotCreatorApproved);
    Rows = FixtureBaselines();
    for (FTSTSSCharacterBaselineRow& Row : Rows) Row.Approval = ETSTSSApproval::CreatorApproved;
    Issues.Reset();
    TestTrue(TEXT("Approved rows pass shipping validation"),
             FTSTSSCombatData::ValidateBaselines(Rows, true, Issues));
    Rows[3].Approval = ETSTSSApproval::Proposed;
    ExpectBaselineIssue(*this, TEXT("Proposed rows blocked from shipping"), Rows, true,
                        ETSTSSDataIssue::NotCreatorApproved);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSCombatDataActionsTest,
    "TSTSS.CombatData.ActionDefinitions",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSCombatDataActionsTest::RunTest(const FString& Parameters)
{
    TArray<FTSTSSDataIssueEntry> Issues;
    if (!TestTrue(TEXT("Fixture actions valid"),
                  FTSTSSCombatData::ValidateActions(FixtureActions(), false, Issues)))
        return false;
    TestEqual(TEXT("No issues on valid fixture"), Issues.Num(), 0);

    TArray<FTSTSSActionDefRow> Rows = FixtureActions();
    Rows[0].ActionId = NAME_None;
    ExpectActionIssue(*this, TEXT("Empty id rejected"), Rows, false,
                      ETSTSSDataIssue::InvalidActionId);

    Rows = FixtureActions();
    Rows[1].ActionId = Rows[0].ActionId;
    ExpectActionIssue(*this, TEXT("Duplicate id rejected"), Rows, false,
                      ETSTSSDataIssue::DuplicateAction);

    Rows = FixtureActions();
    Rows[0].Cost = -1;
    ExpectActionIssue(*this, TEXT("Negative cost rejected"), Rows, false,
                      ETSTSSDataIssue::ValueOutOfRange);

    Rows = FixtureActions();
    Rows[0].Power = -1;
    ExpectActionIssue(*this, TEXT("Negative power rejected"), Rows, false,
                      ETSTSSDataIssue::ValueOutOfRange);

    Rows = FixtureActions();
    Rows[0].Power = FTSTSSCombatData::MaxDataValue + 1;
    ExpectActionIssue(*this, TEXT("Oversized power rejected"), Rows, false,
                      ETSTSSDataIssue::ValueOutOfRange);

    Rows = FixtureActions();
    Rows[0].Category = static_cast<ETSTSSActionCategory>(255);
    ExpectActionIssue(*this, TEXT("Unknown action category rejected"), Rows, false,
                      ETSTSSDataIssue::InvalidActionCategory);

    Rows = FixtureActions();
    Rows[0].Target = static_cast<ETSTSSActionTarget>(255);
    ExpectActionIssue(*this, TEXT("Unknown target rejected"), Rows, false,
                      ETSTSSDataIssue::InvalidActionTarget);

    // Downstream conversion must not invent a target when deserialization
    // produces an unknown enum value, even in source-only review mode.
    TMap<FName, FTSTSSAbilitySpec> SentinelCatalog;
    FTSTSSAbilitySpec SentinelAbility;
    SentinelAbility.AbilityId = TEXT("PreserveFixture");
    SentinelCatalog.Add(SentinelAbility.AbilityId, SentinelAbility);
    TMap<FName, TSet<FName>> SentinelLearned;
    SentinelLearned.Add(TEXT("Ender"), TSet<FName>{TEXT("PreserveFixture")});
    TArray<FTSTSSDataIssueEntry> BadEnumIssues;
    TestFalse(TEXT("Invalid enum cannot be bridged into a combat catalog"),
        FTSTSSCombatData::TryBuildAbilityData(
            FixtureBaselines(), Rows, LevelsAll(1), false,
            SentinelCatalog, SentinelLearned, BadEnumIssues));
    TestTrue(TEXT("Invalid bridge target recorded"),
        HasIssue(BadEnumIssues, ETSTSSDataIssue::InvalidActionTarget));
    TestEqual(TEXT("Rejected enum conversion keeps prior catalog"),
              SentinelCatalog.Num(), 1);
    TestTrue(TEXT("Rejected enum conversion preserves prior learned set"),
        SentinelLearned.FindChecked(TEXT("Ender")).Contains(TEXT("PreserveFixture")));

    Rows = FixtureActions();
    Rows[0].UnlockLevel = 0;
    ExpectActionIssue(*this, TEXT("Unlock level below 1 rejected"), Rows, false,
                      ETSTSSDataIssue::InvalidUnlockLevel);

    Rows = FixtureActions();
    Rows[1].Target = ETSTSSActionTarget::Enemy;  // TestMend is a healing action
    ExpectActionIssue(*this, TEXT("Healing an enemy rejected"), Rows, false,
                      ETSTSSDataIssue::HealingTargetsEnemy);

    Rows = FixtureActions();
    Rows[0].Learners.Reset();
    ExpectActionIssue(*this, TEXT("Action nobody can learn rejected"), Rows, false,
                      ETSTSSDataIssue::NoLearners);

    Rows = FixtureActions();
    Rows[0].Learners.Add(TEXT("Talen"));
    ExpectActionIssue(*this, TEXT("Non-protagonist learner rejected"), Rows, false,
                      ETSTSSDataIssue::UnknownLearner);

    Rows = FixtureActions();
    Rows[0].Learners.Add(TEXT("Ender"));
    ExpectActionIssue(*this, TEXT("Duplicate learner rejected"), Rows, false,
                      ETSTSSDataIssue::DuplicateLearner);

    // Affinity is metadata, never a restriction: a Spirit character may learn a Fire action.
    Issues.Reset();
    TestTrue(TEXT("Cross-affinity learner accepted"),
             FTSTSSCombatData::ValidateActions(FixtureActions(), false, Issues));

    ExpectActionIssue(*this, TEXT("Placeholder actions blocked from shipping"),
                      FixtureActions(), true, ETSTSSDataIssue::NotCreatorApproved);
    Rows = FixtureActions();
    for (FTSTSSActionDefRow& Row : Rows) Row.Approval = ETSTSSApproval::CreatorApproved;
    Issues.Reset();
    TestTrue(TEXT("Approved actions pass shipping validation"),
             FTSTSSCombatData::ValidateActions(Rows, true, Issues));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSCombatDataActivePartyTest,
    "TSTSS.CombatData.ActiveParty",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSCombatDataActivePartyTest::RunTest(const FString& Parameters)
{
    TArray<FTSTSSDataIssueEntry> Issues;
    TestTrue(TEXT("Three distinct protagonists accepted"),
             FTSTSSCombatData::ValidateActiveParty(
                 {TEXT("Reson"), TEXT("Ender"), TEXT("Lyra")}, Issues));
    TestEqual(TEXT("No issues"), Issues.Num(), 0);

    const TArray<TArray<FName>> Bad = {
        {},                                                        // empty
        {TEXT("Ender"), TEXT("Lyra")},                             // too few
        {TEXT("Ender"), TEXT("Lyra"), TEXT("Ionia"), TEXT("Reson")},  // too many
        {TEXT("Ender"), TEXT("Ender"), TEXT("Lyra")},              // duplicate
        {TEXT("Ender"), TEXT("Lyra"), TEXT("Talen")}               // not a protagonist
    };
    for (const TArray<FName>& Party : Bad)
    {
        TArray<FTSTSSDataIssueEntry> BadIssues;
        TestFalse(TEXT("Invalid active party rejected"),
                  FTSTSSCombatData::ValidateActiveParty(Party, BadIssues));
        TestTrue(TEXT("Reported as InvalidActiveParty"),
                 HasIssue(BadIssues, ETSTSSDataIssue::InvalidActiveParty));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSCombatDataBridgeTest,
    "TSTSS.CombatData.CatalogBridge",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSCombatDataBridgeTest::RunTest(const FString& Parameters)
{
    TMap<FName, FTSTSSAbilitySpec> Catalog;
    TMap<FName, TSet<FName>> Learned;
    TArray<FTSTSSDataIssueEntry> Issues;
    if (!TestTrue(TEXT("Level 1 build succeeds"), FTSTSSCombatData::TryBuildAbilityData(
            FixtureBaselines(), FixtureActions(), LevelsAll(1), false, Catalog, Learned, Issues)))
        return false;
    TestEqual(TEXT("Catalog holds every action"), Catalog.Num(), 4);
    TestEqual(TEXT("Every protagonist has a learned set"), Learned.Num(), 5);
    const FTSTSSAbilitySpec* Mend = Catalog.Find(TEXT("TestMend"));
    if (!TestTrue(TEXT("Mend present"), Mend != nullptr)) return false;
    TestTrue(TEXT("Mend heals"), Mend->bHealing);
    TestTrue(TEXT("Mend targets allies"), Mend->Target == FTSTSSAbilitySpec::ETarget::Ally);
    TestEqual(TEXT("Mend cost carried over"), Mend->Cost, 2);

    // Level gating: Mend unlocks for Lyra at level 3, Technique for Reson at level 2.
    TestFalse(TEXT("Lyra lacks Mend at level 1"), Learned.FindChecked(TEXT("Lyra")).Contains(TEXT("TestMend")));
    TestFalse(TEXT("Reson lacks Technique at level 1"), Learned.FindChecked(TEXT("Reson")).Contains(TEXT("TestTechnique")));
    TestTrue(TEXT("Ender knows Strike at level 1"), Learned.FindChecked(TEXT("Ender")).Contains(TEXT("TestStrike")));
    TestFalse(TEXT("Ionia does not know Ender's Ember"), Learned.FindChecked(TEXT("Ionia")).Contains(TEXT("TestEmber")));

    // Same data through the existing deterministic core.
    FTSTSSCombatant Ender;
    Ender.CharacterId = TEXT("Ender"); Ender.Health = 10; Ender.MaxHealth = 20;
    Ender.Resource = 5; Ender.MaxResource = 5;
    FTSTSSCombatant Lyra = Ender;
    Lyra.CharacterId = TEXT("Lyra"); Lyra.Health = 12; Lyra.MaxHealth = 12;
    FTSTSSCombatant Foe = Ender;
    Foe.CharacterId = TEXT("Foe"); Foe.Health = 8; Foe.MaxHealth = 8;
    TMap<FName, FName> Teams;
    Teams.Add(TEXT("Ender"), TEXT("crew")); Teams.Add(TEXT("Lyra"), TEXT("crew"));
    Teams.Add(TEXT("Foe"), TEXT("enemy"));

    FTSTSSCombatTurnState EnderFirst;
    if (!TestTrue(TEXT("Begin Ender-first"), FTSTSSCombatTurns::TryBegin(
            {Ender, Foe}, {TEXT("Ender"), TEXT("Foe")}, EnderFirst))) return false;
    FTSTSSCombatTurnState Out;
    if (!TestTrue(TEXT("Built Strike accepted by the core"), FTSTSSCombatAbilities::TryUse(
            EnderFirst, TEXT("Ender"), TEXT("Foe"), TEXT("TestStrike"), Catalog, Learned,
            Teams, TEXT("crew"), TEXT("enemy"), Out))) return false;
    if (!TestEqual(TEXT("Roster size"), Out.Roster.Num(), 2)) return false;
    TestEqual(TEXT("Strike damage = power 3 + attack 1"), Out.Roster[1].Health, 4);
    TestEqual(TEXT("Strike cost spent"), Out.Roster[0].Resource, 3);

    // Cross-affinity: Ender (Spirit) uses the Fire-tagged Ember. Affinity does not restrict.
    FTSTSSCombatTurnState Ember;
    TestTrue(TEXT("Cross-affinity action accepted"), FTSTSSCombatAbilities::TryUse(
        EnderFirst, TEXT("Ender"), TEXT("Foe"), TEXT("TestEmber"), Catalog, Learned,
        Teams, TEXT("crew"), TEXT("enemy"), Ember));

    FTSTSSCombatTurnState LyraFirst;
    if (!TestTrue(TEXT("Begin Lyra-first"), FTSTSSCombatTurns::TryBegin(
            {Lyra, Ender, Foe}, {TEXT("Lyra"), TEXT("Ender"), TEXT("Foe")}, LyraFirst))) return false;
    FTSTSSCombatTurnState MendOut;
    TestFalse(TEXT("Mend blocked before its unlock level"), FTSTSSCombatAbilities::TryUse(
        LyraFirst, TEXT("Lyra"), TEXT("Ender"), TEXT("TestMend"), Catalog, Learned,
        Teams, TEXT("crew"), TEXT("enemy"), MendOut));

    TMap<FName, FTSTSSAbilitySpec> Catalog3;
    TMap<FName, TSet<FName>> Learned3;
    if (!TestTrue(TEXT("Level 3 build succeeds"), FTSTSSCombatData::TryBuildAbilityData(
            FixtureBaselines(), FixtureActions(), LevelsAll(3), false, Catalog3, Learned3, Issues)))
        return false;
    if (!TestTrue(TEXT("Mend accepted at its unlock level"), FTSTSSCombatAbilities::TryUse(
            LyraFirst, TEXT("Lyra"), TEXT("Ender"), TEXT("TestMend"), Catalog3, Learned3,
            Teams, TEXT("crew"), TEXT("enemy"), MendOut))) return false;
    if (!TestEqual(TEXT("Roster size"), MendOut.Roster.Num(), 3)) return false;
    TestEqual(TEXT("Heal = power 4 + attack 1"), MendOut.Roster[1].Health, 15);
    TestEqual(TEXT("Mend cost spent"), MendOut.Roster[0].Resource, 3);

    // All-or-nothing: invalid input must leave the caller's outputs untouched.
    FTSTSSAbilitySpec Sentinel;
    Sentinel.AbilityId = TEXT("Sentinel");
    TMap<FName, FTSTSSAbilitySpec> KeptCatalog;
    KeptCatalog.Add(Sentinel.AbilityId, Sentinel);
    TMap<FName, TSet<FName>> KeptLearned;
    KeptLearned.Add(TEXT("Sentinel"), TSet<FName>{TEXT("Sentinel")});

    TMap<FName, int32> MissingAepex = LevelsAll(1);
    MissingAepex.Remove(TEXT("Aepex"));
    TArray<FTSTSSDataIssueEntry> BuildIssues;
    TestFalse(TEXT("Missing level rejected"), FTSTSSCombatData::TryBuildAbilityData(
        FixtureBaselines(), FixtureActions(), MissingAepex, false, KeptCatalog, KeptLearned, BuildIssues));
    TestTrue(TEXT("Missing level reported for Aepex"),
             HasIssue(BuildIssues, ETSTSSDataIssue::MissingLevel, TEXT("Aepex")));
    TestEqual(TEXT("Catalog untouched on failure"), KeptCatalog.Num(), 1);
    TestEqual(TEXT("Learned untouched on failure"), KeptLearned.Num(), 1);

    TMap<FName, int32> ZeroLevel = LevelsAll(1);
    ZeroLevel.Add(TEXT("Lyra"), 0);
    BuildIssues.Reset();
    TestFalse(TEXT("Level below 1 rejected"), FTSTSSCombatData::TryBuildAbilityData(
        FixtureBaselines(), FixtureActions(), ZeroLevel, false, KeptCatalog, KeptLearned, BuildIssues));
    TestTrue(TEXT("Invalid level reported for Lyra"),
             HasIssue(BuildIssues, ETSTSSDataIssue::InvalidLevel, TEXT("Lyra")));

    TMap<FName, int32> ExtraCharacter = LevelsAll(1);
    ExtraCharacter.Add(TEXT("Talen"), 1);
    BuildIssues.Reset();
    TestFalse(TEXT("Level for a non-protagonist rejected"), FTSTSSCombatData::TryBuildAbilityData(
        FixtureBaselines(), FixtureActions(), ExtraCharacter, false, KeptCatalog, KeptLearned, BuildIssues));
    TestTrue(TEXT("Non-protagonist level reported"),
             HasIssue(BuildIssues, ETSTSSDataIssue::UnknownCharacter, TEXT("Talen")));

    BuildIssues.Reset();
    TestFalse(TEXT("Placeholder data rejected in shipping mode"), FTSTSSCombatData::TryBuildAbilityData(
        FixtureBaselines(), FixtureActions(), LevelsAll(1), true, KeptCatalog, KeptLearned, BuildIssues));
    TestTrue(TEXT("Shipping rejection reported"),
             HasIssue(BuildIssues, ETSTSSDataIssue::NotCreatorApproved));
    TestEqual(TEXT("Catalog still untouched"), KeptCatalog.Num(), 1);
    return true;
}
#endif
