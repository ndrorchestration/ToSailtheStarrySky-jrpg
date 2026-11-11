#include "TSTSSPartyGearMenuReviewWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "GameFramework/PlayerController.h"

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
    RefreshReviewLabels();
    return true;
}

bool UTSTSSPartyGearMenuReviewWidget::TryRefreshStoryStageReview(
    ETSTSSPartySliceReviewStage RequestedStage)
{
    if (!bInitialized) return false;
    if (ActiveStage == RequestedStage) return true;
    // Only the real First Wake story transition is accepted from gameplay.
    // This API cannot synthesize the separate Lyra recruitment event.
    if (ActiveStage != ETSTSSPartySliceReviewStage::FirstWake ||
        RequestedStage != ETSTSSPartySliceReviewStage::AfterSplashdown)
        return false;
    ActiveStage = RequestedStage;
    RefreshReviewLabels();
    return true;
}

void UTSTSSPartyGearMenuReviewWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    if (!WidgetTree) return;

    UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>();
    UBorder* Panel = WidgetTree->ConstructWidget<UBorder>();
    UVerticalBox* Column = WidgetTree->ConstructWidget<UVerticalBox>();
    if (!Canvas || !Panel || !Column) return;
    WidgetTree->RootWidget = Canvas;

    Panel->SetBrushColor(FLinearColor(0.014f, 0.026f, 0.044f, 0.96f));
    Panel->SetPadding(FMargin(22.f));
    Panel->AddChild(Column);
    UCanvasPanelSlot* PanelSlot = Canvas->AddChildToCanvas(Panel);
    PanelSlot->SetAnchors(FAnchors(0.53f, 0.09f, 0.96f, 0.91f));
    PanelSlot->SetOffsets(FMargin(0.f));

    AddReviewText(WidgetTree, Column,
        TEXT("FIELD EQUIPMENT"), 27,
        FLinearColor(0.90f, 0.83f, 0.60f, 1.f), 8.f);
    AddReviewText(WidgetTree, Column,
        TEXT("PRELUDE LOADOUT / INTERACTIVE REVIEW"), 14,
        FLinearColor(0.46f, 0.78f, 0.82f, 1.f), 14.f);
    StageLabel = AddReviewText(WidgetTree, Column,
        TEXT("WAITING FOR AUTHORIZED REVIEW STAGE"), 15,
        FLinearColor::White, 12.f);
    AddReviewText(WidgetTree, Column,
        TEXT("Equipment here is a transient test fixture, not saved inventory."),
        13, FLinearColor(0.75f, 0.80f, 0.81f, 1.f), 14.f);

    SlotButtons.Reset();
    SlotLabels.Reset();
    for (int32 OwnerIndex = 0; OwnerIndex < 3; ++OwnerIndex)
    {
        AddReviewText(WidgetTree, Column,
            ReviewOwner(OwnerIndex).ToString().ToUpper(), 20,
            FLinearColor(0.90f, 0.90f, 0.83f, 1.f), 5.f);
        UHorizontalBox* Buttons = WidgetTree->ConstructWidget<UHorizontalBox>();
        if (!Buttons) return;
        Column->AddChildToVerticalBox(Buttons)->SetPadding(FMargin(0.f, 0.f, 0.f, 15.f));
        for (int32 SlotIndex = 0; SlotIndex < 3; ++SlotIndex)
        {
            UButton* Button = WidgetTree->ConstructWidget<UButton>();
            UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>();
            if (!Button || !Text) return;
            FSlateFontInfo Font = Text->GetFont();
            Font.Size = 13;
            Text->SetFont(Font);
            Text->SetColorAndOpacity(FSlateColor(FLinearColor(0.94f, 0.94f, 0.86f, 1.f)));
            Text->SetText(FText::FromString(SlotName(ReviewSlot(SlotIndex))));
            Button->SetContent(Text);
            Buttons->AddChildToHorizontalBox(Button)->SetPadding(FMargin(0.f, 0.f, 8.f, 0.f));
            SlotButtons.Add(Button);
            SlotLabels.Add(Text);

            const int32 I = OwnerIndex * 3 + SlotIndex;
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
            default: break;
            }
        }
    }

    StatusLabel = AddReviewText(WidgetTree, Column,
        TEXT("REVIEW ONLY - NO CHARACTER GRANT"), 15,
        FLinearColor(0.47f, 0.84f, 0.83f, 1.f), 15.f);
    UButton* Close = WidgetTree->ConstructWidget<UButton>();
    UTextBlock* CloseText = WidgetTree->ConstructWidget<UTextBlock>();
    if (!Close || !CloseText) return;
    CloseText->SetText(FText::FromString(TEXT("  RETURN TO VOYAGE  ")));
    Close->SetContent(CloseText);
    Close->OnClicked.AddDynamic(this, &UTSTSSPartyGearMenuReviewWidget::OnCloseClicked);
    Column->AddChildToVerticalBox(Close);
    RefreshReviewLabels();
}

void UTSTSSPartyGearMenuReviewWidget::RefreshReviewLabels()
{
    if (StageLabel)
    {
        StageLabel->SetText(FText::FromString(
            ActiveStage == ETSTSSPartySliceReviewStage::FirstWake
                ? TEXT("FIRST WAKE | ENDER + IONIA")
                : ActiveStage == ETSTSSPartySliceReviewStage::AfterSplashdown
                ? TEXT("SPLASHDOWN | LYRA NOT YET RECRUITED")
                : ActiveStage == ETSTSSPartySliceReviewStage::LyraRecruited
                ? TEXT("EXPLICIT LYRA RECRUITMENT REVIEW")
                : TEXT("INVALID REVIEW STAGE")));
    }
    for (int32 I=0; I<9 && I<SlotLabels.Num() && I<SlotButtons.Num(); ++I)
    {
        const FName Owner = ReviewOwner(I/3);
        const auto GearSlot = ReviewSlot(I%3);
        const bool bAllowed = bInitialized &&
            FTSTSSPartySliceReviewEquipment::IsMemberAvailable(ActiveStage, Owner);
        SlotButtons[I]->SetIsEnabled(bAllowed);
        const FTSTSSReviewGearSlots* Slots = ReviewState.EquippedByCharacter.Find(Owner);
        const bool bEquipped = Slots && !SlotValue(*Slots, GearSlot).IsNone();
        const FString Copy = FString::Printf(TEXT("%s: %s"),
            SlotName(GearSlot),
            !bAllowed ? TEXT("LOCKED")
                : bEquipped ? TEXT("EQUIPPED") : TEXT("UNEQUIPPED"));
        SlotLabels[I]->SetText(FText::FromString(Copy));
    }
}

bool UTSTSSPartyGearMenuReviewWidget::TryToggleSlot(int32 Index)
{
    if (!bInitialized || Index < 0 || Index >= 9) return false;
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
    if (APlayerController* Controller = GetOwningPlayer())
    {
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
