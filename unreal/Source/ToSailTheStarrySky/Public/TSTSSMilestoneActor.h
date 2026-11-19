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
    // Fail-closed whitelist; no direct interaction may certify physical sea events.
    static bool IsManualBeatAllowed(ETSTSSFirstWakeBeat Beat);
    UFUNCTION(BlueprintCallable, Category="TSTSS|First Wake")
    bool TryActivate(UTSTSSFirstWakeState* State);
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|First Wake")
    ETSTSSFirstWakeBeat Milestone = ETSTSSFirstWakeBeat::FlyerDiscovered;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|First Wake")
    bool bIsInspectionStation = false;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|First Wake", meta=(EditCondition="bIsInspectionStation"))
    ETSTSSInspectionStation InspectionStation = ETSTSSInspectionStation::Lift;
    UFUNCTION(BlueprintImplementableEvent, Category="TSTSS|First Wake")
    void OnMilestoneActivated();
protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<class UStaticMeshComponent> InteractionMesh;
};
