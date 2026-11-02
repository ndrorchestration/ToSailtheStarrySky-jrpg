param(
    [Parameter(Mandatory=$true)][string]$EngineRoot,
    [switch]$SkipTests,
    [string]$ExpectedHead = ''
)
$ErrorActionPreference = 'Stop'
$Project = (Resolve-Path (Join-Path $PSScriptRoot '../ToSailTheStarrySky.uproject')).Path
$BuildTool = Join-Path $EngineRoot 'Engine/Build/BatchFiles/Build.bat'
$EditorCmd = Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
if (-not (Test-Path $BuildTool -PathType Leaf)) { throw "Missing Unreal Build.bat at $BuildTool" }
if (-not (Test-Path $EditorCmd -PathType Leaf)) { throw "Missing UnrealEditor-Cmd.exe at $EditorCmd" }
# The project .uproject uses the 5.8 family, but a native review receipt must
# identify the exact tested Windows patch. Reject a wrong/stale EngineRoot.
$VersionPath = Join-Path $EngineRoot 'Engine/Build/Build.version'
if (-not (Test-Path $VersionPath -PathType Leaf)) { throw "Missing Engine/Build/Build.version at $VersionPath" }
try {
    $EngineVersion = Get-Content -LiteralPath $VersionPath -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
} catch {
    throw "Could not parse Unreal Engine version metadata at $VersionPath : $_"
}
if ($null -eq $EngineVersion.MajorVersion -or $null -eq $EngineVersion.MinorVersion -or
    $null -eq $EngineVersion.PatchVersion) {
    throw "Incomplete Unreal Engine version metadata at $VersionPath"
}
if ($EngineVersion.MajorVersion -ne 5 -or $EngineVersion.MinorVersion -ne 8 -or
    $EngineVersion.PatchVersion -ne 4) {
    throw ("Incorrect Unreal version: found {0}.{1}.{2}; this review requires 5.8.4" -f
        $EngineVersion.MajorVersion, $EngineVersion.MinorVersion, $EngineVersion.PatchVersion)
}
Write-Host "Verified Unreal Engine build metadata: 5.8.4 (not a native build PASS)"
$EvidenceRoot = Join-Path $PSScriptRoot '../Saved/MigrationEvidence'
$GitHead = (git -C (Join-Path $PSScriptRoot '../..') rev-parse HEAD)
if ($LASTEXITCODE -ne 0 -or -not $GitHead) { throw 'Unable to resolve repository HEAD' }
if ($GitHead -notmatch '^[0-9a-fA-F]{40}$') { throw "Unexpected Git SHA: $GitHead" }
if ($ExpectedHead -ne '' -and $ExpectedHead -notmatch '^[0-9a-fA-F]{40}$') {
    throw 'ExpectedHead must be a full 40-character Git commit SHA'
}
if ($ExpectedHead -ne '' -and $GitHead -ne $ExpectedHead) {
    throw "Source HEAD differs from the explicitly requested review commit: actual=$GitHead expected=$ExpectedHead"
}
$WorkingTree = @(git -C (Join-Path $PSScriptRoot '../..') status --porcelain)
if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect working tree' }
if ($WorkingTree.Count -gt 0) { throw 'Working tree has uncommitted changes; evidence cannot be bound to HEAD' }
# Every verification attempt receives a fresh, non-overwriting receipt folder.
# Keep previous success AND failure logs for head-specific review and debugging.
$RunId = ('{0}-{1}-{2}' -f $GitHead.Substring(0, 12),
    ([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')),
    ([guid]::NewGuid().ToString('N').Substring(0, 8)))
$Evidence = Join-Path $EvidenceRoot $RunId
# Parent directory is ignored, but may not exist in a fresh isolated checkout.
New-Item -Path $EvidenceRoot -ItemType Directory -Force -ErrorAction Stop | Out-Null
if (Test-Path $Evidence) { throw "Evidence folder already exists; refusing overwrite: $Evidence" }
New-Item -Path $Evidence -ItemType Directory -ErrorAction Stop | Out-Null
$GitHead | Set-Content (Join-Path $Evidence 'head.txt')
Write-Host "Review evidence directory (unique; retained on failure): $Evidence"
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
if (Test-Path $ReportDirectory) { throw 'Review automation evidence collision; refusing overwrite' }
New-Item -Path $ReportDirectory -ItemType Directory -ErrorAction Stop | Out-Null
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
    'TSTSS.Combat.TransactionalActions',
    'TSTSS.Combat.RejectsInvalidActionsWithoutMutation',
    'TSTSS.Combat.TurnOrderAndAtomicity',
    'TSTSS.Combat.AbilityAuthorization',
    'TSTSS.Combat.MagicAndWeaponTechniques',
    'TSTSS.Combat.InitiativeAndActiveParty',
    'TSTSS.Combat.TurnManagerTerminalOutcomes',
    'TSTSS.CombatData.ProtagonistContracts',
    'TSTSS.CombatData.ActionDefinitions',
    'TSTSS.CombatData.ActiveParty',
    'TSTSS.CombatData.CatalogBridge',
    'TSTSS.CombatIntegration.DataContractCannotAutoAuthorize',
    'TSTSS.CombatIntegration.ProgressiveRecruitmentPartySize',
    'TSTSS.CombatData.NonExecutableSkillReconciliation',
    'TSTSS.CombatIntegration.DesignOnlyTurnManagerDenial',
    'TSTSS.FirstWake.InteractionCameraBoomReach',
    'TSTSS.FirstWake.ReviewObjectivesAreReadOnly',
    'TSTSS.Combat.EncounterCompletion',
    'TSTSS.FirstWake.RequiresOrderedMilestones',
    'TSTSS.FirstWake.WaterLandingRequiresMeasuredStability',
    'TSTSS.FirstWake.WaterLandingRestore',
    'TSTSS.FirstWake.WaterLandingNegativePaths',
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
Write-Host "Native build and reported automation checks passed at $GitHead. Evidence retained at $Evidence. Visual acceptance remains separate."
