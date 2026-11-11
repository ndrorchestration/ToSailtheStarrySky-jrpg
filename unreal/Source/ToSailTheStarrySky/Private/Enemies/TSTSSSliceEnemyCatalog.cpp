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
        Next.DisplayName = TEXT("Dock Skitter [provisional]");
        Next.MaxHP = 20;
        Next.MaxResource = 4;
        Next.Attack = 3;
        Next.Defense = 2;
        Next.Agility = 8;
        Next.AbilityIds = {TEXT("SliceReview_SkitterSnap"),
                           TEXT("SliceReview_SkitterLunge")};
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
    return Table;
#endif
}
