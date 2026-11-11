#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Enemies/TSTSSSliceEnemyCatalog.h"
#include "TSTSSSliceEnemyReviewAI.generated.h"

class UTSS_CombatTurnManager;

// Optional non-shipping Blueprint action: it does not own or duplicate combat math.
UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSSliceEnemyReviewAI : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category="TSTSS|Slice Review|Enemies")
    static bool TryActReviewEnemy(UTSS_CombatTurnManager* Manager,
                                  ETSTSSSliceEnemyKind Kind,
                                  FName InstanceId);
};
