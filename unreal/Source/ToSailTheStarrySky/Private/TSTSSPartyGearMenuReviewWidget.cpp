#include "TSTSSPartyGearMenuReviewWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/ScrollBox.h"
#include "Components/SizeBox.h"
#include "TSTSSCombatData.h"
#include "TSTSSJobClassSystem.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSSaveGame.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/HUD.h"
#include "Engine/Engine.h"

namespace
{
    FName ReviewOwner(int32 Index)
    {
        switch (Index)
        {
        case 0: return TEXT("Ender");
        case 1: return TEXT("Ionia");
        case 2: return TEXT("Lyra");
        default: return NAME_None;
        }
    }

    ETSTSSReviewGearSlot ReviewSlot(int32 Index)
    {
        switch (Index)
        {
        case 0: return ETSTSSReviewGearSlot::Weapon;
        case 1: return ETSTSSReviewGearSlot::Armor;
        case 2: return ETSTSSReviewGearSlot::Accessory;
        default: return static_cast<ETSTSSReviewGearSlot>(255);
        }
    }

    FName SlotValue(const FTSTSSReviewGearSlots& Slots, ETSTSSReviewGearSlot Slot)
    {
        switch (Slot)
        {
        case ETSTSSReviewGearSlot::Weapon: return Slots.WeaponInstance;
        case ETSTSSReviewGearSlot::Armor: return Slots.ArmorInstance;
        case ETSTSSReviewGearSlot::Accessory: return Slots.AccessoryInstance;
        default: return NAME_None;
        }
    }

    const TCHAR* SlotName(ETSTSSReviewGearSlot Slot)
    {
        switch (Slot)
        {
        case ETSTSSReviewGearSlot::Weapon: return TEXT("WEAPON");
        case ETSTSSReviewGearSlot::Armor: return TEXT("ARMOR");
        case ETSTSSReviewGearSlot::Accessory: return TEXT("ACCESSORY");
        default: return TEXT("INVALID");
        }
    }

    UTextBlock* AddReviewText(UWidgetTree* Tree, UVerticalBox* Column,
        const FString& Copy, int32 Size, const FLinearColor& Color, float Bottom)
    {
        if (!Tree || !Column) return nullptr;
        UTextBlock* Text = Tree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
        if (!Text) return nullptr;
        Text->SetText(FText::FromString(Copy));
        Text->SetColorAndOpacity(FSlateColor(Color));
        FSlateFontInfo Font = Text->GetFont();
        Font.Size = Size;
        Text->SetFont(Font);
        Text->SetAutoWrapText(true);
        Column->AddChildToVerticalBox(Text)->SetPadding(FMargin(0.f, 0.f, 0.f, Bottom));
        return Text;
    }
}

bool UTSTSSPartyGearMenuReviewWidget::TryApplyReviewToggle(
    const FTSTSSReviewGearState& State,
    ETSTSSPartySliceReviewStage Stage,
    FName CharacterId,
    ETSTSSReviewGearSlot Slot,
    bool bEquip,
    FTSTSSReviewGearState& OutState)
{
    if (!FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Stage, CharacterId))
        return false;
    if (Slot != ETSTSSReviewGearSlot::Weapon &&
        Slot != ETSTSSReviewGearSlot::Armor &&
        Slot != ETSTSSReviewGearSlot::Accessory)
        return false;

    const FTSTSSReviewGearSlots* Equipped = State.EquippedByCharacter.Find(CharacterId);
    if (!Equipped) return false;
    const FName Current = SlotValue(*Equipped, Slot);
    FName Desired = NAME_None;

    if (bEquip)
    {
        // Only previously owned, single-matching equipment can be re-equipped.
        // No unknown item ID, trade or story grant is accepted.
        for (const TPair<FName, FTSTSSReviewGearInstance>& Owned : State.OwnedInstances)
        {
            if (Owned.Value.OwnerId == CharacterId && Owned.Value.Slot == Slot)
            {
                if (!Desired.IsNone()) return false; // ambiguous owned slot
                Desired = Owned.Key;
            }
        }
        if (Desired.IsNone()) return false;
    }

    if (Current == Desired) return false;
    return FTSTSSReviewEquipment::TryEquip(
        State, CharacterId, Slot, Desired, OutState);
}

bool UTSTSSPartyGearMenuReviewWidget::TryBeginEquipmentReview(
    ETSTSSPartySliceReviewStage Stage)
{
    FTSTSSReviewGearState Candidate;
    if (!FTSTSSPartySliceReviewEquipment::TryBuildEquippedReviewFixture(
        Stage, Candidate))
    {
        return false;
    }
    ReviewState = MoveTemp(Candidate);
    ActiveStage = Stage;
    bInitialized = true;
    ActivePage = ETSTSSReviewMenuPage::Equipment;
    RenderReviewPage();
    return true;
}

bool UTSTSSPartyGearMenuReviewWidget::TryRefreshStoryStageReview(
    ETSTSSPartySliceReviewStage RequestedStage)
{
    if (!bInitialized) return false;
    if (ActiveStage == RequestedStage) return true;
    // The real saved First Wake story may advance OR rewind on quickload.
    // Neither transition is the separate Lyra recruitment event. Never
    // admit LyraRecruited from this display-only projection.
    const bool bWasPreviewStage =
        ActiveStage == ETSTSSPartySliceReviewStage::FirstWake ||
        ActiveStage == ETSTSSPartySliceReviewStage::AfterSplashdown;
    const bool bIsPreviewStage =
        RequestedStage == ETSTSSPartySliceReviewStage::FirstWake ||
        RequestedStage == ETSTSSPartySliceReviewStage::AfterSplashdown;
    if (!bWasPreviewStage || !bIsPreviewStage) return false;
    ActiveStage = RequestedStage;
    // A saved snapshot must be rebound only if it still matches story stage.
    LoadedSavedRosterSnapshot.Reset();
    bHasValidLoadedRosterSnapshot = false;
    RenderReviewPage();
    return true;
}


bool UTSTSSPartyGearMenuReviewWidget::TryProjectValidatedSavedRosterForReview(
    const UTSTSSSaveGame* Save,
    ETSTSSPartySliceReviewStage Stage,
    TArray<FTSTSSCombatant>& OutRoster)
{
    if (!IsValid(Save) || !Save->IsStructurallyValid() ||
        !Save->bFirstWakeStarted || Save->PartyRoster.IsEmpty() ||
        (Stage != ETSTSSPartySliceReviewStage::FirstWake &&
         Stage != ETSTSSPartySliceReviewStage::AfterSplashdown))
        return false;

    // A splashdown beat is not the separate Lyra recruitment receipt.
    // Never surface a future-party member from a save in First Wake.
    const bool bSavedAfterSplashdown =
        static_cast<uint8>(Save->FirstWakeBeat) >=
        static_cast<uint8>(ETSTSSFirstWakeBeat::FlotationConfirmed);
    if (bSavedAfterSplashdown !=
        (Stage == ETSTSSPartySliceReviewStage::AfterSplashdown))
        return false;
    for (const FTSTSSCombatant& Member : Save->PartyRoster)
    {
        if (!FTSTSSPartySliceReviewEquipment::IsMemberAvailable(
                Stage, Member.CharacterId))
            return false;
    }
    OutRoster = Save->PartyRoster;
    return true;
}

bool UTSTSSPartyGearMenuReviewWidget::TryBindLoadedSaveRosterForReview(
    const UTSTSSSaveGame* Save)
{
    if (!bInitialized || !IsValid(StoryReviewState) || !IsValid(Save) ||
        StoryReviewState->HasStarted() != Save->bFirstWakeStarted ||
        StoryReviewState->GetCurrentBeat() != Save->FirstWakeBeat ||
        StoryReviewState->GetInspectionMask() != Save->InspectionMask)
        return false;
    TArray<FTSTSSCombatant> Candidate;
    if (!TryProjectValidatedSavedRosterForReview(
            Save, ActiveStage, Candidate))
        return false;
    LoadedSavedRosterSnapshot = MoveTemp(Candidate);
    bHasValidLoadedRosterSnapshot = true;
    RenderReviewPage();
    return true;
}

void UTSTSSPartyGearMenuReviewWidget::ClearLoadedSaveRosterForReview()
{
    LoadedSavedRosterSnapshot.Reset();
    bHasValidLoadedRosterSnapshot = false;
    RenderReviewPage();
}

bool UTSTSSPartyGearMenuReviewWidget::TryBindFirstWakeStoryForReview(
    UTSTSSFirstWakeState* State)
{
    if (!bInitialized || !IsValid(State)) return false;
    StoryReviewState = State;
    RenderReviewPage();
    return true;
}

bool UTSTSSPartyGearMenuReviewWidget::IsShipConfigurationSelectableForReview(
    FName ConfigurationId)
{
    // Story milestone != permission to drive a future ship configuration.
    // No ship config is presently connected to an authenticated gameplay gate.
    (void)ConfigurationId;
    return false;
}

void UTSTSSPartyGearMenuReviewWidget::OpenPageForReview(
    ETSTSSReviewMenuPage Page)
{
    if (!bInitialized || Page > ETSTSSReviewMenuPage::System) return;
    ActivePage = Page;
    RenderReviewPage();
}

void UTSTSSPartyGearMenuReviewWidget::ChangeShipPage(
    ETSTSSShipReviewPage Page)
{
    if (!bInitialized || Page > ETSTSSShipReviewPage::Cargo) return;
    ActiveShipPage = Page;
    ActivePage = ETSTSSReviewMenuPage::Ship;
    RenderReviewPage();
}

void UTSTSSPartyGearMenuReviewWidget::SuspendReviewScreenWarnings()
{
#if !UE_BUILD_SHIPPING
    // Engine developer overlays render AFTER UMG and otherwise obscure
    // the user's menu. Restore both process-local flags on close.
    if (!GEngine) return;
    if (GEngine->bEnableOnScreenDebugMessagesDisplay)
    {
        bRestoreOnScreenMessagesAfterClose = true;
        GEngine->bEnableOnScreenDebugMessagesDisplay = false;
    }
    if (!GEngine->bSuppressMapWarnings)
    {
        bRestoreMapWarningsAfterClose = true;
        GEngine->bSuppressMapWarnings = true;
    }
#endif
}

void UTSTSSPartyGearMenuReviewWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    if (!WidgetTree) return;

    UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>();
    UBorder* Backdrop = WidgetTree->ConstructWidget<UBorder>();
    UBorder* Panel = WidgetTree->ConstructWidget<UBorder>();
    UHorizontalBox* Layout = WidgetTree->ConstructWidget<UHorizontalBox>();
    UVerticalBox* NavigationColumn = WidgetTree->ConstructWidget<UVerticalBox>();
    UScrollBox* Scroll = WidgetTree->ConstructWidget<UScrollBox>();
    ContentColumn = WidgetTree->ConstructWidget<UVerticalBox>();
    if (!Canvas || !Backdrop || !Panel || !Layout ||
        !NavigationColumn || !Scroll || !ContentColumn)
        return;
    WidgetTree->RootWidget = Canvas;
    // Full-screen, deliberately opaque menu canvas: the world HUD and
    // debug placeholders must never bleed through player-owned UI.
    Backdrop->SetBrushColor(FLinearColor(0.008f, 0.018f, 0.028f, 1.f));
    UCanvasPanelSlot* BackgroundSlot = Canvas->AddChildToCanvas(Backdrop);
    BackgroundSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
    BackgroundSlot->SetOffsets(FMargin(0.f));
    BackgroundSlot->SetZOrder(0);
    Panel->SetBrushColor(FLinearColor(0.020f, 0.043f, 0.058f, 1.f));
    Panel->SetPadding(FMargin(30.f));
    Panel->AddChild(Layout);
    UCanvasPanelSlot* PanelSlot = Canvas->AddChildToCanvas(Panel);
    PanelSlot->SetAnchors(FAnchors(0.026f, 0.032f, 0.974f, 0.968f));
    PanelSlot->SetOffsets(FMargin(0.f));
    PanelSlot->SetZOrder(1);

    USizeBox* NavigationWidth = WidgetTree->ConstructWidget<USizeBox>();
    if (!NavigationWidth) return;
    NavigationWidth->SetWidthOverride(246.f);
    NavigationWidth->AddChild(NavigationColumn);
    Layout->AddChildToHorizontalBox(NavigationWidth)->
        SetPadding(FMargin(0.f, 0.f, 28.f, 0.f));
    Layout->AddChildToHorizontalBox(Scroll)->
        SetSize(FSlateChildSize(ESlateSizeRule::Fill));
    Scroll->AddChild(ContentColumn);

    AddReviewText(WidgetTree, NavigationColumn,
        TEXT("TO SAIL THE\nSTARRY SKY"), 26,
        FLinearColor(0.97f, 0.86f, 0.62f, 1.f), 14.f);
    AddReviewText(WidgetTree, NavigationColumn,
        TEXT("VOYAGE  /  FIELD MANUAL"), 14,
        FLinearColor(0.47f, 0.81f, 0.83f, 1.f), 12.f);
    StageLabel = AddReviewText(WidgetTree, NavigationColumn,
        TEXT("FIRST WAKE"), 14,
        FLinearColor(0.87f, 0.90f, 0.87f, 1.f), 21.f);

    const TCHAR* Titles[] = {
        TEXT("PARTY / STATUS"), TEXT("ITEMS"),
        TEXT("EQUIPMENT"), TEXT("MAGIC / SPELLS"),
        TEXT("SKILLS / ARTS"), TEXT("JOBS / GROWTH"),
        TEXT("FORMATION"), TEXT("JOURNAL"),
        TEXT("AUREATE WAKE"), TEXT("SYSTEM")
    };
    NavigationButtons.Reset();
    for (int32 I=0; I<10; ++I)
    {
        UButton* NavButton = WidgetTree->ConstructWidget<UButton>();
        UTextBlock* NavText = WidgetTree->ConstructWidget<UTextBlock>();
        if (!NavButton || !NavText) return;
        NavText->SetText(FText::FromString(Titles[I]));
        FSlateFontInfo Font = NavText->GetFont();
        Font.Size = 17;
        NavText->SetFont(Font);
        NavText->SetColorAndOpacity(FSlateColor(
            FLinearColor(0.94f, 0.94f, 0.90f, 1.f)));
        NavText->SetJustification(ETextJustify::Left);
        NavButton->SetContent(NavText);
        NavButton->SetBackgroundColor(
            FLinearColor(0.10f, 0.25f, 0.31f, 1.f));
        NavigationButtons.Add(NavButton);
        NavigationColumn->AddChildToVerticalBox(NavButton)->
            SetPadding(FMargin(0.f, 0.f, 0.f, 7.f));
        switch (I)
        {
        case 0: NavButton->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenStatusTab); break;
        case 1: NavButton->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenInventoryTab); break;
        case 2: NavButton->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenEquipmentTab); break;
        case 3: NavButton->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenMagicTab); break;
        case 4: NavButton->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenSkillsTab); break;
        case 5: NavButton->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenJobsTab); break;
        case 6: NavButton->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenFormationTab); break;
        case 7: NavButton->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenJournalTab); break;
        case 8: NavButton->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenShipTab); break;
        case 9: NavButton->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenSystemTab); break;
        }
    }
    StatusLabel = AddReviewText(WidgetTree, NavigationColumn,
        TEXT("REVIEW BUILD  /  NO STORY OR ITEM GRANTS"), 12,
        FLinearColor(0.64f, 0.87f, 0.80f, 1.f), 12.f);
    UButton* CloseButton = WidgetTree->ConstructWidget<UButton>();
    UTextBlock* CloseText = WidgetTree->ConstructWidget<UTextBlock>();
    if (!CloseButton || !CloseText) return;
    CloseText->SetText(FText::FromString(TEXT("RETURN TO VOYAGE")));
    FSlateFontInfo CloseFont = CloseText->GetFont();
    CloseFont.Size = 16;
    CloseText->SetFont(CloseFont);
    CloseText->SetJustification(ETextJustify::Center);
    CloseText->SetColorAndOpacity(FSlateColor(
        FLinearColor(0.95f, 0.94f, 0.87f, 1.f)));
    CloseButton->SetContent(CloseText);
    CloseButton->SetBackgroundColor(
        FLinearColor(0.17f, 0.47f, 0.50f, 1.f));
    CloseButton->OnClicked.AddDynamic(
        this, &UTSTSSPartyGearMenuReviewWidget::OnCloseClicked);
    NavigationColumn->AddChildToVerticalBox(CloseButton);
    RenderReviewPage();
}

void UTSTSSPartyGearMenuReviewWidget::AddPageLine(
    const FString& Value, int32 Size, FLinearColor Color, float Gap)
{
    if (!ContentColumn || !WidgetTree) return;
    // Readable row treatment for roster and item records; this does not
    // imply an equipped, learned or unlocked progression authority.
    if (Value.Contains(TEXT(" | ")) && Size >= 16)
    {
        UBorder* RowPanel = WidgetTree->ConstructWidget<UBorder>();
        UTextBlock* RowLabel = WidgetTree->ConstructWidget<UTextBlock>();
        if (!RowPanel || !RowLabel) return;
        RowPanel->SetBrushColor(
            FLinearColor(0.045f, 0.099f, 0.122f, 1.f));
        RowPanel->SetPadding(FMargin(15.f, 12.f, 15.f, 12.f));
        RowLabel->SetText(FText::FromString(Value));
        RowLabel->SetColorAndOpacity(FSlateColor(Color));
        FSlateFontInfo Font = RowLabel->GetFont();
        Font.Size = Size;
        RowLabel->SetFont(Font);
        RowLabel->SetAutoWrapText(true);
        RowPanel->AddChild(RowLabel);
        ContentColumn->AddChildToVerticalBox(RowPanel)->
            SetPadding(FMargin(0.f, 0.f, 0.f, Gap));
        return;
    }
    AddReviewText(WidgetTree, ContentColumn, Value, Size, Color, Gap);
}

void UTSTSSPartyGearMenuReviewWidget::AddPageHeading(const FString& Value)
{
    AddPageLine(Value, 25, FLinearColor(0.97f, 0.86f, 0.62f, 1.f), 15.f);
    if (!WidgetTree || !ContentColumn) return;
    UBorder* Rule = WidgetTree->ConstructWidget<UBorder>();
    USizeBox* RuleHeight = WidgetTree->ConstructWidget<USizeBox>();
    if (!Rule || !RuleHeight) return;
    Rule->SetBrushColor(FLinearColor(0.54f, 0.44f, 0.27f, 1.f));
    RuleHeight->SetHeightOverride(2.f);
    RuleHeight->AddChild(Rule);
    ContentColumn->AddChildToVerticalBox(RuleHeight)->
        SetPadding(FMargin(0.f, 0.f, 0.f, 23.f));
}

void UTSTSSPartyGearMenuReviewWidget::RenderReviewPage()
{
    if (!WidgetTree || !ContentColumn) return;
    ContentColumn->ClearChildren();
    SlotLabels.Reset();
    SlotButtons.Reset();
    for (int32 I = 0; I < NavigationButtons.Num(); ++I)
    {
        if (UButton* Nav = NavigationButtons[I])
        {
            Nav->SetBackgroundColor(
                static_cast<int32>(ActivePage) == I
                    ? FLinearColor(0.57f, 0.42f, 0.20f, 1.f)
                    : FLinearColor(0.10f, 0.25f, 0.31f, 1.f));
        }
    }
    AddPageLine(TEXT("VOYAGE SYSTEMS  /  FIRST WAKE REVIEW"), 13,
        FLinearColor(0.45f, 0.79f, 0.82f, 1.f), 18.f);
    if (StageLabel)
    {
        StageLabel->SetText(FText::FromString(
            ActiveStage == ETSTSSPartySliceReviewStage::AfterSplashdown
                ? TEXT("AFTER SPLASHDOWN") : TEXT("FIRST WAKE")));
    }
    switch (ActivePage)
    {
    case ETSTSSReviewMenuPage::Status:
    {
        AddPageHeading(TEXT("CHARACTERS / STATUS"));
        AddPageLine(TEXT("Active voyage crew; unapproved stat numbers are never invented."));
        const FName Members[] = {
            TEXT("Ender"), TEXT("Ionia"), TEXT("Lyra"),
            TEXT("Reson"), TEXT("Aepex")
        };
        for (FName Member : Members)
        {
            const bool bAvailable =
                FTSTSSPartySliceReviewEquipment::IsMemberAvailable(
                    ActiveStage, Member);
            const ETSTSSLight Affinity = FTSTSSCombatData::ApprovedAffinity(Member);
            const TCHAR* AffinityName =
                Affinity == ETSTSSLight::Spirit ? TEXT("Spirit") :
                Affinity == ETSTSSLight::Earth ? TEXT("Earth") :
                Affinity == ETSTSSLight::Water ? TEXT("Water") :
                Affinity == ETSTSSLight::Fire ? TEXT("Fire") :
                Affinity == ETSTSSLight::Air ? TEXT("Air") : TEXT("Not established");
            AddPageLine(FString::Printf(TEXT("%s  |  %s  |  Affinity: %s"),
                *Member.ToString(), bAvailable ? TEXT("AVAILABLE") : TEXT("LOCKED"),
                AffinityName), 17);
            if (bAvailable && bHasValidLoadedRosterSnapshot)
            {
                const FTSTSSCombatant* Snapshot = LoadedSavedRosterSnapshot.FindByPredicate(
                    [Member](const FTSTSSCombatant& Row)
                    {
                        return Row.CharacterId == Member;
                    });
                if (Snapshot)
                    AddPageLine(FString::Printf(
                        TEXT("  SAVED HP %d/%d | RESOURCE %d/%d | ATK %d | DEF %d"),
                        Snapshot->Health, Snapshot->MaxHealth,
                        Snapshot->Resource, Snapshot->MaxResource,
                        Snapshot->Attack, Snapshot->Defense), 15,
                        FLinearColor(0.64f, 0.85f, 0.78f, 1.f));
            }
        }
        AddPageLine(bHasValidLoadedRosterSnapshot
            ? TEXT("These are validated LAST-LOADED SAVE values, NOT live combat stats.")
            : TEXT("No validated compatible saved party roster loaded; HP/resource/attack/defense unavailable."));
        AddPageLine(TEXT("Character level, XP and proficiency are not part of the version-2 save roster."));
        AddPageLine(TEXT("Reviewed gear bonuses are independent of saved base stats; not live combat changes."));
        for (const FName Member : {FName(TEXT("Ender")), FName(TEXT("Ionia"))})
        {
            const FTSTSSReviewGearSlots* Slots =
                ReviewState.EquippedByCharacter.Find(Member);
            if (!Slots) continue;
            int32 AttackBonus = 0, DefenseBonus = 0;
            for (const FName ItemId : {
                Slots->WeaponInstance, Slots->ArmorInstance,
                Slots->AccessoryInstance })
            {
                if (ItemId.IsNone()) continue;
                const FTSTSSReviewGearInstance* Item =
                    ReviewState.OwnedInstances.Find(ItemId);
                if (Item && Item->OwnerId == Member)
                {
                    AttackBonus += Item->AttackBonus;
                    DefenseBonus += Item->DefenseBonus;
                }
            }
            AddPageLine(FString::Printf(
                TEXT("%s REVIEW GEAR: ATK +%d | DEF +%d"),
                *Member.ToString(), AttackBonus, DefenseBonus));
        }
        break;
    }
    case ETSTSSReviewMenuPage::Inventory:
    {
        AddPageHeading(TEXT("ITEMS / OWNED REVIEW EQUIPMENT"));
        AddPageLine(TEXT("Transient test gear only. No production consumables, quantities, crafting or selling."));
        TArray<FName> Names;
        ReviewState.OwnedInstances.GetKeys(Names);
        Names.Sort([](const FName& A, const FName& B)
        {
            return A.ToString() < B.ToString();
        });
        for (FName ItemId : Names)
        {
            const FTSTSSReviewGearInstance& Item =
                ReviewState.OwnedInstances.FindChecked(ItemId);
            const FTSTSSReviewGearSlots* Slots =
                ReviewState.EquippedByCharacter.Find(Item.OwnerId);
            const bool bEquipped = Slots &&
                (Slots->WeaponInstance == ItemId ||
                 Slots->ArmorInstance == ItemId ||
                 Slots->AccessoryInstance == ItemId);
            AddPageLine(FString::Printf(
                TEXT("%s | %s | ATK +%d | DEF +%d"),
                *ItemId.ToString(),
                bEquipped ? TEXT("EQUIPPED") : TEXT("OWNED / NOT EQUIPPED"),
                Item.AttackBonus, Item.DefenseBonus));
        }
        AddPageLine(TEXT("Restorative Vial / Resonance Capacitor: scene props only; NOT owned items."));
        break;
    }
    case ETSTSSReviewMenuPage::Equipment:
        RenderEquipmentPage();
        break;
    case ETSTSSReviewMenuPage::Magic:
        AddPageHeading(TEXT("MAGIC / SPELLS"));
        AddPageLine(TEXT("Five Lights are affinities, not automatic spell permissions."));
        AddPageLine(TEXT("Ender: Spirit | Ionia: Earth | Lyra: Water (locked until recruitment)."));
        AddPageLine(TEXT("Reson: Fire | Aepex: Air (not in this playable party)."));
        AddPageLine(TEXT("Learned spell catalog, MP costs, targeting, mastery and spell loadouts: no live authoritative data attached."));
        AddPageLine(TEXT("Casting and assigning spells from this menu are disabled; no unearned unlocks."));
        break;
    case ETSTSSReviewMenuPage::Skills:
        AddPageHeading(TEXT("SKILLS / TECHNIQUES / JOB ARTS"));
        AddPageLine(TEXT("Spell, weapon-technique and job-art data contracts exist."));
        AddPageLine(TEXT("Actual learned skills, weapon mastery, rank prerequisites and equipped abilities require the gameplay progression ledger."));
        AddPageLine(TEXT("Skill assignment and execution are currently unavailable in this review menu."));
        break;
    case ETSTSSReviewMenuPage::Jobs:
        AddPageHeading(TEXT("JOBS / CHARACTER GROWTH"));
        AddPageLine(TEXT("Primary and secondary job selection requires explicit unlocked definitions."));
        AddPageLine(TEXT("Level, proficiency, mastery, jobs and skill transfer remain independent progression axes."));
        AddPageLine(TEXT("The live job catalog has not been admitted to this screen. No job changing or XP granting."));
        break;
    case ETSTSSReviewMenuPage::Formation:
        AddPageHeading(TEXT("PARTY / FORMATION"));
        AddPageLine(TEXT("Opening voyage party: Ender + Captain Ionia."));
        AddPageLine(TEXT("Lyra joins AFTER a distinct post-splashdown recruitment scene, not splashdown alone."));
        AddPageLine(TEXT("Three active combat slots are planned; no bench/party reassignment before legal recruitment."));
        AddPageLine(TEXT("Reson and Aepex remain unavailable during this vertical slice."));
        AddPageLine(TEXT("Formation editing: LOCKED pending authoritative battle-party ownership."));
        break;
    case ETSTSSReviewMenuPage::Journal:
        AddPageHeading(TEXT("VOYAGE / JOURNAL"));
        if (IsValid(StoryReviewState))
        {
            AddPageLine(FString::Printf(TEXT("Current objective: %s"),
                *StoryReviewState->GetReviewObjectiveText()), 18);
            const UEnum* BeatEnum = StaticEnum<ETSTSSFirstWakeBeat>();
            AddPageLine(FString::Printf(TEXT("Story beat: %s"),
                BeatEnum ? *BeatEnum->GetNameStringByValue(
                    static_cast<int64>(StoryReviewState->GetCurrentBeat()))
                    : TEXT("Unknown")));
        }
        else
        {
            AddPageLine(TEXT("First Wake story state unavailable in this review context."));
        }
        AddPageLine(TEXT("Quest archive, bestiary, lore codex and map journal: awaiting verified records."));
        break;
    case ETSTSSReviewMenuPage::Ship:
        RenderShipPage();
        break;
    case ETSTSSReviewMenuPage::System:
        AddPageHeading(TEXT("SYSTEM / OPTIONS"));
        AddPageLine(TEXT("Preliminary controls: WASD move, E interact, J objective, G equipment, M main menu."));
        AddPageLine(TEXT("Normal Game: F5 quicksave / F9 quickload. PIE: F6 review-only save / F9 guarded review load."));
        AddPageLine(TEXT("Audio, graphics, input remapping, accessibility and localization preferences: not yet connected."));
        AddPageLine(TEXT("No menu operation may overwrite an existing player save or bypass save-version validation."));
        break;
    default:
        AddPageHeading(TEXT("UNAVAILABLE MENU PAGE"));
        break;
    }
}

void UTSTSSPartyGearMenuReviewWidget::RenderEquipmentPage()
{
    AddPageHeading(TEXT("EQUIPMENT / FIELD LOADOUT"));
    AddPageLine(TEXT("Transient review ledger. Select equipment slots to equip/unequip owned test gear."));
    for (int32 OwnerIndex=0; OwnerIndex<3; ++OwnerIndex)
    {
        const FName Owner = ReviewOwner(OwnerIndex);
        const bool bAvailable =
            FTSTSSPartySliceReviewEquipment::IsMemberAvailable(ActiveStage, Owner);
        AddPageLine(FString::Printf(TEXT("%s  |  %s"),
            *Owner.ToString().ToUpper(),
            bAvailable ? TEXT("AVAILABLE") : TEXT("RECRUITMENT LOCKED")), 19,
            FLinearColor(0.89f, 0.90f, 0.83f, 1.f));
        UHorizontalBox* Buttons = WidgetTree->ConstructWidget<UHorizontalBox>();
        if (!Buttons) return;
        ContentColumn->AddChildToVerticalBox(Buttons)->
            SetPadding(FMargin(0.f, 0.f, 0.f, 20.f));
        for (int32 SlotIndex=0; SlotIndex<3; ++SlotIndex)
        {
            UButton* Button = WidgetTree->ConstructWidget<UButton>();
            UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>();
            if (!Button || !Label) return;
            FSlateFontInfo Font = Label->GetFont();
            Font.Size = 13;
            Label->SetFont(Font);
            Label->SetColorAndOpacity(FSlateColor(FLinearColor::White));
            Button->SetContent(Label);
            Buttons->AddChildToHorizontalBox(Button)->SetPadding(FMargin(0.f, 0.f, 8.f, 0.f));
            SlotButtons.Add(Button);
            SlotLabels.Add(Label);
            const int32 I = OwnerIndex*3 + SlotIndex;
            switch (I)
            {
            case 0: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::ToggleEnderWeapon); break;
            case 1: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::ToggleEnderArmor); break;
            case 2: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::ToggleEnderAccessory); break;
            case 3: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::ToggleIoniaWeapon); break;
            case 4: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::ToggleIoniaArmor); break;
            case 5: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::ToggleIoniaAccessory); break;
            case 6: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::ToggleLyraWeapon); break;
            case 7: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::ToggleLyraArmor); break;
            case 8: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::ToggleLyraAccessory); break;
            }
        }
    }
    AddPageLine(TEXT("These actions change only the review ledger; 3D mount, inventory save and combat linkage still require integration."));
    RefreshReviewLabels();
}

void UTSTSSPartyGearMenuReviewWidget::RenderShipPage()
{
    AddPageHeading(TEXT("THE AUREATE WAKE / SHIP CONSOLE"));
    AddPageLine(TEXT("Read-only engineering, navigation, crew and configuration review."));
    UHorizontalBox* Tabs = WidgetTree->ConstructWidget<UHorizontalBox>();
    if (!Tabs) return;
    ContentColumn->AddChildToVerticalBox(Tabs)->SetPadding(FMargin(0.f,0.f,0.f,17.f));
    const TCHAR* Names[] = {
        TEXT("STATUS"), TEXT("ENGINE"), TEXT("MODES"), TEXT("CREW"),
        TEXT("ROUTE"), TEXT("UPGRADES"), TEXT("CARGO")
    };
    for (int32 I=0; I<7; ++I)
    {
        UButton* Button = WidgetTree->ConstructWidget<UButton>();
        UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>();
        if (!Button || !Text) return;
        Text->SetText(FText::FromString(Names[I]));
        FSlateFontInfo Font = Text->GetFont();
        Font.Size = 15;
        Text->SetFont(Font);
        Text->SetColorAndOpacity(FSlateColor(
            FLinearColor(0.94f, 0.94f, 0.88f, 1.f)));
        Button->SetContent(Text);
        Button->SetBackgroundColor(
            static_cast<int32>(ActiveShipPage) == I
                ? FLinearColor(0.57f, 0.42f, 0.20f, 1.f)
                : FLinearColor(0.12f, 0.28f, 0.32f, 1.f));
        Tabs->AddChildToHorizontalBox(Button)->SetPadding(FMargin(0.f,0.f,9.f,0.f));
        switch (I)
        {
        case 0: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenShipOverview); break;
        case 1: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenShipEngineering); break;
        case 2: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenShipConfigurations); break;
        case 3: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenShipCrew); break;
        case 4: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenShipNavigation); break;
        case 5: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenShipUpgrades); break;
        case 6: Button->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OpenShipCargo); break;
        }
    }
    switch (ActiveShipPage)
    {
    case ETSTSSShipReviewPage::Overview:
        AddPageHeading(TEXT("VESSEL / STATUS"));
        AddPageLine(TEXT("Aureate Wake: harmonic levitation vessel / evolving design."));
        AddPageLine(TEXT("Hull integrity, power load, fuel, altitude, velocity and stored resources: NO VERIFIED LIVE TELEMETRY."));
        AddPageLine(TEXT("Ship operational and configuration controls are not admitted by this menu."));
        if (IsValid(StoryReviewState))
            AddPageLine(FString::Printf(TEXT("First Wake objective: %s"),
                *StoryReviewState->GetReviewObjectiveText()));
        break;
    case ETSTSSShipReviewPage::Engineering:
    {
        AddPageHeading(TEXT("HARMONIC ENGINEERING / FIRST WAKE"));
        AddPageLine(TEXT("Actual inspection milestone flags, not fabricated engine measurements."));
        const uint8 Mask = IsValid(StoryReviewState)
            ? StoryReviewState->GetInspectionMask() : 0;
        const TCHAR* Labels[] = {TEXT("LIFT"), TEXT("PRESSURE"), TEXT("RESERVE")};
        for (int32 I=0; I<3; ++I)
            AddPageLine(FString::Printf(TEXT("%s INSPECTION: %s"),
                Labels[I], !IsValid(StoryReviewState) ? TEXT("UNAVAILABLE")
                : (Mask & (1u << I)) ? TEXT("COMPLETE")
                : TEXT("NOT YET INSPECTED")));
        AddPageLine(TEXT("True harmonic tuning, repairs, damage, efficiency and reserve telemetry require verified ship-system state."));
        break;
    }
    case ETSTSSShipReviewPage::Configurations:
        AddPageHeading(TEXT("VESSEL CONFIGURATIONS"));
        AddPageLine(TEXT("SKYBORNE    /  Winged flight | Review only, no menu-based transformation."));
        AddPageLine(TEXT("SEABORNE    /  Hydrofoil travel | Review only, no menu-based transformation."));
        AddPageLine(TEXT("SUBMERSIBLE /  Wings tucked | No executable transformation authorized."));
        AddPageLine(TEXT("STARBOURNE  /  Four radial sails | STORY AND ALL-FIVE CREW PLUS SHIP RESONANCE LOCKED."));
        AddPageLine(TEXT("None of these controls is selectable until real mode authority, collision and animation are verified."));
        break;
    case ETSTSSShipReviewPage::Crew:
        AddPageHeading(TEXT("CREW / STATIONS"));
        AddPageLine(TEXT("Captain Ionia: Earth affinity; command essential."));
        AddPageLine(TEXT("Ender: Spirit affinity; harmonic levitation engineering."));
        AddPageLine(TEXT("Lyra: Water affinity; joins only after separate recruitment."));
        AddPageLine(TEXT("Reson: Fire; Aepex: Air ? future crew progression, not in current slice."));
        AddPageLine(TEXT("Crew reassignment is locked. Five Lights full-crew feats require EACH member and the ship."));
        break;
    case ETSTSSShipReviewPage::Navigation:
        AddPageHeading(TEXT("COURSE / NAVIGATION"));
        AddPageLine(TEXT("Route charts, biome visibility and Auroral Ladder navigation require authored world-map state."));
        AddPageLine(TEXT("Hidden Moon Bridge and Starbourne route remain gated by narrative and celestial requirements."));
        AddPageLine(TEXT("No fast travel, waypoint teleportation or ship steering is granted by this console."));
        break;
    case ETSTSSShipReviewPage::Upgrades:
        AddPageHeading(TEXT("SHIP / REPAIR AND UPGRADES"));
        AddPageLine(TEXT("Harmonic calibration, hull reinforcements, wings, hydrofoils and subsystem tuning."));
        AddPageLine(TEXT("Upgrade tiers, crafting cost, inventory requirements, repair damage and availability are not established."));
        AddPageLine(TEXT("No purchase/repair/upgrade operation authorized in this review console."));
        break;
    case ETSTSSShipReviewPage::Cargo:
        AddPageHeading(TEXT("HOLD / CARGO / SUPPLIES"));
        AddPageLine(TEXT("Provisions, expedition supplies, tools, quest cargo and ship inventory."));
        AddPageLine(TEXT("No authoritative cargo counts, weight allowance, storage or supply consumption integrated."));
        AddPageLine(TEXT("No transfers, item spawns or resource changes permitted here."));
        break;
    default:
        AddPageHeading(TEXT("INVALID SHIP SUBPAGE"));
        break;
    }
}

void UTSTSSPartyGearMenuReviewWidget::OpenStatusTab() { OpenPageForReview(ETSTSSReviewMenuPage::Status); }
void UTSTSSPartyGearMenuReviewWidget::OpenInventoryTab() { OpenPageForReview(ETSTSSReviewMenuPage::Inventory); }
void UTSTSSPartyGearMenuReviewWidget::OpenEquipmentTab() { OpenPageForReview(ETSTSSReviewMenuPage::Equipment); }
void UTSTSSPartyGearMenuReviewWidget::OpenMagicTab() { OpenPageForReview(ETSTSSReviewMenuPage::Magic); }
void UTSTSSPartyGearMenuReviewWidget::OpenSkillsTab() { OpenPageForReview(ETSTSSReviewMenuPage::Skills); }
void UTSTSSPartyGearMenuReviewWidget::OpenJobsTab() { OpenPageForReview(ETSTSSReviewMenuPage::Jobs); }
void UTSTSSPartyGearMenuReviewWidget::OpenFormationTab() { OpenPageForReview(ETSTSSReviewMenuPage::Formation); }
void UTSTSSPartyGearMenuReviewWidget::OpenJournalTab() { OpenPageForReview(ETSTSSReviewMenuPage::Journal); }
void UTSTSSPartyGearMenuReviewWidget::OpenShipTab() { OpenPageForReview(ETSTSSReviewMenuPage::Ship); }
void UTSTSSPartyGearMenuReviewWidget::OpenSystemTab() { OpenPageForReview(ETSTSSReviewMenuPage::System); }
void UTSTSSPartyGearMenuReviewWidget::OpenShipOverview() { ChangeShipPage(ETSTSSShipReviewPage::Overview); }
void UTSTSSPartyGearMenuReviewWidget::OpenShipEngineering() { ChangeShipPage(ETSTSSShipReviewPage::Engineering); }
void UTSTSSPartyGearMenuReviewWidget::OpenShipConfigurations() { ChangeShipPage(ETSTSSShipReviewPage::Configurations); }
void UTSTSSPartyGearMenuReviewWidget::OpenShipCrew() { ChangeShipPage(ETSTSSShipReviewPage::Crew); }
void UTSTSSPartyGearMenuReviewWidget::OpenShipNavigation() { ChangeShipPage(ETSTSSShipReviewPage::Navigation); }
void UTSTSSPartyGearMenuReviewWidget::OpenShipUpgrades() { ChangeShipPage(ETSTSSShipReviewPage::Upgrades); }
void UTSTSSPartyGearMenuReviewWidget::OpenShipCargo() { ChangeShipPage(ETSTSSShipReviewPage::Cargo); }

void UTSTSSPartyGearMenuReviewWidget::RefreshReviewLabels()
{
    if (ActivePage != ETSTSSReviewMenuPage::Equipment) return;
    for (int32 I=0; I<9 && I<SlotLabels.Num() && I<SlotButtons.Num(); ++I)
    {
        const FName Owner = ReviewOwner(I/3);
        const auto GearSlot = ReviewSlot(I%3);
        const bool bAllowed = bInitialized &&
            FTSTSSPartySliceReviewEquipment::IsMemberAvailable(ActiveStage, Owner);
        SlotButtons[I]->SetIsEnabled(bAllowed);
        const FTSTSSReviewGearSlots* Slots =
            ReviewState.EquippedByCharacter.Find(Owner);
        const bool bEquipped = Slots && !SlotValue(*Slots, GearSlot).IsNone();
        FString GearName = TEXT("UNEQUIPPED");
        if (bEquipped)
        {
            const FString FullItemId = SlotValue(*Slots, GearSlot).ToString();
            FString OwnerPrefix, ItemSuffix;
            GearName = FullItemId.Split(TEXT("."), &OwnerPrefix, &ItemSuffix)
                ? ItemSuffix : TEXT("EQUIPPED");
        }
        SlotLabels[I]->SetText(FText::FromString(FString::Printf(
            TEXT("%s: %s"), SlotName(GearSlot),
            !bAllowed ? TEXT("LOCKED") : *GearName)));
    }
}

bool UTSTSSPartyGearMenuReviewWidget::TryToggleSlot(int32 Index)
{
    if (!bInitialized || ActivePage != ETSTSSReviewMenuPage::Equipment ||
        Index < 0 || Index >= 9) return false;
    const FName Owner = ReviewOwner(Index/3);
    const auto GearSlot = ReviewSlot(Index%3);
    if (!FTSTSSPartySliceReviewEquipment::IsMemberAvailable(ActiveStage, Owner))
        return false;

    const FTSTSSReviewGearSlots* Slots = ReviewState.EquippedByCharacter.Find(Owner);
    if (!Slots) return false;
    const bool bEquip = SlotValue(*Slots, GearSlot).IsNone();

    FTSTSSReviewGearState Candidate;
    if (!TryApplyReviewToggle(ReviewState, ActiveStage, Owner, GearSlot, bEquip, Candidate))
        return false;
    ReviewState = MoveTemp(Candidate);
    RefreshReviewLabels();
    if (StatusLabel)
    {
        StatusLabel->SetText(FText::FromString(FString::Printf(
            TEXT("%s %s %s (REVIEW ONLY)"), *Owner.ToString(),
            SlotName(GearSlot), bEquip ? TEXT("EQUIPPED") : TEXT("REMOVED"))));
    }
    return true;
}

void UTSTSSPartyGearMenuReviewWidget::CloseReview()
{
    RemoveFromParent();
#if !UE_BUILD_SHIPPING
    if (GEngine)
    {
        if (bRestoreOnScreenMessagesAfterClose)
            GEngine->bEnableOnScreenDebugMessagesDisplay = true;
        if (bRestoreMapWarningsAfterClose)
            GEngine->bSuppressMapWarnings = false;
    }
    bRestoreOnScreenMessagesAfterClose = false;
    bRestoreMapWarningsAfterClose = false;
#endif
    if (APlayerController* Controller = GetOwningPlayer())
    {
        if (bHUDHiddenByReview)
        {
            if (AHUD* HUD = Controller->GetHUD())
                HUD->bShowHUD = true;
            bHUDHiddenByReview = false;
        }
        Controller->bShowMouseCursor = false;
        Controller->SetInputMode(FInputModeGameOnly());
    }
}

void UTSTSSPartyGearMenuReviewWidget::OnCloseClicked() { CloseReview(); }
void UTSTSSPartyGearMenuReviewWidget::ToggleEnderWeapon() { TryToggleSlot(0); }
void UTSTSSPartyGearMenuReviewWidget::ToggleEnderArmor() { TryToggleSlot(1); }
void UTSTSSPartyGearMenuReviewWidget::ToggleEnderAccessory() { TryToggleSlot(2); }
void UTSTSSPartyGearMenuReviewWidget::ToggleIoniaWeapon() { TryToggleSlot(3); }
void UTSTSSPartyGearMenuReviewWidget::ToggleIoniaArmor() { TryToggleSlot(4); }
void UTSTSSPartyGearMenuReviewWidget::ToggleIoniaAccessory() { TryToggleSlot(5); }
void UTSTSSPartyGearMenuReviewWidget::ToggleLyraWeapon() { TryToggleSlot(6); }
void UTSTSSPartyGearMenuReviewWidget::ToggleLyraArmor() { TryToggleSlot(7); }
void UTSTSSPartyGearMenuReviewWidget::ToggleLyraAccessory() { TryToggleSlot(8); }
