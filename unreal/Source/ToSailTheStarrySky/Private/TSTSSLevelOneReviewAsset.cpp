#include "TSTSSLevelOneReviewAsset.h"
#include "TSTSSLevelOneStatRanking.h"

bool UTSTSSLevelOneReviewAsset::IsConsistentForReview() const
{
    if (!bEnableLocalReview || Entries.Num() != 5)
    {
        return false;
    }

    TArray<FTSTSSLevelOneRankCandidate> Candidates;
    Candidates.Reserve(Entries.Num());
    for (const FTSTSSLevelOneDraftStats& Entry : Entries)
    {
        FTSTSSLevelOneRankCandidate Candidate;
        Candidate.CharacterId = Entry.CharacterId;
        Candidate.Level = Entry.Level;
        Candidate.MaxHealth = Entry.MaxHealth;
        Candidate.MaxMagicPoints = Entry.ProposedMaxMP;
        Candidate.MagicPower = Entry.ProposedMAG;
        Candidates.Add(Candidate);
    }
    return FTSTSSLevelOneRankContract::Validate(Candidates);
}
