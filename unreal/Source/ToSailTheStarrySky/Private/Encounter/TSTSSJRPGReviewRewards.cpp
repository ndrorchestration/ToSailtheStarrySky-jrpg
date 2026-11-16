#include "Encounter/TSTSSJRPGReviewRewards.h"

namespace
{
    FTSTSSJRPGReviewLootLine Loot(const TCHAR* Item, const TCHAR* Name,
                                 int32 Quantity)
    {
        FTSTSSJRPGReviewLootLine Line;
        Line.ItemId=FName(Item);
        Line.DisplayName=Name;
        Line.Quantity=Quantity;
        return Line;
    }
}

bool UTSTSSJRPGReviewRewards::IsExactReviewParty(const TArray<FName>& Party)
{
    if (Party.Num()<1 || Party.Num()>3 || Party[0]!=TEXT("Ender")) return false;
    if (Party.Num()>=2 && Party[1]!=TEXT("Ionia")) return false;
    if (Party.Num()==3 && Party[2]!=TEXT("Lyra")) return false;
    return true;
}

bool UTSTSSJRPGReviewRewards::TryMakeReward(
    FName Wave, FTSTSSJRPGReviewReward& Out)
{
    FTSTSSJRPGReviewReward Candidate;
    Candidate.SourceWave=Wave;
    // Deliberately small, provisional synthetic review rewards, not canon.
    // Fixed per-wave results are testable and cannot be RNG rerolled by
    // reopening the result panel.
    if (Wave==TEXT("Review_HarborBanditPatrol"))
    { Candidate.GoldEarned=18; Candidate.XpEachPartyMember=12;
      Candidate.Items={Loot(TEXT("Review_SalvagedRope"),TEXT("Salvaged Rope"),1)}; }
    else if (Wave==TEXT("Review_HarborBanditCaptain"))
    { Candidate.GoldEarned=36; Candidate.XpEachPartyMember=24;
      Candidate.Items={Loot(TEXT("Review_BrassFastener"),TEXT("Brass Fastener"),2)}; }
    else if (Wave==TEXT("Review_WoodlandSporeline"))
    { Candidate.GoldEarned=9; Candidate.XpEachPartyMember=14;
      Candidate.Items={Loot(TEXT("Review_SporeSample"),TEXT("Spore Sample"),1)}; }
    else if (Wave==TEXT("Review_WoodlandSentinel"))
    { Candidate.GoldEarned=15; Candidate.XpEachPartyMember=28;
      Candidate.Items={Loot(TEXT("Review_ResinFragment"),TEXT("Resin Fragment"),2)}; }
    else if (Wave==TEXT("Review_CoastalHunters"))
    { Candidate.GoldEarned=11; Candidate.XpEachPartyMember=15;
      Candidate.Items={Loot(TEXT("Review_SmoothScale"),TEXT("Smooth Scale"),1)}; }
    else if (Wave==TEXT("Review_CoastalShellbacks"))
    { Candidate.GoldEarned=17; Candidate.XpEachPartyMember=23;
      Candidate.Items={Loot(TEXT("Review_ShellPlate"),TEXT("Shell Plate"),1)}; }
    else if (Wave==TEXT("Review_HighlandStalkers"))
    { Candidate.GoldEarned=13; Candidate.XpEachPartyMember=19;
      Candidate.Items={Loot(TEXT("Review_SoftPelt"),TEXT("Soft Pelt"),1)}; }
    else if (Wave==TEXT("Review_HighlandBristle"))
    { Candidate.GoldEarned=19; Candidate.XpEachPartyMember=25;
      Candidate.Items={Loot(TEXT("Review_ToughBristles"),TEXT("Tough Bristles"),2)}; }
    else return false;
    Out=MoveTemp(Candidate);
    return true;
}

bool UTSTSSJRPGReviewRewards::TryAwardOnce(
    int32 TicketSerial,FName WavePreset,const TArray<FName>& ActiveParty,
    FTSTSSJRPGReviewReward& OutReward)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (TicketSerial<=0 || AwardedTickets.Contains(TicketSerial) ||
        !IsExactReviewParty(ActiveParty) ||
        GoldBalance<0 || GoldBalance>1000000) return false;
    FTSTSSJRPGReviewReward Next;
    if (!TryMakeReward(WavePreset,Next) ||
        Next.GoldEarned<=0 || Next.XpEachPartyMember<=0 ||
        Next.Items.IsEmpty()) return false;
    if (GoldBalance>1000000-Next.GoldEarned) return false;
    for (const FName Member:ActiveParty)
    {
        const int32 Current=XpBalances.FindRef(Member);
        if (Current<0 || Current>1000000-Next.XpEachPartyMember)
            return false;
    }
    for (const FTSTSSJRPGReviewLootLine& Line:Next.Items)
    {
        const int32 Current=Inventory.FindRef(Line.ItemId);
        if (Line.ItemId.IsNone() || Line.Quantity<=0 ||
            Current<0 || Current>1000000-Line.Quantity) return false;
    }
    // All checks complete; only now mutate the transient review balances.
    GoldBalance+=Next.GoldEarned;
    for (const FName Member:ActiveParty)
        XpBalances.FindOrAdd(Member)+=Next.XpEachPartyMember;
    for (const FTSTSSJRPGReviewLootLine& Line:Next.Items)
        Inventory.FindOrAdd(Line.ItemId)+=Line.Quantity;
    AwardedTickets.Add(TicketSerial);
    Next.TicketSerial=TicketSerial;
    Next.AwardedPartyIds=ActiveParty;
    OutReward=MoveTemp(Next);
    return true;
#endif
}

int32 UTSTSSJRPGReviewRewards::GetExperienceTotal(FName PartyId) const
{
    return XpBalances.FindRef(PartyId);
}
int32 UTSTSSJRPGReviewRewards::GetItemCount(FName ItemId) const
{
    return Inventory.FindRef(ItemId);
}
