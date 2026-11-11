#include "Misc/AutomationTest.h"
#include "TSTSSPartySliceReviewEquipment.h"
#include "TSTSSPartyGearReviewMountComponent.h"
#include "TSTSSPartyGearMenuReviewWidget.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "UObject/UObjectGlobals.h"

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
    TestFalse(TEXT("splashdown is not proof Lyra has joined"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Splashdown, Lyra));
    TestTrue(TEXT("Lyra available only after distinct recruitment"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Recruited, Lyra));
    for (const FName Excluded : {FName(TEXT("Reson")), FName(TEXT("Aepex"))})
    {
        TestFalse(TEXT("excluded party member never available"),
            FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Recruited, Excluded));
    }

    FTSTSSReviewGearState Before, Sea, After;
    if (!TestTrue(TEXT("build First Wake gear from explicit review fixture"),
        FTSTSSPartySliceReviewEquipment::TryBuildEquippedReviewFixture(Opening, Before)))
        return false;
    TestEqual(TEXT("opening has two protagonists times three slots"),
        Before.OwnedInstances.Num(), 6);
    TestFalse(TEXT("Lyra owns no gear in opening fixture"),
        Before.EquippedByCharacter.Contains(Lyra));

    if (!TestTrue(TEXT("build splashdown gear independently"),
        FTSTSSPartySliceReviewEquipment::TryBuildEquippedReviewFixture(Splashdown, Sea)))
        return false;
    TestEqual(TEXT("splashdown alone grants no Lyra equipment"), Sea.OwnedInstances.Num(), 6);
    TestFalse(TEXT("Lyra remains unavailable before actual recruitment"),
        Sea.EquippedByCharacter.Contains(Lyra));

    FTSTSSReviewGearState Illegal;
    Illegal.EquippedByCharacter.Add(TEXT("Sentinel"), FTSTSSReviewGearSlots());
    TestFalse(TEXT("cannot equip Lyra's unavailable item"),
        FTSTSSReviewEquipment::TryEquip(Sea, Lyra,
            ETSTSSReviewGearSlot::Weapon, TEXT("Lyra.WaterFocus"), Illegal));
    TestTrue(TEXT("rejection preserves caller output state"),
        Illegal.EquippedByCharacter.Contains(TEXT("Sentinel")));

    if (!TestTrue(TEXT("build only after separate recruitment"),
        FTSTSSPartySliceReviewEquipment::TryBuildEquippedReviewFixture(Recruited, After)))
        return false;
    TestEqual(TEXT("after recruitment three protagonists times three slots"),
        After.OwnedInstances.Num(), 9);
    TestEqual(TEXT("only three active equipment owners"),
        After.EquippedByCharacter.Num(), 3);
    TestTrue(TEXT("Lyra owns her water focus after recruitment"),
        After.EquippedByCharacter.Contains(Lyra));
    TestFalse(TEXT("Reson never gets equipment slots"),
        After.EquippedByCharacter.Contains(TEXT("Reson")));
    TestFalse(TEXT("Aepex never gets equipment slots"),
        After.EquippedByCharacter.Contains(TEXT("Aepex")));
    TestFalse(TEXT("Ionia cannot equip Ender's staff"),
        FTSTSSReviewEquipment::TryEquip(After, Ionia,
            ETSTSSReviewGearSlot::Weapon, TEXT("Ender.ResonanceStaff"), Illegal));

    FTSTSSCombatant Base;
    Base.CharacterId = Ender;
    Base.Health = 20; Base.MaxHealth = 20;
    Base.Resource = 8; Base.MaxResource = 8;
    Base.Attack = 2; Base.Defense = 1;
    FTSTSSCombatant Captain = Base; Captain.CharacterId = Ionia;
    FTSTSSCombatant Healer = Base; Healer.CharacterId = Lyra;
    FTSTSSBattleSkillKnowledge Empty;
    TArray<FTSTSSCombatant> Roster;
    FTSTSSBattleSkillKnowledge Knowledge;
    if (!TestTrue(TEXT("equipped review items use existing battle ledger"),
        FTSTSSReviewEquipment::TryProjectAtBattleStart(
            After, {Base, Captain, Healer}, Empty, Roster, Knowledge)))
        return false;
    TestEqual(TEXT("Ender staff attack projection"), Roster[0].Attack, 5);
    TestEqual(TEXT("Ionia saber attack projection"), Roster[1].Attack, 4);
    TestEqual(TEXT("Lyra water focus attack projection"), Roster[2].Attack, 3);
    TestEqual(TEXT("Lyra coat plus pendant defense"), Roster[2].Defense, 4);
    TestEqual(TEXT("weapon class backed by owned review item"),
        Knowledge.WeaponClassByActor.FindRef(Lyra), FName(TEXT("Focus")));
    TestEqual(TEXT("base roster remains unchanged"), Base.Attack, 2);

    FTSTSSReviewGearState Sentinel = After;
    const auto InvalidStage = static_cast<ETSTSSPartySliceReviewStage>(99);
    TestFalse(TEXT("invalid review stage fails closed"),
        FTSTSSPartySliceReviewEquipment::TryBuildEquippedReviewFixture(
            InvalidStage, Sentinel));
    TestEqual(TEXT("invalid stage preserves caller output"), Sentinel.OwnedInstances.Num(), 9);
    TestFalse(TEXT("unknown stage cannot admit any character"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(InvalidStage, Ender));


    // Review UI uses the actual atomic ledger but NEVER grants, persists or
    // promotes equipment. It must reject Lyra in both story-only stages.
    FTSTSSReviewGearState UIUnequipped, UIEquipped;
    TestTrue(TEXT("review UI permits removing owned Ender staff"),
        UTSTSSPartyGearMenuReviewWidget::TryApplyReviewToggle(
            Before, Opening, Ender, ETSTSSReviewGearSlot::Weapon,
            false, UIUnequipped));
    const FTSTSSReviewGearSlots* UIBeforeSlots = Before.EquippedByCharacter.Find(Ender);
    const FTSTSSReviewGearSlots* UIAfterSlots = UIUnequipped.EquippedByCharacter.Find(Ender);
    if (!TestNotNull(TEXT("opening Ender ledger"), UIBeforeSlots) ||
        !TestNotNull(TEXT("UI after Ender ledger"), UIAfterSlots))
        return false;
    TestEqual(TEXT("review UI does not mutate source staff ownership"),
        UIBeforeSlots->WeaponInstance, FName(TEXT("Ender.ResonanceStaff")));
    TestTrue(TEXT("review UI unequip removes exactly weapon slot"),
        UIAfterSlots->WeaponInstance.IsNone());
    TestEqual(TEXT("review UI preserves armor slot"),
        UIBeforeSlots->ArmorInstance, UIAfterSlots->ArmorInstance);
    TestEqual(TEXT("review UI preserves accessory slot"),
        UIBeforeSlots->AccessoryInstance, UIAfterSlots->AccessoryInstance);
    TestTrue(TEXT("review UI re-equips originally owned staff"),
        UTSTSSPartyGearMenuReviewWidget::TryApplyReviewToggle(
            UIUnequipped, Opening, Ender, ETSTSSReviewGearSlot::Weapon,
            true, UIEquipped));
    TestEqual(TEXT("review UI restores same staff instance"),
        UIEquipped.EquippedByCharacter.FindChecked(Ender).WeaponInstance,
        FName(TEXT("Ender.ResonanceStaff")));

    FTSTSSReviewGearState UIInvalid;
    UIInvalid.EquippedByCharacter.Add(TEXT("Sentinel"), FTSTSSReviewGearSlots());
    TestFalse(TEXT("review UI cannot remove unowned Lyra gear in First Wake"),
        UTSTSSPartyGearMenuReviewWidget::TryApplyReviewToggle(
            Before, Opening, Lyra, ETSTSSReviewGearSlot::Weapon,
            false, UIInvalid));
    TestFalse(TEXT("review UI cannot equip Lyra gear at splashdown"),
        UTSTSSPartyGearMenuReviewWidget::TryApplyReviewToggle(
            Sea, Splashdown, Lyra, ETSTSSReviewGearSlot::Weapon,
            true, UIInvalid));
    TestFalse(TEXT("review UI cannot equip Aepex at any stage"),
        UTSTSSPartyGearMenuReviewWidget::TryApplyReviewToggle(
            After, Recruited, TEXT("Aepex"), ETSTSSReviewGearSlot::Weapon,
            true, UIInvalid));
    TestFalse(TEXT("review UI invalid slot fails closed"),
        UTSTSSPartyGearMenuReviewWidget::TryApplyReviewToggle(
            After, Recruited, Ionia, static_cast<ETSTSSReviewGearSlot>(99),
            false, UIInvalid));
    TestFalse(TEXT("review UI duplicate no-change denied"),
        UTSTSSPartyGearMenuReviewWidget::TryApplyReviewToggle(
            Before, Opening, Ender, ETSTSSReviewGearSlot::Weapon,
            true, UIInvalid));
    TestTrue(TEXT("review UI rejections preserve output sentinel"),
        UIInvalid.EquippedByCharacter.Contains(TEXT("Sentinel")));
    TestTrue(TEXT("review UI permits Lyra only after separate recruitment"),
        UTSTSSPartyGearMenuReviewWidget::TryApplyReviewToggle(
            After, Recruited, Lyra, ETSTSSReviewGearSlot::Weapon,
            false, UIInvalid));
    TestTrue(TEXT("recruited Lyra's weapon then cleared"),
        UIInvalid.EquippedByCharacter.FindChecked(Lyra).WeaponInstance.IsNone());

    // The ship console is intentionally non-authoritative. No selection
    // can grant or simulate a vessel transformation by using menu controls.
    for (FName ModeId : {FName(TEXT("Skyborne")), FName(TEXT("Seaborne")),
        FName(TEXT("Submersible")), FName(TEXT("Starbourne")),
        FName(TEXT("UnknownShipMode"))})
    {
        TestFalse(TEXT("ship menu may not execute an unauthorised mode change"),
            UTSTSSPartyGearMenuReviewWidget::IsShipConfigurationSelectableForReview(
                ModeId));
    }

    // Native package loading: these are real staged UE assets, not just GLBs.
    const TPair<FName,FString> ReviewedMeshes[] = {
        {Ender, TEXT("ResonanceStaff")},
        {Ender, TEXT("EngineersVest")},
        {Ender, TEXT("SealedAviatorGoggles")},
        {Ionia, TEXT("CaptainSaber")},
        {Ionia, TEXT("CaptainsCoat")},
        {Ionia, TEXT("EarthCompass")},
        {Lyra, TEXT("WaterFocus")},
        {Lyra, TEXT("TravelCoat")},
        {Lyra, TEXT("WaterPendant")}
    };
    for (const TPair<FName,FString>& Item : ReviewedMeshes)
    {
        const FString Owner = Item.Key.ToString();
        const FString Asset = Owner + TEXT("_") + Item.Value + TEXT("_REVIEW");
        const FString Path = FString::Printf(
            TEXT("/Game/TSTSS/Review/PartyEquipment/%s/%s/StaticMeshes/%s.%s"),
            *Owner, *Asset, *Asset, *Asset);
        UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *Path);
        if (!TestNotNull(*FString::Printf(TEXT("native mesh %s"), *Path), Mesh))
            return false;
        TestTrue(TEXT("native mesh has positive geometry bounds"),
            Mesh->GetBounds().SphereRadius > 0.f);
    }

    // Disposable world actor: review-only mounts are deliberately separate from
    // gameplay character rigs and do not alter the First Wake level or SaveGame.
    UWorld* World = nullptr;
    if (GEngine)
    {
        for (const FWorldContext& Context : GEngine->GetWorldContexts())
        {
            if (Context.World() &&
                (Context.WorldType == EWorldType::Editor ||
                 Context.WorldType == EWorldType::Game ||
                 Context.WorldType == EWorldType::PIE))
            {
                World = Context.World();
                break;
            }
        }
    }
    if (!TestNotNull(TEXT("native editor test world available for disposable gear actor"), World))
        return false;
    AActor* Stand = World->SpawnActor<AActor>();
    if (!TestNotNull(TEXT("spawn disposable preview actor"), Stand)) return false;

    UStaticMeshComponent* WeaponView = NewObject<UStaticMeshComponent>(Stand);
    UStaticMeshComponent* ArmorView = NewObject<UStaticMeshComponent>(Stand);
    UStaticMeshComponent* AccessoryView = NewObject<UStaticMeshComponent>(Stand);
    UTSTSSPartyGearReviewMountComponent* Mount =
        NewObject<UTSTSSPartyGearReviewMountComponent>(Stand);
    Stand->AddInstanceComponent(WeaponView);
    Stand->AddInstanceComponent(ArmorView);
    Stand->AddInstanceComponent(AccessoryView);
    Stand->AddInstanceComponent(Mount);
    WeaponView->RegisterComponent();
    ArmorView->RegisterComponent();
    AccessoryView->RegisterComponent();
    Mount->RegisterComponent();

    const bool bEnderShown = Mount->TryInitializeReviewDisplay(
        Ender, Opening, WeaponView, ArmorView, AccessoryView);
    TestTrue(TEXT("native Ender three-slot mesh preview initialized"), bEnderShown);
    if (bEnderShown)
    {
        TestNotNull(TEXT("weapon mesh actually mounted"), WeaponView->GetStaticMesh().Get());
        TestNotNull(TEXT("armor mesh actually mounted"), ArmorView->GetStaticMesh().Get());
        TestNotNull(TEXT("goggles mesh actually mounted"), AccessoryView->GetStaticMesh().Get());
        UStaticMesh* Original = WeaponView->GetStaticMesh();
        TestFalse(TEXT("Lyra denied at splashdown even in mounted review"),
            Mount->TryInitializeReviewDisplay(
                Lyra, Splashdown, WeaponView, ArmorView, AccessoryView));
        TestTrue(TEXT("denial preserves existing weapon mesh"),
            WeaponView->GetStaticMesh() == Original);
        TestFalse(TEXT("duplicate same-owner mounts denied"),
            Mount->TryInitializeReviewDisplay(
                Ender, Opening, WeaponView, WeaponView, AccessoryView));
        TestTrue(TEXT("unequip changes actual native component"),
            Mount->TrySetReviewSlotEquipped(ETSTSSPartyGearPreviewSlot::Weapon, false));
        TestTrue(TEXT("unequipped native component is empty"),
            WeaponView->GetStaticMesh() == nullptr);
        TestFalse(TEXT("cannot unequip the same item twice"),
            Mount->TrySetReviewSlotEquipped(ETSTSSPartyGearPreviewSlot::Weapon, false));
        TestTrue(TEXT("re-equip returns exact original native mesh"),
            Mount->TrySetReviewSlotEquipped(ETSTSSPartyGearPreviewSlot::Weapon, true));
        TestTrue(TEXT("re-equipped native mesh matches prior binding"),
            WeaponView->GetStaticMesh() == Original);
        TestTrue(TEXT("Lyra can mount only with explicit separate recruitment"),
            Mount->TryInitializeReviewDisplay(
                Lyra, Recruited, WeaponView, ArmorView, AccessoryView));
        TestEqual(TEXT("recruited Lyra owns her actual WaterFocus"),
            Mount->GetEquippedReviewItem(ETSTSSPartyGearPreviewSlot::Weapon),
            FName(TEXT("Lyra.WaterFocus")));
        TestFalse(TEXT("excluded Aepex cannot initialize a visual loadout"),
            Mount->TryInitializeReviewDisplay(
                TEXT("Aepex"), Recruited, WeaponView, ArmorView, AccessoryView));
    }
    // A static character study is not an animated/skeletal fit candidate.
    // No rig, fake socket, or visual asset can authorize a socket attachment.
    USkeletalMeshComponent* Unrigged = NewObject<USkeletalMeshComponent>(Stand);
    Stand->AddInstanceComponent(Unrigged);
    Unrigged->RegisterComponent();
    TestFalse(TEXT("missing skeletal mesh denies three socket mounts"),
        Mount->TryAttachToSkeletalSocketsReview(
            Unrigged, TEXT("hand_r"), TEXT("spine"), TEXT("head")));
    TestFalse(TEXT("null skeleton denies attachment"),
        Mount->TryAttachToSkeletalSocketsReview(
            nullptr, TEXT("hand_r"), TEXT("spine"), TEXT("head")));
    TestFalse(TEXT("duplicate socket identifiers deny attachment"),
        Mount->TryAttachToSkeletalSocketsReview(
            Unrigged, TEXT("hand_r"), TEXT("hand_r"), TEXT("head")));
    TestFalse(TEXT("no visual rig attachment can unlock Aepex"),
        FTSTSSPartySliceReviewEquipment::IsMemberAvailable(
            Recruited, TEXT("Aepex")));

    Stand->Destroy();
    return true;
}
#endif
