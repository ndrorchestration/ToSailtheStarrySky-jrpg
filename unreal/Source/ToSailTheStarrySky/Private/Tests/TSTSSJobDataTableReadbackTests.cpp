#include "Misc/AutomationTest.h"
#include "Engine/DataTable.h"
#include "UObject/UObjectGlobals.h"
#include "TSTSSJobClassSystem.h"

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

    return ImportProblems.Num() == 0;
}
#endif
