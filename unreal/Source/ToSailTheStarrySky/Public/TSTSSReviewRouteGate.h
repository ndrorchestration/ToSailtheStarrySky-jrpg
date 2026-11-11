#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TSTSSReviewRouteSession.h"
#include "TSTSSReviewRouteGate.generated.h"

UCLASS()
class TOSAILTHESTARRYSKY_API ATSTSSReviewRouteGate : public AActor
{
    GENERATED_BODY()
public:
    ATSTSSReviewRouteGate();

    // E-interaction only; neither overlap nor BeginPlay grants progression.
    bool TryTraverse(class ATSTSSExplorerCharacter* Player);

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Review Route")
    ETSTSSReviewMap DepartureStage = ETSTSSReviewMap::DenithHarbor;

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Review Route")
    TObjectPtr<class UStaticMeshComponent> InteractionMesh;

private:
    bool bTriggered = false;
};
