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
    if (!IsValid(State) || State->IsChapterOneActOne())
    {
        return; // This debug overlay must not masquerade as Chapter 1 UI.
    }

    const float Margin = 24.f;
    const float PanelWidth = FMath::Max(0.f, FMath::Min(780.f, Canvas->ClipX - Margin * 2.f));
    if (PanelWidth < 440.f || Canvas->ClipY < 170.f)
    {
        return; // No illegible/offscreen overlay at very small sizes.
    }
    const bool bCompact = PanelWidth < 640.f;
    DrawRect(FLinearColor(0.012f, 0.024f, 0.035f, 0.84f),
             Margin, Margin, PanelWidth, 132.f);
    DrawText(TEXT("FIRST WAKE  |  PRELUDE REVIEW"),
             FLinearColor(0.35f, 0.90f, 0.93f, 1.f),
             Margin + 16.f, Margin + 10.f, GEngine->GetSmallFont(), 1.1f);
    DrawText(State->GetReviewObjectiveText(),
             FLinearColor::White,
             Margin + 16.f, Margin + 38.f, GEngine->GetMediumFont(), 1.f);

    // Three independent inspection lamps, tied to the same story bitmask
    // used by engineering signoff. Drawing cannot set or clear any bits.
    const auto InspectionMask = State->GetInspectionMask();
    const FLinearColor Complete(0.18f, 0.85f, 0.62f, 1.f);
    const FLinearColor Incomplete(0.28f, 0.34f, 0.40f, 1.f);
    DrawRect((InspectionMask & 0x01u) ? Complete : Incomplete,
             Margin + 16.f, Margin + 64.f, 11.f, 11.f);
    DrawRect((InspectionMask & 0x02u) ? Complete : Incomplete,
             Margin + 38.f, Margin + 64.f, 11.f, 11.f);
    DrawRect((InspectionMask & 0x04u) ? Complete : Incomplete,
             Margin + 60.f, Margin + 64.f, 11.f, 11.f);
    DrawText(bCompact ? TEXT("Systems: Lift / Pressure / Reserve")
                      : TEXT("ENGINEERING INSPECTIONS  |  Lift / Pressure / Reserve"),
             FLinearColor(0.77f, 0.84f, 0.86f, 1.f),
             Margin + 84.f, Margin + 62.f, GEngine->GetSmallFont(), bCompact ? 0.75f : 0.85f);

    DrawText(bCompact ? TEXT("WASD E interact J | PIE F6 save F9 load F7 Continue")
                      : TEXT("WASD: move | E: interact | J: objective | PIE F6: save F9: load | F7: Continue preview/confirm"),
             FLinearColor(0.77f, 0.84f, 0.86f, 1.f),
             Margin + 16.f, Margin + 88.f, GEngine->GetSmallFont(), bCompact ? 0.72f : 0.9f);
    DrawText(bCompact ? TEXT("Review only: no sea landing or Chapter 1 approval")
                      : TEXT("Review only: no launch, water landing, or Chapter 1 progression authorized"),
             FLinearColor(0.96f, 0.77f, 0.45f, 1.f),
             Margin + 16.f, Margin + 109.f, GEngine->GetSmallFont(), bCompact ? 0.72f : 0.75f);
#endif
}
