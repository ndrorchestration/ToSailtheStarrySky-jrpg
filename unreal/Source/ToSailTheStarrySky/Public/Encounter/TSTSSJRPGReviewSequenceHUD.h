#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Encounter/TSTSSJRPGReviewPresentation.h"
#include "Encounter/TSTSSJRPGReviewRewards.h"
#include "TSTSSJRPGReviewSequenceHUD.generated.h"

class UBorder;
class UTextBlock;

// Native full-screen sequence overlays for the review field and battle.
// Transient UMG only: no scene, screen resolution, save or input ownership.
UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSJRPGReviewSequenceHUD : public UUserWidget
{
    GENERATED_BODY()
public:
    void UpdatePresentation(ETSTSSJRPGReviewSequencePhase Phase,
                            float Progress,
                            const FTSTSSJRPGReviewReward& Reward,
                            bool bHasReward,
                            int32 GoldBalance);
protected:
    virtual void NativeConstruct() override;
private:
    UPROPERTY(Transient) TObjectPtr<UBorder> ScreenVeil;
    UPROPERTY(Transient) TObjectPtr<UBorder> ResultPanel;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> Headline;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> RewardLines;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> Footer;
};
