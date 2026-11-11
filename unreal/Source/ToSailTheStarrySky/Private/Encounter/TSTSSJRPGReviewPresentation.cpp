#include "Encounter/TSTSSJRPGReviewPresentation.h"
#include "Math/UnrealMathUtility.h"

float UTSTSSJRPGReviewPresentation::Duration(
    ETSTSSJRPGReviewSequencePhase InPhase)
{
    switch(InPhase)
    {
    case ETSTSSJRPGReviewSequencePhase::EncounterFlash: return .42f;
    case ETSTSSJRPGReviewSequencePhase::BattleReveal: return .36f;
    case ETSTSSJRPGReviewSequencePhase::VictoryFanfare: return 1.45f;
    case ETSTSSJRPGReviewSequencePhase::Celebration: return 1.25f;
    case ETSTSSJRPGReviewSequencePhase::ReturnFlash: return .46f;
    default: return 0.f;
    }
}

bool UTSTSSJRPGReviewPresentation::TryBegin(int32 TicketSerial)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (ActiveTicket!=0 || TicketSerial<=0 ||
        Phase!=ETSTSSJRPGReviewSequencePhase::Exploration) return false;
    ActiveTicket=TicketSerial;
    SetPhase(ETSTSSJRPGReviewSequencePhase::EncounterFlash);
    return true;
#endif
}

bool UTSTSSJRPGReviewPresentation::Advance(float DeltaSeconds)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const float Length=Duration(Phase);
    if (Length<=0.f || !FMath::IsFinite(DeltaSeconds) ||
        DeltaSeconds<=0.f || DeltaSeconds>.25f) return false;
    Elapsed=FMath::Min(Length,Elapsed+DeltaSeconds);
    if (Elapsed<Length) return true;
    switch(Phase)
    {
    case ETSTSSJRPGReviewSequencePhase::EncounterFlash:
        SetPhase(ETSTSSJRPGReviewSequencePhase::BattleReveal);break;
    case ETSTSSJRPGReviewSequencePhase::VictoryFanfare:
        SetPhase(ETSTSSJRPGReviewSequencePhase::Celebration);break;
    case ETSTSSJRPGReviewSequencePhase::Celebration:
        SetPhase(ETSTSSJRPGReviewSequencePhase::Rewards);break;
    case ETSTSSJRPGReviewSequencePhase::ReturnFlash:
        SetPhase(ETSTSSJRPGReviewSequencePhase::ReturnReady);break;
    default:break;
    }
    return true;
#endif
}

bool UTSTSSJRPGReviewPresentation::TryAbortBeforeCombat(int32 TicketSerial)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (ActiveTicket!=TicketSerial || TicketSerial<=0 ||
        (Phase!=ETSTSSJRPGReviewSequencePhase::EncounterFlash &&
         Phase!=ETSTSSJRPGReviewSequencePhase::BattleReveal)) return false;
    ActiveTicket=0;
    SetPhase(ETSTSSJRPGReviewSequencePhase::Exploration);
    return true;
#endif
}

bool UTSTSSJRPGReviewPresentation::TryEnterCombat(int32 TicketSerial)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (ActiveTicket!=TicketSerial || TicketSerial<=0 ||
        !IsAwaitingBattleStart()) return false;
    SetPhase(ETSTSSJRPGReviewSequencePhase::Combat);
    return true;
#endif
}

bool UTSTSSJRPGReviewPresentation::TryResolveVictory(int32 TicketSerial)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (ActiveTicket!=TicketSerial || TicketSerial<=0 ||
        Phase!=ETSTSSJRPGReviewSequencePhase::Combat) return false;
    SetPhase(ETSTSSJRPGReviewSequencePhase::VictoryFanfare);
    return true;
#endif
}

bool UTSTSSJRPGReviewPresentation::TryResolveDefeat(int32 TicketSerial)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (ActiveTicket!=TicketSerial || TicketSerial<=0 ||
        Phase!=ETSTSSJRPGReviewSequencePhase::Combat) return false;
    SetPhase(ETSTSSJRPGReviewSequencePhase::Defeat);
    return true;
#endif
}

bool UTSTSSJRPGReviewPresentation::TryFlee(int32 TicketSerial)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (ActiveTicket!=TicketSerial || TicketSerial<=0 ||
        Phase!=ETSTSSJRPGReviewSequencePhase::Combat) return false;
    SetPhase(ETSTSSJRPGReviewSequencePhase::ReturnFlash);
    return true;
#endif
}

bool UTSTSSJRPGReviewPresentation::TryDismissResult(int32 TicketSerial)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (ActiveTicket!=TicketSerial || TicketSerial<=0 ||
        (Phase!=ETSTSSJRPGReviewSequencePhase::Rewards &&
         Phase!=ETSTSSJRPGReviewSequencePhase::Defeat)) return false;
    SetPhase(ETSTSSJRPGReviewSequencePhase::ReturnFlash);
    return true;
#endif
}

bool UTSTSSJRPGReviewPresentation::TryFinishReturn(int32 TicketSerial)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (ActiveTicket!=TicketSerial || TicketSerial<=0 ||
        Phase!=ETSTSSJRPGReviewSequencePhase::ReturnReady) return false;
    ActiveTicket=0;
    SetPhase(ETSTSSJRPGReviewSequencePhase::Exploration);
    return true;
#endif
}

float UTSTSSJRPGReviewPresentation::GetPhaseProgress() const
{
    const float Length=Duration(Phase);
    return Length>0.f ? FMath::Clamp(Elapsed/Length,0.f,1.f) : 0.f;
}
