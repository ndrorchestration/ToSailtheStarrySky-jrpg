#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Math/RandomStream.h"
#include "TSTSSJRPGEncounterDirector.generated.h"

// Geography labels are research profiles, NOT approved First Wake spawns.
// New biomes must be explicitly mapped to encounters before they are admitted.
UENUM(BlueprintType)
enum class ETSTSSJRPGEncounterBiome : uint8
{
    HarborOutskirts,
    Woodland,
    Coast,
    Highlands
};

UENUM(BlueprintType)
enum class ETSTSSJRPGEncounterRate : uint8
{
    Off,
    Reduced,
    Normal,
    Increased
};

USTRUCT(BlueprintType)
struct FTSTSSJRPGEncounterContext
{
    GENERATED_BODY()

    // All three must be explicitly granted by the actual exploration authority.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Encounter|Authority")
    bool bTraversalActive = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Encounter|Authority")
    bool bAreaAuthorized = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Encounter|Authority")
    bool bPartyAuthorized = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Encounter|Safety")
    bool bSafeZone = true;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Encounter|Safety")
    bool bStorySequenceActive = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Encounter|Safety")
    bool bBattleActive = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Encounter|Safety")
    bool bFastTravelOrTeleport = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Encounter|Safety")
    bool bShipTravel = false;

    // Separate, explicit narrative authorization. Random encounters never
    // become scripted bosses by inferring authority from a biome.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Encounter|Authority")
    bool bScriptedEncounterApproved = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Encounter|Accessibility")
    ETSTSSJRPGEncounterRate Rate = ETSTSSJRPGEncounterRate::Normal;
};

USTRUCT(BlueprintType)
struct FTSTSSJRPGEncounterTicket
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category="Encounter")
    int32 Serial = 0;
    UPROPERTY(BlueprintReadOnly, Category="Encounter")
    FName ReviewWavePreset = NAME_None;
    UPROPERTY(BlueprintReadOnly, Category="Encounter")
    ETSTSSJRPGEncounterBiome Biome = ETSTSSJRPGEncounterBiome::HarborOutskirts;
    UPROPERTY(BlueprintReadOnly, Category="Encounter")
    bool bScripted = false;
    UPROPERTY(BlueprintReadOnly, Category="Encounter")
    bool bReviewOnly = true;
};

// Deterministic, fixed-distance random encounter selection for a classic JRPG.
// No actor spawning, battle state, XP, loot, SaveGame, level or quest mutation.
// A separate adapter must acknowledge/resolve tickets to use the combat system.
UCLASS(ClassGroup=(TSTSS), BlueprintType, meta=(BlueprintSpawnableComponent))
class TOSAILTHESTARRYSKY_API UTSTSSJRPGEncounterDirector : public UActorComponent
{
    GENERATED_BODY()
public:
    UTSTSSJRPGEncounterDirector();

    // Refuse reconfiguration with an outstanding ticket.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Encounters")
    bool TryConfigureReviewBiome(ETSTSSJRPGEncounterBiome Biome, int32 Seed);

    // One frame of physical walking movement; input must be finite,
    // nonnegative and <= 400 cm to reject teleport/reset spikes.
    // OutTicket is untouched unless a NEW encounter is selected.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Encounters")
    bool TryRecordWalking(float DeltaCm, const FTSTSSJRPGEncounterContext& Context,
                          FTSTSSJRPGEncounterTicket& OutTicket);

    // A boss/event may bypass the random counter only under separate explicit
    // scripted-admission. Never an automatic boss or story spawn.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Encounters")
    bool TryRequestScripted(FName ReviewWavePreset,
                            const FTSTSSJRPGEncounterContext& Context,
                            FTSTSSJRPGEncounterTicket& OutTicket);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Encounters")
    bool TryAcknowledgeBattleStart(int32 TicketSerial);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Encounters")
    bool TryCompleteBattle(int32 TicketSerial);

    UFUNCTION(BlueprintPure, Category="TSTSS|Encounters")
    bool HasOutstandingTicket() const { return bPending; }

    UFUNCTION(BlueprintPure, Category="TSTSS|Encounters")
    float GetWalkingDistanceSinceBattleCm() const { return DistanceCm; }

    UFUNCTION(BlueprintPure, Category="TSTSS|Encounters")
    bool IsReviewRegionConfigured() const { return bConfigured; }

private:
    static bool IsValidBiome(ETSTSSJRPGEncounterBiome Biome);
    static bool IsValidRate(ETSTSSJRPGEncounterRate Rate);
    static bool IsWalkingAuthorized(const FTSTSSJRPGEncounterContext& Context);
    static bool IsAllowedReviewWave(ETSTSSJRPGEncounterBiome Biome, FName Preset);
    bool TryIssue(bool bScripted, FName Preset, FTSTSSJRPGEncounterTicket& OutTicket);
    FName SelectWeightedWave();

    FRandomStream Random;
    float DistanceCm = 0.f;
    float StepRemainderCm = 0.f;
    int32 NextTicketSerial = 1;
    ETSTSSJRPGEncounterBiome ConfiguredBiome = ETSTSSJRPGEncounterBiome::HarborOutskirts;
    FTSTSSJRPGEncounterTicket PendingTicket;
    bool bConfigured = false;
    bool bPending = false;
    bool bBattleStarted = false;

    static constexpr float CheckIntervalCm = 300.f;
    static constexpr float MinimumWalkCm = 1800.f;
    static constexpr float GuaranteedEncounterCm = 5700.f;
};
