#pragma once

#include "CoreMinimal.h"
#include "Combat/TSS_CombatTurnManager.h"
#include "Engine/DataTable.h"
#include "TSTSSSliceEnemyCatalog.generated.h"

// Provisional native UE enemy review catalog. No story placement or canonical species approval.
// These archetypes do not authorize a story encounter or a player skill.
UENUM(BlueprintType)
enum class ETSTSSSliceEnemyKind : uint8
{
    HarmonicShear,
    AetherLeakWisp,
    DockSkitter,
    BanditCutpurse,
    BanditSlinger,
    BanditCaptain,
    Thornvine,
    Sporecap,
    RootSentinel,
    ReefEel,
    TidefinRaptor,
    ShellbackCrab,
    CliffLynx,
    Bristleboar,
    NightGlider
};

UENUM(BlueprintType)
enum class ETSTSSSliceEnemyFamily : uint8
{
    Anomaly,
    Bandit,
    Flora,
    Aquatic,
    Fauna
};

USTRUCT(BlueprintType)
struct TOSAILTHESTARRYSKY_API FTSTSSSliceEnemyDescriptor
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category="Slice Review")
    FName ArchetypeId = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="Slice Review")
    FString DisplayName;

    UPROPERTY(BlueprintReadOnly, Category="Slice Review")
    ETSTSSSliceEnemyFamily Family = ETSTSSSliceEnemyFamily::Anomaly;

    UPROPERTY(BlueprintReadOnly, Category="Slice Review")
    FName HabitatTag = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="Slice Review")
    bool bLeader = false;

    UPROPERTY(BlueprintReadOnly, Category="Slice Review")
    int32 MaxHP = 0;

    UPROPERTY(BlueprintReadOnly, Category="Slice Review")
    int32 MaxResource = 0;

    UPROPERTY(BlueprintReadOnly, Category="Slice Review")
    int32 Attack = 0;

    UPROPERTY(BlueprintReadOnly, Category="Slice Review")
    int32 Defense = 0;

    UPROPERTY(BlueprintReadOnly, Category="Slice Review")
    int32 Agility = 0;

    UPROPERTY(BlueprintReadOnly, Category="Slice Review")
    TArray<FName> AbilityIds;

    // This review registry never authorizes a location, quest, or shipping content.
    UPROPERTY(BlueprintReadOnly, Category="Slice Review")
    bool bStoryPlacementApproved = false;
};

class TOSAILTHESTARRYSKY_API FTSTSSSliceEnemyCatalog
{
public:
    // Failure preserves the caller's output.
    static bool TryDescribe(ETSTSSSliceEnemyKind Kind,
                            FTSTSSSliceEnemyDescriptor& Out);

    // Produces a new, unique-ID encounter member for the EXISTING turn manager.
    // Does not initialize encounters or change campaign progression.
    static bool TryMakeReviewParticipant(ETSTSSSliceEnemyKind Kind,
                                         FName InstanceId,
                                         FTSS_CombatParticipant& Out);

    // Default DesignOnly is non-executable; review execution requires an explicit
    // opt-in and is unavailable in shipping builds. All rows are ENEMY-ONLY.
    // Caller owns the returned transient table and supplies it to SkillTable.
    static UDataTable* MakeReviewSkillTable(UObject* Outer,
                                           bool bExplicitReviewExecution = false);
};
