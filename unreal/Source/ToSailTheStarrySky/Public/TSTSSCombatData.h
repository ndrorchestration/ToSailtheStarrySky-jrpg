#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "TSTSSCombatAbilities.h"
#include "TSTSSCombatData.generated.h"

// Data contract for combat definitions: schema, validation and a bridge into the
// existing deterministic combat core (FTSTSSCombatAbilities::TryUse).
//
// This file defines SHAPE and RULES only. It contains no canonical spells, techniques,
// stats or equipment. Every value must come from creator-supplied data tables, and
// shipping validation rejects anything not marked CreatorApproved.

// The Five Lights are narrative affinities. They are an optional tag, never a
// requirement that a character may only use matching actions.
UENUM(BlueprintType)
enum class ETSTSSLight : uint8
{
    None,
    Spirit,
    Earth,
    Water,
    Fire,
    Air
};

UENUM(BlueprintType)
enum class ETSTSSActionCategory : uint8
{
    Attack,
    Spell,
    WeaponTechnique,
    Support
};

UENUM(BlueprintType)
enum class ETSTSSActionTarget : uint8
{
    Self,
    Ally,
    Enemy
};

// Provenance gate. Placeholder = fixture/test only. Proposed = awaiting creator review.
UENUM(BlueprintType)
enum class ETSTSSApproval : uint8
{
    Placeholder,
    Proposed,
    CreatorApproved
};

// One DataTable row per action. Costs draw on the single combat resource pool that the
// existing core models today. Whether weapon techniques use a separate pool is an
// open creator decision and is deliberately NOT modelled here. Resonance is a narrative
// energy and has no field in this schema by design.
USTRUCT(BlueprintType)
struct TOSAILTHESTARRYSKY_API FTSTSSActionDefRow : public FTableRowBase
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName ActionId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) ETSTSSActionCategory Category = ETSTSSActionCategory::Attack;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) ETSTSSActionTarget Target = ETSTSSActionTarget::Enemy;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 Cost = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 Power = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bHealing = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) ETSTSSLight Affinity = ETSTSSLight::None;
    // Minimum character level at which the learners below gain the action.
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 UnlockLevel = 1;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FName> Learners;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) ETSTSSApproval Approval = ETSTSSApproval::Placeholder;
};

// One DataTable row per protagonist. StartMagic is a single aggregate magic stat until
// the damage formula separates physical and aether scaling.
USTRUCT(BlueprintType)
struct TOSAILTHESTARRYSKY_API FTSTSSCharacterBaselineRow : public FTableRowBase
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName CharacterId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) ETSTSSLight Affinity = ETSTSSLight::None;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 StartMaxHP = 1;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 StartMaxMP = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 StartMagic = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) ETSTSSApproval Approval = ETSTSSApproval::Placeholder;
};

enum class ETSTSSDataIssue : uint8
{
    MissingProtagonist,
    UnknownCharacter,
    DuplicateCharacter,
    WrongAffinity,
    ValueOutOfRange,
    MagicOrderViolation,
    MpOrderViolation,
    HpOrderViolation,
    InvalidActionId,
    DuplicateAction,
    InvalidActionCategory,
    InvalidActionTarget,
    InvalidUnlockLevel,
    NoLearners,
    UnknownLearner,
    DuplicateLearner,
    HealingTargetsEnemy,
    NotCreatorApproved,
    MissingLevel,
    InvalidLevel,
    InvalidActiveParty
};

struct FTSTSSDataIssueEntry
{
    ETSTSSDataIssue Code = ETSTSSDataIssue::UnknownCharacter;
    FName Subject = NAME_None;
};

// Validators APPEND to OutIssues (callers pass a fresh array) and return true only when
// no issue was added by that call. Nothing here mutates its inputs.
class TOSAILTHESTARRYSKY_API FTSTSSCombatData
{
public:
    // Party order is fixed: Ender, Ionia, Lyra, Reson, Aepex.
    static const TArray<FName>& Protagonists();
    static ETSTSSLight ApprovedAffinity(FName CharacterId);

    // Sanity ceiling that catches data-entry errors such as an extra zero.
    static constexpr int32 MaxDataValue = 1000000;
    static constexpr int32 ActivePartySize = 3;

    // Approved starting-stat ordering (strict; ties at a constrained rank fail):
    //   magic and MP: Ender first, Lyra second, then the rest.
    //   HP: Lyra lowest, Ender second lowest, then the rest.
    // Ionia, Reson and Aepex may tie one another.
    static bool ValidateBaselines(const TArray<FTSTSSCharacterBaselineRow>& Baselines,
                                  bool bShipping,
                                  TArray<FTSTSSDataIssueEntry>& OutIssues);

    static bool ValidateActions(const TArray<FTSTSSActionDefRow>& Actions,
                                bool bShipping,
                                TArray<FTSTSSDataIssueEntry>& OutIssues);

    static bool ValidateActiveParty(const TArray<FName>& ActiveIds,
                                    TArray<FTSTSSDataIssueEntry>& OutIssues);

    // All-or-nothing. Validates everything, then derives the catalog and per-character
    // learned set that FTSTSSCombatAbilities::TryUse consumes. Levels must contain every
    // protagonist at level >= 1. On failure the output maps are left untouched.
    static bool TryBuildAbilityData(const TArray<FTSTSSCharacterBaselineRow>& Baselines,
                                    const TArray<FTSTSSActionDefRow>& Actions,
                                    const TMap<FName, int32>& Levels,
                                    bool bShipping,
                                    TMap<FName, FTSTSSAbilitySpec>& OutCatalog,
                                    TMap<FName, TSet<FName>>& OutLearned,
                                    TArray<FTSTSSDataIssueEntry>& OutIssues);
};
