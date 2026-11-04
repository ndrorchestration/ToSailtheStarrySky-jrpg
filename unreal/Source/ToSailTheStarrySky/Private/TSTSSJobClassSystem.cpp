#include "TSTSSJobClassSystem.h"

bool FTSTSSJobClassSystem::TryReadJobDefinitionsForReview(
    const UDataTable& Table,
    TMap<FName, FTSTSSJobDefinitionRow>& OutDefinitions)
{
    if (Table.GetRowStruct() != FTSTSSJobDefinitionRow::StaticStruct()
        || Table.GetRowMap().IsEmpty())
    {
        return false;
    }

    TMap<FName, FTSTSSJobDefinitionRow> CandidateDefinitions;
    for (const TPair<FName, uint8*>& Entry : Table.GetRowMap())
    {
        const FTSTSSJobDefinitionRow* Row =
            reinterpret_cast<const FTSTSSJobDefinitionRow*>(Entry.Value);
        if (Entry.Key.IsNone()
            || !Row
            || Row->JobId != Entry.Key
            || Row->DisplayName.IsEmpty()
            || CandidateDefinitions.Contains(Row->JobId))
        {
            return false;
        }
        CandidateDefinitions.Add(Row->JobId, *Row);
    }

    OutDefinitions = MoveTemp(CandidateDefinitions);
    return true;
}

bool FTSTSSJobClassSystem::TryBuildJobSelectionPreviewForReview(
    const FTSTSSJobLoadoutState& Current,
    const UDataTable& Table,
    TArray<FTSTSSJobSelectionPreviewRow>& OutRows)
{
    if (!IsProtagonist(Current.CharacterId)
        || Current.NativeProfession != CanonicalNativeProfession(Current.CharacterId)
        || Current.CharacterLevel < 1)
    {
        return false;
    }

    TMap<FName, FTSTSSJobDefinitionRow> Definitions;
    if (!TryReadJobDefinitionsForReview(Table, Definitions))
    {
        return false;
    }

    TArray<FName> Keys;
    Definitions.GetKeys(Keys);
    Keys.Sort([](const FName& Left, const FName& Right)
    {
        return Left.ToString() < Right.ToString();
    });

    TArray<FTSTSSJobSelectionPreviewRow> CandidateRows;
    for (const FName& JobId : Keys)
    {
        const FTSTSSJobDefinitionRow& Definition = Definitions.FindChecked(JobId);
        FTSTSSJobSelectionPreviewRow Choice;
        Choice.JobId = JobId;
        Choice.DisplayName = Definition.DisplayName;
        Choice.bExplicitlyUnlocked = Current.ExplicitlyUnlockedJobs.Contains(JobId);

        FTSTSSJobLoadoutState IgnoredCandidate;
        Choice.bPrimaryReviewSelectable = TrySelectJobs(
            Current, Definitions, JobId, NAME_None, IgnoredCandidate);
        Choice.bSecondaryReviewSelectable = !Current.PrimaryJob.IsNone()
            && TrySelectJobs(Current, Definitions, Current.PrimaryJob,
                JobId, IgnoredCandidate);
        CandidateRows.Add(MoveTemp(Choice));
    }

    OutRows = MoveTemp(CandidateRows);
    return true;
}

bool FTSTSSJobClassSystem::IsProtagonist(FName CharacterId)
{
    return CharacterId == TEXT("Ender")
        || CharacterId == TEXT("Ionia")
        || CharacterId == TEXT("Lyra")
        || CharacterId == TEXT("Reson")
        || CharacterId == TEXT("Aepex");
}

FName FTSTSSJobClassSystem::CanonicalNativeProfession(FName CharacterId)
{
    return CharacterId == TEXT("Ender") ? FName(TEXT("Rift Scholar")) : NAME_None;
}

bool FTSTSSJobClassSystem::TrySelectJobs(
    const FTSTSSJobLoadoutState& Current,
    const TMap<FName, FTSTSSJobDefinitionRow>& JobDefinitions,
    FName RequestedPrimary,
    FName RequestedSecondary,
    FTSTSSJobLoadoutState& OutState)
{
    // Invalid identity, uninitialized progression, or invented native profession
    // cannot be sanitized by a job change.
    if (!IsProtagonist(Current.CharacterId)
        || Current.NativeProfession != CanonicalNativeProfession(Current.CharacterId)
        || Current.CharacterLevel < 1
        || RequestedPrimary.IsNone()
        || RequestedPrimary == RequestedSecondary)
    {
        return false;
    }

    const auto Selectable = [&](FName JobId, bool bSecondary) -> bool
    {
        if (!Current.ExplicitlyUnlockedJobs.Contains(JobId))
        {
            return false;
        }
        const FTSTSSJobDefinitionRow* Definition = JobDefinitions.Find(JobId);
        return Definition
            && Definition->JobId == JobId
            && Definition->ReviewStatus == ETSTSSJobReviewStatus::ReviewSelectable
            && (bSecondary ? Definition->bSecondaryEligible : Definition->bPrimaryEligible);
    };

    if (!Selectable(RequestedPrimary, false)
        || (!RequestedSecondary.IsNone() && !Selectable(RequestedSecondary, true)))
    {
        return false;
    }

    FTSTSSJobLoadoutState Next = Current;
    Next.PrimaryJob = RequestedPrimary;
    Next.SecondaryJob = RequestedSecondary;
    OutState = MoveTemp(Next);
    return true;
}

bool FTSTSSJobClassSystem::IsSkillEligibleForReview(
    const FTSTSSJobLoadoutState& State,
    const FTSTSSJobSkillPolicy& Policy)
{
    if (!IsProtagonist(State.CharacterId)
        || State.NativeProfession != CanonicalNativeProfession(State.CharacterId)
        || State.PrimaryJob.IsNone()
        || Policy.SkillId.IsNone()
        || Policy.TrainedJobId.IsNone()
        || !State.LearnedSkillIds.Contains(Policy.SkillId))
    {
        return false;
    }

    if (State.PrimaryJob == Policy.TrainedJobId)
    {
        return true;
    }

    if (Policy.bAllowSecondaryJob && State.SecondaryJob == Policy.TrainedJobId)
    {
        return true;
    }

    // Two independent opt-ins: policy permits transfer AND this protagonist
    // individually learned/registered the exact skill for off-job use.
    return Policy.bAllowExplicitOffJobTransfer
        && State.ExplicitOffJobTransferSkillIds.Contains(Policy.SkillId);
}
