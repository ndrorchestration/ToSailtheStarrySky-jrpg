#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TSTSSBattleSkillSystem.h"
#include "TSS_CombatTurnManager.generated.h"

// Blueprint-facing adaptation of the existing TSTSS turn/ability authorities.
// This component never invents or independently applies combat damage.
UENUM(BlueprintType)
enum class ETSS_CombatPhase : uint8
{
    NotStarted,
    TurnSelection,
    ResolvingAction,
    TurnComplete,
    Victory,
    Defeat,
    Draw
};

USTRUCT(BlueprintType)
struct FTSS_CombatParticipant
{
    GENERATED_BODY()

    // Must match Stats.CharacterId. Explicit ownership is validated at initialization.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    FName ParticipantId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    FTSTSSCombatant Stats;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    int32 Agility = 10;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    bool bIsPlayerParty = false;

    // These are explicitly authored unlocks, NOT inferred from Five Lights or affinity.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat|Access")
    TArray<FName> LearnedSkills;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat|Access")
    TMap<FName, int32> MasteryRanks;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat|Access")
    FName EquippedWeaponClass = NAME_None;
};

USTRUCT(BlueprintType)
struct FTSS_CombatCommand
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    FName SourceParticipantId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    FName TargetParticipantId = NAME_None;

    // Stable skill row name. Avoid unresolved/unsafe placeholder AbilityDataAsset pointers.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    FName SkillId = NAME_None;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FTSSOnCombatPhaseChanged, ETSS_CombatPhase, NewPhase);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FTSSOnTurnStarted, FName, ActiveParticipantId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FiveParams(FTSSOnSkillAccepted,
    FName, SkillId, FName, ActorId, FName, TargetId,
    FName, VfxCueId, FName, AnimationCueId);

UCLASS(ClassGroup=(TSTSS), meta=(BlueprintSpawnableComponent))
class TOSAILTHESTARRYSKY_API UTSS_CombatTurnManager : public UActorComponent
{
    GENERATED_BODY()

public:
    UTSS_CombatTurnManager();

    // Only UDataTable rows of type FTSTSSBattleSkillRow with explicit
    // ReviewExecutable admission can resolve. Null means all commands are denied.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Combat")
    TObjectPtr<UDataTable> SkillTable = nullptr;

    // Full roster may contain up to five canonical protagonists; the active
    // selection is explicit (1..3). No silent first-three truncation.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Combat")
    bool InitializeEncounter(const TArray<FTSS_CombatParticipant>& PlayerRoster,
                             const TArray<FName>& ActivePlayerIds,
                             const TArray<FTSS_CombatParticipant>& Enemies);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Combat")
    bool SubmitCommand(const FTSS_CombatCommand& Command);

    // Review-only: area damage is resolved against the complete present
    // combat roster using real actor positions supplied by the encounter
    // owner. TargetParticipantId MUST equal the caster, not a chosen foe.
    // Exactly one MP charge, turn and accepted-cue broadcast per cast.
    bool SubmitResonantPulseArea(
        const FTSS_CombatCommand& Command,
        const TMap<FName, FVector>& ParticipantWorldPositions);

    UFUNCTION(BlueprintPure, Category="TSTSS|Combat")
    ETSS_CombatPhase GetCurrentPhase() const { return CurrentPhase; }

    UFUNCTION(BlueprintPure, Category="TSTSS|Combat")
    FName GetActiveParticipantId() const;

    UFUNCTION(BlueprintPure, Category="TSTSS|Combat")
    TArray<FName> GetReservePartyIds() const { return ReservePartyIds; }

    UFUNCTION(BlueprintPure, Category="TSTSS|Combat")
    TArray<FTSTSSCombatant> GetCombatantSnapshot() const { return BattleState.Combat.Roster; }

    UFUNCTION(BlueprintPure, Category="TSTSS|Combat")
    int32 GetCurrentRound() const { return BattleState.Combat.Round; }

    UFUNCTION(BlueprintPure, Category="TSTSS|Combat|Status")
    int32 GetCenteringRoundsRemaining(FName PartyMember) const;

    UFUNCTION(BlueprintPure, Category="TSTSS|Combat|Status")
    int32 GetCenteringEffectiveDefense(FName PartyMember) const;

    UPROPERTY(BlueprintAssignable, Category="TSTSS|Combat|Events")
    FTSSOnCombatPhaseChanged OnPhaseChanged;

    UPROPERTY(BlueprintAssignable, Category="TSTSS|Combat|Events")
    FTSSOnTurnStarted OnTurnStarted;

    // Metadata only. The receiver may preview cues; nothing spawns Niagara or plays a montage.
    UPROPERTY(BlueprintAssignable, Category="TSTSS|Combat|Events")
    FTSSOnSkillAccepted OnSkillAccepted;

private:
    bool CommitAcceptedAction(
        FTSTSSBattleSkillState&& Candidate,
        const FTSTSSBattleSkillCue& CandidateCue);

    static bool ValidateParticipant(const FTSS_CombatParticipant& Participant,
                                    bool bExpectedPlayer);
    static bool IsCanonicalPlayer(FName ParticipantId);

    // Non-USTRUCT runtime state is intentionally NOT saved by component reflection.
    // Versioned SaveGame support requires a separate explicit implementation.
    FTSTSSBattleSkillState BattleState;
    FTSTSSBattleSkillKnowledge Knowledge;
    TMap<FName, FName> Factions;

    UPROPERTY(Transient)
    TArray<FName> ReservePartyIds;

    ETSS_CombatPhase CurrentPhase = ETSS_CombatPhase::NotStarted;
};
