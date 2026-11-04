#include "Misc/AutomationTest.h"
#include "TSTSSJobClassSystem.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSHybridCharacterJobContractTest,
    "TSTSS.Design.HybridCharacterJobs",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSHybridCharacterJobContractTest::RunTest(const FString& Parameters)
{
    TestTrue(TEXT("five known identities accepted"),
        FTSTSSJobClassSystem::IsProtagonist(TEXT("Aepex")));
    TestFalse(TEXT("invented identity rejected"),
        FTSTSSJobClassSystem::IsProtagonist(TEXT("TestSixth")));
    TestEqual(TEXT("Ender native profession remains Rift Scholar"),
        FTSTSSJobClassSystem::CanonicalNativeProfession(TEXT("Ender")),
        FName(TEXT("Rift Scholar")));
    TestTrue(TEXT("Ionia job remains unnamed"),
        FTSTSSJobClassSystem::CanonicalNativeProfession(TEXT("Ionia")).IsNone());

    FTSTSSJobDefinitionRow Scholar;
    Scholar.JobId = TEXT("ReviewScholar");
    Scholar.ReviewStatus = ETSTSSJobReviewStatus::ReviewSelectable;
    Scholar.bSecondaryEligible = true;

    FTSTSSJobDefinitionRow Guard;
    Guard.JobId = TEXT("ReviewGuard");
    Guard.ReviewStatus = ETSTSSJobReviewStatus::ReviewSelectable;
    Guard.bSecondaryEligible = true;

    FTSTSSJobDefinitionRow Unadmitted;
    Unadmitted.JobId = TEXT("ReviewSeer"); // Explicitly NOT a canonical class.
    TMap<FName, FTSTSSJobDefinitionRow> Jobs;
    Jobs.Add(Scholar.JobId, Scholar);
    Jobs.Add(Guard.JobId, Guard);
    Jobs.Add(Unadmitted.JobId, Unadmitted);

    FTSTSSJobLoadoutState Ender;
    Ender.CharacterId = TEXT("Ender");
    Ender.NativeProfession = TEXT("Rift Scholar");
    Ender.PrimaryJob = TEXT("ReviewScholar");
    Ender.CharacterLevel = 9;
    Ender.JobProficiencyById.Add(TEXT("ReviewScholar"), 3);
    Ender.SchoolMasteryById.Add(TEXT("Lumen"), 2);
    Ender.WeaponMasteryById.Add(TEXT("Staff"), 4);
    Ender.RelationshipProgressByCharacter.Add(TEXT("Ionia"), 7);
    Ender.LearnedSkillIds.Add(TEXT("ReviewSigil"));

    FTSTSSJobLoadoutState Output;
    Output.CharacterId = TEXT("Sentinel");
    TestFalse(TEXT("job catalog presence never unlocks a job"),
        FTSTSSJobClassSystem::TrySelectJobs(
            Ender, Jobs, TEXT("ReviewGuard"), NAME_None, Output));
    TestEqual(TEXT("failed selection preserves output"),
        Output.CharacterId, FName(TEXT("Sentinel")));
    Ender.ExplicitlyUnlockedJobs.Add(TEXT("ReviewScholar"));
    Ender.ExplicitlyUnlockedJobs.Add(TEXT("ReviewGuard"));
    Ender.ExplicitlyUnlockedJobs.Add(TEXT("ReviewSeer"));

    TestFalse(TEXT("design-only job not selectable even if unlocked"),
        FTSTSSJobClassSystem::TrySelectJobs(
            Ender, Jobs, TEXT("ReviewSeer"), NAME_None, Output));
    TestFalse(TEXT("duplicate primary-secondary selection denied"),
        FTSTSSJobClassSystem::TrySelectJobs(
            Ender, Jobs, TEXT("ReviewGuard"), TEXT("ReviewGuard"), Output));
    TestFalse(TEXT("unknown job denied"),
        FTSTSSJobClassSystem::TrySelectJobs(
            Ender, Jobs, TEXT("Unknown"), NAME_None, Output));

    Guard.bSecondaryEligible = false;
    Jobs.Add(Guard.JobId, Guard);
    TestFalse(TEXT("secondary slot requires explicit eligibility"),
        FTSTSSJobClassSystem::TrySelectJobs(
            Ender, Jobs, TEXT("ReviewScholar"), TEXT("ReviewGuard"), Output));
    Guard.bSecondaryEligible = true;
    Jobs.Add(Guard.JobId, Guard);

    if (!TestTrue(TEXT("explicitly unlocked review dual-job loadout selected"),
        FTSTSSJobClassSystem::TrySelectJobs(
            Ender, Jobs, TEXT("ReviewGuard"), TEXT("ReviewScholar"), Output)))
    {
        return false;
    }

    TestEqual(TEXT("native identity immutable"),
        Output.NativeProfession, FName(TEXT("Rift Scholar")));
    TestEqual(TEXT("character level unchanged"), Output.CharacterLevel, 9);
    TestEqual(TEXT("job proficiency preserved"),
        Output.JobProficiencyById.FindRef(TEXT("ReviewScholar")), 3);
    TestEqual(TEXT("magic mastery preserved"),
        Output.SchoolMasteryById.FindRef(TEXT("Lumen")), 2);
    TestEqual(TEXT("weapon mastery preserved"),
        Output.WeaponMasteryById.FindRef(TEXT("Staff")), 4);
    TestEqual(TEXT("relationships preserved"),
        Output.RelationshipProgressByCharacter.FindRef(TEXT("Ionia")), 7);
    TestTrue(TEXT("learned skill preserved"), Output.LearnedSkillIds.Contains(TEXT("ReviewSigil")));
    TestFalse(TEXT("loadout did not teach unrelated skill"),
        Output.LearnedSkillIds.Contains(TEXT("ReviewSpell")));
    TestTrue(TEXT("input untouched"), Ender.SecondaryJob.IsNone());

    FTSTSSJobSkillPolicy Skill;
    Skill.SkillId = TEXT("ReviewSigil");
    Skill.TrainedJobId = TEXT("ReviewScholar");
    TestFalse(TEXT("secondary job grants no implicit skill access"),
        FTSTSSJobClassSystem::IsSkillEligibleForReview(Output, Skill));
    Skill.bAllowSecondaryJob = true;
    TestTrue(TEXT("explicit secondary permission and learned skill admit preview"),
        FTSTSSJobClassSystem::IsSkillEligibleForReview(Output, Skill));
    Skill.SkillId = TEXT("ReviewSpell");
    TestFalse(TEXT("permission never teaches an unlearned skill"),
        FTSTSSJobClassSystem::IsSkillEligibleForReview(Output, Skill));

    Skill.SkillId = TEXT("ReviewSigil");
    Skill.TrainedJobId = TEXT("OtherJob");
    Skill.bAllowSecondaryJob = false;
    Skill.bAllowExplicitOffJobTransfer = true;
    TestFalse(TEXT("off-job transfer requires individual opt-in"),
        FTSTSSJobClassSystem::IsSkillEligibleForReview(Output, Skill));
    Output.ExplicitOffJobTransferSkillIds.Add(Skill.SkillId);
    TestTrue(TEXT("explicit learned transfer can pass preview gate"),
        FTSTSSJobClassSystem::IsSkillEligibleForReview(Output, Skill));
    Skill.bAllowExplicitOffJobTransfer = false;
    TestFalse(TEXT("skill policy can revoke transfer eligibility"),
        FTSTSSJobClassSystem::IsSkillEligibleForReview(Output, Skill));

    Ender.NativeProfession = TEXT("InventedClass");
    FTSTSSJobLoadoutState Rejected;
    Rejected.CharacterId = TEXT("Sentinel");
    TestFalse(TEXT("native profession cannot be rewritten by changing job"),
        FTSTSSJobClassSystem::TrySelectJobs(
            Ender, Jobs, TEXT("ReviewGuard"), NAME_None, Rejected));
    TestEqual(TEXT("identity rejection atomic"), Rejected.CharacterId,
        FName(TEXT("Sentinel")));
    return true;
}
#endif
