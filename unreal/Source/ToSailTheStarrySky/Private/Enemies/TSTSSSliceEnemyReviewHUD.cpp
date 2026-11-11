#include "Enemies/TSTSSSliceEnemyReviewHUD.h"
#include "TSTSSCombatAbilities.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/ProgressBar.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"

namespace
{
    UTextBlock* AddLine(UWidgetTree* Tree, UVerticalBox* Box,
                        const TCHAR* Name, int32 FontSize, FLinearColor Color)
    {
        UTextBlock* Line=Tree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(),FName(Name));
        FSlateFontInfo Font=Line->GetFont();
        Font.Size=FontSize;
        Line->SetFont(Font);
        Line->SetColorAndOpacity(FSlateColor(Color));
        Line->SetAutoWrapText(true);
        if (UVerticalBoxSlot* Slot=Box->AddChildToVerticalBox(Line))
        {
            Slot->SetPadding(FMargin(14.f,6.f));
        }
        return Line;
    }

    UProgressBar* AddHealth(UWidgetTree* Tree, UVerticalBox* Box,
                            const TCHAR* Name, FLinearColor Color)
    {
        UProgressBar* Bar=Tree->ConstructWidget<UProgressBar>(
            UProgressBar::StaticClass(),FName(Name));
        Bar->SetFillColorAndOpacity(Color);
        Bar->SetPercent(0.f);
        if (UVerticalBoxSlot* Slot=Box->AddChildToVerticalBox(Bar))
        {
            Slot->SetPadding(FMargin(18.f,0.f,18.f,9.f));
        }
        return Bar;
    }

    const FTSTSSCombatant* FindCombatant(const TArray<FTSTSSCombatant>& Snapshot,
                                         FName Id)
    {
        return Snapshot.FindByPredicate([Id](const FTSTSSCombatant& Foe) {
            return Foe.CharacterId==Id;
        });
    }
}

void UTSTSSSliceEnemyReviewHUD::NativeConstruct()
{
    Super::NativeConstruct();
#if !UE_BUILD_SHIPPING
    if (!WidgetTree) WidgetTree=NewObject<UWidgetTree>(this, TEXT("ReviewTree"));
    if (WidgetTree->RootWidget) return;

    UCanvasPanel* Canvas=WidgetTree->ConstructWidget<UCanvasPanel>(
        UCanvasPanel::StaticClass(), TEXT("EnemyReviewCanvas"));
    WidgetTree->RootWidget=Canvas;
    UBorder* Background=WidgetTree->ConstructWidget<UBorder>(
        UBorder::StaticClass(),TEXT("EnemyReviewPanel"));
    Background->SetBrushColor(FLinearColor(.025f,.055f,.085f,.91f));
    UCanvasPanelSlot* CanvasSlot=Canvas->AddChildToCanvas(Background);
    CanvasSlot->SetAnchors(FAnchors(0.f,0.f,0.f,0.f));
    CanvasSlot->SetPosition(FVector2D(24.f,24.f));
    CanvasSlot->SetSize(FVector2D(510.f,435.f));
    UVerticalBox* Stack=WidgetTree->ConstructWidget<UVerticalBox>(
        UVerticalBox::StaticClass(),TEXT("ReviewVerticalStack"));
    Background->SetContent(Stack);
    Title=AddLine(WidgetTree,Stack,TEXT("ReviewTitle"),19,
                  FLinearColor(.40f,.84f,.94f));
    Status=AddLine(WidgetTree,Stack,TEXT("ReviewPhase"),15,
                   FLinearColor(1.f,.77f,.46f));
    Instruction=AddLine(WidgetTree,Stack,TEXT("ReviewControls"),13,
                        FLinearColor(.85f,.88f,.91f));
    ActionText=AddLine(WidgetTree,Stack,TEXT("ReviewAction"),14,
                       FLinearColor(.98f,.80f,.44f));
    EnemyOne=AddLine(WidgetTree,Stack,TEXT("ReviewEnemyOne"),15,
                     FLinearColor(.96f,.96f,1.f));
    EnemyOneBar=AddHealth(WidgetTree,Stack,TEXT("ReviewEnemyHP1"),
                          FLinearColor(.92f,.36f,.31f));
    EnemyTwo=AddLine(WidgetTree,Stack,TEXT("ReviewEnemyTwo"),15,
                     FLinearColor(.96f,.96f,1.f));
    EnemyTwoBar=AddHealth(WidgetTree,Stack,TEXT("ReviewEnemyHP2"),
                          FLinearColor(.94f,.57f,.27f));
    UpdateReviewHUD(TEXT("Harbor Patrol"),TEXT("PRESS F7/F8/F9 TO BEGIN"),
                    TEXT("All enemies provisional; no SaveGame."),{}, {});
#endif
}

void UTSTSSSliceEnemyReviewHUD::UpdateReviewHUD(
    const FString& WaveName, const FString& BattleState,
    const FString& LastAction, const TArray<FTSTSSCombatant>& Snapshot,
    const TArray<FName>& EnemyIds, bool bHybridReviewInput)
{
#if !UE_BUILD_SHIPPING
    if (!IsValid(Title.Get()) || !IsValid(Status.Get())) return;
    Title->SetText(FText::FromString(
        TEXT("TO SAIL THE STARRY SKY  /  ENEMY REVIEW\n") + WaveName));
    Status->SetText(FText::FromString(BattleState));
    Instruction->SetText(FText::FromString(bHybridReviewInput
        ? TEXT("WALKING ENCOUNTER /  J/K TARGET 1/2\n"
               "ESC FLEE (DURING TURN) / ENTER RETURN AFTER BATTLE\n"
               "REVIEW GOLD / ITEMS / XP ON VICTORY (NO SAVEGAME)")
        : TEXT("F7 Ender  F8 +Ionia  F9 +Lyra (post-splashdown)\n"
               "Q/E change wave (before battle)  R reset\n"
               "J/K attack foe 1/2  |  REVIEW ONLY")));
    ActionText->SetText(FText::FromString(LastAction));

    const UTextBlock* Names[]={EnemyOne.Get(),EnemyTwo.Get()};
    UProgressBar* Bars[]={EnemyOneBar.Get(),EnemyTwoBar.Get()};
    UTextBlock* Labels[]={EnemyOne.Get(),EnemyTwo.Get()};
    for (int32 I=0;I<2;++I)
    {
        const FTSTSSCombatant* Foe=EnemyIds.IsValidIndex(I)
            ? FindCombatant(Snapshot, EnemyIds[I]) : nullptr;
        const FString Label=Foe ? FString::Printf(
            TEXT("%d. %s   HP %d / %d"),I+1,
            *Foe->CharacterId.ToString(),Foe->Health,Foe->MaxHealth)
            : FString::Printf(TEXT("%d. SELECT A REVIEW BATTLE"),I+1);
        if (Labels[I]) Labels[I]->SetText(FText::FromString(Label));
        if (Bars[I]) Bars[I]->SetPercent((Foe && Foe->MaxHealth>0)
            ? FMath::Clamp(static_cast<float>(Foe->Health)/Foe->MaxHealth,0.f,1.f)
            : 0.f);
    }
#endif
}
