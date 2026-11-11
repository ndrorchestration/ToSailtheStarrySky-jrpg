#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Combat/TSS_CombatTurnManager.h"
#include "TSTSSResonatorFocusReviewActor.generated.h"

class UCameraComponent;
class UPointLightComponent;
class USceneComponent;
class UStaticMeshComponent;
class UTextRenderComponent;
class UDataTable;
class USoundBase;
class UTSTSSResonatorFocusHUD;

// Opt-in, non-shipping playable battle sandbox for TWO explicitly learned
// review spells. Never placed in First Wake, maps, or production save systems.
// The actual UTSS_CombatTurnManager executes both spells and physical AI hits.
UCLASS(Blueprintable)
class TOSAILTHESTARRYSKY_API ATSTSSResonatorFocusReviewActor : public AActor
{
    GENERATED_BODY()
public:
    ATSTSSResonatorFocusReviewActor();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere,Category="TSTSS|Review")
    bool bEnableFocusReview=false;

    // Explicit reviewer-only party stage; Ionia participates after her entry.
    UPROPERTY(EditAnywhere,Category="TSTSS|Review")
    bool bIoniaRecruitedForReview=true;

    UFUNCTION(BlueprintCallable,Category="TSTSS|Review")
    bool TryCastCentering();

    UFUNCTION(BlueprintCallable,Category="TSTSS|Review")
    bool TryCastResonantPulse();

    UFUNCTION(BlueprintPure,Category="TSTSS|Review")
    bool IsReviewReady() const {return bReviewReady;}

    UFUNCTION(BlueprintPure,Category="TSTSS|Review")
    UTSS_CombatTurnManager* GetReviewCombatManager() const
    {return CombatManager.Get();}

private:
    UPROPERTY(VisibleAnywhere) TObjectPtr<USceneComponent> ReviewRoot;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> ReviewCamera;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Ground;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UPointLightComponent> ArenaKeyLight;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UPointLightComponent> ArenaFillLight;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> EnderProxy;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> IoniaProxy;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> FoeProxy;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UTextRenderComponent> Label;

    UPROPERTY(VisibleAnywhere) TObjectPtr<UTSS_CombatTurnManager> CombatManager;
    UPROPERTY(Transient) TObjectPtr<UDataTable> AcceptedReviewTable;
    UPROPERTY(Transient) TObjectPtr<UTSTSSResonatorFocusHUD> ReviewHUD;
    UPROPERTY(Transient) TObjectPtr<USoundBase> CenteringSfx;
    UPROPERTY(Transient) TObjectPtr<USoundBase> PulseSfx;

    bool bReviewReady=false;
    bool bInputBound=false;
    float AutoTurnCountdown=.5f;
    float UiRefreshCountdown=0.f;
    FString LastReviewEvent;

    bool TryInitArena();
    void TryAttachReviewPlayer();
    bool TryCast(FName Skill,FName Target);
    void RefreshHUD();
    void PlaySound(USoundBase* Cue);

    void CastCenteringKey();
    void CastPulseKey();

    UFUNCTION()
    void OnAcceptedSkill(FName SkillId,FName ActorId,FName TargetId,
                         FName VfxCueId,FName AnimationCueId);
};
