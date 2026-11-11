#include "Misc/AutomationTest.h"
#include "TSTSSResonatorVfxActor.h"

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSResonatorCueContractTest,
    "TSTSS.Magic.ResonatorCueContract",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSResonatorCueContractTest::RunTest(const FString& Parameters)
{
    struct FPair { FName Spell; FName Visual; };
    const FPair ApprovedReviewPairs[] = {
        {TEXT("Ender_ResonantPulse"), TEXT("VFX.Ender.ResonantPulse")},
        {TEXT("Ender_TuningLance"), TEXT("VFX.Ender.TuningLance")},
        {TEXT("Ender_EchoMend"), TEXT("VFX.Ender.EchoMend")},
        {TEXT("Ender_CorrespondenceThread"), TEXT("VFX.Ender.CorrespondenceThread")},
        {TEXT("Ender_LatticeBreak"), TEXT("VFX.Ender.LatticeBreak")},
        {TEXT("Ender_MindRipple"), TEXT("VFX.Ender.MindRipple")},
        {TEXT("Ender_FocusHarmonic"), TEXT("VFX.Ender.FocusHarmonic")},
        {TEXT("Ender_ConcordanceBurst"), TEXT("VFX.Ender.ConcordanceBurst")},
        {TEXT("Ender_ThoughtChord"), TEXT("VFX.Ender.ThoughtChord")}
    };
    for (const FPair& Pair : ApprovedReviewPairs)
    {
        TestTrue(TEXT("registered review visual"), ATSTSSResonatorVfxActor::IsKnownCue(Pair.Visual));
        FTSTSSBattleSkillCue Accepted;
        Accepted.ActorId = TEXT("Ender");
        Accepted.TargetId = TEXT("Foe");
        Accepted.SkillId = Pair.Spell;
        Accepted.VfxCueId = Pair.Visual;
        TestTrue(TEXT("accepted cue pair"), ATSTSSResonatorVfxActor::IsAcceptedEnderCue(Accepted));
        Accepted.SkillId = TEXT("UnrelatedSpell");
        TestFalse(TEXT("mismatched spell cannot spawn this cue"),
                  ATSTSSResonatorVfxActor::IsAcceptedEnderCue(Accepted));
    }
    FTSTSSBattleSkillCue Invalid;
    Invalid.ActorId = TEXT("Ender");
    Invalid.TargetId = TEXT("Foe");
    Invalid.SkillId = TEXT("Ender_ResonantPulse");
    Invalid.VfxCueId = TEXT("VFX.Unknown");
    TestFalse(TEXT("unregistered visual denied"), ATSTSSResonatorVfxActor::IsKnownCue(Invalid.VfxCueId));
    TestFalse(TEXT("unregistered visual rejected"), ATSTSSResonatorVfxActor::IsAcceptedEnderCue(Invalid));
    Invalid.VfxCueId = TEXT("VFX.Ender.ResonantPulse");
    Invalid.ActorId = TEXT("Ionia");
    TestFalse(TEXT("other caster denied"), ATSTSSResonatorVfxActor::IsAcceptedEnderCue(Invalid));
    Invalid.ActorId = TEXT("Ender");
    Invalid.TargetId = NAME_None;
    TestFalse(TEXT("missing target denied"), ATSTSSResonatorVfxActor::IsAcceptedEnderCue(Invalid));
    return true;
}

#endif
