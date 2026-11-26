#pragma once
#include "CoreMinimal.h"

// Public-safe authored opening review. Cue starts use the same sequence clock.
// The end of the internal monologue is creator-specified; all other lines
// remain draft performance copy. No quest, roster, or save authority.
namespace TSTSSFirstWakeOpening
{
struct FCue
{
    float Start;
    const TCHAR* Shot;
    const TCHAR* Copy;
    bool bSpoken;
};
inline constexpr float Duration = 86.f;
inline constexpr FCue Cues[] = {
    {0.f, TEXT("Stars / first harmonic"), TEXT(""), false},
    {3.f, TEXT("Stars"), TEXT("The universe is a rather curious thing."), false},
    {7.f, TEXT("Planetary horizon"), TEXT("It spends billions of years arranging matter into increasingly complicated patterns, only for some of those patterns to begin wondering why they exist at all."), false},
    {19.f, TEXT("Sunlight"), TEXT("A particularly ambitious arrangement, if you ask me."), false},
    {23.f, TEXT("Coastal descent"), TEXT("Here, on our little world, we've discovered how to persuade the wind, negotiate with gravity, and coax remarkably useful things from the invisible."), false},
    {34.f, TEXT("Hilltonia / volcanic uplands"), TEXT("Naturally, the more we understand, the more we discover how little we actually know. Personally, I find that rather exciting."), false},
    {45.f, TEXT("Greenwood canopy"), TEXT("I suppose finding one's place in the universe is a different sort of problem altogether. There doesn't seem to be an equation for that one."), false},
    {55.f, TEXT("Greenwood trail"), TEXT("But perhaps you don't need to have everything figured out before you begin."), false},
    {61.f, TEXT("Ender / staff"), TEXT("Sometimes, all that's required is a road, a little curiosity, and believing in yourself... even if you're the only one that does."), false},
    {71.f, TEXT("Ender / discordant staff"), TEXT("Well, that's certainly not the frequency I was looking for."), true},
    {77.f, TEXT("Ender / harmonic response"), TEXT("Ah! There you are. At least one of us knows what we're doing."), true},
    {83.f, TEXT("Third-person handoff"), TEXT("PRELUDE — First Wake\nThe Greenwood — Discover Hilltonia"), false},
};
inline int32 CueAt(float Seconds)
{
    int32 Result = 0;
    for (int32 Index = 1; Index < UE_ARRAY_COUNT(Cues); ++Index)
    {
        if (Seconds < Cues[Index].Start) break;
        Result = Index;
    }
    return Result;
}
}
