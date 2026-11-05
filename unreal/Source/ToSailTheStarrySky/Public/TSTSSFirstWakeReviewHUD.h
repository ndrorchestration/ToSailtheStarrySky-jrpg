#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "TSTSSFirstWakeReviewHUD.generated.h"

// Temporary Prelude review overlay, deliberately separate from production UI.
// Reads the existing story state every frame; never advances a beat or saves.
UCLASS(NotBlueprintable)
class TOSAILTHESTARRYSKY_API ATSTSSFirstWakeReviewHUD : public AHUD
{
    GENERATED_BODY()

public:
    virtual void DrawHUD() override;
};
