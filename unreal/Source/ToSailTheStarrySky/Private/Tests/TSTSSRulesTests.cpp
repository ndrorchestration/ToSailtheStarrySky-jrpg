#include "Misc/AutomationTest.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSCombatRules.h"
#include "TSTSSSaveGame.h"
#include "TSTSSPersistence.h"
#include "TSTSSWaterLandingGate.h"
#include "Kismet/GameplayStatics.h"

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSFirstWakeOrderTest,
    "TSTSS.FirstWake.RequiresOrderedMilestones",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSFirstWakeOrderTest::RunTest(const FString& Parameters)
{
    UTSTSSFirstWakeState* State = NewObject<UTSTSSFirstWakeState>();
    TestFalse(TEXT("Cannot skip directly to boarding"), State->AdvanceTo(ETSTSSFirstWakeBeat::BoardedAureateWake));
    TestTrue(TEXT("Starts with flyer"), State->AdvanceTo(ETSTSSFirstWakeBeat::FlyerDiscovered));
    TestFalse(TEXT("Cannot repeat flyer"), State->AdvanceTo(ETSTSSFirstWakeBeat::FlyerDiscovered));
    TestTrue(TEXT("Ionia hired next"), State->AdvanceTo(ETSTSSFirstWakeBeat::IoniaHired));
    TestFalse(TEXT("Cannot skip checks and launch"), State->AdvanceTo(ETSTSSFirstWakeBeat::SeaContact));
    State->Reset();
    TestFalse(TEXT("Reset clears started state"), State->HasStarted());
    TestFalse(TEXT("Reject impossible unstarted saved milestone"),
        State->Restore(false, ETSTSSFirstWakeBeat::Launched));
    TestTrue(TEXT("Restore valid progressed story"),
        State->Restore(true, ETSTSSFirstWakeBeat::EngineeringChecked, 0x07));
    TestEqual(TEXT("Restored beat matches save"),
        State->GetCurrentBeat(), ETSTSSFirstWakeBeat::EngineeringChecked);
    TestFalse(TEXT("Cannot skip from restored beat"),
        State->AdvanceTo(ETSTSSFirstWakeBeat::FlotationConfirmed));
    TestTrue(TEXT("Continue from restored beat"),
        State->AdvanceTo(ETSTSSFirstWakeBeat::Launched));
    TestFalse(TEXT("Generic progression cannot forge sea contact"),
        State->AdvanceTo(ETSTSSFirstWakeBeat::SeaContact));
    TestFalse(TEXT("Prelude stays active before splashdown"), State->IsChapterOneActOne());
    TestTrue(TEXT("Restored splashdown marks Chapter 1 Act 1"),
        State->Restore(true, ETSTSSFirstWakeBeat::FlotationConfirmed, 0x07));
    TestTrue(TEXT("Chapter 1 boundary survives save restoration"), State->IsChapterOneActOne());
    TestTrue(TEXT("Post-splashdown reserve inspection advances in Chapter 1"),
        State->AdvanceTo(ETSTSSFirstWakeBeat::EmptyReserveInspected));
    TestTrue(TEXT("Chapter 1 remains active during recovery"), State->IsChapterOneActOne());
    State->Reset();
    TestFalse(TEXT("New game returns to Prelude"), State->IsChapterOneActOne());
    State->Reset();
    TestTrue(TEXT("Start flyer"), State->AdvanceTo(ETSTSSFirstWakeBeat::FlyerDiscovered));
    TestTrue(TEXT("Hire Ionia"), State->AdvanceTo(ETSTSSFirstWakeBeat::IoniaHired));
    TestTrue(TEXT("Board"), State->AdvanceTo(ETSTSSFirstWakeBeat::BoardedAureateWake));
    TestFalse(TEXT("Engineering blocked without inspections"), State->AdvanceTo(ETSTSSFirstWakeBeat::EngineeringChecked));
    TestTrue(TEXT("Lift inspection"), State->InspectStation(ETSTSSInspectionStation::Lift));
    TestFalse(TEXT("Duplicate lift rejected"), State->InspectStation(ETSTSSInspectionStation::Lift));
    TestTrue(TEXT("Pressure inspection"), State->InspectStation(ETSTSSInspectionStation::Pressure));
    TestFalse(TEXT("Still missing reserve"), State->AdvanceTo(ETSTSSFirstWakeBeat::EngineeringChecked));
    TestTrue(TEXT("Reserve inspection"), State->InspectStation(ETSTSSInspectionStation::Reserve));
    TestTrue(TEXT("Engineering signoff after all checks"), State->AdvanceTo(ETSTSSFirstWakeBeat::EngineeringChecked));
    TestFalse(TEXT("No late inspection"), State->InspectStation(ETSTSSInspectionStation::Reserve));
    TestFalse(TEXT("Reject missing inspection evidence on restore"), State->Restore(true, ETSTSSFirstWakeBeat::Launched, 0));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSCombatAtomicTest,
    "TSTSS.Combat.TransactionalActions",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSCombatAtomicTest::RunTest(const FString& Parameters)
{
    FTSTSSCombatant Ender;
    Ender.CharacterId = TEXT("Ender");
    Ender.Health = 6; Ender.MaxHealth = 20;
    Ender.Resource = 5; Ender.MaxResource = 10;
    Ender.Attack = 4;
    FTSTSSCombatant Ionia;
    Ionia.CharacterId = TEXT("Ionia");
    Ionia.Health = 15; Ionia.MaxHealth = 20;
    Ionia.Resource = 4; Ionia.MaxResource = 10;
    Ionia.Attack = 3; Ionia.Defense = 2;
    const TArray<FTSTSSCombatant> Initial{Ender, Ionia};
    TArray<FTSTSSCombatant> After;
    FTSTSSCombatAction Action;
    Action.ActorId = TEXT("Ender");
    Action.TargetId = TEXT("Ender");
    Action.ResourceCost = 2;
    Action.Power = 3;
    Action.bHealing = true;
    if (!TestTrue(TEXT("Self-heal is legal"), UTSTSSCombatRules::TryApplyAction(Initial, Action, After))) return false;
    if (!TestEqual(TEXT("Self-heal output roster size"), After.Num(), 2)) return false;
    TestEqual(TEXT("Self-heal applies resource"), After[0].Resource, 3);
    TestEqual(TEXT("Self-heal applies healing"), After[0].Health, 13);
    TestEqual(TEXT("Initial remains untouched"), Initial[0].Health, 6);
    Action.ResourceCost = 99;
    const int32 PriorHealth = After[0].Health;
    TestFalse(TEXT("Unaffordable action rejected"), UTSTSSCombatRules::TryApplyAction(Initial, Action, After));
    TestEqual(TEXT("Rejected action leaves output unchanged"), After[0].Health, PriorHealth);
    Action.ResourceCost = 1;
    Action.bHealing = false;
    Action.TargetId = TEXT("Ionia");
    if (!TestTrue(TEXT("Valid damage"), UTSTSSCombatRules::TryApplyAction(Initial, Action, After))) return false;
    if (!TestEqual(TEXT("Damage output roster size"), After.Num(), 2)) return false;
    TestEqual(TEXT("Defense accounted for"), After[1].Health, 10);
    return true;
}

// Regression coverage for the UE-side atomic resolver migrated from the Godot study.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSCombatRejectionTest,
    "TSTSS.Combat.RejectsInvalidActionsWithoutMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSCombatRejectionTest::RunTest(const FString& Parameters)
{
    FTSTSSCombatant Ender;
    Ender.CharacterId = TEXT("Ender");
    Ender.Health = 12; Ender.MaxHealth = 20;
    Ender.Resource = 3; Ender.MaxResource = 5;
    Ender.Attack = 2;

    FTSTSSCombatant Foe;
    Foe.CharacterId = TEXT("Foe");
    Foe.Health = 10; Foe.MaxHealth = 10;
    Foe.Resource = 0; Foe.MaxResource = 0;
    const TArray<FTSTSSCombatant> Initial{Ender, Foe};
    TArray<FTSTSSCombatant> Output = Initial;
    FTSTSSCombatAction Action;
    Action.ActorId = TEXT("Ender");
    Action.TargetId = TEXT("Foe");
    Action.Power = 2;

    Action.ResourceCost = 4;
    TestFalse(TEXT("Unaffordable action is rejected"), UTSTSSCombatRules::TryApplyAction(Initial, Action, Output));
    TestEqual(TEXT("Rejected action preserves output HP"), Output[1].Health, 10);
    TestEqual(TEXT("Rejected action preserves output resources"), Output[0].Resource, 3);

    Action.ResourceCost = 0;
    Action.TargetId = TEXT("Missing");
    TestFalse(TEXT("Unknown target is rejected"), UTSTSSCombatRules::TryApplyAction(Initial, Action, Output));
    TestEqual(TEXT("Unknown target preserves output"), Output[1].Health, 10);

    Action.TargetId = TEXT("Foe");
    Action.Power = -1;
    TestFalse(TEXT("Negative power is rejected"), UTSTSSCombatRules::TryApplyAction(Initial, Action, Output));
    Action.Power = 2;

    TArray<FTSTSSCombatant> Duplicates{Ender, Ender, Foe};
    TestFalse(TEXT("Duplicate roster IDs are rejected"), UTSTSSCombatRules::TryApplyAction(Duplicates, Action, Output));
    TestEqual(TEXT("Duplicate roster rejection preserves output size"), Output.Num(), 2);
    TestEqual(TEXT("Input roster remains unchanged"), Initial[1].Health, 10);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSSaveValidationTest,
    "TSTSS.Save.RejectsUnsupportedSchema",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSSaveValidationTest::RunTest(const FString& Parameters)
{
    UTSTSSSaveGame* Save = NewObject<UTSTSSSaveGame>();
    TestTrue(TEXT("Default save is structurally valid"), Save->IsStructurallyValid());
    Save->SchemaVersion = 999;
    TestFalse(TEXT("Future schema is rejected"), Save->IsStructurallyValid());
    Save->SchemaVersion = UTSTSSSaveGame::CurrentVersion;
    Save->FirstWakeBeat = ETSTSSFirstWakeBeat::Launched;
    TestFalse(TEXT("Unstarted late milestone is rejected"), Save->IsStructurallyValid());
    Save->bFirstWakeStarted = true;
    Save->InspectionMask = 0x07;
    TestTrue(TEXT("Valid inspected launch save accepted"), Save->IsStructurallyValid());
    Save->InspectionMask = 0x03;
    TestFalse(TEXT("Partial inspections cannot restore a launch"), Save->IsStructurallyValid());
    Save->InspectionMask = 0xFF;
    TestFalse(TEXT("Unknown inspection bits rejected"), Save->IsStructurallyValid());
    Save->InspectionMask = 0x07;
    FTSTSSCombatant Stranger;
    Stranger.CharacterId = TEXT("NotACanonicalCharacter");
    Save->PartyRoster.Add(Stranger);
    TestFalse(TEXT("Unknown party identity rejected"), Save->IsStructurallyValid());
    Save->PartyRoster.Reset();
    for (const TCHAR* Id : {TEXT("Ender"), TEXT("Ionia"), TEXT("Lyra"), TEXT("Reson"), TEXT("Aepex")})
    {
        FTSTSSCombatant Member;
        Member.CharacterId = FName(Id);
        Save->PartyRoster.Add(Member);
    }
    TestTrue(TEXT("Five valid identities accepted"), Save->IsStructurallyValid());
    Save->PartyRoster.Add(Save->PartyRoster[0]);
    TestFalse(TEXT("Oversized roster rejected"), Save->IsStructurallyValid());
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSSaveSlotGuardTest,
    "TSTSS.Save.RejectsUnsafeSlots",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSSaveSlotGuardTest::RunTest(const FString& Parameters)
{
    TestTrue(TEXT("Safe slot accepted"), UTSTSSPersistence::IsValidSlotName(TEXT("first_wake_01")));
    TestFalse(TEXT("Path traversal rejected"), UTSTSSPersistence::IsValidSlotName(TEXT("../escape")));
    TestFalse(TEXT("Empty slot rejected"), UTSTSSPersistence::IsValidSlotName(TEXT("")));
    TestFalse(TEXT("Slash rejected"), UTSTSSPersistence::IsValidSlotName(TEXT("a/b")));
    TestFalse(TEXT("Spaces rejected"), UTSTSSPersistence::IsValidSlotName(TEXT("my save")));
    TestFalse(TEXT("Non-ASCII slot rejected"), UTSTSSPersistence::IsValidSlotName(FString::Chr(233)));
    TestFalse(TEXT("Long slot rejected"), UTSTSSPersistence::IsValidSlotName(FString::ChrN(49, TEXT('a'))));
    TestTrue(TEXT("Missing invalid slot returns null"), UTSTSSPersistence::LoadProgress(TEXT("../escape")) == nullptr);
    UTSTSSSaveGame* Save = NewObject<UTSTSSSaveGame>();
    Save->SchemaVersion = 99;
    TestFalse(TEXT("Invalid payload write rejected"), UTSTSSPersistence::SaveProgress(TEXT("test_slot"), Save));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSSaveRoundTripTest,
    "TSTSS.Save.RoundTripFirstWakeAndParty",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSSaveRoundTripTest::RunTest(const FString& Parameters)
{
    // Dedicated test slot; never overwrite a player's normal slot.
    const FString Slot = TEXT("tstss_automation_roundtrip_v1");
    if (UGameplayStatics::DoesSaveGameExist(Slot, 0))
    {
        AddError(TEXT("Test slot already exists; refusing to overwrite it"));
        return false;
    }
    UTSTSSSaveGame* Original = NewObject<UTSTSSSaveGame>();
    Original->bFirstWakeStarted = true;
    Original->FirstWakeBeat = ETSTSSFirstWakeBeat::EngineeringChecked;
    Original->InspectionMask = 0x07;
    FTSTSSCombatant Ender;
    Ender.CharacterId = TEXT("Ender");
    Ender.Health = 14; Ender.MaxHealth = 20;
    Ender.Resource = 4; Ender.MaxResource = 9;
    Ender.Attack = 3; Ender.Defense = 2;
    Original->PartyRoster.Add(Ender);
    if (!TestTrue(TEXT("Save succeeds"), UTSTSSPersistence::SaveProgress(Slot, Original)))
    {
        return false;
    }
    const UTSTSSSaveGame* Loaded = UTSTSSPersistence::LoadProgress(Slot);
    const bool bLoaded = TestNotNull(TEXT("Valid save reloads"), Loaded);
    if (bLoaded)
    {
        TestEqual(TEXT("Schema version preserved"), Loaded->SchemaVersion, UTSTSSSaveGame::CurrentVersion);
        TestTrue(TEXT("Started state preserved"), Loaded->bFirstWakeStarted);
        TestEqual(TEXT("First Wake milestone preserved"), Loaded->FirstWakeBeat, ETSTSSFirstWakeBeat::EngineeringChecked);
        TestEqual(TEXT("Inspection evidence preserved"), Loaded->InspectionMask, static_cast<uint8>(0x07));
        TestEqual(TEXT("Party size preserved"), Loaded->PartyRoster.Num(), 1);
        if (Loaded->PartyRoster.Num() == 1)
        {
            TestEqual(TEXT("Character ID preserved"), Loaded->PartyRoster[0].CharacterId, FName(TEXT("Ender")));
            TestEqual(TEXT("Health preserved"), Loaded->PartyRoster[0].Health, 14);
            TestEqual(TEXT("Resources preserved"), Loaded->PartyRoster[0].Resource, 4);
        }
    }
    TestTrue(TEXT("Test slot cleaned up"), UGameplayStatics::DeleteGameInSlot(Slot, 0));
    return bLoaded;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSWaterLandingTest,
    "TSTSS.FirstWake.WaterLandingRequiresMeasuredStability",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSWaterLandingTest::RunTest(const FString& Parameters)
{
    UTSTSSFirstWakeState* Story = NewObject<UTSTSSFirstWakeState>();
    UTSTSSWaterLandingGate* Gate = NewObject<UTSTSSWaterLandingGate>();
    Story->Restore(true, ETSTSSFirstWakeBeat::Launched, 0x07);
    TestFalse(TEXT("No water contact"), Gate->Observe(0.1f, false, 0.f, Story));
    TestEqual(TEXT("Unchanged without collision"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::Launched);
    TestFalse(TEXT("Impact is not stable flotation"), Gate->Observe(0.1f, true, 180.f, Story));
    TestEqual(TEXT("Collision records contact"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    for (int32 Step = 0; Step < 10; ++Step) Gate->Observe(0.1f, true, 5.f, Story);
    TestFalse(TEXT("Invalid delta rejected"), Gate->Observe(-0.1f, true, 5.f, Story));
    TestEqual(TEXT("Invalid observation clears stability timer"), Gate->GetStableContactSeconds(), 0.f);
    for (int32 Step = 0; Step < 10; ++Step) Gate->Observe(0.1f, true, 5.f, Story);
    TestFalse(TEXT("Losing overlap clears timer"), Gate->Observe(0.1f, false, 0.f, Story));
    TestEqual(TEXT("Contact reset does not undo established story contact"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    TestEqual(TEXT("Contact gap resets stable seconds"), Gate->GetStableContactSeconds(), 0.f);
    TestEqual(TEXT("Brief contact is insufficient"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    bool bConfirmed = false;
    for (int32 Step = 0; Step < 21; ++Step)
        bConfirmed |= Gate->Observe(0.1f, true, 5.f, Story);
    TestTrue(TEXT("Sustained stable overlap confirms flotation"), bConfirmed);
    TestEqual(TEXT("Flotation beat recorded"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::FlotationConfirmed);
    return true;
}
#endif
