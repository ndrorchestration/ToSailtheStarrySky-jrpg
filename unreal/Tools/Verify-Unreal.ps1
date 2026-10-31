param(
    [Parameter(Mandatory=$true)][string]$EngineRoot,
    [switch]$SkipTests
)
$ErrorActionPreference = 'Stop'
# A different UE version or half-installed editor must never be accepted as a
# native game build. Check 5.8.4+ and the real MSVC + SDK before invoking UBT.
$PrereqGate = Join-Path $PSScriptRoot 'Check-UnrealHost.ps1'
if (-not (Test-Path -LiteralPath $PrereqGate -PathType Leaf)) {
    throw 'Missing Unreal native host prerequisites checker'
}
& $PrereqGate -EngineRoot $EngineRoot -RequireReady
if ($LASTEXITCODE -ne 0) {
    throw "Unreal native host prerequisites failed ($LASTEXITCODE); not attempting Build.bat"
}
$Project = (Resolve-Path (Join-Path $PSScriptRoot '../ToSailTheStarrySky.uproject')).Path
$BuildTool = Join-Path $EngineRoot 'Engine/Build/BatchFiles/Build.bat'
$EditorCmd = Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
if (-not (Test-Path $BuildTool)) { throw "Missing Unreal Build.bat at $BuildTool" }
if (-not (Test-Path $EditorCmd)) { throw "Missing UnrealEditor-Cmd.exe at $EditorCmd" }
$Evidence = Join-Path $PSScriptRoot '../Saved/MigrationEvidence'
$GitHead = (git -C (Join-Path $PSScriptRoot '../..') rev-parse HEAD)
if ($LASTEXITCODE -ne 0 -or -not $GitHead) { throw 'Unable to resolve repository HEAD' }
$WorkingTree = @(git -C (Join-Path $PSScriptRoot '../..') status --porcelain)
if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect working tree' }
if ($WorkingTree.Count -gt 0) { throw 'Working tree has uncommitted changes; evidence cannot be bound to HEAD' }
New-Item -Path $Evidence -ItemType Directory -Force | Out-Null
$GitHead | Set-Content (Join-Path $Evidence 'head.txt')
& $BuildTool ToSailTheStarrySkyEditor Win64 Development "-Project=$Project" -WaitMutex 2>&1 |
    Tee-Object (Join-Path $Evidence 'build.log')
if ($LASTEXITCODE -ne 0) { throw "Unreal editor build failed ($LASTEXITCODE)" }
if ($SkipTests) {
    # Build-only evidence still requires a stable, clean checkout.
    $BuildHead = (git -C (Join-Path $PSScriptRoot '../..') rev-parse HEAD)
    if ($LASTEXITCODE -ne 0 -or $BuildHead -ne $GitHead) {
        throw "Repository HEAD changed during build; initial=$GitHead final=$BuildHead"
    }
    $BuildTree = @(git -C (Join-Path $PSScriptRoot '../..') status --porcelain)
    if ($LASTEXITCODE -ne 0 -or $BuildTree.Count -gt 0) {
        throw 'Working tree changed during build; build-only evidence rejected'
    }
    Write-Host "Editor build completed at $GitHead; automation tests deliberately skipped. No automation PASS is claimed."
    exit 0
}
$ReportDirectory = Join-Path $Evidence 'AutomationReport'
if (Test-Path $ReportDirectory) { Remove-Item $ReportDirectory -Recurse -Force }
New-Item -Path $ReportDirectory -ItemType Directory -Force | Out-Null
$ExportArgument = '-ReportExportPath=' + $ReportDirectory
& $EditorCmd $Project -unattended -nop4 -nullrhi '-ExecCmds=Automation RunTests TSTSS; Quit' $ExportArgument -log 2>&1 |
    Tee-Object (Join-Path $Evidence 'automation.log')
if ($LASTEXITCODE -ne 0) { throw "Unreal automation command failed ($LASTEXITCODE)" }
$ReportPath = Join-Path $Evidence 'AutomationReport/index.json'
if (-not (Test-Path $ReportPath)) { throw 'No automation JSON evidence; refusing to mark PASS' }
$Report = Get-Content $ReportPath -Raw | ConvertFrom-Json
if ($null -eq $Report.succeeded -or $null -eq $Report.failed -or $null -eq $Report.notRun) {
    throw 'Automation report schema missing required summary fields; cannot claim PASS'
}
if ($Report.failed -gt 0 -or $Report.notRun -gt 0) {
    throw "Automation evidence incomplete: succeeded=$($Report.succeeded), failed=$($Report.failed), notRun=$($Report.notRun)"
}
# Require evidence for named critical tests, not merely an aggregate success count.
# Unreal AutomationTool exports per-test entries under tests[].fullTestPath/state.
$RequiredTests = @(
    'TSTSS.AureateWake.Review.FourFormMechanics',
    'TSTSS.Combat.TransactionalActions',
    'TSTSS.Combat.RejectsInvalidActionsWithoutMutation',
    'TSTSS.Combat.TurnOrderAndAtomicity',
    'TSTSS.Combat.AbilityAuthorization',
    'TSTSS.Combat.EncounterCompletion',
    'TSTSS.FirstWake.RequiresOrderedMilestones',
    'TSTSS.FirstWake.WaterLandingRequiresMeasuredStability',
    'TSTSS.FirstWake.WaterLandingRestore',
    'TSTSS.FirstWake.WaterLandingNegativePaths',
    'TSTSS.FirstWake.WaterlineGeometry',
    'TSTSS.Save.RejectsUnsupportedSchema',
    'TSTSS.Save.RejectsUnsafeSlots',
    'TSTSS.Save.RoundTripFirstWakeAndParty'
)
$Entries = @($Report.tests)
if ($Entries.Count -eq 0 -or $null -eq $Entries[0]) {
    throw 'No per-test automation evidence; refusing aggregate-only PASS'
}
if ($Report.succeeded -lt $RequiredTests.Count) {
    throw "Automation success count $($Report.succeeded) is below required test count $($RequiredTests.Count)"
}
foreach ($TestName in $RequiredTests) {
    $Matches = @($Entries | Where-Object { $_.fullTestPath -eq $TestName })
    if ($Matches.Count -ne 1) {
        throw "Required test missing or duplicated in report: $TestName"
    }
    if ($Matches[0].state -ne 'Success') {
        throw "Required test is not successful: $TestName ($($Matches[0].state))"
    }
}
# Recheck the checkout after execution so a moving branch cannot inherit stale evidence.
$FinalHead = (git -C (Join-Path $PSScriptRoot '../..') rev-parse HEAD)
if ($LASTEXITCODE -ne 0 -or $FinalHead -ne $GitHead) {
    throw "Repository HEAD changed during verification; initial=$GitHead final=$FinalHead"
}
$FinalWorkingTree = @(git -C (Join-Path $PSScriptRoot '../..') status --porcelain)
if ($LASTEXITCODE -ne 0 -or $FinalWorkingTree.Count -gt 0) {
    throw 'Working tree changed during verification; refusing to bind PASS to a dirty checkout'
}
Write-Host "Native build and reported automation checks passed at $GitHead. Visual acceptance remains separate."
