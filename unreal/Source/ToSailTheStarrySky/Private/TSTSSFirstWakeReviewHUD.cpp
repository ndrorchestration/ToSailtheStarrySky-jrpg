#include "TSTSSFirstWakeReviewHUD.h"
#include "TSTSSExplorerCharacter.h"
#include "TSTSSFirstWakeState.h"
#include "Engine/Engine.h"
#include "Engine/Canvas.h"
#include "Engine/World.h"
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
    // Isolated Seabourne visual-review map must not inherit the Prelude
    // objective ("Find Ionia's flyer") or pretend sailing is playable.
    const UWorld* World = GetWorld();
    if (World && World->GetOutermost() &&
        World->GetOutermost()->GetName() ==
            TEXT("/Game/TSTSS/Review/SeabourneRecovery/L_CoastalShip_SeabourneReview"))
    {
        const float Margin = 24.f;
        const float Width = FMath::Min(670.f, Canvas->ClipX - Margin * 2.f);
        if (Width >= 440.f && Canvas->ClipY >= 170.f)
        {
            DrawRect(FLinearColor(0.012f, 0.024f, 0.035f, 0.87f),
                     Margin, Margin, Width, 106.f);
            DrawText(TEXT("AUREATE WAKE  |  SEABOURNE VISUAL REVIEW"),
                     FLinearColor(0.35f, 0.90f, 0.93f, 1.f),
                     Margin + 16.f, Margin + 12.f,
                     GEngine->GetSmallFont(), 1.06f);
            DrawText(TEXT("Noncanonical proxy  |  Wings folded; hydrofoils deployed"),
                     FLinearColor::White, Margin + 16.f, Margin + 41.f,
                     GEngine->GetSmallFont(), 0.90f);
            DrawText(TEXT("WASD: explore pier  |  No ship sailing / story progression here"),
                     FLinearColor(0.96f, 0.77f, 0.45f, 1.f),
                     Margin + 16.f, Margin + 72.f,
                     GEngine->GetSmallFont(), 0.83f);
        }
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

    DrawText(bCompact ? TEXT("WASD E interact J objective K scene | PIE F6 save F9 load F7 Continue")
                      : TEXT("WASD: move | E: interact | J: objective | K: gated scene | PIE F6: save F9: load | F7: Continue preview/confirm"),
             FLinearColor(0.77f, 0.84f, 0.86f, 1.f),
             Margin + 16.f, Margin + 88.f, GEngine->GetSmallFont(), bCompact ? 0.72f : 0.9f);
    DrawText(bCompact ? TEXT("Review only: no sea landing or Chapter 1 approval")
                      : TEXT("Review only: no launch, water landing, or Chapter 1 progression authorized"),
             FLinearColor(0.96f, 0.77f, 0.45f, 1.f),
             Margin + 16.f, Margin + 109.f, GEngine->GetSmallFont(), bCompact ? 0.72f : 0.75f);

    // Strongly contrasted review-only interaction prompt. The pawn uses the
    // exact camera trace and *separate* 300 cm pawn reach as E; display does
    // not grant an action, broaden reach or advance the story.
    if (Canvas->ClipX >= 640.f && Canvas->ClipY >= 360.f)
    {
        const FString AimedPrompt = Explorer->GetReviewAimStatus();
        const bool bReady = AimedPrompt.StartsWith(TEXT("[E]"));
        const FString Prompt = AimedPrompt.IsEmpty()
            ? TEXT("FOLLOW THE GOLD MARKER  |  LOOK AT IT TO INTERACT")
            : AimedPrompt;
        const float Width = FMath::Min(690.f, Canvas->ClipX - 48.f);
        const float Left = (Canvas->ClipX - Width) * 0.5f;
        const float Top = Canvas->ClipY - 88.f;
        const FLinearColor Accent = bReady
            ? FLinearColor(1.f, 0.81f, 0.39f, 1.f)
            : FLinearColor(0.76f, 0.88f, 0.93f, 1.f);
        DrawRect(FLinearColor(0.015f, 0.028f, 0.039f, 0.92f),
                 Left, Top, Width, 55.f);
        DrawRect(Accent, Left, Top, 5.f, 55.f);
        DrawText(Prompt, Accent, Left + 20.f, Top + 15.f,
                 GEngine->GetMediumFont(), Width < 580.f ? .70f : .90f);
        // A minimal reticle makes aiming at the true E visibility ray clear.
        DrawRect(Accent, Canvas->ClipX * .5f - 3.f,
                 Canvas->ClipY * .5f - 3.f, 6.f, 6.f);
    }

    // Hilltonia is a walkable, non-interactive review extension, NOT a new
    // story marker. A geographically scoped wayfinding panel distinguishes
    // the stone road and forest track from the gold [E] plot interactions.
    // It is not a compass, pathfinder, quest authorization or saved state.
    if (World && World->GetOutermost() &&
        World->GetOutermost()->GetName() ==
            TEXT("/Game/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview") &&
        (World->WorldType == EWorldType::PIE ||
         World->WorldType == EWorldType::Game) &&
        World->GetNetMode() == NM_Standalone &&
        Canvas->ClipX >= 1260.f && Canvas->ClipY >= 500.f)
    {
        const FVector Position = Explorer->GetActorLocation();
        if (!Position.ContainsNaN() &&
            FMath::IsFinite(Position.X) &&
            FMath::IsFinite(Position.Y) &&
            FMath::IsFinite(Position.Z) &&
            Position.X <= -2800.f && Position.X >= -9700.f &&
            Position.Y >= -3650.f && Position.Y <= 1200.f)
        {
            const bool bWoodland = Position.X < -6500.f &&
                Position.X > -8100.f && Position.Y < -850.f;
            const bool bVillage = Position.X <= -6800.f;
            const TCHAR* Direction = bWoodland
                ? TEXT("WOODLAND TRACK  |  FOLLOW THE FOREST ROAD")
                : bVillage
                    ? TEXT("HILLTONIA SQUARE  |  FOREST PATH INLAND")
                    : TEXT("HARBOR TO HILLTONIA  |  FOLLOW ROAD WEST");
            const float Left = Canvas->ClipX - 410.f;
            const float Top = 24.f;
            DrawRect(FLinearColor(0.012f, 0.036f, 0.026f, 0.91f),
                     Left, Top, 386.f, 101.f);
            DrawText(TEXT("HILLTONIA  |  EXPLORATION ROUTE"),
                     FLinearColor(0.69f, 0.94f, 0.78f, 1.f),
                     Left + 12.f, Top + 12.f,
                     GEngine->GetSmallFont(), 0.94f);
            DrawText(Direction, FLinearColor::White,
                     Left + 12.f, Top + 43.f,
                     GEngine->GetSmallFont(), 0.78f);
            DrawText(TEXT("WASD: walk  |  Scenery is NOT an [E] quest target"),
                     FLinearColor(0.96f, 0.81f, 0.48f, 1.f),
                     Left + 12.f, Top + 72.f,
                     GEngine->GetSmallFont(), 0.74f);
        }
    }
#endif
}
