#include "Misc/AutomationTest.h"
#include "Engine/DataTable.h"
#include "UObject/UObjectGlobals.h"
#include "TSTSSJobClassSystem.h"
#include "TSTSSJobSelectionReviewWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSJobTableReadbackTest,
    "TSTSS.Design.HybridJobTableReadback",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSJobTableReadbackTest::RunTest(const FString& Parameters)
{
    // Disposable, in-memory fixture. No Content/ asset, production job,
    // ability grant, SaveGame change, or creator approval is created here.
    UDataTable* Table = NewObject<UDataTable>(GetTransientPackage());
    if (!TestNotNull(TEXT("transient Unreal DataTable allocated"), Table))
    {
        return false;
    }

    TMap<FName, const uint8*> NoInitialRows;
    const TArray<FString> SchemaProblems =
        Table->CreateTableFromRawData(NoInitialRows, FTSTSSJobDefinitionRow::StaticStruct());
    TestEqual(TEXT("row-struct setup errors"), SchemaProblems.Num(), 0);
    TestTrue(TEXT("Unreal stores expected reflected job row struct"),
        Table->GetRowStruct() == FTSTSSJobDefinitionRow::StaticStruct());

    // Unreal JSON DataTable import uses "Name" as row key and only deliberately
    // authored fixture IDs. Both default to DesignOnly and cannot be selected.
    const FString Fixture = TEXT(R"JSON([
        {
            "Name": "ReviewScholar",
            "JobId": "ReviewScholar",
            "DisplayName": "Review Scholar [Noncanonical Fixture]",
            "ReviewStatus": "DesignOnly",
            "bPrimaryEligible": true,
            "bSecondaryEligible": false
        },
        {
            "Name": "ReviewGuard",
            "JobId": "ReviewGuard",
            "DisplayName": "Review Guard [Noncanonical Fixture]",
            "ReviewStatus": "DesignOnly",
            "bPrimaryEligible": true,
            "bSecondaryEligible": false
        }
    ])JSON");
    const TArray<FString> ImportProblems = Table->CreateTableFromJSONString(Fixture);
    for (const FString& Problem : ImportProblems)
    {
        AddError(FString::Printf(TEXT("Job JSON fixture import: %s"), *Problem));
    }
    if (!TestEqual(TEXT("only two noncanonical imported rows"), Table->GetRowMap().Num(), 2))
    {
        return false;
    }

    const FTSTSSJobDefinitionRow* Scholar =
        Table->FindRow<FTSTSSJobDefinitionRow>(TEXT("ReviewScholar"), TEXT("JobDataTableTest"));
    const FTSTSSJobDefinitionRow* Guard =
        Table->FindRow<FTSTSSJobDefinitionRow>(TEXT("ReviewGuard"), TEXT("JobDataTableTest"));
    if (!TestNotNull(TEXT("Scholar row readback"), Scholar)
        || !TestNotNull(TEXT("Guard row readback"), Guard))
    {
        return false;
    }
    TestEqual(TEXT("Scholar authored ID matches key"), Scholar->JobId, FName(TEXT("ReviewScholar")));
    TestEqual(TEXT("Guard authored ID matches key"), Guard->JobId, FName(TEXT("ReviewGuard")));
    TestTrue(TEXT("imported rows are DesignOnly by explicit admission"),
        Scholar->ReviewStatus == ETSTSSJobReviewStatus::DesignOnly
        && Guard->ReviewStatus == ETSTSSJobReviewStatus::DesignOnly);
    TestFalse(TEXT("neither fixture grants secondary slot"),
        Scholar->bSecondaryEligible || Guard->bSecondaryEligible);

    TMap<FName, FTSTSSJobDefinitionRow> Definitions;
    if (!TestTrue(TEXT("strict DataTable catalog readback succeeds"),
        FTSTSSJobClassSystem::TryReadJobDefinitionsForReview(*Table, Definitions)))
    {
        return false;
    }
    TestEqual(TEXT("strict catalog contains two rows"), Definitions.Num(), 2);
    FTSTSSJobLoadoutState Ender;
    Ender.CharacterId = TEXT("Ender");
    Ender.NativeProfession = TEXT("Rift Scholar");
    Ender.ExplicitlyUnlockedJobs.Add(Scholar->JobId);
    Ender.ExplicitlyUnlockedJobs.Add(Guard->JobId);
    FTSTSSJobLoadoutState Output;
    Output.CharacterId = TEXT("NeverOverwrite");
    TestFalse(TEXT("imported DesignOnly job denied even with explicit unlock"),
        FTSTSSJobClassSystem::TrySelectJobs(
            Ender, Definitions, Scholar->JobId, NAME_None, Output));
    TestEqual(TEXT("data-driven rejection keeps caller output unchanged"),
        Output.CharacterId, FName(TEXT("NeverOverwrite")));

    // A DataTable row can have a distinct key and in-row JobId. Reject the
    // whole catalog instead of silently overwriting the first definition.
    FTSTSSJobDefinitionRow Alias = Definitions.FindChecked(FName(TEXT("ReviewScholar")));
    Table->AddRow(TEXT("ReviewAlias"), Alias);
    TestFalse(TEXT("aliased/duplicate job ID rejects full catalog"),
        FTSTSSJobClassSystem::TryReadJobDefinitionsForReview(*Table, Definitions));
    TestEqual(TEXT("alias failure preserves prior catalog"), Definitions.Num(), 2);
    TestFalse(TEXT("alias not admitted"), Definitions.Contains(TEXT("ReviewAlias")));
    Table->RemoveRow(TEXT("ReviewAlias"));

    FTSTSSJobDefinitionRow Untitled = Definitions.FindChecked(FName(TEXT("ReviewGuard")));
    Untitled.JobId = TEXT("ReviewUntitled");
    Untitled.DisplayName = FText::GetEmpty();
    Table->AddRow(TEXT("ReviewUntitled"), Untitled);
    TestFalse(TEXT("missing displayed job name denies catalog"),
        FTSTSSJobClassSystem::TryReadJobDefinitionsForReview(*Table, Definitions));
    TestEqual(TEXT("missing name never clobbers prior rows"), Definitions.Num(), 2);
    Table->RemoveRow(TEXT("ReviewUntitled"));

    UDataTable* EmptyTable = NewObject<UDataTable>(GetTransientPackage());
    EmptyTable->CreateTableFromRawData(NoInitialRows, FTSTSSJobDefinitionRow::StaticStruct());
    TestFalse(TEXT("empty authored catalog rejects without changing output"),
        FTSTSSJobClassSystem::TryReadJobDefinitionsForReview(*EmptyTable, Definitions));
    UDataTable* WrongSchema = NewObject<UDataTable>(GetTransientPackage());
    WrongSchema->CreateTableFromRawData(NoInitialRows, FTableRowBase::StaticStruct());
    TestFalse(TEXT("unrelated DataTable schema rejected"),
        FTSTSSJobClassSystem::TryReadJobDefinitionsForReview(*WrongSchema, Definitions));
    TestEqual(TEXT("all failure paths preserve accepted catalog"), Definitions.Num(), 2);

    TArray<FTSTSSJobSelectionPreviewRow> Preview;
    TestTrue(TEXT("DesignOnly catalog produces read-only menu projection"),
        FTSTSSJobClassSystem::TryBuildJobSelectionPreviewForReview(
            Ender, *Table, Preview));
    if (!TestEqual(TEXT("preview has exactly two rows"), Preview.Num(), 2))
    {
        return false;
    }
    TestEqual(TEXT("preview uses deterministic job ID ordering"),
        Preview[0].JobId, FName(TEXT("ReviewGuard")));
    TestFalse(TEXT("DesignOnly unlocked Guard cannot be selected"),
        Preview[0].bPrimaryReviewSelectable || Preview[0].bSecondaryReviewSelectable);
    TestFalse(TEXT("DesignOnly unlocked Scholar cannot be selected"),
        Preview[1].bPrimaryReviewSelectable || Preview[1].bSecondaryReviewSelectable);

    // Real transient UMG objects, no saved widget blueprint or world actor.
    UWidgetTree* ReviewTree = NewObject<UWidgetTree>(GetTransientPackage());
    if (!TestTrue(TEXT("real transient UMG tree built from denied jobs"),
        UTSTSSJobSelectionReviewWidget::TryPopulateReviewTree(*ReviewTree, Preview)))
    {
        return false;
    }
    UVerticalBox* DeniedRoot = Cast<UVerticalBox>(ReviewTree->RootWidget);
    if (!TestNotNull(TEXT("UMG root is a real vertical panel"), DeniedRoot))
    {
        return false;
    }
    TestEqual(TEXT("header plus two real job labels"), DeniedRoot->GetChildrenCount(), 3);
    UTextBlock* DeniedGuard = Cast<UTextBlock>(DeniedRoot->GetChildAt(1));
    if (!TestNotNull(TEXT("locked Guard is an actual text widget"), DeniedGuard))
    {
        return false;
    }
    TestFalse(TEXT("locked Guard UMG label is disabled"), DeniedGuard->GetIsEnabled());
    TestTrue(TEXT("explicit locked text is readable without relying on color"),
        DeniedGuard->GetText().ToString().Contains(TEXT("LOCKED: NOT ADMITTED")));

    // ReviewSelectable is only a disposable test-fixture status.
    FTSTSSJobDefinitionRow SelectableScholar = Definitions.FindChecked(FName(TEXT("ReviewScholar")));
    FTSTSSJobDefinitionRow SelectableGuard = Definitions.FindChecked(FName(TEXT("ReviewGuard")));
    SelectableScholar.ReviewStatus = ETSTSSJobReviewStatus::ReviewSelectable;
    SelectableGuard.ReviewStatus = ETSTSSJobReviewStatus::ReviewSelectable;
    SelectableScholar.bSecondaryEligible = true;
    SelectableGuard.bSecondaryEligible = true;
    Table->RemoveRow(TEXT("ReviewScholar"));
    Table->RemoveRow(TEXT("ReviewGuard"));
    Table->AddRow(TEXT("ReviewScholar"), SelectableScholar);
    Table->AddRow(TEXT("ReviewGuard"), SelectableGuard);
    Ender.PrimaryJob = TEXT("ReviewScholar");
    TestTrue(TEXT("preview reuses explicit existing selection gates"),
        FTSTSSJobClassSystem::TryBuildJobSelectionPreviewForReview(
            Ender, *Table, Preview));
    TestTrue(TEXT("unlocked Guard can be primary in review fixture"),
        Preview[0].bExplicitlyUnlocked && Preview[0].bPrimaryReviewSelectable);
    TestTrue(TEXT("unlocked Guard may be secondary under current Scholar"),
        Preview[0].bSecondaryReviewSelectable);
    TestFalse(TEXT("duplicate primary Scholar cannot occupy secondary slot"),
        Preview[1].bSecondaryReviewSelectable);
    TestTrue(TEXT("menu projection never grants learned skills"),
        Ender.LearnedSkillIds.IsEmpty());

    // Changing the review fixture redraws real UMG labels, not gameplay.
    TestTrue(TEXT("UMG redraw accepts explicitly admitted review fixture"),
        UTSTSSJobSelectionReviewWidget::TryPopulateReviewTree(*ReviewTree, Preview));
    UVerticalBox* AdmittedRoot = Cast<UVerticalBox>(ReviewTree->RootWidget);
    if (!TestNotNull(TEXT("admitted UMG panel is present"), AdmittedRoot))
    {
        return false;
    }
    UTextBlock* EnabledGuard = Cast<UTextBlock>(AdmittedRoot->GetChildAt(1));
    UTextBlock* EnabledScholar = Cast<UTextBlock>(AdmittedRoot->GetChildAt(2));
    if (!TestNotNull(TEXT("Guard review label exists"), EnabledGuard)
        || !TestNotNull(TEXT("Scholar review label exists"), EnabledScholar))
    {
        return false;
    }
    TestTrue(TEXT("admitted review Guard label is enabled"), EnabledGuard->GetIsEnabled());
    TestTrue(TEXT("admitted Guard label names both review slots"),
        EnabledGuard->GetText().ToString().Contains(TEXT("SECONDARY REVIEW")));
    TestTrue(TEXT("admitted Scholar primary review label enabled"),
        EnabledScholar->GetIsEnabled());
    TestTrue(TEXT("scholar duplicate secondary visibly unavailable"),
        EnabledScholar->GetText().ToString().Contains(TEXT("SECONDARY UNAVAILABLE")));
    UWidget* SavedRoot = ReviewTree->RootWidget;
    TArray<FTSTSSJobSelectionPreviewRow> InvalidRows = Preview;
    InvalidRows[1].JobId = InvalidRows[0].JobId;
    TestFalse(TEXT("duplicate UMG row IDs reject entire widget redraw"),
        UTSTSSJobSelectionReviewWidget::TryPopulateReviewTree(*ReviewTree, InvalidRows));
    TestTrue(TEXT("invalid UMG data leaves previously valid root intact"),
        ReviewTree->RootWidget == SavedRoot);

    FTSTSSJobLoadoutState InvalidIdentity = Ender;
    InvalidIdentity.CharacterId = TEXT("UnknownSixth");
    TestFalse(TEXT("unknown character cannot acquire a menu projection"),
        FTSTSSJobClassSystem::TryBuildJobSelectionPreviewForReview(
            InvalidIdentity, *Table, Preview));
    TestEqual(TEXT("invalid identity preserves prior preview rows"), Preview.Num(), 2);
    TestEqual(TEXT("invalid identity preserves first preview row"),
        Preview[0].JobId, FName(TEXT("ReviewGuard")));

    // A malformed table must not leak a partial menu into the output.
    Table->AddRow(TEXT("ReviewAlias"), SelectableGuard);
    TestFalse(TEXT("mismatched DataTable identity rejects entire preview"),
        FTSTSSJobClassSystem::TryBuildJobSelectionPreviewForReview(
            Ender, *Table, Preview));
    TestEqual(TEXT("malformed catalog preserves prior menu"), Preview.Num(), 2);
    Table->RemoveRow(TEXT("ReviewAlias"));

    return ImportProblems.Num() == 0;
}
#endif
