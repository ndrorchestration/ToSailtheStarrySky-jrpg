[CmdletBinding()]
param(
    [string]$EngineRoot = "",
    [int]$MinimumPatch = 4,
    [switch]$RequireReady
)
$ErrorActionPreference = 'Stop'
$ExpectedVersion = '5.8.4+'
$Project = Join-Path $PSScriptRoot '..\ToSailTheStarrySky.uproject'
$Candidate = if ($EngineRoot) {
    $EngineRoot
} elseif ($env:TSTSS_UNREAL_ENGINE_ROOT) {
    $env:TSTSS_UNREAL_ENGINE_ROOT
} else {
    Join-Path $env:ProgramFiles 'Epic Games\UE_5.8'
}
$Build = Join-Path $Candidate 'Engine\Build\BatchFiles\Build.bat'
$Editor = Join-Path $Candidate 'Engine\Binaries\Win64\UnrealEditor.exe'
$EditorCmd = Join-Path $Candidate 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$VersionFile = Join-Path $Candidate 'Engine\Build\Build.version'
$EngineVersion = ""
$EngineVersionValid = $false
$VersionError = ""
if (Test-Path -LiteralPath $VersionFile -PathType Leaf) {
    try {
        $Manifest = Get-Content -LiteralPath $VersionFile -Raw | ConvertFrom-Json
        $EngineVersion = ('{0}.{1}.{2}' -f $Manifest.MajorVersion, $Manifest.MinorVersion, $Manifest.PatchVersion)
        $EngineVersionValid = [bool](
            $Manifest.MajorVersion -eq 5 -and $Manifest.MinorVersion -eq 8 -and
            $Manifest.PatchVersion -ge $MinimumPatch)
    } catch {
        $VersionError = "Unparseable Unreal Build.version"
    }
}
$ProgramFilesX86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
$Vswhere = Join-Path $ProgramFilesX86 'Microsoft Visual Studio\Installer\vswhere.exe'
$VsRoot = ""
if (Test-Path -LiteralPath $Vswhere) {
    $Found = @(& $Vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2>$null)
    if ($LASTEXITCODE -eq 0 -and $Found.Count -gt 0) {
        $VsRoot = [string]$Found[0]
    }
}
$WindowsKit = Join-Path $ProgramFilesX86 'Windows Kits\10\Include'
$UnrealValid = (Test-Path -LiteralPath $Build -PathType Leaf) -and
    (Test-Path -LiteralPath $Editor -PathType Leaf) -and
    (Test-Path -LiteralPath $EditorCmd -PathType Leaf)
$ProjectValid = Test-Path -LiteralPath $Project -PathType Leaf
$CxxValid = [bool]$VsRoot
$SdkValid = Test-Path -LiteralPath $WindowsKit -PathType Container
$Ready = $UnrealValid -and $EngineVersionValid -and $ProjectValid -and $CxxValid -and $SdkValid
$Missing = @()
if (-not $UnrealValid) { $Missing += "Unreal 5.8 Engine Build.bat + Editor binaries" }
if (-not $EngineVersionValid) { $Missing += "Unreal Build.version requires 5.8 patch >= $MinimumPatch" }
if (-not $ProjectValid) { $Missing += "ToSailTheStarrySky.uproject" }
if (-not $CxxValid) { $Missing += "Visual Studio C++ x64 build tools" }
if (-not $SdkValid) { $Missing += "Windows SDK 10 headers" }
$Output = [ordered]@{
    authority = "NATIVE_HOST_PREREQUISITES_ONLY_NOT_A_BUILD_OR_RENDER"
    expected_engine = $ExpectedVersion
    candidate_path = $Candidate
    detected_engine_version = $EngineVersion
    engine_version_manifest_valid = [bool]$EngineVersionValid
    version_error = $VersionError
    engine_binaries_present = [bool]$UnrealValid
    vs_cpp_toolchain_present = $CxxValid
    windows_sdk_present = [bool]$SdkValid
    project_exists = [bool]$ProjectValid
    ready_for_native_build_attempt = [bool]$Ready
    missing = $Missing
}
$Output | ConvertTo-Json -Depth 4
if ($RequireReady -and -not $Ready) { exit 2 }
exit 0
