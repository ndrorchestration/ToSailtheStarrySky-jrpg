#include "Enemies/TSTSSSliceEnemyCatalog.h"

namespace
{
    constexpr int32 MaxInstanceIdLength = 64;

    bool IsPartyName(const FName Id)
    {
        return Id == TEXT("Ender") || Id == TEXT("Ionia") ||
               Id == TEXT("Lyra") || Id == TEXT("Reson") || Id == TEXT("Aepex");
    }

    void AddRow(UDataTable* Table, const TCHAR* Id, int32 Power, int32 Cost,
                int32 Cooldown, const TCHAR* Vfx, const TCHAR* Animation,
                bool bExplicitReviewExecution)
    {
        FTSTSSBattleSkillRow Row;
        Row.SkillId = FName(Id);
        // This is a mechanical damage action, not an affinity-granted spell.
        Row.Kind = ETSTSSBattleSkillKind::JobArt;
        Row.Admission = bExplicitReviewExecution
            ? ETSTSSBattleSkillAdmission::ReviewExecutable
            : ETSTSSBattleSkillAdmission::DesignOnly;
        Row.Target = ETSTSSBattleSkillTarget::Enemy;
        Row.Power = Power;
        Row.ResourceCost = Cost;
        Row.CooldownActorTurns = Cooldown;
        Row.VfxCueId = FName(Vfx);
        Row.AnimationCueId = FName(Animation);
        Table->AddRow(Row.SkillId, Row);
    }
}

bool FTSTSSSliceEnemyCatalog::TryDescribe(
    ETSTSSSliceEnemyKind Kind, FTSTSSSliceEnemyDescriptor& Out)
{
    FTSTSSSliceEnemyDescriptor Next;
    switch (Kind)
    {
    case ETSTSSSliceEnemyKind::HarmonicShear:
        Next.ArchetypeId = TEXT("windShear");
        Next.HabitatTag = TEXT("Storm");
        Next.DisplayName = TEXT("Harmonic Shear Elemental");
        Next.MaxHP = 14;
        Next.MaxResource = 6;
        Next.Attack = 2;
        Next.Defense = 1;
        Next.Agility = 13;
        Next.AbilityIds = {TEXT("SliceReview_GaleForce"),
                           TEXT("SliceReview_ShearCut")};
        break;
    case ETSTSSSliceEnemyKind::AetherLeakWisp:
        Next.ArchetypeId = TEXT("aetherLeak");
        Next.HabitatTag = TEXT("Anomaly");
        Next.DisplayName = TEXT("Aether Leak Wisp [provisional]");
        Next.MaxHP = 10;
        Next.MaxResource = 8;
        Next.Attack = 1;
        Next.Defense = 0;
        Next.Agility = 17;
        Next.AbilityIds = {TEXT("SliceReview_WispSpark"),
                           TEXT("SliceReview_WispSurge")};
        break;
    case ETSTSSSliceEnemyKind::DockSkitter:
        Next.ArchetypeId = TEXT("dockSkitterReview");
        Next.Family = ETSTSSSliceEnemyFamily::Fauna;
        Next.HabitatTag = TEXT("Harbor");
        Next.DisplayName = TEXT("Dock Skitter [provisional]");
        Next.MaxHP = 20;
        Next.MaxResource = 4;
        Next.Attack = 3;
        Next.Defense = 2;
        Next.Agility = 8;
        Next.AbilityIds = {TEXT("SliceReview_SkitterSnap"),
                           TEXT("SliceReview_SkitterLunge")};
        break;
    case ETSTSSSliceEnemyKind::BanditCutpurse:
        Next.ArchetypeId = TEXT("banditCutpurseReview");
        Next.DisplayName = TEXT("Quayside Cutpurse [provisional]");
        Next.Family = ETSTSSSliceEnemyFamily::Bandit;
        Next.HabitatTag = TEXT("Harbor");
        Next.bLeader = false;
        Next.MaxHP = 22;
        Next.MaxResource = 4;
        Next.Attack = 4;
        Next.Defense = 1;
        Next.Agility = 15;
        Next.AbilityIds = {TEXT("SliceReview_CutpurseSlash"),
                           TEXT("SliceReview_CutpurseBackstab")};
        break;
    case ETSTSSSliceEnemyKind::BanditSlinger:
        Next.ArchetypeId = TEXT("banditSlingerReview");
        Next.DisplayName = TEXT("Quayside Slinger [provisional]");
        Next.Family = ETSTSSSliceEnemyFamily::Bandit;
        Next.HabitatTag = TEXT("Harbor");
        Next.bLeader = false;
        Next.MaxHP = 18;
        Next.MaxResource = 6;
        Next.Attack = 3;
        Next.Defense = 1;
        Next.Agility = 14;
        Next.AbilityIds = {TEXT("SliceReview_SlingerShot"),
                           TEXT("SliceReview_SlingerVolley")};
        break;
    case ETSTSSSliceEnemyKind::BanditCaptain:
        Next.ArchetypeId = TEXT("banditCaptainReview");
        Next.DisplayName = TEXT("Bandit Captain [provisional]");
        Next.Family = ETSTSSSliceEnemyFamily::Bandit;
        Next.HabitatTag = TEXT("Harbor");
        Next.bLeader = true;
        Next.MaxHP = 44;
        Next.MaxResource = 10;
        Next.Attack = 6;
        Next.Defense = 3;
        Next.Agility = 12;
        Next.AbilityIds = {TEXT("SliceReview_CaptainStrike"),
                           TEXT("SliceReview_CaptainHeavyBlow")};
        break;
    case ETSTSSSliceEnemyKind::Thornvine:
        Next.ArchetypeId = TEXT("thornvineReview");
        Next.DisplayName = TEXT("Thornvine Creeper [provisional]");
        Next.Family = ETSTSSSliceEnemyFamily::Flora;
        Next.HabitatTag = TEXT("Woodland");
        Next.bLeader = false;
        Next.MaxHP = 26;
        Next.MaxResource = 6;
        Next.Attack = 4;
        Next.Defense = 2;
        Next.Agility = 6;
        Next.AbilityIds = {TEXT("SliceReview_VineLash"),
                           TEXT("SliceReview_ThornBurst")};
        break;
    case ETSTSSSliceEnemyKind::Sporecap:
        Next.ArchetypeId = TEXT("sporecapReview");
        Next.DisplayName = TEXT("Sporecap Stalker [provisional]");
        Next.Family = ETSTSSSliceEnemyFamily::Flora;
        Next.HabitatTag = TEXT("Woodland");
        Next.bLeader = false;
        Next.MaxHP = 19;
        Next.MaxResource = 9;
        Next.Attack = 2;
        Next.Defense = 1;
        Next.Agility = 9;
        Next.AbilityIds = {TEXT("SliceReview_SporeTap"),
                           TEXT("SliceReview_BloomPulse")};
        break;
    case ETSTSSSliceEnemyKind::RootSentinel:
        Next.ArchetypeId = TEXT("rootSentinelReview");
        Next.DisplayName = TEXT("Root Sentinel [provisional]");
        Next.Family = ETSTSSSliceEnemyFamily::Flora;
        Next.HabitatTag = TEXT("Woodland");
        Next.bLeader = false;
        Next.MaxHP = 48;
        Next.MaxResource = 7;
        Next.Attack = 5;
        Next.Defense = 5;
        Next.Agility = 4;
        Next.AbilityIds = {TEXT("SliceReview_RootBash"),
                           TEXT("SliceReview_BarkCrush")};
        break;
    case ETSTSSSliceEnemyKind::ReefEel:
        Next.ArchetypeId = TEXT("reefEelReview");
        Next.DisplayName = TEXT("Reef Eel [provisional]");
        Next.Family = ETSTSSSliceEnemyFamily::Aquatic;
        Next.HabitatTag = TEXT("Coastal");
        Next.bLeader = false;
        Next.MaxHP = 20;
        Next.MaxResource = 9;
        Next.Attack = 3;
        Next.Defense = 0;
        Next.Agility = 18;
        Next.AbilityIds = {TEXT("SliceReview_EelTailWhip"),
                           TEXT("SliceReview_EelSurgeBite")};
        break;
    case ETSTSSSliceEnemyKind::TidefinRaptor:
        Next.ArchetypeId = TEXT("tidefinRaptorReview");
        Next.DisplayName = TEXT("Tidefin Hunter [provisional]");
        Next.Family = ETSTSSSliceEnemyFamily::Aquatic;
        Next.HabitatTag = TEXT("Coastal");
        Next.bLeader = false;
        Next.MaxHP = 30;
        Next.MaxResource = 6;
        Next.Attack = 5;
        Next.Defense = 2;
        Next.Agility = 15;
        Next.AbilityIds = {TEXT("SliceReview_FinRake"),
                           TEXT("SliceReview_TideLunge")};
        break;
    case ETSTSSSliceEnemyKind::ShellbackCrab:
        Next.ArchetypeId = TEXT("shellbackCrabReview");
        Next.DisplayName = TEXT("Shellback Crab [provisional]");
        Next.Family = ETSTSSSliceEnemyFamily::Aquatic;
        Next.HabitatTag = TEXT("Coastal");
        Next.bLeader = false;
        Next.MaxHP = 38;
        Next.MaxResource = 5;
        Next.Attack = 4;
        Next.Defense = 6;
        Next.Agility = 5;
        Next.AbilityIds = {TEXT("SliceReview_PincerSnap"),
                           TEXT("SliceReview_ShellSlam")};
        break;
    case ETSTSSSliceEnemyKind::CliffLynx:
        Next.ArchetypeId = TEXT("cliffLynxReview");
        Next.DisplayName = TEXT("Cliff Lynx [provisional]");
        Next.Family = ETSTSSSliceEnemyFamily::Fauna;
        Next.HabitatTag = TEXT("Highlands");
        Next.bLeader = false;
        Next.MaxHP = 24;
        Next.MaxResource = 6;
        Next.Attack = 5;
        Next.Defense = 1;
        Next.Agility = 18;
        Next.AbilityIds = {TEXT("SliceReview_LynxClaw"),
                           TEXT("SliceReview_LynxPounce")};
        break;
    case ETSTSSSliceEnemyKind::Bristleboar:
        Next.ArchetypeId = TEXT("bristleboarReview");
        Next.DisplayName = TEXT("Bristleboar [provisional]");
        Next.Family = ETSTSSSliceEnemyFamily::Fauna;
        Next.HabitatTag = TEXT("Highlands");
        Next.bLeader = false;
        Next.MaxHP = 40;
        Next.MaxResource = 6;
        Next.Attack = 5;
        Next.Defense = 4;
        Next.Agility = 7;
        Next.AbilityIds = {TEXT("SliceReview_BoarTusk"),
                           TEXT("SliceReview_BoarCharge")};
        break;
    case ETSTSSSliceEnemyKind::NightGlider:
        Next.ArchetypeId = TEXT("nightGliderReview");
        Next.DisplayName = TEXT("Night Glider [provisional]");
        Next.Family = ETSTSSSliceEnemyFamily::Fauna;
        Next.HabitatTag = TEXT("Highlands");
        Next.bLeader = false;
        Next.MaxHP = 17;
        Next.MaxResource = 10;
        Next.Attack = 3;
        Next.Defense = 0;
        Next.Agility = 20;
        Next.AbilityIds = {TEXT("SliceReview_GliderWingCut"),
                           TEXT("SliceReview_GliderDive")};
        break;
    default:
        return false;
    }
    // Intentionally no code path sets Next.bStoryPlacementApproved to true.
    Out = MoveTemp(Next);
    return true;
}

bool FTSTSSSliceEnemyCatalog::TryMakeReviewParticipant(
    ETSTSSSliceEnemyKind Kind, FName InstanceId, FTSS_CombatParticipant& Out)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (InstanceId.IsNone() || IsPartyName(InstanceId) ||
        InstanceId.ToString().Len() > MaxInstanceIdLength)
    {
        return false;
    }
    FTSTSSSliceEnemyDescriptor Definition;
    if (!TryDescribe(Kind, Definition)) return false;

    FTSS_CombatParticipant Next;
    Next.ParticipantId = InstanceId;
    Next.Stats.CharacterId = InstanceId;
    Next.Stats.Health = Definition.MaxHP;
    Next.Stats.MaxHealth = Definition.MaxHP;
    Next.Stats.Resource = Definition.MaxResource;
    Next.Stats.MaxResource = Definition.MaxResource;
    Next.Stats.Attack = Definition.Attack;
    Next.Stats.Defense = Definition.Defense;
    Next.Agility = Definition.Agility;
    Next.bIsPlayerParty = false;
    Next.LearnedSkills = Definition.AbilityIds;
    Out = MoveTemp(Next);
    return true;
#endif
}

UDataTable* FTSTSSSliceEnemyCatalog::MakeReviewSkillTable(
    UObject* Outer, bool bExplicitReviewExecution)
{
#if UE_BUILD_SHIPPING
    return nullptr;
#else
    if (!IsValid(Outer)) return nullptr;
    UDataTable* Table = NewObject<UDataTable>(Outer);
    Table->RowStruct = FTSTSSBattleSkillRow::StaticStruct();
    AddRow(Table, TEXT("SliceReview_GaleForce"), 2, 0, 0,
           TEXT("VFX_ShearGale"), TEXT("ANIM_ShearSweep"), bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_ShearCut"), 3, 2, 1,
           TEXT("VFX_ShearCut"), TEXT("ANIM_ShearLash"), bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_WispSpark"), 1, 0, 0,
           TEXT("VFX_WispSpark"), TEXT("ANIM_WispPulse"), bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_WispSurge"), 3, 3, 2,
           TEXT("VFX_WispSurge"), TEXT("ANIM_WispBurst"), bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_SkitterSnap"), 2, 0, 0,
           TEXT("VFX_SkitterSnap"), TEXT("ANIM_SkitterSnap"), bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_SkitterLunge"), 4, 2, 2,
           TEXT("VFX_SkitterLunge"), TEXT("ANIM_SkitterLunge"), bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_CutpurseSlash"), 2, 0, 0,
           TEXT("VFX_CutpurseSlash"), TEXT("ANIM_CutpurseSlash"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_CutpurseBackstab"), 5, 2, 2,
           TEXT("VFX_CutpurseBackstab"), TEXT("ANIM_CutpurseBackstab"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_SlingerShot"), 2, 0, 0,
           TEXT("VFX_SlingerShot"), TEXT("ANIM_SlingerShot"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_SlingerVolley"), 4, 2, 1,
           TEXT("VFX_SlingerVolley"), TEXT("ANIM_SlingerVolley"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_CaptainStrike"), 4, 0, 0,
           TEXT("VFX_CaptainStrike"), TEXT("ANIM_CaptainStrike"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_CaptainHeavyBlow"), 7, 4, 2,
           TEXT("VFX_CaptainHeavyBlow"), TEXT("ANIM_CaptainHeavyBlow"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_VineLash"), 2, 0, 0,
           TEXT("VFX_VineLash"), TEXT("ANIM_VineLash"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_ThornBurst"), 5, 3, 2,
           TEXT("VFX_ThornBurst"), TEXT("ANIM_ThornBurst"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_SporeTap"), 2, 0, 0,
           TEXT("VFX_SporeTap"), TEXT("ANIM_SporeTap"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_BloomPulse"), 4, 3, 2,
           TEXT("VFX_BloomPulse"), TEXT("ANIM_BloomPulse"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_RootBash"), 3, 0, 0,
           TEXT("VFX_RootBash"), TEXT("ANIM_RootBash"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_BarkCrush"), 6, 4, 2,
           TEXT("VFX_BarkCrush"), TEXT("ANIM_BarkCrush"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_EelTailWhip"), 2, 0, 0,
           TEXT("VFX_EelTailWhip"), TEXT("ANIM_EelTailWhip"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_EelSurgeBite"), 5, 3, 2,
           TEXT("VFX_EelSurgeBite"), TEXT("ANIM_EelSurgeBite"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_FinRake"), 2, 0, 0,
           TEXT("VFX_FinRake"), TEXT("ANIM_FinRake"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_TideLunge"), 5, 3, 2,
           TEXT("VFX_TideLunge"), TEXT("ANIM_TideLunge"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_PincerSnap"), 2, 0, 0,
           TEXT("VFX_PincerSnap"), TEXT("ANIM_PincerSnap"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_ShellSlam"), 5, 3, 2,
           TEXT("VFX_ShellSlam"), TEXT("ANIM_ShellSlam"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_LynxClaw"), 2, 0, 0,
           TEXT("VFX_LynxClaw"), TEXT("ANIM_LynxClaw"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_LynxPounce"), 5, 3, 2,
           TEXT("VFX_LynxPounce"), TEXT("ANIM_LynxPounce"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_BoarTusk"), 2, 0, 0,
           TEXT("VFX_BoarTusk"), TEXT("ANIM_BoarTusk"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_BoarCharge"), 7, 4, 2,
           TEXT("VFX_BoarCharge"), TEXT("ANIM_BoarCharge"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_GliderWingCut"), 2, 0, 0,
           TEXT("VFX_GliderWingCut"), TEXT("ANIM_GliderWingCut"),
           bExplicitReviewExecution);
    AddRow(Table, TEXT("SliceReview_GliderDive"), 5, 3, 2,
           TEXT("VFX_GliderDive"), TEXT("ANIM_GliderDive"),
           bExplicitReviewExecution);
    return Table;
#endif
}
