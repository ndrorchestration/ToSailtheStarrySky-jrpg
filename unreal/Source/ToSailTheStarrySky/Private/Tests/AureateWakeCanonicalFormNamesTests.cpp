// Runtime/reflection acceptance test for creator-approved displayed ship form names.
// Runs only inside a native Unreal Editor build. This is NOT an authorization gate.
#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "AureateWakePreviewActor.h"
#include "UObject/UnrealType.h"
#include "UObject/UObjectGlobals.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAureateWakeCanonicalFormNames,
    "TSTSS.AureateWake.Canon.FormDisplayNames",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FAureateWakeCanonicalFormNames::RunTest(const FString& Parameters)
{
    const UEnum* Forms = StaticEnum<EAureateWakeForm>();
    if (!TestNotNull(TEXT("Reflected Aureate Wake form enum"), Forms))
    {
        return false;
    }

    struct FFormCase
    {
        EAureateWakeForm Form;
        const TCHAR* InternalName;
        const TCHAR* DisplayName;
    };

    // The stable native values are intentional legacy IDs for existing assets.
    const FFormCase Cases[] = {
        { EAureateWakeForm::Skyborne, TEXT("Skyborne"), TEXT("Skybourne") },
        { EAureateWakeForm::Seaborne, TEXT("Seaborne"), TEXT("Seabourne") },
        { EAureateWakeForm::Submersible, TEXT("Submersible"), TEXT("Submersible") },
        { EAureateWakeForm::Orbiter, TEXT("Orbiter"), TEXT("Starbourne") },
    };

    for (int32 Index = 0; Index < 4; ++Index)
    {
        const FFormCase& Row = Cases[Index];
        const int64 Value = static_cast<int64>(Row.Form);
        const FString Label = FString::Printf(TEXT("Aureate form slot %d"), Index);

        TestEqual(Label + TEXT(" retained original enum ordinal"), Value, static_cast<int64>(Index));
        TestEqual(Label + TEXT(" retained existing C++ identifier"),
            Forms->GetNameStringByValue(Value), FString(Row.InternalName));
        TestEqual(Label + TEXT(" exposes creator-approved display label"),
            Forms->GetDisplayNameTextByValue(Value).ToString(), FString(Row.DisplayName));
    }

    const AAureateWakePreviewActor* Defaults = GetDefault<AAureateWakePreviewActor>();
    if (TestNotNull(TEXT("Native ship actor default object"), Defaults))
    {
        TestFalse(TEXT("Starbourne debug preview remains gated off by default"),
            Defaults->bAllowOrbiterPreview);
    }
    return !HasAnyErrors();
}
#endif
