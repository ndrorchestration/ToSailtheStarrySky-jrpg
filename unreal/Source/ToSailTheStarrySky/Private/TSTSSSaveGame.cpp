#include "TSTSSSaveGame.h"

bool UTSTSSSaveGame::IsStructurallyValid() const
{
    if (!IsSupportedVersion() ||
        (InspectionMask & ~0x07u) != 0 ||
        (!bFirstWakeStarted && InspectionMask != 0) ||
        (InspectionMask != 0 && static_cast<uint8>(FirstWakeBeat) < static_cast<uint8>(ETSTSSFirstWakeBeat::BoardedAureateWake)) ||
        (static_cast<uint8>(FirstWakeBeat) >= static_cast<uint8>(ETSTSSFirstWakeBeat::EngineeringChecked) && InspectionMask != 0x07) ||
        static_cast<uint8>(FirstWakeBeat) >
            static_cast<uint8>(ETSTSSFirstWakeBeat::ReturnedToBerth) ||
        (!bFirstWakeStarted && FirstWakeBeat != ETSTSSFirstWakeBeat::FlyerDiscovered))
    {
        return false;
    }
    // The story roster has five identities; reject oversized or unknown rosters.
    if (PartyRoster.Num() > 5) return false;
    const TSet<FName> Allowed{FName(TEXT("Ender")), FName(TEXT("Ionia")), FName(TEXT("Lyra")), FName(TEXT("Reson")), FName(TEXT("Aepex"))};
    TSet<FName> Seen;
    for (const FTSTSSCombatant& Member : PartyRoster)
    {
        if (Member.CharacterId.IsNone() || !Allowed.Contains(Member.CharacterId) || Seen.Contains(Member.CharacterId) ||
            Member.MaxHealth <= 0 || Member.Health < 0 ||
            Member.Health > Member.MaxHealth || Member.MaxResource < 0 ||
            Member.Resource < 0 || Member.Resource > Member.MaxResource ||
            Member.Attack < 0 || Member.Defense < 0)
        {
            return false;
        }
        Seen.Add(Member.CharacterId);
    }
    return true;
}
