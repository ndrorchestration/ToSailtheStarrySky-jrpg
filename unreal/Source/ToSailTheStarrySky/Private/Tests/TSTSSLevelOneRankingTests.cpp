#include "Misc/AutomationTest.h"
#include "TSTSSLevelOneStatRanking.h"

#if WITH_DEV_AUTOMATION_TESTS

namespace
{
    FTSTSSLevelOneRankCandidate ReviewProfile(
        const TCHAR* Id, int32 HP, int32 MP, int32 MAG)
    {
        FTSTSSLevelOneRankCandidate Result;
        Result.CharacterId = FName(Id);
        Result.Level = 1;
        Result.MaxHealth = HP;
        Result.MaxMagicPoints = MP;
        Result.MagicPower = MAG;
        return Result;
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSLevelOneRankReviewTest,
    "TSTSS.Design.LevelOneStatRanks",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSLevelOneRankReviewTest::RunTest(const FString& Parameters)
{
    // Fixtures deliberately illustrative; no numeric canon or default character
    // initialization is inferred from these values.
    const TArray<FTSTSSLevelOneRankCandidate> Baseline{
        ReviewProfile(TEXT("Ender"), 101, 64, 27),
        ReviewProfile(TEXT("Ionia"), 112, 28, 8),
        ReviewProfile(TEXT("Lyra"), 86, 52, 19),
        ReviewProfile(TEXT("Reson"), 123, 20, 9),
        ReviewProfile(TEXT("Aepex"), 108, 38, 11)
    };
    TestTrue(TEXT("Approved Level 1 relative rankings"), 
        FTSTSSLevelOneRankContract::Validate(Baseline));

    // Input-array ordering must not grant priority or change the five-id contract.
    TArray<FTSTSSLevelOneRankCandidate> Reordered = Baseline;
    Reordered.Swap(0, 4);
    Reordered.Swap(1, 3);
    TestTrue(TEXT("Character array order is irrelevant"),
        FTSTSSLevelOneRankContract::Validate(Reordered));

    // The creator has NOT specified an order among Ionia, Reson, Aepex.
    // Changing their internal HP/MP/MAG ranking must remain legal.
    TArray<FTSTSSLevelOneRankCandidate> UnrankedThree = Baseline;
    UnrankedThree[1].MaxHealth = 150;
    UnrankedThree[3].MaxHealth = 107;
    UnrankedThree[4].MaxHealth = 120;
    UnrankedThree[1].MaxMagicPoints = 49;
    UnrankedThree[3].MaxMagicPoints = 35;
    UnrankedThree[4].MaxMagicPoints = 20;
    UnrankedThree[1].MagicPower = 17;
    UnrankedThree[3].MagicPower = 1;
    UnrankedThree[4].MagicPower = 12;
    TestTrue(TEXT("No internal ranking imposed on Ionia/Reson/Aepex"),
        FTSTSSLevelOneRankContract::Validate(UnrankedThree));

    // Strict rankings can be satisfied at the lower integer boundary, and
    // equality among the unconstrained three is permitted.
    TArray<FTSTSSLevelOneRankCandidate> Boundary = Baseline;
    Boundary[2].MaxHealth = 1; Boundary[0].MaxHealth = 2;
    Boundary[1].MaxHealth = 3; Boundary[3].MaxHealth = 3;
    Boundary[4].MaxHealth = 3;
    Boundary[0].MaxMagicPoints = 2; Boundary[2].MaxMagicPoints = 1;
    Boundary[1].MaxMagicPoints = 0; Boundary[3].MaxMagicPoints = 0;
    Boundary[4].MaxMagicPoints = 0;
    Boundary[0].MagicPower = 2; Boundary[2].MagicPower = 1;
    Boundary[1].MagicPower = 0; Boundary[3].MagicPower = 0;
    Boundary[4].MagicPower = 0;
    TestTrue(TEXT("Strict two-rank boundary accepts tied lower-three zero MAG/MP"),
        FTSTSSLevelOneRankContract::Validate(Boundary));

    TArray<FTSTSSLevelOneRankCandidate> Variant = Baseline;
    Variant[0].MagicPower = Variant[2].MagicPower;
    TestFalse(TEXT("Ender/Lyra tied MAG rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant[1].MaxMagicPoints = Variant[2].MaxMagicPoints;
    TestFalse(TEXT("Ionia/Lyra tied MP rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant[4].MaxHealth = Variant[0].MaxHealth;
    TestFalse(TEXT("Aepex/Ender tied HP rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant[3].MagicPower = Variant[0].MagicPower + 1;
    TestFalse(TEXT("Reson exceeding Ender MAG rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant[0].MaxHealth = Variant[2].MaxHealth;
    TestFalse(TEXT("Ender/Lyra tied HP rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant[1].CharacterId = FName(TEXT("Ender"));
    TestFalse(TEXT("Duplicate canonical character rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant.RemoveAt(1);
    TestFalse(TEXT("Incomplete five-person roster rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant[1].CharacterId = FName(TEXT("Talen"));
    TestFalse(TEXT("Unexpected party member rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant[2].Level = 2;
    TestFalse(TEXT("Non-Level-1 profile rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant[0].MaxMagicPoints = -1;
    TestFalse(TEXT("Negative starting MP rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant[4].MaxHealth = 0;
    TestFalse(TEXT("Zero HP rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant[0].MaxMagicPoints = 1000000;
    TestFalse(TEXT("Out-of-range MP rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant[4].MagicPower = -1;
    TestFalse(TEXT("Negative MAG rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    Variant = Baseline;
    Variant[0].Level = 0;
    TestFalse(TEXT("Invalid Level 0 rejected"),
        FTSTSSLevelOneRankContract::Validate(Variant));

    // Source inputs remain intact across all validation calls.
    TestEqual(TEXT("Reference Ender magic unchanged"), Baseline[0].MagicPower, 27);
    TestEqual(TEXT("Reference Lyra HP unchanged"), Baseline[2].MaxHealth, 86);
    return true;
}
#endif
