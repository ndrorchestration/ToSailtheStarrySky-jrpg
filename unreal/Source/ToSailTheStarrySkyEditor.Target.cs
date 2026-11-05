using UnrealBuildTool;
using System.Collections.Generic;

public class ToSailTheStarrySkyEditorTarget : TargetRules
{
    public ToSailTheStarrySkyEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V7;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
        ExtraModuleNames.Add("ToSailTheStarrySky");
    }
}
