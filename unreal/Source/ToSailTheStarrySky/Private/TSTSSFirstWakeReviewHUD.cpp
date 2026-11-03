#include "TSTSSFirstWakeReviewHUD.h"
#include "TSTSSExplorerCharacter.h"
#include "TSTSSFirstWakeState.h"
#include "Engine/Engine.h"
#include "Engine/Canvas.h"
#include "GameFramework/PlayerController.h"

// Draw only in non-shipping review builds. The story state remains the
// authority; no separate HUD progression, timers or persistent cache.
void ATSTSSFirstWakeReviewHUD::DrawHUD()
{
    Super::DrawHUD();
#if !UE_BUILD_SHIPPING
    if (!Canvas || !GEngine || !PlayerOwner)
    {
        return;
    }
    const ATSTSSExplorerCharacter* Explorer =
        Cast<ATSTSSExplorerCharacter>(PlayerOwner->GetPawn());
    if (!IsValid(Explorer))
    {
        return;
    }
    const UTSTSSFirstWakeState* State = Explorer->GetFirstWakeState();
    if (!IsValid(State))
    {
        return;
    }

    const float Margin = 24.f;
    const float PanelWidth = FMath::Max(0.f, FMath::Min(780.f, Canvas->ClipX - Margin * 2.f));
    if (PanelWidth < 440.f || Canvas->ClipY < 160.f)
    {
        return; // No illegible/offscreen overlay at very small sizes.
    }
    DrawRect(FLinearColor(0.012f, 0.024f, 0.035f, 0.84f),
             Margin, Margin, PanelWidth, 122.f);
    DrawText(TEXT("FIRST WAKE  |  PRELUDE REVIEW"),
             FLinearColor(0.35f, 0.90f, 0.93f, 1.f),
             Margin + 16.f, Margin + 10.f, GEngine->GetSmallFont(), 1.1f);
    DrawText(State->GetReviewObjectiveText(),
             FLinearColor::White,
             Margin + 16.f, Margin + 38.f, GEngine->GetMediumFont(), 1.f);
    DrawText(TEXT("WASD: move  |  E: interact  |  J: objective  |  F5/F9: review save/load"),
             FLinearColor(0.77f, 0.84f, 0.86f, 1.f),
             Margin + 16.f, Margin + 82.f, GEngine->GetSmallFont(), 0.9f);
    DrawText(TEXT("Review only: no launch, water landing, or Chapter 1 progression authorized"),
             FLinearColor(0.96f, 0.77f, 0.45f, 1.f),
             Margin + 16.f, Margin + 101.f, GEngine->GetSmallFont(), 0.75f);
#endif
}
