#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TSTSSOpeningReviewWidget.generated.h"

class UButton;
class UFileMediaSource;
class UMediaPlayer;
class UMediaSoundComponent;
class UMediaTexture;
class UWidget;

// Explicitly opted-in review screen; never the project's default menu.
UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSOpeningReviewWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    UWidget* GetInitialFocus() const;
protected:
    virtual void NativeOnInitialized() override;
    virtual void NativeDestruct() override;
private:
    UFUNCTION()
    void BeginJourney();
    UFUNCTION()
    void OnMovieOpened(FString OpenedUrl);
    UFUNCTION()
    void OnMovieOpenFailed(FString FailedUrl);

    UPROPERTY() TObjectPtr<UButton> NewGameButton;
    UPROPERTY() TObjectPtr<UButton> VideoButton;
    UPROPERTY() TObjectPtr<UWidget> FallbackPanel;
    UPROPERTY() TObjectPtr<UWidget> VideoPanel;
    UPROPERTY() TObjectPtr<UMediaPlayer> MoviePlayer;
    UPROPERTY() TObjectPtr<UMediaTexture> MovieTexture;
    UPROPERTY() TObjectPtr<UFileMediaSource> MovieSource;
    UPROPERTY() TObjectPtr<UMediaSoundComponent> MovieSound;
};
