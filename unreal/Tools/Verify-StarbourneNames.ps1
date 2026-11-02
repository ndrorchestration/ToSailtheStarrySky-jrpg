# Starbourne display names: exact-head, no-install, fail-closed native acceptance.
# Safe to run -PreflightOnly while other Unreal tasks occupy the workstation.
[CmdletBinding()]
param(
    [string]$EngineRoot = '',
    [Int64]$MinFreeMemoryBytes = 6442450944,
    [switch]$PreflightOnly
)
$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$Project = (Resolve-Path (Join-Path $PSScriptRoot '../ToSailTheStarrySky.uproject')).Path
$Engine = if ($EngineRoot) { $EngineRoot } elseif ($env:TSTSS_UNREAL_ENGINE_ROOT) {
    $env:TSTSS_UNREAL_ENGINE_ROOT
} else { Join-Path $env:ProgramFiles 'Epic Games/UE_5.8' }
$HostGate = Join-Path $PSScriptRoot 'Check-UnrealHost.ps1'
$Build = Join-Path $Engine 'Engine/Build/BatchFiles/Build.bat'
$EditorCmd = Join-Path $Engine 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$TestName = 'TSTSS.AureateWake.Canon.FormDisplayNames'

function Git-Identity {
    $Head = (& git -C $RepoRoot rev-parse HEAD 2>$null)
    if ($LASTEXITCODE -ne 0 -or $Head -notmatch '^[0-9a-f]{40}$') {
        throw 'Cannot bind verification to exactly one SHA-1 repository HEAD'
    }
    $Changes = @(& git -C $RepoRoot status --porcelain 2>$null | Where-Object { $_ })
    if ($LASTEXITCODE -ne 0 -or $Changes.Count -gt 0) {
        throw 'Fail closed: source checkout has pending changes'
    }
    return [string]$Head
}
function System-Preflight {
    $Os = Get-CimInstance Win32_OperatingSystem
    if ($null -eq $Os -or $null -eq $Os.FreePhysicalMemory) {
        throw 'Cannot measure physical memory: refuse to launch Unreal'
    }
    $Free = [Int64]$Os.FreePhysicalMemory * 1024
    $Processes = @(Get-CimInstance Win32_Process | Where-Object {
        $_.Name -in @('UnrealEditor.exe','UnrealEditor-Cmd.exe',
                      'UnrealBuildTool.exe','LiveCodingConsole.exe') -or
        ($_.Name -eq 'dotnet.exe' -and $_.CommandLine -match 'UnrealBuildTool')
    })
    return [ordered]@{
        authority = 'NATIVE_STARBOURNE_VERIFICATION_PREFLIGHT_ONLY'
        ready = ($Processes.Count -eq 0 -and $Free -ge $MinFreeMemoryBytes)
        free_physical_memory_bytes = $Free
        minimum_free_memory_bytes = $MinFreeMemoryBytes
        blocking_process_ids = @($Processes | ForEach-Object { $_.ProcessId })
        blocking_process_names = @($Processes | ForEach-Object { $_.Name })
    }
}
$HeadAtStart = Git-Identity
if (-not (Test-Path -LiteralPath $HostGate -PathType Leaf) -or
    -not (Test-Path -LiteralPath $Build -PathType Leaf) -or
    -not (Test-Path -LiteralPath $EditorCmd -PathType Leaf)) {
    throw 'Missing Unreal host checker or native editor tools; no software installation authorized'
}
$Readiness = System-Preflight
$Readiness.source_head = $HeadAtStart
$Readiness | ConvertTo-Json -Depth 5
if (-not $Readiness.ready) {
    Write-Output 'HOLD: competing Unreal process(es) or insufficient free RAM; no native build attempted'
    exit 20
}
if ($PreflightOnly) {
    Write-Output 'PREFLIGHT_READY_ONLY: no native compile or automation performed'
    exit 0
}
& $HostGate -EngineRoot $Engine -RequireReady
if ($LASTEXITCODE -ne 0) {
    throw 'Unreal native prerequisite gate failed; refusing compilation'
}
$Evidence = Join-Path $RepoRoot "unreal/Saved/StarbourneNative/$HeadAtStart"
if (Test-Path -LiteralPath $Evidence) {
    throw 'Refusing to reuse or overwrite existing native receipt directory'
}
New-Item -ItemType Directory -Path $Evidence -Force | Out-Null
$HeadAtStart | Set-Content -LiteralPath (Join-Path $Evidence 'head.txt')

# No native hot reload or live patch of another active editor.
& $Build ToSailTheStarrySkyEditor Win64 Development "-Project=$Project" -WaitMutex -NoLiveCoding -NoHotReloadFromIDE -nowrite 2>&1 |
    Tee-Object -FilePath (Join-Path $Evidence 'build.log')
$BuildExit = $LASTEXITCODE
if ($BuildExit -ne 0) { throw "Exact-head UE C++/UHT build failed with exit $BuildExit" }
if ((Git-Identity) -ne $HeadAtStart) {
    throw 'Source SHA or cleanliness changed after build; refusing stale evidence'
}
$PreTest = System-Preflight
if (-not $PreTest.ready) {
    throw 'Another Unreal process is active or memory is low; refusing automation'
}
$ReportDir = Join-Path $Evidence 'AutomationReport'
New-Item -ItemType Directory -Path $ReportDir | Out-Null
& $EditorCmd $Project -unattended -nop4 -nullrhi -NoSplash -NoSound -NoLiveCoding "-ExecCmds=Automation RunTests $TestName; Quit" '-testexit=Automation Test Queue Empty' "-ReportExportPath=$ReportDir" -log 2>&1 |
    Tee-Object -FilePath (Join-Path $Evidence 'automation.log')
$AutomationExit = $LASTEXITCODE
if ($AutomationExit -ne 0) { throw "Native Unreal automation failed with exit $AutomationExit" }
$ReportFile = Join-Path $ReportDir 'index.json'
if (-not (Test-Path -LiteralPath $ReportFile -PathType Leaf)) {
    throw 'Native automation JSON report missing; no success can be claimed'
}
$Report = Get-Content -LiteralPath $ReportFile -Raw | ConvertFrom-Json
if ($null -eq $Report.succeeded -or $null -eq $Report.failed -or
    $null -eq $Report.notRun -or $Report.failed -ne 0 -or
    $Report.notRun -ne 0 -or $Report.succeeded -lt 1) {
    throw 'Native automation summary is incomplete or unsuccessful'
}
$Entries = @($Report.tests | Where-Object { $_ -and $_.fullTestPath -eq $TestName })
if ($Entries.Count -ne 1 -or $Entries[0].state -ne 'Success') {
    throw 'Reflected Starbourne display-name test missing or not successful'
}
if ((Git-Identity) -ne $HeadAtStart) {
    throw 'Source SHA or cleanliness changed after native automation'
}
$Receipt = [ordered]@{
    authority = 'UE58_NATIVE_STARBOURNE_FORM_DISPLAY_NAMES_VERIFIED'
    head = $HeadAtStart
    test = $TestName
    native_build_exit = $BuildExit
    automation_exit = $AutomationExit
    succeeded = $Report.succeeded
    failed = $Report.failed
    not_run = $Report.notRun
    starbourne_gameplay_unlocked = $false
    creator_model_approved = $false
}
$Receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $Evidence 'verified.json')
$Receipt | ConvertTo-Json -Depth 5
