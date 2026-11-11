# Portable, engine-free unit fixtures for the actual native UBT overlap gate.
# AST-load only the guard FUNCTION, never the rest of Verify-Unreal.ps1;
# no editor, compiler, network, source writes, or real process termination.
$ErrorActionPreference = 'Stop'
$Source = Join-Path $PSScriptRoot 'Verify-Unreal.ps1'
$Tokens = $null
$Errors = $null
$Ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $Source, [ref]$Tokens, [ref]$Errors)
if ($Errors.Count -ne 0) { throw "Native verifier did not parse" }
$Definitions = @($Ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
    $node.Name -eq 'Assert-NoOtherUnrealBuild'
}, $true))
if ($Definitions.Count -ne 1) { throw 'Expected exactly one native UBT admission gate' }
. ([scriptblock]::Create($Definitions[0].Extent.Text))
$script:MockProcessSet = @()
function Get-CimInstance {
    [CmdletBinding()]
    param([Parameter(Position = 0)][string]$Class, [string]$Filter)
    if ($Class -ne 'Win32_Process' -or $Filter -notmatch 'cmd\.exe') {
        throw 'HOLD: unexpected process-query scope'
    }
    return $script:MockProcessSet
}
$Passed = 0
function MustPass([string]$Name, [object[]]$Processes) {
    $script:MockProcessSet = @($Processes)
    Assert-NoOtherUnrealBuild -Phase $Name
    $script:Passed++
}
function MustHold([string]$Name, [object[]]$Processes) {
    $script:MockProcessSet = @($Processes)
    $Held = $false
    try {
        Assert-NoOtherUnrealBuild -Phase $Name
    } catch {
        if ($_.Exception.Message -notmatch 'another UnrealBuildTool or Build\.bat is already active') {
            throw "$Name rejected unexpectedly: $($_.Exception.Message)"
        }
        $Held = $true
    }
    if (-not $Held) { throw "${Name}: verifier let another UBT enter its global queue" }
    $script:Passed++
}
function P([string]$Name, [string]$Line) {
    return [pscustomobject]@{ Name = $Name; CommandLine = $Line }
}
MustPass 'idle' @()
MustPass 'ordinary-dotnet' @((P 'dotnet.exe' 'dotnet test unrelated.dll'))
MustPass 'ordinary-command-shell' @((P 'cmd.exe' 'cmd.exe /c git status'))
MustHold 'other-ubt-dotnet' @((P 'dotnet.exe' 'dotnet Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll TSTSS-LyraEditor Win64 Development'))
MustHold 'other-build-batch' @((P 'cmd.exe' 'cmd.exe /c "C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat" OtherEditor Win64 Development'))
MustHold 'case-insensitive-command' @((P 'cmd.exe' 'C:/Engine/Build/BatchFiles/BUILD.BAT TSTSS-LyraEditor Win64 Development'))
MustHold 'real-build-among-ordinary-processes' @(
    (P 'cmd.exe' 'cmd.exe /c echo status'),
    (P 'dotnet.exe' 'dotnet UnrealBuildTool.dll ToSailTheStarrySkyEditor Win64 Development')
)
if ($Passed -ne 7) { throw "UBT admission fixture count changed: $Passed" }
Write-Output "PASS: $Passed isolated UBT-overlap admission fixtures; no Unreal, saves, or external processes affected"
