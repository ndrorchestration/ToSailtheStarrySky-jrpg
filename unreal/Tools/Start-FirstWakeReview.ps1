param(
    [Parameter(Mandatory=$true)][string]$EngineRoot,
    [Parameter(Mandatory=$true)][string]$ExpectedHead,
    [switch]$OpenEditor
)
$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if ((Split-Path $RepoRoot -Leaf) -ne 'TSTSS_GameAssembly_20261104') {
    throw 'Use the isolated game assembly checkout'
}
if ($ExpectedHead -notmatch '^[a-fA-F0-9]{40}$') { throw 'Full ExpectedHead required' }
$Head = (& git -C $RepoRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $Head -ne $ExpectedHead) { throw 'ExpectedHead mismatch' }
if (@(git -C $RepoRoot status --porcelain).Count -ne 0 -or $LASTEXITCODE -ne 0) {
    throw 'Clean source required'
}
$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Project = Join-Path $ProjectDir 'ToSailTheStarrySky.uproject'
$Editor = Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor.exe'
$Version = Get-Content (Join-Path $EngineRoot 'Engine/Build/Build.version') -Raw | ConvertFrom-Json
if ($Version.MajorVersion -ne 5 -or $Version.MinorVersion -ne 8 -or $Version.PatchVersion -ne 4) {
    throw 'Unreal Engine 5.8.4 required'
}
if (-not (Test-Path $Editor -PathType Leaf)) { throw 'Editor missing' }
function Get-ReviewHash([string]$Path) {
    $Hash = [Security.Cryptography.SHA256]::Create()
    try {
        return [BitConverter]::ToString($Hash.ComputeHash([IO.File]::ReadAllBytes($Path))).Replace('-','').ToLowerInvariant()
    } finally { $Hash.Dispose() }
}
$Map = '/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2'
$MapFile = Join-Path $ProjectDir 'Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap'
$MapHash = '4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80'
if ((Get-ReviewHash $MapFile) -ne $MapHash) { throw 'Prelude map changed' }
if (@(Get-ChildItem (Join-Path $ProjectDir 'Saved/SaveGames') -Filter '*.sav' -File -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'Existing saves protected; use a fresh review workspace'
}
if (@(Get-Process UnrealEditor,UnrealEditor-Cmd,LiveCodingConsole -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'Existing Unreal session active'
}
# Require actual per-test evidence from this source head, not a previous branch.
. (Join-Path $PSScriptRoot 'Assert-NativeAutomationReport.ps1')
$VerifierText = Get-Content (Join-Path $PSScriptRoot 'Verify-Unreal.ps1') -Raw
$Required = @([regex]::Matches($VerifierText, "'(TSTSS\.[^']+)'") | ForEach-Object { $_.Groups[1].Value })
$NativeAccepted = $false
foreach ($Dir in @(Get-ChildItem (Join-Path $ProjectDir 'Saved/MigrationEvidence') -Directory -ErrorAction SilentlyContinue)) {
    $HeadFile = Join-Path $Dir.FullName 'head.txt'
    $ReportFile = Join-Path $Dir.FullName 'AutomationReport/index.json'
    if ((Test-Path $HeadFile) -and (Test-Path $ReportFile) -and
        (Get-Content $HeadFile -Raw).Trim() -eq $Head) {
        $null = Assert-TSTSSNativeAutomationReport -ReportPath $ReportFile -RequiredTests $Required
        $NativeAccepted = $true
    }
}
if (-not $NativeAccepted) { throw 'Exact-head native automation evidence missing' }
. (Join-Path $PSScriptRoot 'Assert-NativePreludeMapReceipt.ps1')
$MapAccepted = $false
foreach ($File in @(Get-ChildItem (Join-Path $ProjectDir 'Saved/NativePreludeMapQA') -Filter '*.json' -File -ErrorAction SilentlyContinue)) {
    $Report = Get-Content $File.FullName -Raw | ConvertFrom-Json
    if ($Report.source_sha -eq $Head) {
        $null = Assert-TSTSSNativePreludeMapReceipt -Report $Report -ExpectedHead $Head -ExpectedMapSha $MapHash
        $MapAccepted = $true
    }
}
if (-not $MapAccepted) { throw 'Exact-head native map admission missing' }
$Configs = @()
foreach ($Name in @('DefaultEngine.ini','DefaultInput.ini')) {
    $Path = Join-Path $ProjectDir ('Config/' + $Name)
    if ((Get-Item $Path).IsReadOnly) { throw 'Pre-existing config read-only state; do not adopt it' }
    $Configs += [pscustomobject]@{ Path=$Path; Hash=(Get-ReviewHash $Path) }
}
$FreeKiB = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
if ($FreeKiB -lt 6500000) { throw 'Insufficient free RAM for graphical review' }
Write-Output "FIRST_WAKE_REVIEW_READY HEAD=$Head MAP=$Map"
Write-Output 'Controls in PIE: WASD, mouse, E interact, J objective, F6 review save, F9 isolated review load. F5 is reserved for Editor shortcuts in PIE.'
Write-Output 'This seven-stop Prelude ends at engineering signoff. Launch/Splashdown and cinematic art are not complete.'
if (-not $OpenEditor) { return }
try {
    foreach ($Config in $Configs) { (Get-Item $Config.Path).IsReadOnly = $true }
    # Open the real level explicitly; never rewrite global startup map/config.
    $Arguments = @( ('"{0}"' -f $Project), $Map, '-d3d11', '-log')
    $Process = Start-Process -FilePath $Editor -ArgumentList $Arguments -PassThru
    Write-Output "FIRST_WAKE_EDITOR_STARTED PID=$($Process.Id). Press Play in Editor; input and visual acceptance remain unverified."
    $Process.WaitForExit()
    if ($Process.ExitCode -ne 0) { throw "Editor exited with code $($Process.ExitCode)" }
} finally {
    foreach ($Config in $Configs) { (Get-Item $Config.Path).IsReadOnly = $false }
}
foreach ($Config in $Configs) {
    if ((Get-ReviewHash $Config.Path) -ne $Config.Hash) { throw 'Tracked config changed during review' }
}
if ((Get-ReviewHash $MapFile) -ne $MapHash) { throw 'Review map changed during session' }
if ((& git -C $RepoRoot rev-parse HEAD).Trim() -ne $Head -or
    @(git -C $RepoRoot status --porcelain).Count -ne 0) { throw 'Review source changed during session' }
Write-Output 'Editor closed; config attributes restored. No automatic gameplay PASS claimed.'
