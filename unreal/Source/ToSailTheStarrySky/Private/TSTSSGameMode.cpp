#include "TSTSSGameMode.h"
#include "TSTSSExplorerCharacter.h"
#include "TSTSSFirstWakeReviewHUD.h"

ATSTSSGameMode::ATSTSSGameMode()
{
    DefaultPawnClass = ATSTSSExplorerCharacter::StaticClass();
#if !UE_BUILD_SHIPPING
    // Review-only overlay: live objective is derived from the pawn's state.
    // No UMG dependency or production UI/art authority is introduced.
    HUDClass = ATSTSSFirstWakeReviewHUD::StaticClass();
#endif
}
