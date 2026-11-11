#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "TSTSSResonatorFocusGameMode.generated.h"

// Review-only map override. Never replaces the real First Wake global game
// mode, saves, quest HUD or player pawn in the canonical campaign maps.
UCLASS()
class TOSAILTHESTARRYSKY_API ATSTSSResonatorFocusGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    ATSTSSResonatorFocusGameMode();
    bool IsFocusSpectatorStartEnabled() const { return bStartPlayersAsSpectators; }
    virtual void BeginPlay() override;
};
