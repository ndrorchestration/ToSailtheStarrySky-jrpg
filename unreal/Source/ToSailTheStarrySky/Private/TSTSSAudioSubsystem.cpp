#include "TSTSSAudioSubsystem.h"

#include "Components/AudioComponent.h"
#include "Engine/World.h"
#include "HAL/PlatformTime.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"

void UTSTSSAudioSubsystem::Deinitialize()
{
    for (auto& Entry : ActiveLoops)
    {
        if (IsValid(Entry.Value))
        {
            Entry.Value->Stop();
        }
    }
    ActiveLoops.Reset();
    Registered.Reset();
    LastPlayedSeconds.Reset();
    Super::Deinitialize();
}

bool UTSTSSAudioSubsystem::RegisterCue(const FTSTSSAudioCue& Cue)
{
    if (Cue.EventId.IsNone() || !IsValid(Cue.Sound) ||
        !FMath::IsFinite(Cue.Gain) || Cue.Gain < 0.f || Cue.Gain > 1.f ||
        !FMath::IsFinite(Cue.CooldownSeconds) || Cue.CooldownSeconds < 0.f)
    {
        LastReceipt = TEXT("DENIED_BAD_REGISTRATION");
        return false;
    }
    StopCue(Cue.EventId, 0.0f);
    Registered.Add(Cue.EventId, Cue);
    LastPlayedSeconds.Remove(Cue.EventId);
    LastReceipt = FString::Printf(TEXT("REGISTERED:%s"), *Cue.EventId.ToString());
    return true;
}

float UTSTSSAudioSubsystem::GetCategoryVolume(ETSTSSAudioCategory Category) const
{
    const float* Value = CategoryVolumes.Find(Category);
    return Value ? *Value : 1.f;
}

float UTSTSSAudioSubsystem::EffectiveVolume(const FTSTSSAudioCue& Cue) const
{
    if (bMuted) return 0.f;
    return FMath::Clamp(Cue.Gain * GetCategoryVolume(Cue.Category) *
                        GetCategoryVolume(ETSTSSAudioCategory::Master), 0.f, 1.f);
}

void UTSTSSAudioSubsystem::RefreshLoopVolumes()
{
    for (auto& Entry : ActiveLoops)
    {
        const FTSTSSAudioCue* Cue = Registered.Find(Entry.Key);
        if (IsValid(Entry.Value) && Cue)
        {
            Entry.Value->SetVolumeMultiplier(EffectiveVolume(*Cue));
        }
    }
}

void UTSTSSAudioSubsystem::SetCategoryVolume(ETSTSSAudioCategory Category, float Volume)
{
    if (!FMath::IsFinite(Volume)) return;
    CategoryVolumes.Add(Category, FMath::Clamp(Volume, 0.f, 1.f));
    RefreshLoopVolumes();
}

void UTSTSSAudioSubsystem::SetMuted(bool bInMuted)
{
    bMuted = bInMuted;
    RefreshLoopVolumes();
    LastReceipt = bMuted ? TEXT("MUTED") : TEXT("UNMUTED");
}

bool UTSTSSAudioSubsystem::HasCue(FName EventId) const
{
    const FTSTSSAudioCue* Cue = Registered.Find(EventId);
    return Cue != nullptr && IsValid(Cue->Sound);
}

bool UTSTSSAudioSubsystem::EmitCue(FName EventId, FVector Location)
{
    const FTSTSSAudioCue* Cue = Registered.Find(EventId);
    if (!Cue || !IsValid(Cue->Sound) || !GetWorld())
    {
        LastReceipt = FString::Printf(TEXT("SILENT_UNREGISTERED:%s"), *EventId.ToString());
        return false;
    }
    const float Volume = EffectiveVolume(*Cue);
    if (Volume <= 0.f)
    {
        LastReceipt = FString::Printf(TEXT("SILENT_MUTED:%s"), *EventId.ToString());
        return false;
    }
    const TObjectPtr<UAudioComponent>* Existing = ActiveLoops.Find(EventId);
    if (Cue->bLooping && Existing && IsValid(*Existing) && (*Existing)->IsPlaying())
    {
        LastReceipt = FString::Printf(TEXT("ALREADY_PLAYING:%s"), *EventId.ToString());
        return true;
    }
    // If a non-looping or previously stopped sound occupies a loop slot,
    // discard its stale handle. Spawned components auto-destroy on stop/end.
    if (Cue->bLooping && Existing)
    {
        ActiveLoops.Remove(EventId);
    }
    const double Now = FPlatformTime::Seconds();
    if (const double* Last = LastPlayedSeconds.Find(EventId))
    {
        if (Now - *Last < Cue->CooldownSeconds)
        {
            LastReceipt = FString::Printf(TEXT("COOLDOWN:%s"), *EventId.ToString());
            return false;
        }
    }

    if (Cue->bLooping)
    {
        UAudioComponent* Component = Cue->bSpatial
            ? UGameplayStatics::SpawnSoundAtLocation(this, Cue->Sound.Get(), Location,
                                                      FRotator::ZeroRotator, Volume, 1.f, 0.f,
                                                      nullptr, nullptr, true)
            : UGameplayStatics::SpawnSound2D(this, Cue->Sound.Get(), Volume,
                                              1.f, 0.f, nullptr, false, true);
        if (!IsValid(Component))
        {
            LastReceipt = FString::Printf(TEXT("SILENT_SPAWN_FAILURE:%s"), *EventId.ToString());
            return false;
        }
        ActiveLoops.Add(EventId, Component);
    }
    else if (Cue->bSpatial)
    {
        UGameplayStatics::PlaySoundAtLocation(this, Cue->Sound.Get(), Location, Volume);
    }
    else
    {
        UGameplayStatics::PlaySound2D(this, Cue->Sound.Get(), Volume);
    }
    LastPlayedSeconds.Add(EventId, Now);
    LastReceipt = FString::Printf(TEXT("PLAY_REQUESTED:%s"), *EventId.ToString());
    return true;
}

bool UTSTSSAudioSubsystem::StopCue(FName EventId, float FadeOutSeconds)
{
    TObjectPtr<UAudioComponent>* Component = ActiveLoops.Find(EventId);
    if (!Component || !IsValid(*Component)) return false;
    if (FMath::IsFinite(FadeOutSeconds) && FadeOutSeconds > 0.f)
        (*Component)->FadeOut(FMath::Clamp(FadeOutSeconds, 0.f, 10.f), 0.f);
    else
        (*Component)->Stop();
    ActiveLoops.Remove(EventId);
    LastReceipt = FString::Printf(TEXT("STOP_REQUESTED:%s"), *EventId.ToString());
    return true;
}
