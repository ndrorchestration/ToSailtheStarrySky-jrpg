#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TSTSSSliceEnemyReviewHUD.generated.h"

class UTextBlock;
class UProgressBar;
struct FTSTSSCombatant;

// Native UMG review-only overlay. Does NOT replace or edit a game's primary HUD.
// Every displayed HP value comes from UTSS_CombatTurnManager's snapshot.
UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSSliceEnemyReviewHUD : public UUserWidget
{
    GENERATED_BODY()
public:
    void UpdateReviewHUD(const FString& WaveName, const FString& BattleState,
                         const FString& LastAction,
                         const TArray<FTSTSSCombatant>& Snapshot,
                         const TArray<FName>& EnemyIds,
                         bool bHybridReviewInput = false);

protected:
    virtual void NativeConstruct() override;

private:
    UPROPERTY(Transient) TObjectPtr<UTextBlock> Title;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> Status;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> Instruction;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> ActionText;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> EnemyOne;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> EnemyTwo;
    UPROPERTY(Transient) TObjectPtr<UProgressBar> EnemyOneBar;
    UPROPERTY(Transient) TObjectPtr<UProgressBar> EnemyTwoBar;
};
