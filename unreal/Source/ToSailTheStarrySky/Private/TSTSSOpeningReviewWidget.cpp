#include "TSTSSOpeningReviewWidget.h"
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
    if (!MoviePlayer || !VideoPanel || !FallbackPanel) return;
    MoviePlayer->SetLooping(true);
    FallbackPanel->SetVisibility(ESlateVisibility::Collapsed);
    VideoPanel->SetVisibility(ESlateVisibility::Visible);
    if (VideoButton && GetOwningPlayer()) VideoButton->SetUserFocus(GetOwningPlayer());
}

void UTSTSSOpeningReviewWidget::OnMovieOpenFailed(FString FailedUrl)
{
    (void)FailedUrl;
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

    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_REVIEW_NEW_GAME_ROUTE route=%s progress_reset_by_fresh_map=1"),
        *PreludeMap);
    UGameplayStatics::OpenLevel(Controller, FName(*PreludeMap));
}
