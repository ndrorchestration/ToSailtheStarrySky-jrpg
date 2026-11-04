param(
    [Parameter(Mandatory=$true)][string]$EngineRoot,
    [Parameter(Mandatory=$true)][string]$ExpectedHead,
    [switch]$OpenEditor
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if ((Split-Path $Root -Leaf) -cne 'TSTSS_AssetAssembly_20261104') {
    throw 'HOLD: use only the isolated asset-assembly review checkout'
}
if ($ExpectedHead -notmatch '^[a-fA-F0-9]{40}$') {
    throw 'HOLD: full exact 40-character expected source SHA required'
}
$ActualHead = (& git -C $Root rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $ActualHead -cne $ExpectedHead) {
    throw 'HOLD: expected Git source head mismatch'
}
$TrackedChanges = @(& git -C $Root status --porcelain --untracked-files=no)
if ($LASTEXITCODE -ne 0 -or $TrackedChanges.Count -gt 0) {
    throw 'HOLD: tracked source changes present in asset review workspace'
}
# Native stage was run at a historical source SHA; subsequently added changes
# must be verification/docs only. Gameplay, config and UE dependencies unchanged.
$StageSourceHead = 'be9bc0e42d3cdf4f52a5c6bc3bcc8273a0d7e94d'
& git -C $Root merge-base --is-ancestor $StageSourceHead $ActualHead
if ($LASTEXITCODE -ne 0) { throw 'HOLD: native stage provenance is not an ancestor' }
$GameplayDiff = @(& git -C $Root diff --name-only $StageSourceHead $ActualHead -- 'unreal/Source' 'unreal/Config' 'unreal/ToSailTheStarrySky.uproject' 'unreal/Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap')
if ($LASTEXITCODE -ne 0 -or $GameplayDiff.Count -gt 0) {
    throw 'HOLD: gameplay/config/engine files changed after native stage'
}
$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Project = Join-Path $ProjectDir 'ToSailTheStarrySky.uproject'
$Editor = Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor.exe'
$Version = Get-Content (Join-Path $EngineRoot 'Engine/Build/Build.version') -Raw | ConvertFrom-Json
if ($Version.MajorVersion -ne 5 -or $Version.MinorVersion -ne 8 -or $Version.PatchVersion -ne 4 -or
    -not (Test-Path -LiteralPath $Editor -PathType Leaf)) {
    throw 'HOLD: Unreal Editor 5.8.4 required'
}
function Get-Sha256([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "HOLD: missing file $Path" }
    $Stream = [IO.File]::OpenRead($Path)
    $Hasher = [Security.Cryptography.SHA256]::Create()
    try {
        return [BitConverter]::ToString($Hasher.ComputeHash($Stream)).Replace('-','').ToLowerInvariant()
    } finally {
        $Stream.Dispose()
        $Hasher.Dispose()
    }
}
$Map = '/Game/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3'
$MapFile = Join-Path $ProjectDir 'Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3.umap'
$MapHash = '54b4e266683347fc950a56c8ac8691d99aaddb41d61e304ddf0f5b4d0730e2b5'
$BaseFile = Join-Path $ProjectDir 'Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap'
$BaseHash = '4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80'
if ((Get-Sha256 $MapFile) -cne $MapHash -or (Get-Sha256 $BaseFile) -cne $BaseHash) {
    throw 'HOLD: new asset scene or original First Wake V2 map digest changed'
}
$EvidenceDir = Join-Path $ProjectDir 'Saved/AssetAssemblyEvidence'
$Stage = Get-Content (Join-Path $EvidenceDir 'first_wake_asset_scene_native_v3_20261104.json') -Raw | ConvertFrom-Json
$Readback = Get-Content (Join-Path $EvidenceDir 'first_wake_asset_scene_readback_v3_20261104.json') -Raw | ConvertFrom-Json
$StageHost = Get-Content (Join-Path $EvidenceDir 'host_asset_stage_v3_20261104.json') -Raw | ConvertFrom-Json
if ($Stage.status -cne 'NATIVE_ASSET_WORLD_SAVED_PENDING_INDEPENDENT_READBACK' -or
    $Readback.status -cne 'INDEPENDENT_NATIVE_SAVED_WORLD_READBACK_PASS_NOT_PIE' -or
    $Readback.map_sha256 -cne $MapHash -or $Stage.new_map_sha256 -cne $MapHash -or
    $Readback.imported_asset_actor_count -ne 10 -or $Readback.milestone_count -ne 7 -or
    $Readback.player_start_count -ne 1 -or $StageHost.editor_exit_code -ne 0 -or
    $StageHost.source_head -cne $StageSourceHead) {
    throw 'HOLD: source-locked native stage and independent map readback evidence incomplete'
}
foreach ($Pair in $StageHost.native_asset_sha256.PSObject.Properties) {
    $Path = Join-Path (Join-Path $ProjectDir 'Content') $Pair.Name
    if ((Get-Sha256 $Path) -cne $Pair.Value) {
        throw 'HOLD: imported native review asset digest changed'
    }
}
if (@(Get-ChildItem (Join-Path $ProjectDir 'Saved/SaveGames') -Filter '*.sav' -File -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'HOLD: protected existing review saves; do not overwrite or delete'
}
if (@(Get-Process UnrealEditor,UnrealEditor-Cmd,LiveCodingConsole -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'HOLD: another Unreal Editor or Live Coding process active'
}
$FreeKiB = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
if ($FreeKiB -lt 6815744) { throw 'HOLD: below 6.5 GiB free RAM graphical review gate' }
if ((Get-PSDrive -Name C).Free -lt 14GB) {
    throw 'HOLD: below 14 GiB free disk for graphical review'
}
$Protected = @()
foreach ($Name in @('DefaultEngine.ini','DefaultInput.ini')) {
    $Path = Join-Path $ProjectDir ('Config/' + $Name)
    $File = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($File.IsReadOnly) { throw 'HOLD: config already read-only; no ownership assumed' }
    $Protected += [pscustomobject]@{Path=$Path;Hash=(Get-Sha256 $Path)}
}
foreach ($Path in @($MapFile,$BaseFile)) {
    $File = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($File.IsReadOnly) { throw 'HOLD: review map already read-only; no ownership assumed' }
    $Protected += [pscustomobject]@{Path=$Path;Hash=(Get-Sha256 $Path)}
}
Write-Output "FIRST_WAKE_ASSET_REVIEW_PREFLIGHT_PASS HEAD=$ActualHead MAP=$Map"
Write-Output 'Review-only art. Native map is saved/read back; this does not certify gameplay, cinematic assets or ship physics.'
Write-Output 'Press Play in Editor, then test WASD/mouse, E, J, F5/F9 in a protected disposable save workspace.'
if (-not $OpenEditor) { return }
try {
    foreach ($Item in $Protected) { (Get-Item -LiteralPath $Item.Path).IsReadOnly = $true }
    $Arguments = @(('"{0}"' -f $Project), $Map, '-d3d11', '-log')
    $Process = Start-Process -FilePath $Editor -ArgumentList $Arguments -PassThru
    Write-Output "FIRST_WAKE_ASSET_REVIEW_EDITOR_STARTED PID=$($Process.Id); gameplay not yet verified"
    $Process.WaitForExit()
    if ($Process.ExitCode -ne 0) { throw "Editor exited with code $($Process.ExitCode)" }
} finally {
    foreach ($Item in $Protected) { (Get-Item -LiteralPath $Item.Path).IsReadOnly = $false }
}
foreach ($Item in $Protected) {
    if ((Get-Sha256 $Item.Path) -cne $Item.Hash) {
        throw 'HOLD: tracked config or review map changed during graphical Editor session'
    }
}
if ((& git -C $Root rev-parse HEAD).Trim() -cne $ActualHead -or
    @(& git -C $Root status --porcelain --untracked-files=no).Count -gt 0) {
    throw 'HOLD: tracked Git source changed during graphical review'
}
Write-Output 'Editor closed without tracked/map changes. This remains review-only; actual PIE acceptance must be documented separately.'
