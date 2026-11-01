#include "Misc/AutomationTest.h"
#include "TSTSSBattleSkillSystem.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSBattleSpellTechniqueTest,
    "TSTSS.Combat.MagicAndWeaponTechniques",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSBattleSpellTechniqueTest::RunTest(const FString& Parameters)
{
    FTSTSSCombatant Ender;
    Ender.CharacterId = TEXT("Ender"); Ender.Health = 15; Ender.MaxHealth = 20;
    Ender.Resource = 12; Ender.MaxResource = 12; Ender.Attack = 2;
    FTSTSSCombatant Foe = Ender;
    Foe.CharacterId = TEXT("Foe"); Foe.Health = 20; Foe.MaxHealth = 20;
    Foe.Defense = 1;
    FTSTSSBattleSkillState Initial;
    if (!TestTrue(TEXT("start combat"), FTSTSSCombatTurns::TryBegin(
        {Ender, Foe}, {TEXT("Ender"), TEXT("Foe")}, Initial.Combat))) return false;

    TMap<FName, FName> Factions;
    Factions.Add(TEXT("Ender"), TEXT("crew"));
    Factions.Add(TEXT("Foe"), TEXT("enemy"));
    FTSTSSBattleSkillKnowledge Knowledge;
    Knowledge.LearnedByActor.Add(TEXT("Ender"),
        TSet<FName>{TEXT("ReviewSpark"), TEXT("ReviewStaffStrike"), TEXT("ReviewMend")});

    FTSTSSBattleSkillRow Spark;
    Spark.SkillId = TEXT("ReviewSpark");
    Spark.Kind = ETSTSSBattleSkillKind::Spell;
    Spark.Admission = ETSTSSBattleSkillAdmission::ReviewExecutable;
    Spark.RequiredSchool = TEXT("Fire");
    Spark.RequiredMasteryRank = 1;
    Spark.Power = 4; Spark.ResourceCost = 3;
    Spark.CooldownActorTurns = 1;
    Spark.VfxCueId = TEXT("VFX.Review.FireSpark");

    FTSTSSBattleSkillState Result;
    FTSTSSBattleSkillCue Cue;
    TestFalse(TEXT("mastery is not inferred from learned or story affinity"),
        FTSTSSBattleSkillSystem::TryUseRow(Initial, Knowledge, Factions,
            TEXT("crew"), TEXT("enemy"), TEXT("Ender"), TEXT("Foe"),
            Spark.SkillId, Spark, Result, Cue));
    TestEqual(TEXT("denial leaves output unused"), Result.Combat.AcceptedActions, 0);
    Knowledge.MasteryByActor.FindOrAdd(TEXT("Ender")).Add(TEXT("Fire"), 1);

    FTSTSSBattleSkillRow Unadmitted = Spark;
    Unadmitted.Admission = ETSTSSBattleSkillAdmission::DesignOnly;
    TestFalse(TEXT("design-only seed cannot execute"),
        FTSTSSBattleSkillSystem::TryUseRow(Initial, Knowledge, Factions,
            TEXT("crew"), TEXT("enemy"), TEXT("Ender"), TEXT("Foe"),
            Spark.SkillId, Unadmitted, Result, Cue));

    if (!TestTrue(TEXT("explicitly mastered spell executes"),
        FTSTSSBattleSkillSystem::TryUseRow(Initial, Knowledge, Factions,
            TEXT("crew"), TEXT("enemy"), TEXT("Ender"), TEXT("Foe"),
            Spark.SkillId, Spark, Result, Cue))) return false;
    TestEqual(TEXT("damage including defense"), Result.Combat.Roster[1].Health, 15);
    TestEqual(TEXT("MP spent"), Result.Combat.Roster[0].Resource, 9);
    TestEqual(TEXT("source unchanged"), Initial.Combat.Roster[1].Health, 20);
    TestEqual(TEXT("cue is emitted after acceptance"), Cue.VfxCueId,
              FName(TEXT("VFX.Review.FireSpark")));

    FTSTSSBattleSkillRow Staff;
    Staff.SkillId = TEXT("ReviewStaffStrike");
    Staff.Kind = ETSTSSBattleSkillKind::WeaponTechnique;
    Staff.Admission = ETSTSSBattleSkillAdmission::ReviewExecutable;
    Staff.RequiredWeaponClass = TEXT("Staff");
    Staff.Power = 2;
    FTSTSSBattleSkillState Rejected = Result;
    FTSTSSBattleSkillCue RejectedCue = Cue;
    TestFalse(TEXT("missing staff blocks staff technique"),
        FTSTSSBattleSkillSystem::TryUseRow(Initial, Knowledge, Factions,
            TEXT("crew"), TEXT("enemy"), TEXT("Ender"), TEXT("Foe"),
            Staff.SkillId, Staff, Rejected, RejectedCue));
    TestEqual(TEXT("reject preserves accepted outcome"), Rejected.Combat.Roster[1].Health, 15);
    TestEqual(TEXT("reject preserves cue"), RejectedCue.SkillId, Spark.SkillId);
    Knowledge.WeaponClassByActor.Add(TEXT("Ender"), TEXT("Staff"));

    FTSTSSBattleSkillRow Mend;
    Mend.SkillId = TEXT("ReviewMend");
    Mend.Kind = ETSTSSBattleSkillKind::Spell;
    Mend.Admission = ETSTSSBattleSkillAdmission::ReviewExecutable;
    Mend.RequiredSchool = TEXT("Water"); Mend.RequiredMasteryRank = 1;
    Mend.bHealing = true; Mend.Target = ETSTSSBattleSkillTarget::Self;
    Mend.Power = 3; Mend.ResourceCost = 2;
    TestFalse(TEXT("no Water mastery blocks restoration"),
        FTSTSSBattleSkillSystem::TryUseRow(Initial, Knowledge, Factions,
            TEXT("crew"), TEXT("enemy"), TEXT("Ender"), TEXT("Ender"),
            Mend.SkillId, Mend, Rejected, RejectedCue));
    Knowledge.MasteryByActor.FindOrAdd(TEXT("Ender")).Add(TEXT("Water"), 1);
    FTSTSSBattleSkillState Healing;
    FTSTSSBattleSkillCue HealingCue;
    if (!TestTrue(TEXT("self healing works with explicit Water mastery"),
        FTSTSSBattleSkillSystem::TryUseRow(Initial, Knowledge, Factions,
            TEXT("crew"), TEXT("enemy"), TEXT("Ender"), TEXT("Ender"),
            Mend.SkillId, Mend, Healing, HealingCue))) return false;
    TestEqual(TEXT("healing capped"), Healing.Combat.Roster[0].Health, 20);
    TestEqual(TEXT("self healing charges resource"), Healing.Combat.Roster[0].Resource, 10);

    // Roll a full turn through the same skill executor to advance actor-local cooldowns.
    FTSTSSBattleSkillRow Claw;
    Claw.SkillId = TEXT("ReviewClaw");
    Claw.Kind = ETSTSSBattleSkillKind::JobArt;
    Claw.Admission = ETSTSSBattleSkillAdmission::ReviewExecutable;
    Claw.Power = 1;
    Knowledge.LearnedByActor.Add(TEXT("Foe"), TSet<FName>{TEXT("ReviewClaw")});
    FTSTSSBattleSkillState AfterFoe;
    FTSTSSBattleSkillCue AfterFoeCue;
    if (!TestTrue(TEXT("foe advances turn"), FTSTSSBattleSkillSystem::TryUseRow(
        Result, Knowledge, Factions, TEXT("crew"), TEXT("enemy"),
        TEXT("Foe"), TEXT("Ender"), Claw.SkillId, Claw,
        AfterFoe, AfterFoeCue))) return false;
    TestFalse(TEXT("same spell blocked on next actor turn"),
        FTSTSSBattleSkillSystem::TryUseRow(AfterFoe, Knowledge, Factions,
        TEXT("crew"), TEXT("enemy"), TEXT("Ender"), TEXT("Foe"),
        Spark.SkillId, Spark, Rejected, RejectedCue));
    FTSTSSBattleSkillState AfterStaff;
    FTSTSSBattleSkillCue AfterStaffCue;
    if (!TestTrue(TEXT("staff skill executes when staff is equipped"),
        FTSTSSBattleSkillSystem::TryUseRow(AfterFoe, Knowledge, Factions,
        TEXT("crew"), TEXT("enemy"), TEXT("Ender"), TEXT("Foe"),
        Staff.SkillId, Staff, AfterStaff, AfterStaffCue))) return false;
    FTSTSSBattleSkillState AfterSecondFoe;
    FTSTSSBattleSkillCue SecondFoeCue;
    if (!TestTrue(TEXT("second foe turn"), FTSTSSBattleSkillSystem::TryUseRow(
        AfterStaff, Knowledge, Factions, TEXT("crew"), TEXT("enemy"),
        TEXT("Foe"), TEXT("Ender"), Claw.SkillId, Claw,
        AfterSecondFoe, SecondFoeCue))) return false;
    FTSTSSBattleSkillState Recast;
    FTSTSSBattleSkillCue RecastCue;
    TestTrue(TEXT("spell cooldown expires after intervening actor turn"),
        FTSTSSBattleSkillSystem::TryUseRow(AfterSecondFoe, Knowledge, Factions,
        TEXT("crew"), TEXT("enemy"), TEXT("Ender"), TEXT("Foe"),
        Spark.SkillId, Spark, Recast, RecastCue));
    TestEqual(TEXT("successful recast advances actor count"),
        Recast.AcceptedTurnsByActor.FindRef(TEXT("Ender")), 3);
    return true;
}
#endif
