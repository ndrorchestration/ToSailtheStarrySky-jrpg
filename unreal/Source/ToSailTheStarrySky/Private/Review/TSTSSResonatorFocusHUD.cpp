#include "Review/TSTSSResonatorFocusHUD.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"

namespace
{
UTextBlock* MakeLine(UWidgetTree* Tree,UVerticalBox* Stack,const TCHAR* Name,
                     int32 Size,const FLinearColor& Color)
{
    UTextBlock* Line=Tree->ConstructWidget<UTextBlock>(
        UTextBlock::StaticClass(),FName(Name));
    FSlateFontInfo Font=Line->GetFont();
    Font.Size=Size;
    Line->SetFont(Font);
    Line->SetAutoWrapText(true);
    Line->SetColorAndOpacity(FSlateColor(Color));
    if(UVerticalBoxSlot* Slot=Stack->AddChildToVerticalBox(Line))
        Slot->SetPadding(FMargin(15.f,7.f));
    return Line;
}
}

void UTSTSSResonatorFocusHUD::NativeConstruct()
{
    Super::NativeConstruct();
#if !UE_BUILD_SHIPPING
    if(!WidgetTree) WidgetTree=NewObject<UWidgetTree>(this);
    if(WidgetTree->RootWidget) return;
    UCanvasPanel* Canvas=WidgetTree->ConstructWidget<UCanvasPanel>(
        UCanvasPanel::StaticClass(),TEXT("FocusCanvas"));
    WidgetTree->RootWidget=Canvas;
    UBorder* Back=WidgetTree->ConstructWidget<UBorder>(
        UBorder::StaticClass(),TEXT("FocusHudPanel"));
    Back->SetBrushColor(FLinearColor(.016f,.047f,.079f,.94f));
    UCanvasPanelSlot* Slot=Canvas->AddChildToCanvas(Back);
    Slot->SetAnchors(FAnchors(0.f,0.f));
    Slot->SetPosition(FVector2D(18.f,18.f));
    Slot->SetSize(FVector2D(560.f,415.f));
    UVerticalBox* Stack=WidgetTree->ConstructWidget<UVerticalBox>(
        UVerticalBox::StaticClass(),TEXT("FocusLayout"));
    Back->SetContent(Stack);
    HeadingText=MakeLine(WidgetTree,Stack,TEXT("Header"),19,
                         FLinearColor(.50f,.96f,.87f));
    CombatText=MakeLine(WidgetTree,Stack,TEXT("Combatants"),16,
                        FLinearColor(.87f,.95f,1.f));
    ActionText=MakeLine(WidgetTree,Stack,TEXT("Action"),16,
                        FLinearColor(1.f,.79f,.45f));
    ControlsText=MakeLine(WidgetTree,Stack,TEXT("Controls"),14,
                          FLinearColor(.65f,.87f,.89f));
    SetReviewState(TEXT("RESONATOR / FOCUS REVIEW"),
        TEXT("Preparing exact admitted spell rows"),TEXT(""),
        TEXT("1 Centering  |  2 Resonant Pulse"));
#endif
}

void UTSTSSResonatorFocusHUD::SetReviewState(
    const FString& Header,const FString& Combatants,
    const FString& LastAction,const FString& Controls)
{
#if !UE_BUILD_SHIPPING
    if (!IsValid(HeadingText.Get()) || !IsValid(CombatText.Get()) ||
        !IsValid(ActionText.Get()) || !IsValid(ControlsText.Get())) return;
    HeadingText->SetText(FText::FromString(Header));
    CombatText->SetText(FText::FromString(Combatants));
    ActionText->SetText(FText::FromString(LastAction));
    ControlsText->SetText(FText::FromString(Controls));
#endif
}
