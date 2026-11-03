param(
    [Parameter(Mandatory=$true)][string]$EngineRoot,
    [Parameter(Mandatory=$true)][string]$ExpectedHead,
    [switch]$PreflightOnly
)
$ErrorActionPreference = 'Stop'

# The operator authorizes only the independent PR713 map-QA worktree.
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if ((Split-Path $RepoRoot -Leaf) -ne 'TSTSS_PR713_NativeMapQA_20261102') {
    throw 'HOLD: not the named disposable PR713 native-map worktree'
}
$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Project = Join-Path $ProjectDir 'ToSailTheStarrySky.uproject'
$Verifier = Join-Path $PSScriptRoot 'verify_pr713_native_prelude_map.py'
$EditorCmd = Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$VersionPath = Join-Path $EngineRoot 'Engine/Build/Build.version'
$MapPath = Join-Path $ProjectDir 'Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap'
$MapExpected = '4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80'
if ($ExpectedHead -notmatch '^[a-fA-F0-9]{40}$') {
    throw 'HOLD: ExpectedHead must be a full 40-character Git SHA'
}
if (-not (Test-Path -LiteralPath $EditorCmd -PathType Leaf) -or
    -not (Test-Path -LiteralPath $VersionPath -PathType Leaf)) {
    throw 'HOLD: Unreal Editor commandlet or version metadata missing'
}
$Version = Get-Content -LiteralPath $VersionPath -Raw -ErrorAction Stop |
    ConvertFrom-Json -ErrorAction Stop
if ($Version.MajorVersion -ne 5 -or $Version.MinorVersion -ne 8 -or
    $Version.PatchVersion -ne 4) {
    throw 'HOLD: this native map review requires installed Unreal Engine 5.8.4'
}
if (-not (Test-Path -LiteralPath $Project -PathType Leaf) -or
    -not (Test-Path -LiteralPath $Verifier -PathType Leaf) -or
    -not (Test-Path -LiteralPath $MapPath -PathType Leaf)) {
    throw 'HOLD: required exact-review project, Python script or V2 map missing'
}
$Head = (& git -C $RepoRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $Head -ne $ExpectedHead) {
    throw "HOLD: exact checkout Git HEAD differs from expected commit"
}
$BeforeTree = @(git -C $RepoRoot status --porcelain)
if ($LASTEXITCODE -ne 0 -or $BeforeTree.Count -gt 0) {
    throw 'HOLD: tracked or untracked project changes before native map review'
}
$MapBefore = (Get-FileHash -LiteralPath $MapPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($MapBefore -ne $MapExpected) {
    throw 'HOLD: tracked V2 Prelude map digest mismatch'
}

$ConfigHashes = @{}
foreach ($name in @('DefaultEngine.ini', 'DefaultInput.ini')) {
    $path = Join-Path $ProjectDir ('Config/' + $name)
    $item = Get-Item -LiteralPath $path -ErrorAction Stop
    if (-not $item.IsReadOnly) {
        throw "HOLD: disposable project $name must be write-protected before Editor execution"
    }
    $ConfigHashes[$name] = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
}
$SaveDir = Join-Path $ProjectDir 'Saved/SaveGames'
if (Test-Path -LiteralPath $SaveDir) {
    $ExistingSaves = @(Get-ChildItem -LiteralPath $SaveDir -Filter '*.sav' -File -ErrorAction Stop)
    if ($ExistingSaves.Count -gt 0) {
        throw 'HOLD: isolated review workspace contains SaveGame files; do not modify or delete them'
    }
}

# This guard must run before Editor startup and before creating any receipt.
$ActiveEditors = @(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','LiveCodingConsole' -ErrorAction SilentlyContinue)
if ($ActiveEditors.Count -gt 0) {
    throw 'HOLD: active Unreal Editor or Live Coding session; do not stop other work to force native QA'
}
if ($PreflightOnly) {
    Write-Output "NATIVE_PRELUDE_MAP_PREFLIGHT_PASS_NO_EDITOR_LAUNCHED HEAD=$Head"
    return
}
# No build in this script: Verify-Unreal.ps1 -SkipTests must already have
# passed for this exact SHA and tooling. This launcher only admits the map QA.
$BuildEvidenceRoot = Join-Path $ProjectDir 'Saved/MigrationEvidence'
$BuildReceipts = @(
    Get-ChildItem -LiteralPath $BuildEvidenceRoot -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like ($Head.Substring(0, 12) + '-*') }
)
if ($BuildReceipts.Count -eq 0) {
    throw 'HOLD: no source-locked build verification receipt; run Verify-Unreal.ps1 -SkipTests first'
}
$BuildApproved = $false
foreach ($receipt in $BuildReceipts) {
    $headFile = Join-Path $receipt.FullName 'head.txt'
    $logFile = Join-Path $receipt.FullName 'build.log'
    if ((Test-Path -LiteralPath $headFile) -and
        (Test-Path -LiteralPath $logFile) -and
        ((Get-Content -LiteralPath $headFile -Raw).Trim() -eq $Head)) {
        # Check only that a run was issued; its success still requires the
        # review operator to inspect Verify-Unreal's exit status/log.
        $BuildApproved = $true
    }
}
if (-not $BuildApproved) {
    throw 'HOLD: exact-SHA build receipt files absent or inconsistent'
}
$OutputRoot = Join-Path $ProjectDir 'Saved/NativePreludeMapQA'
$BeforeReceipts = @{}
if (Test-Path -LiteralPath $OutputRoot) {
    foreach ($f in @(Get-ChildItem -LiteralPath $OutputRoot -Filter '*.json' -File)) {
        $BeforeReceipts[$f.FullName] = $true
    }
}
$RunId = ('{0}-{1}-{2}' -f $Head.Substring(0, 12),
    [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'),
    [guid]::NewGuid().ToString('N').Substring(0,8))
$LauncherRoot = Join-Path $OutputRoot 'LauncherReceipts'
New-Item -Path $LauncherRoot -ItemType Directory -Force -ErrorAction Stop | Out-Null
$LocalReceipt = Join-Path $LauncherRoot $RunId
if (Test-Path -LiteralPath $LocalReceipt) {
    throw 'HOLD: native map run evidence already exists; refusing overwrite'
}
New-Item -Path $LocalReceipt -ItemType Directory -ErrorAction Stop | Out-Null
$Head | Set-Content -LiteralPath (Join-Path $LocalReceipt 'head.txt')
$LogFile = Join-Path $LocalReceipt 'editor-map-commandlet.log'
$env:TSTSS_REVIEW_EXPECTED_HEAD = $Head
try {
    # Source-locked read-only Editor inspection, not a game or PIE launch.
    & $EditorCmd $Project '-run=pythonscript' "-script=$Verifier" '-unattended' '-nop4' '-nullrhi' '-log' 2>&1 |
        Tee-Object -FilePath $LogFile
    if ($LASTEXITCODE -ne 0) {
        throw "HOLD: native Editor map commandlet failed with exit code $LASTEXITCODE"
    }
} finally {
    Remove-Item Env:TSTSS_REVIEW_EXPECTED_HEAD -ErrorAction SilentlyContinue
}
$LogBody = Get-Content -LiteralPath $LogFile -Raw
if (-not $LogBody.Contains('TSTSS_NATIVE_PRELUDE_MAP_QA_PASS')) {
    throw 'HOLD: Editor returned without the actual native map-QA PASS sentinel'
}
$NewReceipts = @(
    Get-ChildItem -LiteralPath $OutputRoot -Filter '*.json' -File -ErrorAction Stop |
    Where-Object { -not $BeforeReceipts.ContainsKey($_.FullName) }
)
if ($NewReceipts.Count -ne 1) {
    throw 'HOLD: native Editor did not create exactly one fresh, non-overwriting map-QA report'
}
$Payload = Get-Content -LiteralPath $NewReceipts[0].FullName -Raw -ErrorAction Stop |
    ConvertFrom-Json -ErrorAction Stop
if ($Payload.status -ne 'NATIVE_EDITOR_MAP_AND_REAL_ACTORS_PASS_NOT_PIE' -or
    $Payload.source_sha -ne $Head -or $Payload.native_milestone_actor_count -ne 7 -or
    $Payload.map_sha256 -ne $MapExpected -or
    $Payload.actual_pie_player_input_tested -ne $false -or
    $Payload.actual_savegame_disk_roundtrip_tested -ne $false -or
    $Payload.chapter_one_act_one -ne $false -or
    $Payload.render_or_water_physics_approved -ne $false) {
    throw 'HOLD: native map-QA receipt incomplete, contradicted or claiming unsupported PIE/gameplay acceptance'
}
if ((Get-FileHash -LiteralPath $MapPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $MapBefore) {
    throw 'HOLD: Unreal modified the tracked Prelude review map'
}
foreach ($name in $ConfigHashes.Keys) {
    $hash = (Get-FileHash -LiteralPath (Join-Path $ProjectDir ('Config/' + $name)) -Algorithm SHA256).Hash
    if ($hash -ne $ConfigHashes[$name]) {
        throw 'HOLD: Unreal modified tracked input or engine default configuration'
    }
}
if (((& git -C $RepoRoot rev-parse HEAD).Trim() -ne $Head) -or
    (@(git -C $RepoRoot status --porcelain).Count -gt 0)) {
    throw 'HOLD: exact source HEAD or working-tree custody changed during real Editor map QA'
}
Write-Output "NATIVE_EDITOR_MAP_ACTORS_PASS_NOT_PIE HEAD=$Head"
Write-Output "NATIVE_EDITOR_MAP_REPORT_SHA256=$((Get-FileHash -LiteralPath $NewReceipts[0].FullName -Algorithm SHA256).Hash)"
Write-Output "PIE_P01_P13=NOT_TESTED"
