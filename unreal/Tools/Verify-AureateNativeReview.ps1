param(
    [Parameter(Mandatory=$true)][string]$RepositoryRoot,
    [Parameter(Mandatory=$true)][string]$ExpectedHead,
    [Parameter(Mandatory=$true)][string]$WorktreePath,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# Isolate everything from existing Unreal sessions, production scenes and main.
if ($ExpectedHead -notmatch '^[0-9a-fA-F]{40}$') {
    throw 'ExpectedHead must be a full immutable commit SHA.'
}
if (Test-Path -LiteralPath $WorktreePath) {
    throw "Review worktree already exists; refusing overwrite: $WorktreePath"
}
$Evidence = $WorktreePath + '-evidence'
if (Test-Path -LiteralPath $Evidence) {
    throw "Evidence already exists; refusing overwrite: $Evidence"
}
$BuildTool = Join-Path $EngineRoot 'Engine/Build/BatchFiles/Build.bat'
$EditorCmd = Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
foreach ($item in @($BuildTool, $EditorCmd)) {
    if (-not (Test-Path -LiteralPath $item)) { throw "Unreal 5.8 tool missing: $item" }
}
$ActualCommit = (& git -C $RepositoryRoot rev-parse "$ExpectedHead^{commit}").Trim()
if ($LASTEXITCODE -ne 0 -or $ActualCommit -ne $ExpectedHead) {
    throw "Expected source commit not found locally: $ExpectedHead"
}
& git -C $RepositoryRoot worktree add --detach $WorktreePath $ExpectedHead
if ($LASTEXITCODE -ne 0) { throw 'Could not create isolated review worktree.' }
$Checkout = (& git -C $WorktreePath rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $Checkout -ne $ExpectedHead) {
    throw "Worktree head mismatch: $Checkout"
}
New-Item -ItemType Directory -Path $Evidence -ErrorAction Stop | Out-Null
$ExpectedHead | Set-Content -Path (Join-Path $Evidence 'source-head.txt')
$Project = Join-Path $WorktreePath 'unreal/ToSailTheStarrySky.uproject'
if (-not (Test-Path -LiteralPath $Project)) { throw "Missing Unreal project: $Project" }

# Single compile worker to limit contention with other Unreal/editor processes.
& $BuildTool ToSailTheStarrySkyEditor Win64 Development "-Project=$Project" -WaitMutex -NoHotReloadFromIDE '-MaxParallelActions=1' 2>&1 |
    Tee-Object -FilePath (Join-Path $Evidence 'build.log')
$BuildExit = $LASTEXITCODE
if ($BuildExit -ne 0) { throw "UE 5.8.4 native build failed ($BuildExit)." }

$ReportDirectory = Join-Path $Evidence 'NativeAutomationReport'
New-Item -ItemType Directory -Path $ReportDirectory -ErrorAction Stop | Out-Null
$ReportArgument = '-ReportExportPath=' + $ReportDirectory
& $EditorCmd $Project -unattended -nop4 -nullrhi -nosplash -NoSound '-ExecCmds=Automation RunTests TSTSS' '-TestExit=Automation Test Queue Empty' $ReportArgument -log 2>&1 |
    Tee-Object -FilePath (Join-Path $Evidence 'automation.log')
$TestExit = $LASTEXITCODE
if ($TestExit -ne 0) { throw "Native automation process failed ($TestExit)." }
$ReportPath = Join-Path $ReportDirectory 'index.json'
if (-not (Test-Path -LiteralPath $ReportPath)) { throw 'No native automation JSON report.' }
$Report = Get-Content -LiteralPath $ReportPath -Raw | ConvertFrom-Json
if ($null -eq $Report.succeeded -or $null -eq $Report.failed -or $null -eq $Report.notRun) {
    throw 'Report summary missing required fields.'
}
if ($Report.failed -ne 0 -or $Report.notRun -ne 0 -or $Report.succeeded -lt 13) {
    throw "Incomplete native results: passed=$($Report.succeeded) failed=$($Report.failed) notRun=$($Report.notRun)"
}
$Ship = @($Report.tests | Where-Object {
    $_.fullTestPath -eq 'TSTSS.Ship.PreviewFormsAndOrbiterHold' -and $_.state -eq 'Success'
})
if ($Ship.Count -ne 1) { throw 'Native ship gate absent, duplicated or unsuccessful.' }
$FinalCommit = (& git -C $WorktreePath rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $FinalCommit -ne $ExpectedHead) {
    throw "Worktree HEAD moved during verification: $FinalCommit"
}
Write-Output "PASS: native Unreal Editor build and $($Report.succeeded) TSTSS tests at $ExpectedHead"
Write-Output "Evidence: $Evidence"
Write-Output 'Not verified: authored GLB rendering, wing-root clearance, final art, Orbiter unlock or gameplay release.'
