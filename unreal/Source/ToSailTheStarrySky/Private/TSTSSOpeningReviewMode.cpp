#include "TSTSSOpeningReviewMode.h"
#include "TSTSSOpeningReviewWidget.h"
#include "Blueprint/UserWidget.h"
#include "GameFramework/HUD.h"

ATSTSSOpeningReviewMode::ATSTSSOpeningReviewMode()
{
    PlayerControllerClass = ATSTSSOpeningReviewController::StaticClass();
}

void ATSTSSOpeningReviewController::BeginPlay()
{
    Super::BeginPlay();
    if (!IsLocalController()) return;
    UTSTSSOpeningReviewWidget* Screen = CreateWidget<UTSTSSOpeningReviewWidget>(this, UTSTSSOpeningReviewWidget::StaticClass());
    if (!Screen) return;
    Screen->AddToViewport(100);
    bShowMouseCursor = true;
    UWidget* Focus = Screen->GetInitialFocus();
    SetInputMode(FInputModeUIOnly().SetWidgetToFocus(Focus ? Focus->TakeWidget() : Screen->TakeWidget()).SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock));
    if (AHUD* CurrentHUD = GetHUD()) CurrentHUD->bShowHUD = false;
}
