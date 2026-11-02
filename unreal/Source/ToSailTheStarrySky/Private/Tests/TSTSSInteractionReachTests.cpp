#include "Misc/AutomationTest.h"
#include "TSTSSInteractionReach.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSCameraInteractionReachTest,
    "TSTSS.FirstWake.InteractionCameraBoomReach",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSCameraInteractionReachTest::RunTest(const FString& Parameters)
{
    // Actual default spring arm is 360 cm; pawn interaction setting is 300.
    // Pure camera-origin 300 cm trace would end 60 cm behind the pawn.
    const FVector Pawn(0.f, 0.f, 130.f);
    const FVector Camera(-360.f, 0.f, 130.f);
    const FVector Target(190.f, 0.f, 130.f);
    const float Reach = 300.f;
    const float FromCamera = TSTSSInteractionReach::GetCameraTraceLength(
        Camera, Pawn, Reach);
    TestEqual(TEXT("Camera offset included in ray length"),
              FromCamera, 660.f);
    TestTrue(TEXT("Reachable marker lies within extended camera ray"),
        FVector::Dist(Camera, Target) <= FromCamera);
    TestTrue(TEXT("Reachable marker remains inside pawn-based reach"),
        TSTSSInteractionReach::IsInsidePlayerReach(Pawn, Target, Reach));
    TestFalse(TEXT("Past 300 cm cannot be interacted with"),
        TSTSSInteractionReach::IsInsidePlayerReach(
            Pawn, FVector(301.f, 0.f, 130.f), Reach));
    TestTrue(TEXT("Exactly 300 cm is still allowed"),
        TSTSSInteractionReach::IsInsidePlayerReach(
            Pawn, FVector(300.f, 0.f, 130.f), Reach));
    TestEqual(TEXT("No boom offset means normal player range"),
        TSTSSInteractionReach::GetCameraTraceLength(Pawn, Pawn, Reach),
        Reach);
    TestEqual(TEXT("Zero reach rejects tracing"),
        TSTSSInteractionReach::GetCameraTraceLength(Camera, Pawn, 0.f),
        0.f);
    TestFalse(TEXT("Negative player reach rejected"),
        TSTSSInteractionReach::IsInsidePlayerReach(Pawn, Pawn, -1.f));
    const float Invalid = std::numeric_limits<float>::quiet_NaN();
    TestEqual(TEXT("Nonfinite reach rejects camera trace"),
        TSTSSInteractionReach::GetCameraTraceLength(Camera, Pawn, Invalid),
        0.f);
    TestFalse(TEXT("Nonfinite impact rejected"),
        TSTSSInteractionReach::IsInsidePlayerReach(
            Pawn, FVector(Invalid, 0.f, 130.f), Reach));
    TestEqual(TEXT("Nonfinite camera location rejected"),
        TSTSSInteractionReach::GetCameraTraceLength(
            FVector(Invalid, 0.f, 130.f), Pawn, Reach), 0.f);
    return true;
}
#endif
