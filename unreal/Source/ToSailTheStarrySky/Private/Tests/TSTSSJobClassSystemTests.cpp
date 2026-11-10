#include "Misc/AutomationTest.h"
#include "TSTSSJobClassSystem.h"
#include "TSTSSCrewWorkshopReview.h"

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

    // Creator requirements: ALL five can equip allowed primary/secondary jobs.
    // Role/affinity descriptors are never a fixed class admission restriction.
    const FName CharacterIds[] = {
        TEXT("Ender"), TEXT("Ionia"), TEXT("Lyra"), TEXT("Reson"), TEXT("Aepex")
    };
    const FName Affinities[] = {
        TEXT("Spirit"), TEXT("Earth"), TEXT("Water"), TEXT("Fire"), TEXT("Air")
    };
    for (int32 Index = 0; Index < 5; ++Index)
    {
        FTSTSSCrewRoleProfile Profile;
        TestTrue(TEXT("known protagonist has stable role profile"),
            FTSTSSCrewWorkshopReview::TryGetRoleProfile(CharacterIds[Index], Profile));
        TestEqual(TEXT("story affinity preserved"), Profile.FiveLightAffinity,
            Affinities[Index]);
        TestTrue(TEXT("every protagonist is job-flexible"), Profile.bCanEquipUnlockedJobs);

        FTSTSSJobLoadoutState Character;
        Character.CharacterId = CharacterIds[Index];
        Character.NativeProfession =
            FTSTSSJobClassSystem::CanonicalNativeProfession(CharacterIds[Index]);
        Character.ExplicitlyUnlockedJobs.Add(TEXT("ReviewScholar"));
        Character.ExplicitlyUnlockedJobs.Add(TEXT("ReviewGuard"));
        FTSTSSJobLoadoutState Selected;
        TestTrue(TEXT("all five may choose admitted primary plus secondary jobs"),
            FTSTSSJobClassSystem::TrySelectJobs(
                Character, Jobs, TEXT("ReviewGuard"), TEXT("ReviewScholar"), Selected));
        TestEqual(TEXT("primary class is chosen, not fixed to narrative role"),
            Selected.PrimaryJob, FName(TEXT("ReviewGuard")));
        TestEqual(TEXT("native identity unaffected by selection"),
            Selected.NativeProfession, Character.NativeProfession);
    }

    FTSTSSCrewRoleProfile UnknownProfile;
    UnknownProfile.CharacterId = TEXT("PreserveSentinel");
    TestFalse(TEXT("unknown character profile rejected"),
        FTSTSSCrewWorkshopReview::TryGetRoleProfile(TEXT("Unknown"), UnknownProfile));
    TestEqual(TEXT("unknown character rejection leaves output unchanged"),
        UnknownProfile.CharacterId, FName(TEXT("PreserveSentinel")));

    FTSTSSCrewRoleProfile LyraProfile;
    FTSTSSCrewWorkshopReview::TryGetRoleProfile(TEXT("Lyra"), LyraProfile);
    TestTrue(TEXT("Lyra naturally heals but is not class-locked"),
        LyraProfile.bDefaultHealer && LyraProfile.bCanEquipUnlockedJobs);
    FTSTSSCrewRoleProfile ResonProfile;
    FTSTSSCrewWorkshopReview::TryGetRoleProfile(TEXT("Reson"), ResonProfile);
    TestTrue(TEXT("Reson armsmaster and ace pilot are persistent aptitudes"),
        ResonProfile.bArmsmaster && ResonProfile.bAcePilot);
    FTSTSSCrewRoleProfile AepexProfile;
    FTSTSSCrewWorkshopReview::TryGetRoleProfile(TEXT("Aepex"), AepexProfile);
    TestTrue(TEXT("Aepex can build upgrades independent of battle class"),
        AepexProfile.bWorkshopBuilder && AepexProfile.bCanEquipUnlockedJobs);
    FTSTSSCrewRoleProfile IoniaProfile;
    FTSTSSCrewWorkshopReview::TryGetRoleProfile(TEXT("Ionia"), IoniaProfile);
    TestTrue(TEXT("Ionia retains captain authority"), IoniaProfile.bCaptain);

    FTSTSSCrewWorkshopReviewState Crew;
    Crew.RecruitedCharacters.Add(TEXT("Ender"));
    Crew.RecruitedCharacters.Add(TEXT("Ionia"));
    Crew.bAtSafeWorkshop = true;
    Crew.ReviewMaterials.Add(TEXT("ReviewAlloy"), 4);
    Crew.ExplicitlyUnlockedUpgradeIds.Add(TEXT("ReviewStabilizer"));
    FTSTSSWorkshopUpgradeReview ReviewUpgrade;
    ReviewUpgrade.UpgradeId = TEXT("ReviewStabilizer");
    ReviewUpgrade.Target = ETSTSSWorkshopTarget::Vessel;
    ReviewUpgrade.TargetId = TEXT("AureateWake");
    ReviewUpgrade.MaterialId = TEXT("ReviewAlloy");
    ReviewUpgrade.MaterialCost = 3;
    ReviewUpgrade.bReviewSelectable = true;
    ReviewUpgrade.bRequiresEnderObservation = true;
    ReviewUpgrade.RequiredObservationId = TEXT("ReviewPhaseAnomaly");

    FTSTSSCrewWorkshopReviewState Sentinel;
    Sentinel.ReviewMaterials.Add(TEXT("Sentinel"), 99);
    TestFalse(TEXT("Aepex cannot install before joining"),
        FTSTSSCrewWorkshopReview::TryInstallReviewUpgrade(Crew, ReviewUpgrade, Sentinel));
    TestEqual(TEXT("denial preserves caller destination"),
        Sentinel.ReviewMaterials.FindRef(TEXT("Sentinel")), 99);
    Crew.RecruitedCharacters.Add(TEXT("Aepex"));
    Crew.bCaptainAuthorizedVesselWork = true;
    TestFalse(TEXT("harmonic upgrade requires observed clue"),
        FTSTSSCrewWorkshopReview::TryInstallReviewUpgrade(Crew, ReviewUpgrade, Sentinel));
    TestFalse(TEXT("unobserved diagnostic cannot be recorded"),
        FTSTSSCrewWorkshopReview::TryRecordEngineObservation(
            Crew, TEXT("ReviewPhaseAnomaly"), false, Sentinel));
    TestTrue(TEXT("Ender records direct clue without claiming its meaning"),
        FTSTSSCrewWorkshopReview::TryRecordEngineObservation(
            Crew, TEXT("ReviewPhaseAnomaly"), true, Sentinel));
    TestFalse(TEXT("recorded clue does not auto-install upgrade"),
        Sentinel.InstalledReviewUpgradeIds.Contains(TEXT("ReviewStabilizer")));
    TestFalse(TEXT("missing captain approval denies vessel work"),
        [&]()
        {
            FTSTSSCrewWorkshopReviewState Blocked = Sentinel;
            Blocked.bCaptainAuthorizedVesselWork = false;
            return FTSTSSCrewWorkshopReview::TryInstallReviewUpgrade(
                Blocked, ReviewUpgrade, Crew);
        }());

    FTSTSSCrewWorkshopReviewState Installed;
    TestTrue(TEXT("Aepex + Ender clue + Ionia authority permits review installation"),
        FTSTSSCrewWorkshopReview::TryInstallReviewUpgrade(
            Sentinel, ReviewUpgrade, Installed));
    TestEqual(TEXT("material deduction is transactional"),
        Installed.ReviewMaterials.FindRef(TEXT("ReviewAlloy")), 1);
    TestTrue(TEXT("installed review receipt recorded"),
        Installed.InstalledReviewUpgradeIds.Contains(TEXT("ReviewStabilizer")));
    TestEqual(TEXT("original inventory is untouched"),
        Sentinel.ReviewMaterials.FindRef(TEXT("ReviewAlloy")), 4);
    TestFalse(TEXT("duplicate upgrade rejected"),
        FTSTSSCrewWorkshopReview::TryInstallReviewUpgrade(
            Installed, ReviewUpgrade, Crew));

    FTSTSSWorkshopUpgradeReview GearUpgrade = ReviewUpgrade;
    GearUpgrade.UpgradeId = TEXT("ReviewGear");
    GearUpgrade.Target = ETSTSSWorkshopTarget::Equipment;
    GearUpgrade.TargetId = TEXT("ReviewBoots");
    GearUpgrade.MaterialCost = 1;
    GearUpgrade.bRequiresEnderObservation = false;
    GearUpgrade.RequiredObservationId = NAME_None;
    Installed.ExplicitlyUnlockedUpgradeIds.Add(GearUpgrade.UpgradeId);
    TestTrue(TEXT("Aepex can independently install ordinary gear upgrades"),
        FTSTSSCrewWorkshopReview::TryInstallReviewUpgrade(
            Installed, GearUpgrade, Crew));
    TestEqual(TEXT("ordinary gear spends its reviewed material"),
        Crew.ReviewMaterials.FindRef(TEXT("ReviewAlloy")), 0);
    GearUpgrade.Target = static_cast<ETSTSSWorkshopTarget>(255);
    TestFalse(TEXT("invalid workshop target fails closed"),
        FTSTSSCrewWorkshopReview::TryInstallReviewUpgrade(
            Installed, GearUpgrade, Crew));

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
