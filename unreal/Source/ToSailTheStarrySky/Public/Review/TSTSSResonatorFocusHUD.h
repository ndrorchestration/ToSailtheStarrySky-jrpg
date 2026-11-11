#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TSTSSResonatorFocusHUD.generated.h"

class UTextBlock;

// Real UMG HUD for a strictly isolated playable Resonator ability sandbox.
UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSResonatorFocusHUD : public UUserWidget
{
    GENERATED_BODY()
public:
    void SetReviewState(const FString& Header,
                        const FString& Combatants,
                        const FString& LastAction,
                        const FString& Controls);
protected:
    virtual void NativeConstruct() override;
private:
    UPROPERTY(Transient) TObjectPtr<UTextBlock> HeadingText;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> CombatText;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> ActionText;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> ControlsText;
};
