#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "TSTSSCombatAbilities.h"
#include "TSTSSBattleSkillSystem.generated.h"

// These are runtime/mechanical categories; the Five Lights are NOT combat schools.
UENUM(BlueprintType)
enum class ETSTSSBattleSkillKind : uint8
{
    Spell,
    WeaponTechnique,
    JobArt
};

UENUM(BlueprintType)
enum class ETSTSSBattleSkillTarget : uint8
{
    Self,
    Ally,
    Enemy
};

// Explicit admission is required even when a design catalog contains the row.
UENUM(BlueprintType)
enum class ETSTSSBattleSkillAdmission : uint8
{
    DesignOnly,
    ReviewExecutable
};

// DataTable-ready, opt-in review contract. Never infer skills from story affinity.
USTRUCT(BlueprintType)
struct TOSAILTHESTARRYSKY_API FTSTSSBattleSkillRow : public FTableRowBase
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Identity") FName SkillId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Identity") ETSTSSBattleSkillKind Kind = ETSTSSBattleSkillKind::Spell;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Identity") ETSTSSBattleSkillAdmission Admission = ETSTSSBattleSkillAdmission::DesignOnly;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Gameplay") ETSTSSBattleSkillTarget Target = ETSTSSBattleSkillTarget::Enemy;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Gameplay") int32 Power = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Gameplay") int32 ResourceCost = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Gameplay") int32 CooldownActorTurns = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Gameplay") bool bHealing = false;
    // These opt-in fields are currently admitted ONLY for Ender_Centering.
    // They do not confer job mastery, add unrecruited allies, or make a
    // generic no-damage support ability executable without permission.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Gameplay") bool bPartyPhysicalDefenseBuff = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Gameplay") int32 PhysicalDefenseBuffPercent = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Gameplay") int32 BuffDurationRounds = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Access") FName RequiredSchool = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Access") int32 RequiredMasteryRank = 0;
    // One additional cross-school requirement; complex multi-school syntheses stay DesignOnly.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Access") FName RequiredSecondarySchool = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Access") int32 RequiredSecondaryRank = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Access") FName RequiredWeaponClass = NAME_None;
    // Cue IDs are presentation requests only; this class does not spawn Niagara or animations.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Presentation") FName VfxCueId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Presentation") FName AnimationCueId = NAME_None;
};

// Separate learned knowledge, school mastery and equipped weapon from the combat state.
struct FTSTSSBattleSkillKnowledge
{
    TMap<FName, TSet<FName>> LearnedByActor;
    TMap<FName, TMap<FName, int32>> MasteryByActor;
    TMap<FName, FName> WeaponClassByActor;
};

// A bounded defensive status on the participant, not a permanent stat edit.
struct FTSTSSPhysicalDefenseBuff
{
    int32 Percent = 0;
    int32 ExpiresAtRound = 0;  // exclusive; round-based, not wall-clock
};

// Transactional counters. All combat actions must flow through this system for cooldowns
// to advance correctly. Persist/migrate this state before integrating into production saves.
struct FTSTSSBattleSkillState
{
    FTSTSSCombatTurnState Combat;
    TMap<FName, int32> AcceptedTurnsByActor;
    TMap<FName, TMap<FName, int32>> NextAllowedTurnByActorAndSkill;
    TMap<FName, FTSTSSPhysicalDefenseBuff> ActivePhysicalDefenseBuffs;
};

struct FTSTSSBattleSkillCue
{
    FName SkillId = NAME_None;
    FName ActorId = NAME_None;
    FName TargetId = NAME_None;
    FName VfxCueId = NAME_None;
    FName AnimationCueId = NAME_None;
};

class TOSAILTHESTARRYSKY_API FTSTSSBattleSkillSystem
{
public:
    // Source-authored First Wake review radius: 600 cm, centered on Ender.
    // Only an accepted, spatially resolved action may spend the MP/turn.
    static constexpr double ResonantPulseRadiusCm = 600.0;

    // The only admitted gameplay path for Ender_ResonantPulse. Participant
    // positions MUST originate from real world actors at the point of cast;
    // a client-supplied coordinate map is NOT authorization for production.
    // On any failure ALL three outputs remain unchanged.
    static bool TryUseResonantPulseArea(
        const FTSTSSBattleSkillState& State,
        const FTSTSSBattleSkillKnowledge& Knowledge,
        const TMap<FName, FName>& Factions,
        FName PartyFaction, FName OpponentFaction,
        FName ActorId, const FTSTSSBattleSkillRow& Row,
        const TMap<FName, FVector>& ParticipantWorldPositions,
        FTSTSSBattleSkillState& OutState,
        FTSTSSBattleSkillCue& OutCue,
        TArray<FName>& OutAffectedEnemyIds);

    // Fails closed and preserves both outputs on every failed request.
    static bool TryUseRow(
        const FTSTSSBattleSkillState& State,
        const FTSTSSBattleSkillKnowledge& Knowledge,
        const TMap<FName, FName>& Factions,
        FName PartyFaction, FName OpponentFaction,
        FName ActorId, FName TargetId, FName SkillId,
        const FTSTSSBattleSkillRow& Row,
        FTSTSSBattleSkillState& OutState,
        FTSTSSBattleSkillCue& OutCue);

    // Data-driven entry point for UDataTable authoring and QA. RowName == SkillId.
    static bool TryUseDataTable(
        const FTSTSSBattleSkillState& State,
        const FTSTSSBattleSkillKnowledge& Knowledge,
        const TMap<FName, FName>& Factions,
        FName PartyFaction, FName OpponentFaction,
        FName ActorId, FName TargetId, FName SkillId,
        const UDataTable* Skills,
        FTSTSSBattleSkillState& OutState,
        FTSTSSBattleSkillCue& OutCue);

private:
    // Shared legacy authorization/MP/cooldown path: the specialized area
    // entry point is the only caller permitted to resolve Pulse damage.
    static bool TryUseValidatedRow(
        const FTSTSSBattleSkillState& State,
        const FTSTSSBattleSkillKnowledge& Knowledge,
        const TMap<FName, FName>& Factions,
        FName PartyFaction, FName OpponentFaction,
        FName ActorId, FName TargetId, FName SkillId,
        const FTSTSSBattleSkillRow& Row,
        bool bAuthorizedAreaPulse,
        FTSTSSBattleSkillState& OutState,
        FTSTSSBattleSkillCue& OutCue);
};
