#include "Encounter/TSTSSJRPGReviewSequenceHUD.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"

namespace
{
    UTextBlock* MakeText(UWidgetTree* Tree,UVerticalBox* Stack,
                         const TCHAR* Id,int32 Size,FLinearColor Tint)
    {
        UTextBlock* T=Tree->ConstructWidget<UTextBlock>(
            UTextBlock::StaticClass(),FName(Id));
        FSlateFontInfo Font=T->GetFont();
        Font.Size=Size;
        T->SetFont(Font);
        T->SetColorAndOpacity(FSlateColor(Tint));
        T->SetAutoWrapText(true);
        if (UVerticalBoxSlot* Slot=Stack->AddChildToVerticalBox(T))
            Slot->SetPadding(FMargin(22.f,10.f));
        return T;
    }
}

void UTSTSSJRPGReviewSequenceHUD::NativeConstruct()
{
    Super::NativeConstruct();
#if !UE_BUILD_SHIPPING
    if (!WidgetTree) WidgetTree=NewObject<UWidgetTree>(this);
    if (WidgetTree->RootWidget) return;

    UCanvasPanel* Root=WidgetTree->ConstructWidget<UCanvasPanel>(
        UCanvasPanel::StaticClass(),TEXT("JRPGSequenceCanvas"));
    WidgetTree->RootWidget=Root;

    ScreenVeil=WidgetTree->ConstructWidget<UBorder>(
        UBorder::StaticClass(),TEXT("TransitionVeil"));
    UCanvasPanelSlot* VeilSlot=Root->AddChildToCanvas(ScreenVeil);
    VeilSlot->SetAnchors(FAnchors(0.f,0.f,1.f,1.f));
    VeilSlot->SetOffsets(FMargin(0.f));
    ScreenVeil->SetBrushColor(FLinearColor(.01f,.05f,.08f,0.f));

    ResultPanel=WidgetTree->ConstructWidget<UBorder>(
        UBorder::StaticClass(),TEXT("JRPGResultWindow"));
    ResultPanel->SetBrushColor(FLinearColor(.018f,.05f,.09f,.96f));
    UCanvasPanelSlot* PanelSlot=Root->AddChildToCanvas(ResultPanel);
    PanelSlot->SetAnchors(FAnchors(.5f,.5f,.5f,.5f));
    PanelSlot->SetAlignment(FVector2D(.5f,.5f));
    PanelSlot->SetSize(FVector2D(680.f,480.f));
    PanelSlot->SetPosition(FVector2D(0.f,0.f));
    UVerticalBox* Stack=WidgetTree->ConstructWidget<UVerticalBox>(
        UVerticalBox::StaticClass(),TEXT("JRPGResultStack"));
    ResultPanel->SetContent(Stack);

    Headline=MakeText(WidgetTree,Stack,TEXT("JRPGSequenceTitle"),33,
                      FLinearColor(1.f,.80f,.43f));
    RewardLines=MakeText(WidgetTree,Stack,TEXT("JRPGRewardItems"),18,
                         FLinearColor(.87f,.94f,.98f));
    Footer=MakeText(WidgetTree,Stack,TEXT("JRPGSequenceHint"),14,
                    FLinearColor(.49f,.85f,.86f));
    UpdatePresentation(ETSTSSJRPGReviewSequencePhase::Exploration,
                       0.f,FTSTSSJRPGReviewReward(),false,0);
#endif
}

void UTSTSSJRPGReviewSequenceHUD::UpdatePresentation(
    ETSTSSJRPGReviewSequencePhase Phase,float Progress,
    const FTSTSSJRPGReviewReward& Reward,bool bHasReward,int32 GoldBalance)
{
#if !UE_BUILD_SHIPPING
    if (!IsValid(ScreenVeil.Get()) || !IsValid(ResultPanel.Get()) ||
        !IsValid(Headline.Get()) || !IsValid(RewardLines.Get()) ||
        !IsValid(Footer.Get())) return;
    Progress=FMath::Clamp(Progress,0.f,1.f);
    if (Phase==ETSTSSJRPGReviewSequencePhase::Exploration ||
        Phase==ETSTSSJRPGReviewSequencePhase::Combat)
    {
        SetVisibility(ESlateVisibility::Collapsed);
        return;
    }
    SetVisibility(ESlateVisibility::HitTestInvisible);
    ResultPanel->SetVisibility(ESlateVisibility::Collapsed);
    FLinearColor Color(.02f,.08f,.14f,0.f);
    FString Title,Body,Hint;

    switch(Phase)
    {
    case ETSTSSJRPGReviewSequencePhase::EncounterFlash:
        // Quick rhythmic cyan/amber flash layered over the actual field.
        Color=FLinearColor(.08f+.35f*FMath::Sin(Progress*12.f),
                            .24f,.32f,.25f+.65f*Progress);
        Title=TEXT("ENCOUNTER!");
        Hint=TEXT("PREPARING BATTLE / REVIEW ONLY");
        break;
    case ETSTSSJRPGReviewSequencePhase::BattleReveal:
        Color=FLinearColor(.018f,.06f,.095f,1.f-.78f*Progress);
        Title=TEXT("BATTLE!");
        Hint=TEXT("ENTERING TURN-BASED COMBAT");
        break;
    case ETSTSSJRPGReviewSequencePhase::VictoryFanfare:
        Color=FLinearColor(.29f,.15f,.04f,.31f);
        Title=TEXT("VICTORY!");
        Hint=TEXT("BATTLE COMPLETE");
        break;
    case ETSTSSJRPGReviewSequencePhase::Celebration:
        Color=FLinearColor(.13f,.16f,.055f,.17f);
        Title=TEXT("VICTORY!");
        Hint=TEXT("THE PARTY CELEBRATES");
        break;
    case ETSTSSJRPGReviewSequencePhase::Rewards:
        Color=FLinearColor(.012f,.03f,.065f,.75f);
        Title=TEXT("BATTLE REWARDS");
        if (bHasReward && Reward.bReviewOnly)
        {
            Body=FString::Printf(TEXT("GOLD  +%d   |   TOTAL  %d\n"
                "EXPERIENCE  +%d EACH\n"),Reward.GoldEarned,
                GoldBalance,Reward.XpEachPartyMember);
            for(const FName Member:Reward.AwardedPartyIds)
                Body+=FString::Printf(TEXT("   %s  +%d XP\n"),
                                      *Member.ToString(),Reward.XpEachPartyMember);
            Body+=TEXT("\nITEMS RECEIVED:\n");
            for(const FTSTSSJRPGReviewLootLine& Line:Reward.Items)
                Body+=FString::Printf(TEXT("   %s  x%d\n"),
                                      *Line.DisplayName,Line.Quantity);
            Body+=TEXT("\n(Review ledger only; no campaign save.)");
        }
        else Body=TEXT("REWARD ADMISSION FAILED\nNO AWARD GRANTED");
        Hint=TEXT("ENTER  CONTINUE TO EXPLORATION");
        ResultPanel->SetVisibility(ESlateVisibility::Visible);
        break;
    case ETSTSSJRPGReviewSequencePhase::Defeat:
        Color=FLinearColor(.1f,.018f,.035f,.77f);
        Title=TEXT("PARTY DEFEATED");
        Body=TEXT("NO ITEMS, GOLD OR EXPERIENCE AWARDED\n"
                  "The review party returns to the safe camp.");
        Hint=TEXT("ENTER  RETURN TO CAMP");
        ResultPanel->SetVisibility(ESlateVisibility::Visible);
        break;
    case ETSTSSJRPGReviewSequencePhase::ReturnFlash:
        Color=FLinearColor(.05f,.16f,.18f,.25f+.72f*Progress);
        Title=TEXT("RETURNING...");
        Hint=TEXT("RESTORING EXPLORATION");
        break;
    case ETSTSSJRPGReviewSequencePhase::ReturnReady:
        Color=FLinearColor(.02f,.08f,.14f,1.f);
        Title=TEXT("RETURNING...");
        break;
    default:break;
    }
    ScreenVeil->SetBrushColor(Color);
    Headline->SetText(FText::FromString(Title));
    RewardLines->SetText(FText::FromString(Body));
    Footer->SetText(FText::FromString(Hint));
    // Show title/hint on transitions but not the wide item window;
    // the existing main battle HUD stays visible in combat.
    if (ResultPanel->GetVisibility()!=ESlateVisibility::Visible &&
        (Phase==ETSTSSJRPGReviewSequencePhase::EncounterFlash ||
         Phase==ETSTSSJRPGReviewSequencePhase::BattleReveal ||
         Phase==ETSTSSJRPGReviewSequencePhase::VictoryFanfare ||
         Phase==ETSTSSJRPGReviewSequencePhase::Celebration))
    {
        ResultPanel->SetVisibility(ESlateVisibility::Visible);
    }
#endif
}
