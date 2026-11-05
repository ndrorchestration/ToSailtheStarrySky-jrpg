#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "TSTSSCombatRules.generated.h"

// Pure, transactional combat calculations. No world mutation or animation coupling.
USTRUCT(BlueprintType)
struct FTSTSSCombatant
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName CharacterId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 Health = 1;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 MaxHealth = 1;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 Resource = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 MaxResource = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 Attack = 1;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 Defense = 0;
};

USTRUCT(BlueprintType)
struct FTSTSSCombatAction
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName ActorId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName TargetId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 ResourceCost = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 Power = 0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bHealing = false;
};

UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSCombatRules : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // Returns false without modifying OutRoster on invalid/unauthorized actions.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Combat")
    static bool TryApplyAction(const TArray<FTSTSSCombatant>& Roster,
                               const FTSTSSCombatAction& Action,
                               TArray<FTSTSSCombatant>& OutRoster);
};
