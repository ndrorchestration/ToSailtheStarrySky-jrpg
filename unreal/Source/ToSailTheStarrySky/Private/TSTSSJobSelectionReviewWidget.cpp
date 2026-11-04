#include "TSTSSJobSelectionReviewWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"

bool UTSTSSJobSelectionReviewWidget::TryDisplayCatalogForReview(
    const FTSTSSJobLoadoutState& Current,
    const UDataTable& Catalog)
{
    TArray<FTSTSSJobSelectionPreviewRow> Preview;
    if (!FTSTSSJobClassSystem::TryBuildJobSelectionPreviewForReview(
        Current, Catalog, Preview))
    {
        return false;
    }

    if (!WidgetTree)
    {
        WidgetTree = NewObject<UWidgetTree>(
            this, UWidgetTree::StaticClass(), NAME_None, RF_Transient);
    }
    return WidgetTree && TryPopulateReviewTree(*WidgetTree, Preview);
}

bool UTSTSSJobSelectionReviewWidget::TryPopulateReviewTree(
    UWidgetTree& Tree,
    const TArray<FTSTSSJobSelectionPreviewRow>& Rows)
{
    if (Rows.IsEmpty())
    {
        return false;
    }

    // Reject untrusted preview contents before constructing ANY visual nodes.
    TSet<FName> SeenIds;
    for (const FTSTSSJobSelectionPreviewRow& Row : Rows)
    {
        if (Row.JobId.IsNone() || Row.DisplayName.IsEmpty()
            || SeenIds.Contains(Row.JobId)
            || ((Row.bPrimaryReviewSelectable || Row.bSecondaryReviewSelectable)
                && !Row.bExplicitlyUnlocked))
        {
            return false;
        }
        SeenIds.Add(Row.JobId);
    }

    UVerticalBox* Root = Tree.ConstructWidget<UVerticalBox>();
    if (!Root)
    {
        return false;
    }

    UTextBlock* Title = Tree.ConstructWidget<UTextBlock>();
    if (!Title)
    {
        return false;
    }
    Title->SetText(FText::FromString(
        TEXT("JOB SELECTION - DESIGN REVIEW ONLY / NO GAMEPLAY")));
    Root->AddChildToVerticalBox(Title);

    for (const FTSTSSJobSelectionPreviewRow& Row : Rows)
    {
        UTextBlock* Label = Tree.ConstructWidget<UTextBlock>();
        if (!Label)
        {
            return false;
        }

        const bool bAnySelectable =
            Row.bPrimaryReviewSelectable || Row.bSecondaryReviewSelectable;
        FString State;
        if (!Row.bExplicitlyUnlocked)
        {
            State = TEXT("LOCKED: NOT UNLOCKED");
        }
        else if (!bAnySelectable)
        {
            State = TEXT("LOCKED: NOT ADMITTED");
        }
        else
        {
            State = Row.bPrimaryReviewSelectable
                ? TEXT("PRIMARY REVIEW") : TEXT("PRIMARY UNAVAILABLE");
            State += Row.bSecondaryReviewSelectable
                ? TEXT(" | SECONDARY REVIEW")
                : TEXT(" | SECONDARY UNAVAILABLE");
        }

        Label->SetText(FText::FromString(FString::Printf(
            TEXT("%s  -  %s"),
            *Row.DisplayName.ToString(), *State)));
        // Gray-out is supplemental; text labels carry lock information.
        Label->SetIsEnabled(bAnySelectable);
        Root->AddChildToVerticalBox(Label);
    }

    // Root is replaced atomically only after every row has a real UMG label.
    Tree.RootWidget = Root;
    return true;
}
