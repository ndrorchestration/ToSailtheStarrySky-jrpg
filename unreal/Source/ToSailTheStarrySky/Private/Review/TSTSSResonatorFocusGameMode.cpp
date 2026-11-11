#include "Review/TSTSSResonatorFocusGameMode.h"
#include "GameFramework/SpectatorPawn.h"
#include "GameFramework/HUD.h"
#include "GameFramework/PlayerController.h"

ATSTSSResonatorFocusGameMode::ATSTSSResonatorFocusGameMode()
{
    DefaultPawnClass=ASpectatorPawn::StaticClass();
    PlayerControllerClass=APlayerController::StaticClass();
    HUDClass=AHUD::StaticClass(); // NOT ATSTSSFirstWakeReviewHUD.
    bStartPlayersAsSpectators=true;
}
void ATSTSSResonatorFocusGameMode::BeginPlay()
{
    Super::BeginPlay();
#if !UE_BUILD_SHIPPING
    UE_LOG(LogTemp,Display,
        TEXT("TSTSS_FOCUS_GAMEMODE_ACTIVE: no First Wake prelude HUD/pawn"));
#endif
}
