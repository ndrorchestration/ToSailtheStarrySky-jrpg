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
class UTextBlock;
class ULevelSequencePlayer;
class ALevelSequenceActor;

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
    virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;
private:
    UFUNCTION()
    void BeginJourney();
    void StartOpening();
    void StopOpening();
    void RefreshOpeningCue();
    UFUNCTION()
    void FinishOpening();
    UFUNCTION()
    void OnOpeningSequenceFinished();
    UFUNCTION()
    void OnMovieOpened(FString OpenedUrl);
    UFUNCTION()
    void OnMovieOpenFailed(FString FailedUrl);

    bool bOpeningActive = false;
    bool bOpeningCompleted = false;
    bool bOpeningSequenceFinished = false;
    float OpeningSeconds = 0.f;
    int32 OpeningCueIndex = INDEX_NONE;
    UPROPERTY() TObjectPtr<UWidget> OpeningPanel;
    UPROPERTY() TObjectPtr<UTextBlock> OpeningCaption;
    UPROPERTY() TObjectPtr<UTextBlock> OpeningStage;
    UPROPERTY() TObjectPtr<ULevelSequencePlayer> OpeningPlayer;
    UPROPERTY() TObjectPtr<ALevelSequenceActor> OpeningActor;
    UPROPERTY() TObjectPtr<UButton> NewGameButton;
    UPROPERTY() TObjectPtr<UButton> VideoButton;
    UPROPERTY() TObjectPtr<UWidget> FallbackPanel;
    UPROPERTY() TObjectPtr<UWidget> VideoPanel;
    UPROPERTY() TObjectPtr<UMediaPlayer> MoviePlayer;
    UPROPERTY() TObjectPtr<UMediaTexture> MovieTexture;
    UPROPERTY() TObjectPtr<UFileMediaSource> MovieSource;
    UPROPERTY() TObjectPtr<UMediaSoundComponent> MovieSound;
};
