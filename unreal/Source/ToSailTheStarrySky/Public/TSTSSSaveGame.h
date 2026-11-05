#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "TSTSSCombatRules.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSSaveGame.generated.h"

// Versioned save payload; do not silently load unknown future versions.
UCLASS(BlueprintType)
class TOSAILTHESTARRYSKY_API UTSTSSSaveGame : public USaveGame
{
    GENERATED_BODY()
public:
    static constexpr int32 CurrentVersion = 2;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, SaveGame, Category="TSTSS|Save")
    int32 SchemaVersion = CurrentVersion;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category="TSTSS|Save")
    bool bFirstWakeStarted = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category="TSTSS|Save")
    ETSTSSFirstWakeBeat FirstWakeBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category="TSTSS|Save")
    TArray<FTSTSSCombatant> PartyRoster;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category="TSTSS|Save")
    uint8 InspectionMask = 0;

    UFUNCTION(BlueprintPure, Category="TSTSS|Save")
    bool IsSupportedVersion() const { return SchemaVersion == CurrentVersion; }

    UFUNCTION(BlueprintPure, Category="TSTSS|Save")
    bool IsStructurallyValid() const;
};
