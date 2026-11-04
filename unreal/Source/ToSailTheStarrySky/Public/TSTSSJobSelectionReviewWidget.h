#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TSTSSJobClassSystem.h"
#include "TSTSSJobSelectionReviewWidget.generated.h"

class UWidgetTree;
class UDataTable;

// Disposable UMG review board only: no button actions, delegates, gameplay
// mutation, SaveGame data, spawned character, or production asset admission.
UCLASS(Transient, NotBlueprintable)
class TOSAILTHESTARRYSKY_API UTSTSSJobSelectionReviewWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    // Validates the DataTable and protagonist through existing class gates.
    // On invalid input, retains prior widget tree without partial changes.
    bool TryDisplayCatalogForReview(
        const FTSTSSJobLoadoutState& Current,
        const UDataTable& Catalog);

    // For native automation: render the same label tree without a world,
    // owning player or saved Blueprint asset. Null/empty rows are denied.
    static bool TryPopulateReviewTree(
        UWidgetTree& Tree,
        const TArray<FTSTSSJobSelectionPreviewRow>& Rows);
};
