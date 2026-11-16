param(
    [Parameter(Mandatory=$true)][string]$EngineRoot,
    [Parameter(Mandatory=$true)][string]$ExpectedHead,
    [switch]$PreflightOnly
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if ((Split-Path $Root -Leaf) -ne 'TSTSS-Slice-Enemies-20261110') {
    throw 'HOLD: hybrid JRPG map authoring requires the named isolated worktree'
}
if ($ExpectedHead -notmatch '^[a-fA-F0-9]{40}$') {
    throw 'HOLD: full expected source SHA is required'
}
$Head = (& git -C $Root rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $Head -ne $ExpectedHead) {
    throw 'HOLD: exact review HEAD does not match'
}
$Status = @(git -C $Root status --porcelain)
if ($LASTEXITCODE -ne 0 -or $Status.Count -gt 0) {
    throw 'HOLD: clean source checkout required before authoring'
}
$Project = Join-Path $ProjectDir 'ToSailTheStarrySky.uproject'
$EditorCmd = Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$BuildScript = Join-Path $EngineRoot 'Engine/Build/BatchFiles/Build.bat'
$VersionPath = Join-Path $EngineRoot 'Engine/Build/Build.version'
$Original = Join-Path $ProjectDir 'Content/TSTSS/Review/SliceEnemyCombatSandbox_V1.umap'
$Target = Join-Path $ProjectDir 'Content/TSTSS/Review/JRPGHybridEncounterReview_V2.umap'
$Runner = Join-Path $PSScriptRoot 'run_tstss_jrpg_hybrid_review_map.py'
$ReceiptFile = Join-Path $ProjectDir 'Saved/EnemyGalleryV2/hybrid-receipt.json'
if (-not (Test-Path $EditorCmd -PathType Leaf) -or
    -not (Test-Path $BuildScript -PathType Leaf) -or
    -not (Test-Path $VersionPath -PathType Leaf) -or
    -not (Test-Path $Project -PathType Leaf) -or
    -not (Test-Path $Runner -PathType Leaf) -or
    -not (Test-Path $Original -PathType Leaf)) {
    throw 'HOLD: native Unreal editor or required gallery/source unavailable'
}
$Version = Get-Content $VersionPath -Raw | ConvertFrom-Json
if ($Version.MajorVersion -ne 5 -or $Version.MinorVersion -ne 8 -or
    $Version.PatchVersion -ne 4) {
    throw 'HOLD: native review requires Unreal Engine 5.8.4'
}
if (Test-Path $Target -PathType Leaf) { throw 'HOLD: refuse overwrite of V2 map' }
if (Test-Path $ReceiptFile -PathType Leaf) { throw 'HOLD: refuse receipt overwrite' }
$Gallery = Join-Path $ProjectDir 'Content/TSTSS/Review/SliceEnemyGallery_V0.umap'
if (-not (Test-Path $Gallery -PathType Leaf)) {
    throw 'HOLD: original V0 gallery missing'
}
$GallerySha = (Get-FileHash $Gallery -Algorithm SHA256).Hash.ToLowerInvariant()
if ($GallerySha -ne 'deb70ffeecedf572c8bd5b2fab3a515e748d95d27fb2d31f8c0bef2f34c0a022') {
    throw 'HOLD: original V0 gallery drift'
}
$BaseSha = (Get-FileHash $Original -Algorithm SHA256).Hash.ToLowerInvariant()
if ($BaseSha -ne '108c7582ef8f8073907fbd9d78bd7f487a98b5fb6df927335fadb0fb500f4250') {
    throw 'HOLD: native-verified V1 source SHA is different'
}
$Busy = @(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,LiveCodingConsole -ErrorAction SilentlyContinue)
if ($Busy.Count -gt 0) { throw 'HOLD: another Unreal Editor session is active' }
$Free = (Get-CimInstance Win32_OperatingSystem -ErrorAction Stop).FreePhysicalMemory
if ($null -eq $Free -or $Free -lt 5242880) {
    throw 'HOLD: below required 5 GiB free RAM'
}
if ((Get-PSDrive C -ErrorAction Stop).Free -lt (14*1GB)) {
    throw 'HOLD: below required 14 GiB free C: disk'
}
$Evidence = Join-Path $ProjectDir 'Saved/MigrationEvidence'
$Matched = @(Get-ChildItem $Evidence -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like ($Head.Substring(0,12)+'-*') })
$NativeBuild = $false
foreach ($dir in $Matched) {
    $candidate = Join-Path $dir.FullName 'verified-build.json'
    $headFile = Join-Path $dir.FullName 'head.txt'
    if (-not (Test-Path $candidate -PathType Leaf) -or
        -not (Test-Path $headFile -PathType Leaf)) { continue }
    $r = Get-Content $candidate -Raw | ConvertFrom-Json
    if ($r.status -eq 'WIN64_EDITOR_BUILD_PASS_CLEAN_SOURCE' -and
        $r.source_sha -eq $Head -and
        $r.unreal_version -eq '5.8.4' -and
        (Get-Content $headFile -Raw).Trim() -eq $Head) {
        $NativeBuild = $true
    }
}
if (-not $NativeBuild) {
    throw 'HOLD: exact-head clean Win64 Editor build-only receipt missing'
}
if ($PreflightOnly) {
    Write-Output "HYBRID_JRPG_PREFLIGHT_PASS_NOT_PIE HEAD=$Head"
    return
}
function Sha([string]$File) {
    return (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant()
}
$Config = @()
foreach ($name in @('DefaultEngine.ini','DefaultInput.ini')) {
    $path = Join-Path $ProjectDir ('Config/'+$name)
    $file = Get-Item -LiteralPath $path -ErrorAction Stop
    $Config += [pscustomobject]@{
        Path = $path
        OriginalReadOnly = $file.IsReadOnly
        OriginalHash = (Sha $path)
    }
}
$OldEnv = [Environment]::GetEnvironmentVariable('TSTSS_JRPG_HYBRID_EXPECTED_HEAD','Process')
try {
    foreach ($entry in $Config) {
        (Get-Item -LiteralPath $entry.Path).IsReadOnly = $true
    }
    [Environment]::SetEnvironmentVariable('TSTSS_JRPG_HYBRID_EXPECTED_HEAD',$Head,'Process')
    $SaveDir = Join-Path $ProjectDir 'Saved/EnemyGalleryV2'
    if (-not (Test-Path $SaveDir)) { New-Item $SaveDir -ItemType Directory | Out-Null }
    $Log = Join-Path $SaveDir ('author-'+$Head.Substring(0,12)+'.log')
    if (Test-Path $Log) { throw 'HOLD: existing exact-run editor log' }
    & $EditorCmd $Project '-run=pythonscript' "-script=$Runner" "-abslog=$Log" '-unattended' '-nop4' '-nullrhi' '-log'
    if ($LASTEXITCODE -ne 0) {
        throw "HOLD: native review authoring commandlet returned $LASTEXITCODE"
    }
    if (-not (Test-Path $Target -PathType Leaf) -or
        -not (Test-Path $ReceiptFile -PathType Leaf)) {
        throw 'HOLD: map or receipt missing after native editor'
    }
    $Receipt = Get-Content $ReceiptFile -Raw | ConvertFrom-Json
    if ($Receipt.status -ne 'NATIVE_HYBRID_MAP_SAVED_NOT_PIE' -or
        $Receipt.exact_head -ne $Head -or
        $Receipt.map_sha256 -ne (Sha $Target) -or
        (Sha $Original) -ne $BaseSha -or
        (Sha $Gallery) -ne $GallerySha) {
        throw 'HOLD: altered original or incorrect new map source receipt'
    }
    $After = @(git -C $Root status --porcelain)
    if ($After.Count -ne 1 -or
        $After[0] -ne '?? unreal/Content/TSTSS/Review/JRPGHybridEncounterReview_V2.umap') {
        throw 'HOLD: unexpected Git source or asset mutation'
    }
    Write-Output "HYBRID_JRPG_MAP_SAVED_NOT_PIE_OR_VISUAL_APPROVAL HEAD=$Head"
} finally {
    [Environment]::SetEnvironmentVariable('TSTSS_JRPG_HYBRID_EXPECTED_HEAD',$OldEnv,'Process')
    foreach ($entry in $Config) {
        (Get-Item -LiteralPath $entry.Path).IsReadOnly = $entry.OriginalReadOnly
        if ((Sha $entry.Path) -ne $entry.OriginalHash) {
            throw "HOLD: protected Unreal config changed: $($entry.Path)"
        }
    }
}
