#pragma once
#include "CoreMinimal.h"
#include "TSTSSGameMode.h"
#include "GameFramework/PlayerController.h"
#include "TSTSSOpeningReviewMode.generated.h"

// Select this mode explicitly for a disposable review map; ordinary startup is unchanged.
UCLASS()
class TOSAILTHESTARRYSKY_API ATSTSSOpeningReviewController : public APlayerController
{
    GENERATED_BODY()
protected:
    virtual void BeginPlay() override;
};

UCLASS()
class TOSAILTHESTARRYSKY_API ATSTSSOpeningReviewMode : public ATSTSSGameMode
{
    GENERATED_BODY()
public:
    ATSTSSOpeningReviewMode();
};
