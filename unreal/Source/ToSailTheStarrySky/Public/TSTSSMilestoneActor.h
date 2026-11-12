#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSMilestoneActor.generated.h"

UCLASS()
class TOSAILTHESTARRYSKY_API ATSTSSMilestoneActor : public AActor
{
    GENERATED_BODY()
public:
    ATSTSSMilestoneActor();
    UFUNCTION(BlueprintCallable, Category="TSTSS|First Wake")
    bool TryActivate(UTSTSSFirstWakeState* State);
#if WITH_EDITOR
    // Non-authoritative, strictly package-scoped review presentation.
    // The real E interaction and story/inspection gates remain unchanged.
    bool IsReviewActionable(const UTSTSSFirstWakeState* State) const;
    FString GetReviewDisplayName() const;
    void UpdateReviewBeacon(const UTSTSSFirstWakeState* State);
#endif
#if WITH_EDITOR
    // Synchronize review-only marker rays/physical blocking after a successful
    // SaveGame restore. Never modifies story, non-PIE or production actors.
    void ReconcileReviewCollisionAfterRestore(const UTSTSSFirstWakeState* State);
#endif
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|First Wake")
    ETSTSSFirstWakeBeat Milestone = ETSTSSFirstWakeBeat::FlyerDiscovered;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|First Wake")
    bool bIsInspectionStation = false;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|First Wake", meta=(EditCondition="bIsInspectionStation"))
    ETSTSSInspectionStation InspectionStation = ETSTSSInspectionStation::Lift;
    UFUNCTION(BlueprintImplementableEvent, Category="TSTSS|First Wake")
    void OnMilestoneActivated();

protected:
    virtual void BeginPlay() override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<class UStaticMeshComponent> InteractionMesh;
#if WITH_EDITORONLY_DATA
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Review")
    TObjectPtr<class UTextRenderComponent> ReviewBeacon;
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Review")
    TObjectPtr<class UStaticMeshComponent> ReviewBeaconBackdrop;
#endif
#if WITH_EDITOR
    bool bReviewBeaconInitialized = false;
    bool bReviewBeaconAvailable = false;
#endif
};
