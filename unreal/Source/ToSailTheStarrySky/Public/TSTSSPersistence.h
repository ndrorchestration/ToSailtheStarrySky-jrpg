#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "TSTSSSaveGame.h"
#include "TSTSSPersistence.generated.h"

// Initial local-save service, exposed to Blueprints. Does not migrate Godot save files.
UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSPersistence : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="TSTSS|Save")
    static bool SaveProgress(const FString& Slot, const UTSTSSSaveGame* Progress);

    // Returns null for absent, corrupt, or unsupported saves.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Save")
    static UTSTSSSaveGame* LoadProgress(const FString& Slot);

    UFUNCTION(BlueprintPure, Category="TSTSS|Save")
    static bool IsValidSlotName(const FString& Slot);
};
