#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "TSTSSJobClassSystem.generated.h"

// Review admission is NOT production authorization or creator approval.
// Defaults are deliberately unusable until an explicit review fixture opts in.
UENUM(BlueprintType)
enum class ETSTSSJobReviewStatus : uint8
{
    DesignOnly,
    ReviewSelectable
};

USTRUCT(BlueprintType)
struct TOSAILTHESTARRYSKY_API FTSTSSJobDefinitionRow : public FTableRowBase
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Job") FName JobId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Job") FText DisplayName;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Review") ETSTSSJobReviewStatus ReviewStatus = ETSTSSJobReviewStatus::DesignOnly;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Loadout") bool bPrimaryEligible = true;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Loadout") bool bSecondaryEligible = false;
};

// Volatile review-model state. This is deliberately NOT a UPROPERTY, SaveGame,
// party component, automatic unlock/XP provider, or runnable combat permission.
struct FTSTSSJobLoadoutState
{
    FName CharacterId = NAME_None;
    FName NativeProfession = NAME_None;
    FName PrimaryJob = NAME_None;
    FName SecondaryJob = NAME_None;
    TSet<FName> ExplicitlyUnlockedJobs;

    // Independent axes: changing jobs must not reset or award any of them.
    int32 CharacterLevel = 1;
    TMap<FName, int32> JobProficiencyById;
    TMap<FName, int32> SchoolMasteryById;
    TMap<FName, int32> WeaponMasteryById;
    TMap<FName, int32> RelationshipProgressByCharacter;
    TSet<FName> LearnedSkillIds;
    TSet<FName> ExplicitOffJobTransferSkillIds;
};

// An ability's class eligibility is distinct from its learned status, magic
// school mastery, weapon requirements, costs, and ReviewExecutable admission.
// This preview-only policy cannot call FTSTSSBattleSkillSystem::TryUseRow.
struct FTSTSSJobSkillPolicy
{
    FName SkillId = NAME_None;
    FName TrainedJobId = NAME_None;
    bool bAllowSecondaryJob = false;
    bool bAllowExplicitOffJobTransfer = false;
};

class TOSAILTHESTARRYSKY_API FTSTSSJobClassSystem
{
public:
    // Ender's permanent trade is Harmonic Resonance Engineer; combat job remains flexible.
    // Rift Scholar remains a distinct supporting-NPC profession (Wise Woman), not Ender's.
    // A missing profession for other protagonists is intentionally not invented.
    static bool IsProtagonist(FName CharacterId);
    static FName CanonicalNativeProfession(FName CharacterId);

    // Convert an authored DataTable into a catalog without losing row-key
    // integrity or silently overwriting duplicate/misnamed job IDs. Reject
    // empty/wrong-schema/malformed tables transactionally. No job admission.
    static bool TryReadJobDefinitionsForReview(
        const UDataTable& Table,
        TMap<FName, FTSTSSJobDefinitionRow>& OutDefinitions);

    // Both job slots are explicitly selected; they never follow Five Lights,
    // native identity, inventory, affinities, school mastery, or skill learning.
    // On rejection the destination is byte-for-byte logically unchanged.
    static bool TrySelectJobs(
        const FTSTSSJobLoadoutState& Current,
        const TMap<FName, FTSTSSJobDefinitionRow>& JobDefinitions,
        FName RequestedPrimary,
        FName RequestedSecondary,
        FTSTSSJobLoadoutState& OutState);

    // Review-only eligibility. A true result NEVER authorizes combat execution.
    static bool IsSkillEligibleForReview(
        const FTSTSSJobLoadoutState& State,
        const FTSTSSJobSkillPolicy& Policy);
};
