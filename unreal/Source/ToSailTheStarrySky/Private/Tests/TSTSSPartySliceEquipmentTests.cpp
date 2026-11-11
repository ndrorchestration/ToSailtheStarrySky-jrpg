#include "Misc/AutomationTest.h"
#include "TSTSSPartySliceReviewEquipment.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSPartySliceEquipmentStageGateTest,
    "TSTSS.Equipment.PartySliceStageGate",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSPartySliceEquipmentStageGateTest::RunTest(const FString& Parameters)
{
    const FName Ender(TEXT("Ender")), Ionia(TEXT("Ionia")), Lyra(TEXT("Lyra"));
    const auto Opening = ETSTSSPartySliceReviewStage::FirstWake;
    const auto Splashdown = ETSTSSPartySliceReviewStage::AfterSplashdown;
    const auto Recruited = ETSTSSPartySliceReviewStage::LyraRecruited;
    TestTrue(TEXT("Ender available on First Wake"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Opening, Ender));
    TestTrue(TEXT("Ionia available on First Wake"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Opening, Ionia));
    TestFalse(TEXT("Lyra not an opening-voyage party member"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Opening, Lyra));
    TestFalse(TEXT("Reson not a vertical-slice party member"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Splashdown, TEXT("Reson")));
    TestFalse(TEXT("Aepex not a vertical-slice party member"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Splashdown, TEXT("Aepex")));
    TestFalse(TEXT("Splashdown alone does not recruit Lyra"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Splashdown, Lyra));
    TestTrue(TEXT("Lyra becomes eligible only after distinct recruitment"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Recruited, Lyra));
    TestFalse(TEXT("Reson excluded after Lyra recruitment"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Recruited, TEXT("Reson")));
    TestFalse(TEXT("Aepex excluded after Lyra recruitment"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Recruited, TEXT("Aepex")));

    FTSTSSReviewGearState Before, Sea, After;
    if (!TestTrue(TEXT("build First Wake gear from explicit review fixture"),
        FTSTSSPartySliceReviewEquipment::TryBuildEquippedReviewFixture(Opening, Before)))
        return false;
    TestEqual(TEXT("opening has two protagonists times three slots"),
        Before.OwnedInstances.Num(), 6);
    TestFalse(TEXT("Lyra owns no gear in opening fixture"),
        Before.EquippedByCharacter.Contains(Lyra));
    if (!TestTrue(TEXT("build splashdown fixture separately from recruitment"),
        FTSTSSPartySliceReviewEquipment::TryBuildEquippedReviewFixture(Splashdown, Sea)))
        return false;
    TestEqual(TEXT("splashdown without recruitment has only Ender and Ionia equipment"),
        Sea.OwnedInstances.Num(), 6);
    TestFalse(TEXT("splashdown does not grant Lyra equipment"),
        Sea.EquippedByCharacter.Contains(Lyra));
    FTSTSSReviewGearState Illegal;
    Illegal.EquippedByCharacter.Add(TEXT("Sentinel"), FTSTSSReviewGearSlots());
    TestFalse(TEXT("cannot equip Lyra's unavailable item"),
        FTSTSSReviewEquipment::TryEquip(Before, Lyra,
            ETSTSSReviewGearSlot::Weapon,TEXT("Lyra.WaterFocus"),Illegal));
    TestTrue(TEXT("rejection preserves output state"),
        Illegal.EquippedByCharacter.Contains(TEXT("Sentinel")));

    if (!TestTrue(TEXT("build post-recruitment gear fixture"),
        FTSTSSPartySliceReviewEquipment::TryBuildEquippedReviewFixture(Recruited, After)))
        return false;
    TestEqual(TEXT("after Lyra recruitment exactly three protagonists times three slots"),
        After.OwnedInstances.Num(), 9);
    TestEqual(TEXT("only three active equipment owners"),
        After.EquippedByCharacter.Num(), 3);
    TestTrue(TEXT("Lyra gets her owned water focus only after recruitment"),
        After.EquippedByCharacter.Contains(Lyra));
    TestFalse(TEXT("Reson never receives an equipment slot"),
        After.EquippedByCharacter.Contains(TEXT("Reson")));
    TestFalse(TEXT("Aepex never receives an equipment slot"),
        After.EquippedByCharacter.Contains(TEXT("Aepex")));
    TestFalse(TEXT("Ionia cannot equip Ender's staff"),
        FTSTSSReviewEquipment::TryEquip(After, Ionia,
            ETSTSSReviewGearSlot::Weapon,TEXT("Ender.ResonanceStaff"),Illegal));

    FTSTSSCombatant Base;
    Base.CharacterId=Ender;
    Base.Health=20; Base.MaxHealth=20;
    Base.Resource=8; Base.MaxResource=8;
    Base.Attack=2; Base.Defense=1;
    FTSTSSCombatant Captain=Base; Captain.CharacterId=Ionia;
    FTSTSSCombatant Healer=Base; Healer.CharacterId=Lyra;
    FTSTSSBattleSkillKnowledge Empty;
    TArray<FTSTSSCombatant> Roster;
    FTSTSSBattleSkillKnowledge Knowledge;
    if (!TestTrue(TEXT("review gear projects to existing combat ledger"),
        FTSTSSReviewEquipment::TryProjectAtBattleStart(
            After,{Base,Captain,Healer},Empty,Roster,Knowledge)))
        return false;
    TestEqual(TEXT("Ender staff attack projection"), Roster[0].Attack, 5);
    TestEqual(TEXT("Ionia saber attack projection"), Roster[1].Attack, 4);
    TestEqual(TEXT("Lyra water focus attack projection"), Roster[2].Attack, 3);
    TestEqual(TEXT("Lyra coat plus pendant defense"), Roster[2].Defense, 4);
    TestEqual(TEXT("source class is owned equipment, not caller claim"),
        Knowledge.WeaponClassByActor.FindRef(Lyra), FName(TEXT("Focus")));
    TestEqual(TEXT("original character attack unchanged"), Base.Attack, 2);

    FTSTSSReviewGearState Sentinel = After;
    const auto InvalidStage = static_cast<ETSTSSPartySliceReviewStage>(99);
    TestFalse(TEXT("invalid recruitment stage must fail closed"),
        FTSTSSPartySliceReviewEquipment::TryBuildEquippedReviewFixture(
            InvalidStage, Sentinel));
    TestEqual(TEXT("invalid stage preserves output"),
        Sentinel.OwnedInstances.Num(), 9);
    return true;
}
#endif
