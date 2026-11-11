#include "Encounter/TSTSSJRPGEncounterDirector.h"
#include "Math/UnrealMathUtility.h"

UTSTSSJRPGEncounterDirector::UTSTSSJRPGEncounterDirector()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UTSTSSJRPGEncounterDirector::IsValidBiome(ETSTSSJRPGEncounterBiome Biome)
{
    return static_cast<uint8>(Biome) <=
        static_cast<uint8>(ETSTSSJRPGEncounterBiome::Highlands);
}

bool UTSTSSJRPGEncounterDirector::IsValidRate(ETSTSSJRPGEncounterRate Rate)
{
    return static_cast<uint8>(Rate) <=
        static_cast<uint8>(ETSTSSJRPGEncounterRate::Increased);
}

bool UTSTSSJRPGEncounterDirector::IsWalkingAuthorized(
    const FTSTSSJRPGEncounterContext& Context)
{
    return Context.bTraversalActive && Context.bAreaAuthorized &&
        Context.bPartyAuthorized && !Context.bSafeZone &&
        !Context.bStorySequenceActive && !Context.bBattleActive &&
        !Context.bFastTravelOrTeleport && !Context.bShipTravel &&
        IsValidRate(Context.Rate) && Context.Rate!=ETSTSSJRPGEncounterRate::Off;
}

bool UTSTSSJRPGEncounterDirector::IsAllowedReviewWave(
    ETSTSSJRPGEncounterBiome Biome, FName Preset)
{
    if (Preset.IsNone()) return false;
    switch (Biome)
    {
    case ETSTSSJRPGEncounterBiome::HarborOutskirts:
        return Preset == TEXT("Review_HarborBanditPatrol") ||
               Preset == TEXT("Review_HarborBanditCaptain");
    case ETSTSSJRPGEncounterBiome::Woodland:
        return Preset == TEXT("Review_WoodlandSporeline") ||
               Preset == TEXT("Review_WoodlandSentinel");
    case ETSTSSJRPGEncounterBiome::Coast:
        return Preset == TEXT("Review_CoastalHunters") ||
               Preset == TEXT("Review_CoastalShellbacks");
    case ETSTSSJRPGEncounterBiome::Highlands:
        return Preset == TEXT("Review_HighlandStalkers") ||
               Preset == TEXT("Review_HighlandBristle");
    default:
        return false;
    }
}

bool UTSTSSJRPGEncounterDirector::TryConfigureReviewBiome(
    ETSTSSJRPGEncounterBiome Biome, int32 Seed)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (bPending || !IsValidBiome(Biome) || Seed == MIN_int32) return false;
    ConfiguredBiome=Biome;
    Random.Initialize(Seed);
    DistanceCm=0.f;
    StepRemainderCm=0.f;
    bConfigured=true;
    return true;
#endif
}

FName UTSTSSJRPGEncounterDirector::SelectWeightedWave()
{
    // Weighted mix: common encounters dominate, tougher/different profile
    // is less frequent. No boss is auto-authorized as a story event.
    const bool bRare = Random.RandRange(1,100) > 75;
    switch (ConfiguredBiome)
    {
    case ETSTSSJRPGEncounterBiome::HarborOutskirts:
        return bRare ? TEXT("Review_HarborBanditCaptain")
                     : TEXT("Review_HarborBanditPatrol");
    case ETSTSSJRPGEncounterBiome::Woodland:
        return bRare ? TEXT("Review_WoodlandSentinel")
                     : TEXT("Review_WoodlandSporeline");
    case ETSTSSJRPGEncounterBiome::Coast:
        return bRare ? TEXT("Review_CoastalShellbacks")
                     : TEXT("Review_CoastalHunters");
    case ETSTSSJRPGEncounterBiome::Highlands:
        return bRare ? TEXT("Review_HighlandBristle")
                     : TEXT("Review_HighlandStalkers");
    default:
        return NAME_None;
    }
}

bool UTSTSSJRPGEncounterDirector::TryIssue(
    bool bScripted, FName Preset, FTSTSSJRPGEncounterTicket& OutTicket)
{
    if (bPending || !bConfigured || NextTicketSerial<=0 ||
        NextTicketSerial==MAX_int32 ||
        !IsAllowedReviewWave(ConfiguredBiome,Preset)) return false;
    FTSTSSJRPGEncounterTicket Candidate;
    Candidate.Serial=NextTicketSerial++;
    Candidate.ReviewWavePreset=Preset;
    Candidate.Biome=ConfiguredBiome;
    Candidate.bScripted=bScripted;
    Candidate.bReviewOnly=true;
    PendingTicket=Candidate;
    bPending=true;
    bBattleStarted=false;
    OutTicket=Candidate;
    return true;
}

bool UTSTSSJRPGEncounterDirector::TryRecordWalking(
    float DeltaCm, const FTSTSSJRPGEncounterContext& Context,
    FTSTSSJRPGEncounterTicket& OutTicket)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!bConfigured || bPending || !FMath::IsFinite(DeltaCm) ||
        DeltaCm<=0.f || DeltaCm>400.f || !IsValidRate(Context.Rate)) return false;

    if (!IsWalkingAuthorized(Context))
    {
        // Safe areas/ship/scene transitions cannot bank a near-certain
        // ambush for the moment the player exits the protected sequence.
        DistanceCm=0.f;
        StepRemainderCm=0.f;
        return false;
    }

    StepRemainderCm+=DeltaCm;
    while (StepRemainderCm>=CheckIntervalCm)
    {
        StepRemainderCm-=CheckIntervalCm;
        DistanceCm+=CheckIntervalCm;
        if (DistanceCm < MinimumWalkCm) continue;
        int32 Chance=16 + FMath::Clamp(
            FMath::FloorToInt((DistanceCm-MinimumWalkCm)/600.f),0,14);
        if (Context.Rate == ETSTSSJRPGEncounterRate::Reduced)
            Chance=FMath::Max(1,Chance/2);
        if (Context.Rate == ETSTSSJRPGEncounterRate::Increased)
            Chance=FMath::Min(85,Chance*2);
        if (DistanceCm>=GuaranteedEncounterCm ||
            Random.RandRange(1,100)<=Chance)
        {
            return TryIssue(false,SelectWeightedWave(),OutTicket);
        }
    }
    return false;
#endif
}

bool UTSTSSJRPGEncounterDirector::TryRequestScripted(
    FName Preset, const FTSTSSJRPGEncounterContext& Context,
    FTSTSSJRPGEncounterTicket& OutTicket)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    // Scripted battles can occur during a cutscene or protected area
    // ONLY if the narrative authority explicitly permits that preset.
    if (!bConfigured || bPending || !Context.bAreaAuthorized ||
        !Context.bPartyAuthorized || !Context.bScriptedEncounterApproved ||
        Context.bBattleActive || Context.bFastTravelOrTeleport ||
        Context.bShipTravel) return false;
    return TryIssue(true,Preset,OutTicket);
#endif
}

bool UTSTSSJRPGEncounterDirector::TryCancelPending(int32 TicketSerial)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!bPending || bBattleStarted || TicketSerial<=0 ||
        PendingTicket.Serial!=TicketSerial) return false;
    bPending=false;
    bBattleStarted=false;
    PendingTicket=FTSTSSJRPGEncounterTicket();
    DistanceCm=0.f;
    StepRemainderCm=0.f;
    return true;
#endif
}

bool UTSTSSJRPGEncounterDirector::TryAcknowledgeBattleStart(int32 TicketSerial)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!bPending || bBattleStarted || TicketSerial<=0 ||
        PendingTicket.Serial != TicketSerial) return false;
    bBattleStarted=true;
    return true;
#endif
}

bool UTSTSSJRPGEncounterDirector::TryCompleteBattle(int32 TicketSerial)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!bPending || !bBattleStarted || TicketSerial<=0 ||
        PendingTicket.Serial != TicketSerial) return false;
    bPending=false;
    bBattleStarted=false;
    PendingTicket=FTSTSSJRPGEncounterTicket();
    DistanceCm=0.f;
    StepRemainderCm=0.f;
    return true;
#endif
}
