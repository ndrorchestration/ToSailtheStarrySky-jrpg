#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "TSTSSFirstWakeState.generated.h"

// Ordered story milestones. A debug map may drive these without claiming canonical completion.
UENUM(BlueprintType)
enum class ETSTSSFirstWakeBeat : uint8
{
    FlyerDiscovered,
    IoniaHired,
    BoardedAureateWake,
    EngineeringChecked,
    Launched,
    SeaContact,
    FlotationConfirmed,
    EmptyReserveInspected,
    ReturnedToBerth
};

UENUM(BlueprintType)
enum class ETSTSSInspectionStation : uint8
{
    Lift,
    Pressure,
    Reserve
};

UCLASS(BlueprintType)
class TOSAILTHESTARRYSKY_API UTSTSSFirstWakeState : public UObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="TSTSS|First Wake")
    bool AdvanceTo(ETSTSSFirstWakeBeat RequestedBeat);

    UFUNCTION(BlueprintPure, Category="TSTSS|First Wake")
    ETSTSSFirstWakeBeat GetCurrentBeat() const { return CurrentBeat; }

    UFUNCTION(BlueprintPure, Category="TSTSS|First Wake")
    bool HasStarted() const { return bStarted; }

    // Splashdown is the Prelude/Chapter 1 Act 1 boundary.
    // This is a derived view of the existing version-2 save beat, not a new slot.
    UFUNCTION(BlueprintPure, Category="TSTSS|Story")
    bool IsChapterOneActOne() const
    {
        return bStarted && static_cast<uint8>(CurrentBeat) >=
            static_cast<uint8>(ETSTSSFirstWakeBeat::FlotationConfirmed);
    }

    UFUNCTION(BlueprintPure, Category="TSTSS|Story")
    bool IsPreludeComplete() const { return IsChapterOneActOne(); }

    UFUNCTION(BlueprintCallable, Category="TSTSS|First Wake")
    bool InspectStation(ETSTSSInspectionStation Station);

    UFUNCTION(BlueprintPure, Category="TSTSS|First Wake")
    bool AreInspectionsComplete() const { return InspectionMask == 0x07; }

    UFUNCTION(BlueprintPure, Category="TSTSS|First Wake")
    uint8 GetInspectionMask() const { return InspectionMask; }

    UFUNCTION(BlueprintCallable, Category="TSTSS|First Wake")
    void Reset();

    // Restores only in-range states; avoids replaying milestone side effects.
    UFUNCTION(BlueprintCallable, Category="TSTSS|First Wake")
    bool Restore(bool bWasStarted, ETSTSSFirstWakeBeat SavedBeat, uint8 SavedInspectionMask = 0);

private:
    friend class UTSTSSWaterLandingGate;
    // Only the dedicated physics observation gate can progress these events.
    bool AdvanceWaterBeat(ETSTSSFirstWakeBeat RequestedBeat);

    UPROPERTY(VisibleAnywhere, Category="TSTSS|First Wake")
    ETSTSSFirstWakeBeat CurrentBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|First Wake")
    bool bStarted = false;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|First Wake")
    uint8 InspectionMask = 0;
};
