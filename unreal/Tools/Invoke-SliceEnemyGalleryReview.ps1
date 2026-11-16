param(
    [Parameter(Mandatory=$true)][string]$EngineRoot,
    [Parameter(Mandatory=$true)][string]$ExpectedHead,
    [switch]$PreflightOnly
)
$ErrorActionPreference = 'Stop'

# Explicit standalone review-map admission; never stop another project's Editor.
$Root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if ((Split-Path $Root -Leaf) -ne 'TSTSS-Slice-Enemies-20261110') {
    throw 'HOLD: requires the named disposable slice enemy worktree'
}
if ($ExpectedHead -notmatch '^[a-fA-F0-9]{40}$') {
    throw 'HOLD: full ExpectedHead SHA is mandatory'
}
$Actual = (& git -C $Root rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $Actual -ne $ExpectedHead) {
    throw 'HOLD: checked-out Git HEAD differs from exact source request'
}
$TreeStatus = @(git -C $Root status --porcelain)
if ($LASTEXITCODE -ne 0 -or $TreeStatus.Count -ne 0) {
    throw 'HOLD: authoring requires an initially clean disposable worktree'
}

$BuildTool = Join-Path $EngineRoot 'Engine/Build/BatchFiles/Build.bat'
$EditorCmd = Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$VersionPath = Join-Path $EngineRoot 'Engine/Build/Build.version'
$Project = Join-Path $ProjectDir 'ToSailTheStarrySky.uproject'
$Runner = Join-Path $PSScriptRoot 'run_tstss_slice_enemy_gallery.py'
$TargetMap = Join-Path $ProjectDir 'Content/TSTSS/Review/SliceEnemyGallery_V0.umap'
if (-not (Test-Path $BuildTool -PathType Leaf) -or
    -not (Test-Path $EditorCmd -PathType Leaf) -or
    -not (Test-Path $Runner -PathType Leaf) -or
    -not (Test-Path $Project -PathType Leaf) -or
    -not (Test-Path $VersionPath -PathType Leaf)) {
    throw 'HOLD: editor/build/script/project/version files missing'
}
$Version = Get-Content -LiteralPath $VersionPath -Raw | ConvertFrom-Json
if ($Version.MajorVersion -ne 5 -or $Version.MinorVersion -ne 8 -or
    $Version.PatchVersion -ne 4) {
    throw 'HOLD: gallery requires exact Unreal Engine 5.8.4'
}
if (Test-Path -LiteralPath $TargetMap) {
    throw 'HOLD: existing gallery map may not be overwritten'
}
$SaveDir = Join-Path $ProjectDir 'Saved/SaveGames'
if (Test-Path $SaveDir) {
    if (@(Get-ChildItem -LiteralPath $SaveDir -Filter '*.sav' -File).Count -ne 0) {
        throw 'HOLD: disposable gallery contains SaveGame files'
    }
}
$Active = @(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','LiveCodingConsole' -ErrorAction SilentlyContinue)
if ($Active.Count -gt 0) {
    throw 'HOLD: active Unreal Editor/Live Coding; leave other work untouched'
}
$FreeKiB = (Get-CimInstance Win32_OperatingSystem -ErrorAction Stop).FreePhysicalMemory
if ($null -eq $FreeKiB -or $FreeKiB -lt 5242880) {
    throw 'HOLD: require at least 5 GiB free RAM'
}
$Disk = Get-PSDrive C -ErrorAction Stop
if ($null -eq $Disk.Free -or $Disk.Free -lt (14 * 1GB)) {
    throw 'HOLD: require at least 14 GiB free C: disk'
}

# Refuse to author from a stale or merely synthetic source-only result.
$EvidenceRoot = Join-Path $ProjectDir 'Saved/MigrationEvidence'
$Receipts = @(
    Get-ChildItem -LiteralPath $EvidenceRoot -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like ($Actual.Substring(0,12) + '-*') }
)
$Built = $false
foreach ($r in $Receipts) {
    $candidate = Join-Path $r.FullName 'verified-build.json'
    $head = Join-Path $r.FullName 'head.txt'
    if (-not (Test-Path $candidate -PathType Leaf) -or
        -not (Test-Path $head -PathType Leaf)) { continue }
    $v = Get-Content $candidate -Raw | ConvertFrom-Json
    if ($v.status -eq 'WIN64_EDITOR_BUILD_PASS_CLEAN_SOURCE' -and
        $v.source_sha -eq $ExpectedHead -and
        $v.unreal_version -eq '5.8.4' -and
        (Get-Content $head -Raw).Trim() -eq $ExpectedHead) {
        $Built = $true
    }
}
if (-not $Built) {
    throw 'HOLD: exact-head verified clean Unreal Editor build receipt required'
}
if ($PreflightOnly) {
    Write-Output "ENEMY_GALLERY_PREFLIGHT_PASS_NOT_MAP_CREATED HEAD=$Actual"
    return
}
# These are inside the disposable checkout only; original attributes restored
# even on Editor failure. Never expose or allow generated Android AFS tokens.
function Digest([string]$File) {
    $stream = [IO.File]::OpenRead($File)
    try {
        $hash = [Security.Cryptography.SHA256]::Create()
        try { return [BitConverter]::ToString($hash.ComputeHash($stream)).Replace('-','') }
        finally { $hash.Dispose() }
    } finally { $stream.Dispose() }
}
$Names = @('DefaultEngine.ini','DefaultInput.ini')
$Config = @()
foreach ($name in $Names) {
    $p = Join-Path $ProjectDir ('Config/' + $name)
    $item = Get-Item -LiteralPath $p -ErrorAction Stop
    $Config += [pscustomobject]@{
        File = $p
        OriginalReadOnly = $item.IsReadOnly
        BeforeSha = Digest $p
    }
}
$OldEnv = [Environment]::GetEnvironmentVariable('TSTSS_ENEMY_GALLERY_EXPECTED_HEAD','Process')
try {
    foreach ($entry in $Config) {
        (Get-Item -LiteralPath $entry.File).IsReadOnly = $true
    }
    [Environment]::SetEnvironmentVariable('TSTSS_ENEMY_GALLERY_EXPECTED_HEAD',$ExpectedHead,'Process')
    $LogRoot = Join-Path $ProjectDir 'Saved/EnemyGalleryV0'
    if (-not (Test-Path $LogRoot)) {
        New-Item -Path $LogRoot -ItemType Directory -ErrorAction Stop | Out-Null
    }
    $Log = Join-Path $LogRoot ('editor-author-'+$ExpectedHead.Substring(0,12)+'.log')
    if (Test-Path $Log) { throw 'HOLD: review log exists; do not overwrite' }
    & $EditorCmd $Project '-run=pythonscript' "-script=$Runner" "-abslog=$Log" '-unattended' '-nop4' '-nullrhi' '-log'
    if ($LASTEXITCODE -ne 0) {
        throw "HOLD: Unreal gallery authoring failed, exit code $LASTEXITCODE"
    }
    if (-not (Test-Path $TargetMap -PathType Leaf)) {
        throw 'HOLD: editor reported success but no gallery map exists'
    }
    $Receipt = Join-Path $LogRoot 'gallery-receipt.json'
    if (-not (Test-Path $Receipt -PathType Leaf)) {
        throw 'HOLD: gallery map exists but no source-locked receipt exists'
    }
    $Proof = Get-Content $Receipt -Raw | ConvertFrom-Json
    if ($Proof.status -ne 'GALLERY_MAP_SAVED_NOT_PIE_OR_VISUAL_QA' -or
        $Proof.exact_source_sha -ne $ExpectedHead -or
        $Proof.generated_map_sha256 -ne (Digest $TargetMap).ToLowerInvariant()) {
        throw 'HOLD: gallery map receipt/head/digest mismatch'
    }
    Write-Output "ENEMY_GALLERY_MAP_SAVED_NOT_PIE_OR_ART_APPROVAL HEAD=$Actual"
} finally {
    [Environment]::SetEnvironmentVariable('TSTSS_ENEMY_GALLERY_EXPECTED_HEAD',$OldEnv,'Process')
    foreach ($entry in $Config) {
        (Get-Item -LiteralPath $entry.File).IsReadOnly = $entry.OriginalReadOnly
        if ((Digest $entry.File) -ne $entry.BeforeSha) {
            throw "HOLD: protected Unreal config was modified: $($entry.File)"
        }
    }
}
