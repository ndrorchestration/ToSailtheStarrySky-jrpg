#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TSTSSOpeningReviewWidget.generated.h"

class UButton;

// Opt-in review screen; never installed as the project's default menu.
UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSOpeningReviewWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    UWidget* GetInitialFocus() const;
protected:
    virtual void NativeOnInitialized() override;
private:
    UFUNCTION()
    void BeginJourney();
    UPROPERTY()
    TObjectPtr<UButton> NewGameButton;
};
