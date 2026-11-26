#include "TSTSSOpeningReviewWidget.h"
#include "TSTSSFirstWakeOpeningCues.h"
#include "LevelSequence.h"
#include "LevelSequenceActor.h"
#include "LevelSequencePlayer.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Blueprint/WidgetTree.h"
#include "Brushes/SlateColorBrush.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Image.h"
#include "Components/ScaleBox.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "FileMediaSource.h"
#include "GameFramework/HUD.h"
#include "GameFramework/PlayerController.h"
#include "HAL/PlatformFileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/PackageName.h"
#include "MediaPlayer.h"
#include "MediaSoundComponent.h"
#include "MediaTexture.h"
#include "Misc/Paths.h"

void UTSTSSOpeningReviewWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    if (!WidgetTree) return;
    UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass());
    WidgetTree->RootWidget = Root;

    // The fallback stays usable if the private movie is absent or fails to open.
    UCanvasPanel* Fallback = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass());
    FallbackPanel = Fallback;
    UCanvasPanelSlot* FallbackSlot = Root->AddChildToCanvas(Fallback);
    FallbackSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
    FallbackSlot->SetOffsets(FMargin(0));

    UBorder* Veil = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass());
    Veil->SetBrushColor(FLinearColor(0.008f, 0.025f, 0.045f, 0.90f));
    UCanvasPanelSlot* VeilSlot = Fallback->AddChildToCanvas(Veil);
    VeilSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
    VeilSlot->SetOffsets(FMargin(0));

    UVerticalBox* Column = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass());
    UCanvasPanelSlot* ColumnSlot = Fallback->AddChildToCanvas(Column);
    ColumnSlot->SetAnchors(FAnchors(0.08f, 0.16f, 0.82f, 0.86f));
    ColumnSlot->SetOffsets(FMargin(0));
    auto AddText = [this, Column](const TCHAR* Copy, int32 Size, const FLinearColor Color, float BottomPadding)
    {
        UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
        Text->SetText(FText::FromString(Copy));
        Text->SetColorAndOpacity(FSlateColor(Color));
        FSlateFontInfo Font = Text->GetFont();
        Font.Size = Size;
        Text->SetFont(Font);
        Text->SetAutoWrapText(true);
        Column->AddChildToVerticalBox(Text)->SetPadding(FMargin(0.f, 0.f, 0.f, BottomPadding));
    };
    AddText(TEXT("A JOURNEY BEYOND THE HORIZON"), 15, FLinearColor(0.48f, 0.84f, 0.86f, 1.f), 22.f);
    AddText(TEXT("TO SAIL THE"), 30, FLinearColor(0.95f, 0.94f, 0.85f, 1.f), 0.f);
    AddText(TEXT("STARRY SKY"), 54, FLinearColor(0.98f, 0.94f, 0.79f, 1.f), 25.f);
    AddText(TEXT("Every voyage begins with a single note."), 19, FLinearColor(0.76f, 0.85f, 0.85f, 1.f), 40.f);
    NewGameButton = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass());
    NewGameButton->OnClicked.AddDynamic(this, &UTSTSSOpeningReviewWidget::BeginJourney);
    UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
    Label->SetText(FText::FromString(TEXT("  NEW GAME  ")));
    FSlateFontInfo LabelFont = Label->GetFont();
    LabelFont.Size = 20;
    Label->SetFont(LabelFont);
    NewGameButton->AddChild(Label);
    USizeBox* ButtonBox = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass());
    ButtonBox->SetWidthOverride(220.f);
    ButtonBox->SetHeightOverride(50.f);
    ButtonBox->AddChild(NewGameButton);
    Column->AddChildToVerticalBox(ButtonBox);

    const FString MoviePath = FPaths::ConvertRelativePathToFull(
        FPaths::Combine(FPaths::ProjectContentDir(), TEXT("Movies/TSTSS_Title_Review.mp4")));
    if (!FPlatformFileManager::Get().GetPlatformFile().FileExists(*MoviePath)) return;

    MoviePlayer = NewObject<UMediaPlayer>(this);
    MovieTexture = NewObject<UMediaTexture>(this);
    MovieSource = NewObject<UFileMediaSource>(this);
    MovieSource->SetFilePath(MoviePath);
    MoviePlayer->PlayOnOpen = true;
    MoviePlayer->OnMediaOpened.AddDynamic(this, &UTSTSSOpeningReviewWidget::OnMovieOpened);
    MoviePlayer->OnMediaOpenFailed.AddDynamic(this, &UTSTSSOpeningReviewWidget::OnMovieOpenFailed);
    MovieTexture->SetMediaPlayer(MoviePlayer);
    MovieTexture->UpdateResource();

    // A fixed 1280x720 canvas is scaled as a unit: the live hit target tracks
    // the button baked into the 16:9 film, including at non-16:9 viewports.
    UScaleBox* Scale = WidgetTree->ConstructWidget<UScaleBox>(UScaleBox::StaticClass());
    VideoPanel = Scale;
    Scale->SetStretch(EStretch::ScaleToFit);
    Scale->SetVisibility(ESlateVisibility::Collapsed);
    UCanvasPanelSlot* ScaleSlot = Root->AddChildToCanvas(Scale);
    ScaleSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
    ScaleSlot->SetOffsets(FMargin(0));
    USizeBox* Frame = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass());
    Frame->SetWidthOverride(1280.f);
    Frame->SetHeightOverride(720.f);
    Scale->AddChild(Frame);
    UCanvasPanel* MovieCanvas = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass());
    Frame->AddChild(MovieCanvas);

    UImage* MovieImage = WidgetTree->ConstructWidget<UImage>(UImage::StaticClass());
    FSlateBrush MovieBrush;
    MovieBrush.SetResourceObject(MovieTexture);
    MovieBrush.ImageSize = FVector2D(1280.f, 720.f);
    MovieImage->SetBrush(MovieBrush);
    MovieImage->SetVisibility(ESlateVisibility::HitTestInvisible);
    UCanvasPanelSlot* ImageSlot = MovieCanvas->AddChildToCanvas(MovieImage);
    ImageSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
    ImageSlot->SetOffsets(FMargin(0));

    VideoButton = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass());
    VideoButton->SetToolTipText(FText::FromString(TEXT("New Game")));
    FButtonStyle Style;
    Style.SetNormal(FSlateColorBrush(FLinearColor(0.f, 0.f, 0.f, 0.f)));
    Style.SetHovered(FSlateColorBrush(FLinearColor(1.f, 0.83f, 0.4f, 0.14f)));
    Style.SetPressed(FSlateColorBrush(FLinearColor(1.f, 0.9f, 0.6f, 0.26f)));
    VideoButton->SetStyle(Style);
    VideoButton->OnClicked.AddDynamic(this, &UTSTSSOpeningReviewWidget::BeginJourney);
    UCanvasPanelSlot* VideoButtonSlot = MovieCanvas->AddChildToCanvas(VideoButton);
    VideoButtonSlot->SetPosition(FVector2D(84.f, 347.f));
    VideoButtonSlot->SetSize(FVector2D(335.f, 77.f));

    if (APlayerController* Controller = GetOwningPlayer())
    {
        MovieSound = NewObject<UMediaSoundComponent>(Controller);
        MovieSound->SetMediaPlayer(MoviePlayer);
        MovieSound->RegisterComponent();
        MovieSound->Activate();
    }
    if (!MoviePlayer->OpenSource(MovieSource))
    {
        OnMovieOpenFailed(MoviePath);
    }
}

void UTSTSSOpeningReviewWidget::OnMovieOpened(FString OpenedUrl)
{
    (void)OpenedUrl;
    if (bOpeningActive || bOpeningCompleted || !MoviePlayer || !VideoPanel || !FallbackPanel) return;
    MoviePlayer->SetLooping(true);
    FallbackPanel->SetVisibility(ESlateVisibility::Collapsed);
    VideoPanel->SetVisibility(ESlateVisibility::Visible);
    if (VideoButton && GetOwningPlayer()) VideoButton->SetUserFocus(GetOwningPlayer());
}

void UTSTSSOpeningReviewWidget::OnMovieOpenFailed(FString FailedUrl)
{
    (void)FailedUrl;
    if (bOpeningActive || bOpeningCompleted) return;
    if (VideoPanel) VideoPanel->SetVisibility(ESlateVisibility::Collapsed);
    if (FallbackPanel) FallbackPanel->SetVisibility(ESlateVisibility::Visible);
    if (NewGameButton && GetOwningPlayer()) NewGameButton->SetUserFocus(GetOwningPlayer());
}

UWidget* UTSTSSOpeningReviewWidget::GetInitialFocus() const
{
    return VideoPanel && VideoPanel->GetVisibility() == ESlateVisibility::Visible
        ? static_cast<UWidget*>(VideoButton.Get()) : static_cast<UWidget*>(NewGameButton.Get());
}

void UTSTSSOpeningReviewWidget::NativeDestruct()
{
    StopOpening();
    if (MovieSound)
    {
        MovieSound->Stop();
        MovieSound->DestroyComponent();
        MovieSound = nullptr;
    }
    if (MoviePlayer) MoviePlayer->Close();
    Super::NativeDestruct();
}

void UTSTSSOpeningReviewWidget::BeginJourney()
{
    APlayerController* Controller = GetOwningPlayer();
    UWorld* World = Controller ? Controller->GetWorld() : nullptr;
    if (!World || (World->WorldType != EWorldType::PIE &&
                   World->WorldType != EWorldType::Game))
    {
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_REVIEW_NEW_GAME_HOLD reason=not_playable_world"));
        return;
    }

    // Begin at the existing seven-stop playable prelude, not the decorative
    // VS01 staging map. This does not skip hiring, inspections, sea contact,
    // flotation, or any explicit subsequent K scene-travel gate.
    const FString PreludeMap(TEXT("/Game/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview"));
    if (!FPackageName::DoesPackageExist(PreludeMap))
    {
        UE_LOG(LogTemp, Error,
            TEXT("TSTSS_REVIEW_NEW_GAME_HOLD reason=prelude_map_missing path=%s"),
            *PreludeMap);
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 8.f, FColor::Red,
                TEXT("Review New Game unavailable: the playable Prelude map is missing"));
        }
        return; // Keep the menu intact; never pretend the game has started.
    }

#if !UE_BUILD_SHIPPING
    if (!bOpeningCompleted && FParse::Param(FCommandLine::Get(), TEXT("TSTSSFirstWakeNarrationReview")))
    {
        if (!bOpeningActive) StartOpening();
        return;
    }
#endif
    // The title controller explicitly selected UIOnly input. Return focus to
    // gameplay BEFORE opening the traversable review level; otherwise Slate
    // may keep the old menu focused and WASD/E never reach the new pawn.
    RemoveFromParent();
    Controller->bShowMouseCursor = false;
    Controller->SetInputMode(FInputModeGameOnly());
    if (AHUD* CurrentHUD = Controller->GetHUD()) CurrentHUD->bShowHUD = true;
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_REVIEW_NEW_GAME_ROUTE route=%s input_mode=game_only progress_reset_by_fresh_map=1"),
        *PreludeMap);
    UGameplayStatics::OpenLevel(Controller, FName(*PreludeMap));
}

void UTSTSSOpeningReviewWidget::StartOpening()
{
    using namespace TSTSSFirstWakeOpening;
    APlayerController* Controller = GetOwningPlayer();
    UCanvasPanel* Root = WidgetTree ? Cast<UCanvasPanel>(WidgetTree->RootWidget) : nullptr;
    if (!Controller || !Root || bOpeningActive || bOpeningCompleted) return;

    bOpeningActive = true;
    OpeningSeconds = 0.f;
    OpeningCueIndex = INDEX_NONE;
    if (MoviePlayer)
    {
        MoviePlayer->OnMediaOpened.RemoveDynamic(this, &UTSTSSOpeningReviewWidget::OnMovieOpened);
        MoviePlayer->OnMediaOpenFailed.RemoveDynamic(this, &UTSTSSOpeningReviewWidget::OnMovieOpenFailed);
        MoviePlayer->Close();
    }
    if (MovieSound) MovieSound->Stop();
    if (FallbackPanel) FallbackPanel->SetVisibility(ESlateVisibility::Collapsed);
    if (VideoPanel) VideoPanel->SetVisibility(ESlateVisibility::Collapsed);

    // Native Sequencer asset remains private until its visuals, voices and
    // map bindings are verified. No third-party MP4 is used here.
    const TCHAR* SequencePackage = TEXT("/Game/TSTSS/Review/Cinematics/LS_FirstWakeOpening_PRIVATE");
    if (FPackageName::DoesPackageExist(SequencePackage))
    {
        ULevelSequence* Sequence = LoadObject<ULevelSequence>(nullptr,
            TEXT("/Game/TSTSS/Review/Cinematics/LS_FirstWakeOpening_PRIVATE.LS_FirstWakeOpening_PRIVATE"));
        if (Sequence)
        {
            FMovieSceneSequencePlaybackSettings Settings;
            Settings.bAutoPlay = false;
            ALevelSequenceActor* SpawnedActor = nullptr;
            OpeningPlayer = ULevelSequencePlayer::CreateLevelSequencePlayer(
                Controller, Sequence, Settings, SpawnedActor);
            OpeningActor = SpawnedActor;
        }
    }

    UCanvasPanel* Panel = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass());
    OpeningPanel = Panel;
    UCanvasPanelSlot* PanelSlot = Root->AddChildToCanvas(Panel);
    PanelSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
    PanelSlot->SetOffsets(FMargin(0));
    if (!OpeningPlayer)
    {
        UBorder* Black = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass());
        Black->SetBrushColor(FLinearColor(0.008f, 0.012f, 0.02f, 1.f));
        UCanvasPanelSlot* BlackSlot = Panel->AddChildToCanvas(Black);
        BlackSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
        BlackSlot->SetOffsets(FMargin(0));
        Black->SetVisibility(ESlateVisibility::HitTestInvisible);
        OpeningStage = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
        OpeningStage->SetJustification(ETextJustify::Center);
        OpeningStage->SetColorAndOpacity(FSlateColor(FLinearColor(0.7f, 0.8f, 0.85f)));
        UCanvasPanelSlot* StageSlot = Panel->AddChildToCanvas(OpeningStage);
        StageSlot->SetAnchors(FAnchors(0.1f, 0.25f, 0.9f, 0.5f));
        StageSlot->SetOffsets(FMargin(0));
    }
    UBorder* SubtitleBack = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass());
    SubtitleBack->SetBrushColor(FLinearColor(0.015f, 0.02f, 0.03f, 0.85f));
    SubtitleBack->SetPadding(FMargin(20.f, 12.f));
    UCanvasPanelSlot* SubtitleSlot = Panel->AddChildToCanvas(SubtitleBack);
    SubtitleSlot->SetAnchors(FAnchors(0.12f, 0.69f, 0.88f, 0.91f));
    SubtitleSlot->SetOffsets(FMargin(0));
    OpeningCaption = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
    FSlateFontInfo Font = OpeningCaption->GetFont();
    Font.Size = 24;
    OpeningCaption->SetFont(Font);
    OpeningCaption->SetAutoWrapText(true);
    OpeningCaption->SetJustification(ETextJustify::Center);
    OpeningCaption->SetColorAndOpacity(FSlateColor(FLinearColor::White));
    SubtitleBack->AddChild(OpeningCaption);

    UButton* Skip = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass());
    UTextBlock* SkipText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
    SkipText->SetText(FText::FromString(TEXT("  Skip opening  ")));
    Skip->AddChild(SkipText);
    Skip->OnClicked.AddDynamic(this, &UTSTSSOpeningReviewWidget::FinishOpening);
    UCanvasPanelSlot* SkipSlot = Panel->AddChildToCanvas(Skip);
    SkipSlot->SetAnchors(FAnchors(1.f, 0.f));
    SkipSlot->SetAlignment(FVector2D(1.f, 0.f));
    SkipSlot->SetPosition(FVector2D(-24.f, 24.f));
    SkipSlot->SetAutoSize(true);
    Skip->SetUserFocus(Controller);

    UE_LOG(LogTemp, Display, TEXT("TSTSS_FIRST_WAKE_NARRATION_START native_sequence=%d duration=%.1f"),
        OpeningPlayer ? 1 : 0, Duration);
    if (OpeningPlayer) OpeningPlayer->Play();
    RefreshOpeningCue();
}

void UTSTSSOpeningReviewWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);
    if (!bOpeningActive) return;
    // Use the native sequence clock when authored; otherwise a text-only
    // review uses widget tick time. Paused/invalid clocks do not advance.
    if (OpeningPlayer)
    {
        OpeningSeconds = OpeningPlayer->GetCurrentTime().AsSeconds();
        // An ended sequence must not trap the title UI. The asset duration
        // must be checked against the authored cue contract in native QA.
        if (!OpeningPlayer->IsPlaying())
        {
            UE_LOG(LogTemp, Display, TEXT("TSTSS_FIRST_WAKE_NARRATION_SEQUENCE_ENDED seconds=%.2f"), OpeningSeconds);
            FinishOpening();
            return;
        }
    }
    else if (FMath::IsFinite(InDeltaTime) && InDeltaTime > 0.f)
    {
        OpeningSeconds += InDeltaTime;
    }
    if (OpeningSeconds >= TSTSSFirstWakeOpening::Duration)
    {
        FinishOpening();
        return;
    }
    RefreshOpeningCue();
}

void UTSTSSOpeningReviewWidget::RefreshOpeningCue()
{
    using namespace TSTSSFirstWakeOpening;
    const int32 Index = CueAt(OpeningSeconds);
    if (Index == OpeningCueIndex) return;
    OpeningCueIndex = Index;
    const FCue& Cue = Cues[Index];
    if (OpeningCaption) OpeningCaption->SetText(FText::FromString(Cue.Copy));
    if (OpeningStage)
    {
        OpeningStage->SetText(FText::FromString(FString(TEXT("Opening storyboard — text-only review\n")) + Cue.Shot));
    }
    UE_LOG(LogTemp, Display, TEXT("TSTSS_FIRST_WAKE_NARRATION_CUE index=%d spoken=%d"), Index, Cue.bSpoken ? 1 : 0);
}

void UTSTSSOpeningReviewWidget::StopOpening()
{
    bOpeningActive = false;
    if (OpeningPlayer) OpeningPlayer->Stop();
    if (IsValid(OpeningActor)) OpeningActor->Destroy();
    OpeningPlayer = nullptr;
    OpeningActor = nullptr;
    if (OpeningPanel) OpeningPanel->RemoveFromParent();
    OpeningPanel = nullptr;
    OpeningStage = nullptr;
    OpeningCaption = nullptr;
}

void UTSTSSOpeningReviewWidget::FinishOpening()
{
    if (!bOpeningActive) return;
    bOpeningCompleted = true;
    UE_LOG(LogTemp, Display, TEXT("TSTSS_FIRST_WAKE_NARRATION_FINISH seconds=%.2f"), OpeningSeconds);
    StopOpening();
    // Existing validated fresh-map path is the sole gameplay handoff.
    if (FallbackPanel) FallbackPanel->SetVisibility(ESlateVisibility::Visible);
    if (NewGameButton && GetOwningPlayer()) NewGameButton->SetUserFocus(GetOwningPlayer());
    BeginJourney();
}
