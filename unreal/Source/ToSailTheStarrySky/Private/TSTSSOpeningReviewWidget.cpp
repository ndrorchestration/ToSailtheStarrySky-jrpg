#include "TSTSSOpeningReviewWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "GameFramework/HUD.h"
#include "GameFramework/PlayerController.h"

void UTSTSSOpeningReviewWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    if (!WidgetTree) return;
    UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass());
    WidgetTree->RootWidget = Canvas;

    // Keep the live harbor visible under a restrained, legible blue veil.
    UBorder* Veil = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass());
    Veil->SetBrushColor(FLinearColor(0.008f, 0.025f, 0.045f, 0.79f));
    UCanvasPanelSlot* VeilSlot = Canvas->AddChildToCanvas(Veil);
    VeilSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
    VeilSlot->SetOffsets(FMargin(0));

    UVerticalBox* Column = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass());
    UCanvasPanelSlot* ColumnSlot = Canvas->AddChildToCanvas(Column);
    ColumnSlot->SetAnchors(FAnchors(0.08f, 0.16f, 0.82f, 0.86f));
    ColumnSlot->SetOffsets(FMargin(0));

    auto AddText = [this, Column](const TCHAR* Copy, int32 Size, const FLinearColor Color, float BottomPadding)
    {
        UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
        Text->SetText(FText::FromString(Copy));
        Text->SetColorAndOpacity(FSlateColor(Color));
        FSlateFontInfo Font = Text->GetFont();
        Font.Size = Size;
        Text->SetFont(Font);
        Text->SetAutoWrapText(true);
        UVerticalBoxSlot* Slot = Column->AddChildToVerticalBox(Text);
        Slot->SetPadding(FMargin(0.f, 0.f, 0.f, BottomPadding));
    };

    AddText(TEXT("A JOURNEY BEYOND THE HORIZON"), 15, FLinearColor(0.48f, 0.84f, 0.86f, 1.f), 22.f);
    AddText(TEXT("TO SAIL THE"), 30, FLinearColor(0.95f, 0.94f, 0.85f, 1.f), 0.f);
    AddText(TEXT("STARRY SKY"), 54, FLinearColor(0.98f, 0.94f, 0.79f, 1.f), 25.f);
    AddText(TEXT("Every voyage begins with a single note."), 19, FLinearColor(0.76f, 0.85f, 0.85f, 1.f), 40.f);

    NewGameButton = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass());
    NewGameButton->SetIsFocusable(true);
    NewGameButton->SetBackgroundColor(FLinearColor(0.32f, 0.65f, 0.67f, 1.f));
    NewGameButton->OnClicked.AddDynamic(this, &UTSTSSOpeningReviewWidget::BeginJourney);
    UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
    Label->SetText(FText::FromString(TEXT("  NEW GAME  ")));
    FSlateFontInfo LabelFont = Label->GetFont();
    LabelFont.Size = 20;
    Label->SetFont(LabelFont);
    NewGameButton->AddChild(Label);
    USizeBox* ButtonBox = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass());
    ButtonBox->SetWidthOverride(220.f);
    ButtonBox->SetHeightOverride(50.f);
    ButtonBox->AddChild(NewGameButton);
    Column->AddChildToVerticalBox(ButtonBox);
}

UWidget* UTSTSSOpeningReviewWidget::GetInitialFocus() const
{
    return NewGameButton;
}

void UTSTSSOpeningReviewWidget::BeginJourney()
{
    APlayerController* Controller = GetOwningPlayer();
    if (!Controller) return;
    RemoveFromParent();
    Controller->bShowMouseCursor = false;
    Controller->SetInputMode(FInputModeGameOnly());
    if (AHUD* CurrentHUD = Controller->GetHUD()) CurrentHUD->bShowHUD = true;
}
