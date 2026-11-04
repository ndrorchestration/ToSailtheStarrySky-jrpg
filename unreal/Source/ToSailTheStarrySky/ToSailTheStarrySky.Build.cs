using UnrealBuildTool;

public class ToSailTheStarrySky : ModuleRules
{
    public ToSailTheStarrySky(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "UMG" });
    }
}
