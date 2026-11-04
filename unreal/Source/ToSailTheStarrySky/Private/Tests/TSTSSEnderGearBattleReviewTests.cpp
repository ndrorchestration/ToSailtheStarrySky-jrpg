#include "Misc/AutomationTest.h"
#include "TSTSSReviewEquipment.h"
#include "TSTSSJobClassSystem.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSEnderGearBattleReviewTest,
    "TSTSS.CombatIntegration.EnderGearSpellBattleReview",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSEnderGearBattleReviewTest::RunTest(const FString& Parameters)
{
    // Every item and ability is a disposable test fixture, NOT canonical loot.
    const FName Ender(TEXT("Ender")), FoeId(TEXT("ReviewFoe"));
    FTSTSSReviewGearState Inventory;
    FTSTSSReviewGearInstance Staff;
    Staff.InstanceId = TEXT("ReviewStaffInstance");
    Staff.OwnerId = Ender;
    Staff.Slot = ETSTSSReviewGearSlot::Weapon;
    Staff.WeaponClass = TEXT("Staff");
    Staff.AttackBonus = 3;
    Inventory.OwnedInstances.Add(Staff.InstanceId, Staff);

    FTSTSSReviewGearInstance Vest;
    Vest.InstanceId = TEXT("ReviewVestInstance");
    Vest.OwnerId = Ender;
    Vest.Slot = ETSTSSReviewGearSlot::Armor;
    Vest.DefenseBonus = 4;
    Inventory.OwnedInstances.Add(Vest.InstanceId, Vest);

    FTSTSSReviewGearInstance IoniaArmor = Vest;
    IoniaArmor.InstanceId = TEXT("ReviewIoniaArmor");
    IoniaArmor.OwnerId = TEXT("Ionia");
    Inventory.OwnedInstances.Add(IoniaArmor.InstanceId, IoniaArmor);

    FTSTSSReviewGearState WithStaff;
    if (!TestTrue(TEXT("Ender equips an owned fighting staff"),
        FTSTSSReviewEquipment::TryEquip(Inventory, Ender,
            ETSTSSReviewGearSlot::Weapon, Staff.InstanceId, WithStaff))) return false;
    FTSTSSReviewGearState ReadyGear;
    if (!TestTrue(TEXT("Ender equips an owned review vest"),
        FTSTSSReviewEquipment::TryEquip(WithStaff, Ender,
            ETSTSSReviewGearSlot::Armor, Vest.InstanceId, ReadyGear))) return false;

    FTSTSSReviewGearState UntouchedOut;
    UntouchedOut.EquippedByCharacter.Add(TEXT("Sentinel"), FTSTSSReviewGearSlots());
    TestFalse(TEXT("cannot steal another protagonist's armor"),
        FTSTSSReviewEquipment::TryEquip(ReadyGear, Ender,
            ETSTSSReviewGearSlot::Armor, IoniaArmor.InstanceId, UntouchedOut));
    TestTrue(TEXT("rejected equip preserves caller output"),
        UntouchedOut.EquippedByCharacter.Contains(TEXT("Sentinel")));
    TestFalse(TEXT("weapon cannot occupy armor slot"),
        FTSTSSReviewEquipment::TryEquip(ReadyGear, Ender,
            ETSTSSReviewGearSlot::Armor, Staff.InstanceId, UntouchedOut));
    TestFalse(TEXT("repeating identical equip does not mint another item"),
        FTSTSSReviewEquipment::TryEquip(ReadyGear, Ender,
            ETSTSSReviewGearSlot::Weapon, Staff.InstanceId, UntouchedOut));

    FTSTSSCombatant BaseEnder;
    BaseEnder.CharacterId = Ender;
    BaseEnder.Health = 20; BaseEnder.MaxHealth = 20;
    BaseEnder.Resource = 12; BaseEnder.MaxResource = 12;
    BaseEnder.Attack = 2; BaseEnder.Defense = 1;
    FTSTSSCombatant Foe = BaseEnder;
    Foe.CharacterId = FoeId;
    Foe.Health = 40; Foe.MaxHealth = 40;
    Foe.Resource = 0; Foe.MaxResource = 0;
    Foe.Attack = 2; Foe.Defense = 1;

    FTSTSSBattleSkillKnowledge Knowledge;
    Knowledge.LearnedByActor.Add(Ender,
        TSet<FName>{TEXT("ReviewStaffStrike"), TEXT("ReviewStaffArc"), TEXT("ReviewLumenPulse")});
    Knowledge.LearnedByActor.Add(FoeId, TSet<FName>{TEXT("ReviewFoeClaw")});
    // Even a forged caller claim of a Staff cannot bypass the item ledger.
    Knowledge.WeaponClassByActor.Add(Ender, TEXT("Staff"));

    TArray<FTSTSSCombatant> NoGearRoster;
    FTSTSSBattleSkillKnowledge NoGearKnowledge;
    if (!TestTrue(TEXT("base roster can be projected without gear"),
        FTSTSSReviewEquipment::TryProjectAtBattleStart(
            Inventory, {BaseEnder, Foe}, Knowledge, NoGearRoster, NoGearKnowledge))) return false;
    TestFalse(TEXT("caller-supplied staff class is discarded without an owned equip"),
        NoGearKnowledge.WeaponClassByActor.Contains(Ender));
    TestEqual(TEXT("unequipped baseline attack unchanged"), NoGearRoster[0].Attack, 2);

    TArray<FTSTSSCombatant> Roster;
    FTSTSSBattleSkillKnowledge EquippedKnowledge;
    if (!TestTrue(TEXT("project equipped attack, defense and weapon-class together"),
        FTSTSSReviewEquipment::TryProjectAtBattleStart(
            ReadyGear, {BaseEnder, Foe}, Knowledge, Roster, EquippedKnowledge))) return false;
    TestEqual(TEXT("staff adds attack to baseline"), Roster[0].Attack, 5);
    TestEqual(TEXT("vest adds physical defense to baseline"), Roster[0].Defense, 5);
    TestEqual(TEXT("staff class has an inventory-backed source"),
        EquippedKnowledge.WeaponClassByActor.FindRef(Ender), FName(TEXT("Staff")));
    TestEqual(TEXT("original base remains unchanged"), BaseEnder.Attack, 2);

    FTSTSSBattleSkillRow Basic;
    Basic.SkillId = TEXT("ReviewStaffStrike");
    Basic.Kind = ETSTSSBattleSkillKind::WeaponTechnique;
    Basic.RequiredWeaponClass = TEXT("Staff");
    Basic.Power = 0;
    Basic.Admission = ETSTSSBattleSkillAdmission::ReviewExecutable;
    FTSTSSBattleSkillRow Arc = Basic;
    Arc.SkillId = TEXT("ReviewStaffArc");
    Arc.Power = 3; Arc.ResourceCost = 2;
    Arc.AnimationCueId = TEXT("Anim.Review.StaffArc");
    FTSTSSBattleSkillRow Pulse;
    Pulse.SkillId = TEXT("ReviewLumenPulse");
    Pulse.Kind = ETSTSSBattleSkillKind::Spell;
    Pulse.RequiredSchool = TEXT("Lumen");
    Pulse.RequiredMasteryRank = 1;
    Pulse.Power = 5; Pulse.ResourceCost = 3;
    Pulse.VfxCueId = TEXT("VFX.Review.LumenPulse");
    FTSTSSBattleSkillRow Claw;
    Claw.SkillId = TEXT("ReviewFoeClaw");
    Claw.Kind = ETSTSSBattleSkillKind::JobArt;
    Claw.Power = 2;
    Claw.Admission = ETSTSSBattleSkillAdmission::ReviewExecutable;

    TMap<FName, FName> Factions;
    Factions.Add(Ender, TEXT("crew"));
    Factions.Add(FoeId, TEXT("enemy"));
    FTSTSSBattleSkillState Start;
    if (!TestTrue(TEXT("start isolated two-participant review combat"),
        FTSTSSCombatTurns::TryBegin(Roster, {Ender, FoeId}, Start.Combat))) return false;

    FTSTSSBattleSkillState Denied;
    Denied.Combat.AcceptedActions = 99;
    FTSTSSBattleSkillCue DeniedCue;
    DeniedCue.SkillId = TEXT("KeepCue");
    TestFalse(TEXT("review staff action cannot execute without equipment"),
        FTSTSSBattleSkillSystem::TryUseRow(
            Start, NoGearKnowledge, Factions, TEXT("crew"), TEXT("enemy"),
            Ender, FoeId, Basic.SkillId, Basic, Denied, DeniedCue));
    TestEqual(TEXT("no new turn on bad weapon"), Denied.Combat.AcceptedActions, 99);
    TestEqual(TEXT("no cue changed on bad weapon"), DeniedCue.SkillId, FName(TEXT("KeepCue")));

    TestFalse(TEXT("DesignOnly spell is not a combat ability"),
        FTSTSSBattleSkillSystem::TryUseRow(
            Start, EquippedKnowledge, Factions, TEXT("crew"), TEXT("enemy"),
            Ender, FoeId, Pulse.SkillId, Pulse, Denied, DeniedCue));
    Pulse.Admission = ETSTSSBattleSkillAdmission::ReviewExecutable;
    TestFalse(TEXT("being Ender does not automatically grant Lumen mastery"),
        FTSTSSBattleSkillSystem::TryUseRow(
            Start, EquippedKnowledge, Factions, TEXT("crew"), TEXT("enemy"),
            Ender, FoeId, Pulse.SkillId, Pulse, Denied, DeniedCue));
    EquippedKnowledge.MasteryByActor.FindOrAdd(Ender).Add(TEXT("Lumen"), 1);

    // Job preview permission is another independent access gate, NOT a grant.
    FTSTSSJobLoadoutState Job;
    Job.CharacterId = Ender;
    Job.NativeProfession = TEXT("Rift Scholar");
    Job.PrimaryJob = TEXT("ReviewScholar");
    Job.LearnedSkillIds.Add(Pulse.SkillId);
    FTSTSSJobSkillPolicy Policy;
    Policy.SkillId = Pulse.SkillId; Policy.TrainedJobId = TEXT("ReviewGuard");
    TestFalse(TEXT("not trained in the current review job"),
        FTSTSSJobClassSystem::IsSkillEligibleForReview(Job, Policy));

    FTSTSSBattleSkillState AfterStrike, AfterFoe1, AfterArc, AfterFoe2, AfterPulse;
    FTSTSSBattleSkillCue StrikeCue, FoeCue1, ArcCue, FoeCue2, PulseCue;
    if (!TestTrue(TEXT("owned staff basic action resolves actual health"),
        FTSTSSBattleSkillSystem::TryUseRow(
            Start, EquippedKnowledge, Factions, TEXT("crew"), TEXT("enemy"),
            Ender, FoeId, Basic.SkillId, Basic, AfterStrike, StrikeCue))) return false;
    TestEqual(TEXT("weapon-stat damage used"), AfterStrike.Combat.Roster[1].Health, 35);
    if (!TestTrue(TEXT("foe turn resolves against equipped armor"),
        FTSTSSBattleSkillSystem::TryUseRow(
            AfterStrike, EquippedKnowledge, Factions, TEXT("crew"), TEXT("enemy"),
            FoeId, Ender, Claw.SkillId, Claw, AfterFoe1, FoeCue1))) return false;
    TestEqual(TEXT("vest reduces counterstrike to minimum damage"),
        AfterFoe1.Combat.Roster[0].Health, 19);

    if (!TestTrue(TEXT("explicitly equipped staff technique resolves"),
        FTSTSSBattleSkillSystem::TryUseRow(
            AfterFoe1, EquippedKnowledge, Factions, TEXT("crew"), TEXT("enemy"),
            Ender, FoeId, Arc.SkillId, Arc, AfterArc, ArcCue))) return false;
    TestEqual(TEXT("technique damage"), AfterArc.Combat.Roster[1].Health, 27);
    TestEqual(TEXT("technique costs resource"), AfterArc.Combat.Roster[0].Resource, 10);
    TestEqual(TEXT("accepted technique carries animation cue"),
        ArcCue.AnimationCueId, FName(TEXT("Anim.Review.StaffArc")));

    if (!TestTrue(TEXT("foe second turn"),
        FTSTSSBattleSkillSystem::TryUseRow(
            AfterArc, EquippedKnowledge, Factions, TEXT("crew"), TEXT("enemy"),
            FoeId, Ender, Claw.SkillId, Claw, AfterFoe2, FoeCue2))) return false;
    if (!TestTrue(TEXT("mastered and learned review spell executes on same authority"),
        FTSTSSBattleSkillSystem::TryUseRow(
            AfterFoe2, EquippedKnowledge, Factions, TEXT("crew"), TEXT("enemy"),
            Ender, FoeId, Pulse.SkillId, Pulse, AfterPulse, PulseCue))) return false;
    TestEqual(TEXT("spell effect uses existing combat power calculation"),
        AfterPulse.Combat.Roster[1].Health, 17);
    TestEqual(TEXT("spell cost deducted by turn authority"),
        AfterPulse.Combat.Roster[0].Resource, 7);
    TestEqual(TEXT("magic effect cue ID, not an actual Niagara emitter"),
        PulseCue.VfxCueId, FName(TEXT("VFX.Review.LumenPulse")));
    TestEqual(TEXT("all five actions recorded on one authority"),
        AfterPulse.Combat.AcceptedActions, 5);
    TestEqual(TEXT("three Ender turns accounted for"),
        AfterPulse.AcceptedTurnsByActor.FindRef(Ender), 3);
    TestEqual(TEXT("source combat was not mutated"), Start.Combat.AcceptedActions, 0);
    TestEqual(TEXT("source inventory remains owned"), ReadyGear.OwnedInstances.Num(), 3);
    return true;
}
#endif
