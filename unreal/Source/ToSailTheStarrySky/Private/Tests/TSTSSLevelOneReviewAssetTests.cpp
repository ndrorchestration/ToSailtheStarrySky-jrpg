#include "Misc/AutomationTest.h"
#include "UObject/UObjectGlobals.h"
#include "TSTSSLevelOneReviewAsset.h"

#if WITH_DEV_AUTOMATION_TESTS

namespace
{
    FTSTSSLevelOneDraftStats DraftStat(const TCHAR* Id, int32 HP, int32 MP, int32 MAG)
    {
        FTSTSSLevelOneDraftStats Entry;
        Entry.CharacterId = FName(Id);
        Entry.Level = 1;
        Entry.MaxHealth = HP;
        Entry.ProposedMaxMP = MP;
        Entry.ProposedMAG = MAG;
        return Entry;
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSLevelOneReviewAssetTest,
    "TSTSS.Design.LevelOneReviewAsset",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSLevelOneReviewAssetTest::RunTest(const FString& Parameters)
{
    UTSTSSLevelOneReviewAsset* Asset = NewObject<UTSTSSLevelOneReviewAsset>();
    if (!TestNotNull(TEXT("Transient review asset allocated"), Asset))
    {
        return false;
    }
    TestFalse(TEXT("Empty asset cannot pass default gate"), Asset->IsConsistentForReview());
    Asset->Entries = {
        DraftStat(TEXT("Ender"), 101, 64, 27),
        DraftStat(TEXT("Ionia"), 112, 28, 8),
        DraftStat(TEXT("Lyra"), 86, 52, 19),
        DraftStat(TEXT("Reson"), 123, 20, 9),
        DraftStat(TEXT("Aepex"), 108, 38, 11)
    };
    TestFalse(TEXT("Proposed numbers remain disabled by default"),
        Asset->IsConsistentForReview());

    Asset->bEnableLocalReview = true;
    TestTrue(TEXT("Valid illustrative data may be reviewed locally"),
        Asset->IsConsistentForReview());

    Asset->Entries[4].MaxHealth = 100;
    TestFalse(TEXT("HP order inversion denied even with local opt-in"),
        Asset->IsConsistentForReview());
    Asset->Entries[4].MaxHealth = 108;

    Asset->Entries[2].ProposedMaxMP = 28;
    TestFalse(TEXT("MP ranking tie denied"),
        Asset->IsConsistentForReview());
    Asset->Entries[2].ProposedMaxMP = 52;

    Asset->Entries[0].ProposedMAG = 19;
    TestFalse(TEXT("MAG ranking tie denied"),
        Asset->IsConsistentForReview());
    Asset->Entries[0].ProposedMAG = 27;

    Asset->Entries[1].CharacterId = FName(TEXT("Ender"));
    TestFalse(TEXT("Duplicate identity denied"),
        Asset->IsConsistentForReview());
    Asset->Entries[1].CharacterId = FName(TEXT("Ionia"));

    TestTrue(TEXT("Local review recovers after fixing the candidate"),
        Asset->IsConsistentForReview());
    Asset->bEnableLocalReview = false;
    TestFalse(TEXT("Disabling preview revokes review readiness"),
        Asset->IsConsistentForReview());

    TestEqual(TEXT("No modification to candidate entry count"), Asset->Entries.Num(), 5);
    TestEqual(TEXT("No modification to Ender MP"), Asset->Entries[0].ProposedMaxMP, 64);
    return true;
}
#endif
