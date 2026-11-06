#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSReviewContinueManifest.generated.h"

class UTSTSSSaveGame;

// A separate versioned, preview-only binding for the *existing* v2
// First Wake save. Never silently adopt older PIE SaveGames or expand
// the production SaveGame schema with temporary review coordinates.
UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSReviewContinueManifest : public USaveGame
{
    GENERATED_BODY()
public:
    static constexpr int32 CurrentReviewVersion = 1;

    UPROPERTY(SaveGame)
    int32 ReviewVersion = CurrentReviewVersion;
    UPROPERTY(SaveGame)
    FString ReviewProtocol = TEXT("TSTSS_FIRST_WAKE_PIE_CONTINUE_V1");
    UPROPERTY(SaveGame)
    FString PrimarySlot;
    UPROPERTY(SaveGame)
    FString ProjectRoot;
    UPROPERTY(SaveGame)
    FString ReviewMapPackage;
    UPROPERTY(SaveGame)
    FString PrimaryBlake3_160;
    UPROPERTY(SaveGame)
    int32 PrimarySchemaVersion = 2;
    UPROPERTY(SaveGame)
    bool bSavedStoryStarted = false;
    UPROPERTY(SaveGame)
    ETSTSSFirstWakeBeat SavedBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    UPROPERTY(SaveGame)
    uint8 SavedInspectionMask = 0;
    UPROPERTY(SaveGame)
    FVector SavedPawnLocation = FVector::ZeroVector;
    UPROPERTY(SaveGame)
    FRotator SavedPawnRotation = FRotator::ZeroRotator;
    UPROPERTY(SaveGame)
    FRotator SavedControlRotation = FRotator::ZeroRotator;

    // This check is intentionally independent of the actor and never loads
    // any slot, teleports anyone, or advances story. Untrusted sidecar data.
    bool IsBoundFor(const UTSTSSSaveGame* Primary, const FString& ExpectedSlot,
        const FString& ExpectedProjectRoot, const FString& ExpectedMapPackage,
        const FString& ActualPrimaryBlake3_160) const;
};
