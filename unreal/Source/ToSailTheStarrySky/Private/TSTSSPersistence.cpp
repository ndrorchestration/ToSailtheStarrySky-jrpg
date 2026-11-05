#include "TSTSSPersistence.h"
#include "Kismet/GameplayStatics.h"

bool UTSTSSPersistence::IsValidSlotName(const FString& Slot)
{
    if (Slot.IsEmpty() || Slot.Len() > 48)
    {
        return false;
    }
    for (TCHAR Character : Slot)
    {
        if (!((Character >= TEXT('a') && Character <= TEXT('z')) ||
              (Character >= TEXT('A') && Character <= TEXT('Z')) ||
              (Character >= TEXT('0') && Character <= TEXT('9')) ||
              Character == TEXT('_') || Character == TEXT('-')))
        {
            return false;
        }
    }
    return true;
}

bool UTSTSSPersistence::SaveProgress(const FString& Slot, const UTSTSSSaveGame* Progress)
{
    if (!IsValidSlotName(Slot) || !IsValid(Progress) || !Progress->IsStructurallyValid())
    {
        return false;
    }
    return UGameplayStatics::SaveGameToSlot(const_cast<UTSTSSSaveGame*>(Progress), Slot, 0);
}

UTSTSSSaveGame* UTSTSSPersistence::LoadProgress(const FString& Slot)
{
    if (!IsValidSlotName(Slot))
    {
        return nullptr;
    }
    USaveGame* Loaded = UGameplayStatics::LoadGameFromSlot(Slot, 0);
    UTSTSSSaveGame* Progress = Cast<UTSTSSSaveGame>(Loaded);
    return IsValid(Progress) && Progress->IsStructurallyValid() ? Progress : nullptr;
}
