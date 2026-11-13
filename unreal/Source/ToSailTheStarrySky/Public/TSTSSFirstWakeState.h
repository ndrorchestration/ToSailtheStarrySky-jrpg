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

    // Read-only, provisional objective cue for Unreal Prelude playtests.
    // Does not advance the story, grant abilities, or mutate save state.
    UFUNCTION(BlueprintPure, Category="TSTSS|First Wake|Review")
    FString GetReviewObjectiveText() const;

    // Splashdown is the Prelude/Chapter 1 Act 1 boundary.
    // This is a derived view of the existing version-2 save beat, not a new slot.
    UFUNCTION(BlueprintPure, Category="TSTSS|Story")
    bool IsChapterOneActOne() const
    {
        return bStarted && static_cast<uint8>(CurrentBeat) >=
            static_cast<uint8>(ETSTSSFirstWakeBeat::FlotationConfirmed);
    }

    // Review-only, fail-closed ship-mode authorization derived from the saved
    // story beat. This is NOT an unlock API and does not alter save format.
    // A future recovery-state authority must explicitly authorize flight.
    UFUNCTION(BlueprintPure, Category="TSTSS|Ship|Review")
    bool IsSeabourneRecoveryLocked() const { return IsChapterOneActOne(); }

    // Derived from the saved story beat: no separate mode save can drift
    // across reload or travel. Review only; not a ship mesh switch.
    UFUNCTION(BlueprintPure, Category="TSTSS|Ship|Review")
    FName GetReviewShipMode() const
    {
        if (!bStarted) return NAME_None;
        return IsSeabourneRecoveryLocked()
            ? FName(TEXT("Seabourne")) : FName(TEXT("Skybourne"));
    }

    UFUNCTION(BlueprintPure, Category="TSTSS|Ship|Review")
    bool IsReviewShipModeAuthorized(FName RequestedMode) const
    {
        const FName Active = GetReviewShipMode();
        return !Active.IsNone() && RequestedMode == Active;
    }
    UFUNCTION(BlueprintPure, Category="TSTSS|Story")
    bool IsPreludeComplete() const { return IsChapterOneActOne(); }

    UFUNCTION(BlueprintCallable, Category="TSTSS|First Wake")
    bool InspectStation(ETSTSSInspectionStation Station);

    UFUNCTION(BlueprintPure, Category="TSTSS|First Wake")
    bool AreInspectionsComplete() const { return InspectionMask == 0x07; }

    UFUNCTION(BlueprintPure, Category="TSTSS|First Wake")
    uint8 GetInspectionMask() const { return InspectionMask; }

    // Runtime-only timeline generation for cache invalidation after both
    // Restore() and full Reset(). It is not part of the saved game schema.
    uint64 GetRestoreGeneration() const { return RestoreGeneration; }

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

    UPROPERTY(Transient)
    uint64 RestoreGeneration = 0;
};
