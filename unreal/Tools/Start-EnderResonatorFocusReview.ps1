# Native UE5.8.4 review-only focus arena launcher. No other process is killed.
# Requires explicit full source SHA, pristine worktree, 6 pinned asset hashes,
# no other editor/LiveCoding and sufficient RAM/disk. Does NOT assert PIE pass.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-fA-F]{40}$')][string]$ExpectedHead,
    [ValidateRange(640,3840)][int]$Width=1280,
    [ValidateRange(480,2160)][int]$Height=720,
    [string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8',
    [switch]$IntegratedReview,
    [switch]$CheckAssetsOnly
)
$ErrorActionPreference='Stop'
# Authenticated NEONTIC PowerShell 5.1 hosts may omit Get-FileHash.
# Use the same SHA-256 cryptographic algorithm with strict disposal and no bypass.
function Get-TSTSSFocusSHA256([string]$LiteralPath) {
    $Resolved = (Resolve-Path -LiteralPath $LiteralPath -ErrorAction Stop).Path
    $Stream = [System.IO.File]::Open($Resolved,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::Read)
    try {
        $Hasher = [System.Security.Cryptography.SHA256]::Create()
        if ($null -eq $Hasher) { throw 'HOLD: SHA-256 provider unavailable' }
        try {
            $Digest = $Hasher.ComputeHash($Stream)
        } finally {
            $Hasher.Dispose()
        }
        if ($null -eq $Digest -or $Digest.Length -ne 32) {
            throw 'HOLD: invalid asset SHA-256 result'
        }
        return [System.BitConverter]::ToString($Digest).Replace('-','').ToLowerInvariant()
    } finally {
        $Stream.Dispose()
    }
}
$Root=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Project=Join-Path $Root 'unreal'
$ProjectFile=Join-Path $Project 'ToSailTheStarrySky.uproject'
$Executable=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$Version=Join-Path $EngineRoot 'Engine\Build\Build.version'
$ManifestPath=Join-Path $Project 'Docs\Evidence\ender_resonator_focus_native_assets_20261111.json'
# The legacy isolated review is implicit; the joined First Wake checkout requires
# explicit opt-in. Neither case relaxes source SHA or six native asset hashes.
$WorktreeName=Split-Path $Root -Leaf
$DedicatedReview=$WorktreeName -eq 'TSTSS_CenteringPulse_20261111'
$JoinedReview=$WorktreeName -eq 'TSTSS_838_EngineRoomRoute_20261114'
if (($DedicatedReview -and $IntegratedReview) -or
    (-not $DedicatedReview -and -not ($JoinedReview -and $IntegratedReview))) {
    throw 'HOLD: wrong review worktree or missing explicit integration opt-in'
}
if (!(Test-Path -LiteralPath $Executable -PathType Leaf) -or
    !(Test-Path -LiteralPath $Version -PathType Leaf) -or
    !(Test-Path -LiteralPath $ProjectFile -PathType Leaf)) {
    throw 'HOLD: project or engine executable not installed'
}
$Release=Get-Content -LiteralPath $Version -Raw | ConvertFrom-Json
if ($Release.MajorVersion -ne 5 -or $Release.MinorVersion -ne 8 -or $Release.PatchVersion -ne 4) {
    throw 'HOLD: requires Unreal Engine 5.8.4'
}
$Head=(git -C $Root rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $Head -ne $ExpectedHead.ToLowerInvariant()) {
    throw 'HOLD: source HEAD differs from the explicitly requested review commit'
}
$Changed=@(git -C $Root status --porcelain -uall)
if ($LASTEXITCODE -ne 0 -or $Changed.Count -gt 0) {
    throw 'HOLD: dirty source or review assets'
}
$Manifest=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if ($Manifest.schema -ne 'tstss.resonator-focus-native-review.v1' -or
    $Manifest.unreal_version -ne '5.8.4' -or
    $Manifest.other_magic_status -ne 'DesignOnly / Correspondence ON HOLD' -or
    $Manifest.executable_spells.Count -ne 2 -or
    $Manifest.executable_spells[0] -ne 'Ender_Centering' -or
    $Manifest.executable_spells[1] -ne 'Ender_ResonantPulse') {
    throw 'HOLD: review spell admission manifest drift'
}
git -C $Root merge-base --is-ancestor $Manifest.asset_commit $ExpectedHead | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw 'HOLD: pinned asset commit not in source history'
}
$Required=@(
    'L_EnderCenteringPulseReview.umap',
    'DT_EnderResonatorFocusReview.uasset',
    'Audio/SFX_Centering.uasset',
    'Audio/SFX_ResonantPulse.uasset',
    'AudioSource/SFX_Centering.wav',
    'AudioSource/SFX_ResonantPulse.wav'
)
$Native=@($Manifest.assets.PSObject.Properties | ForEach-Object {$_.Name})
$Audio=@($Manifest.source_wav.PSObject.Properties | ForEach-Object {$_.Name})
$Actual=$Native+$Audio
if ($Actual.Count -ne 6 -or @(Compare-Object $Required $Actual).Count -gt 0) {
    throw 'HOLD: native/audio asset inventory drift'
}
foreach ($Relative in $Required) {
    $Path=Join-Path $Project ('Content\TSTSS\Review\ResonatorFocus\' + $Relative)
    if (!(Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw ('HOLD: missing native asset '+$Relative)
    }
    if ($Relative -in $Native) {
        $Digest=$Manifest.assets.$Relative
    } else {
        $Digest=$Manifest.source_wav.$Relative
    }
    if ((Get-TSTSSFocusSHA256 -LiteralPath $Path) -ne $Digest) {
        throw ('HOLD: file hash changed '+$Relative)
    }
}
# Source and six hashed asset custody can be confirmed safely while a different
# Editor is active. This stops here: native/process/memory/play gates NOT checked.
if ($CheckAssetsOnly) {
    Write-Output 'TSTSS_FOCUS_ASSET_CUSTODY_PASS: exact source, UE version, manifest, six SHA256 hashes'
    Write-Output 'NO_EDITOR_LAUNCHED; NATIVE_PROCESS_RAM_PIE_GPU_AUDIO_NOT_TESTED'
    return
}
$Use=@(Get-Process UnrealEditor,UnrealEditor-Cmd,LiveCodingConsole -ErrorAction SilentlyContinue | Where-Object {$_})
if ($Use.Count -gt 0) {
    throw ('HOLD: another Unreal/LiveCoding session is active, no interference. ' +
        (($Use | ForEach-Object {$_.ProcessName+':'+$_.Id}) -join ', '))
}
$Memory=Get-CimInstance Win32_OperatingSystem
$Disk=Get-PSDrive -Name C
if ($Memory.FreePhysicalMemory -lt 6815744 -or $Disk.Free -lt 14GB) {
    throw 'HOLD: need >=6.5 GiB free RAM and >=14 GiB free disk'
}
$Map=$Manifest.map_package
if ($Map -ne '/Game/TSTSS/Review/ResonatorFocus/L_EnderCenteringPulseReview') {
    throw 'HOLD: invalid review map'
}
$LogDir=Join-Path $Project 'Saved\ResonatorFocus'
if (!(Test-Path -LiteralPath $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
$Record=Join-Path $LogDir ('focus-launch-'+$Head.Substring(0,12)+'-'+[guid]::NewGuid().ToString('N')+'.json')
$Parameters=@(
    ('"'+$ProjectFile+'"'),$Map,'-game','-windowed',("-ResX=$Width"),("-ResY=$Height"),
    '-NoSplash','-NoVSync','-log'
)
$Run=Start-Process -FilePath $Executable -ArgumentList $Parameters -WorkingDirectory $Project -PassThru -ErrorAction Stop
$Receipt=[ordered]@{
    status='REVIEW_WINDOW_LAUNCHED_NOT_PLAY_VERIFIED'
    source_sha=$Head
    process_id=$Run.Id
    map=$Map
    engine='5.8.4'
    player_keyboard='NOT_VERIFIED'
    speaker_audio='NOT_VERIFIED'
    gpu_visual='NOT_VERIFIED'
    campaign_integration='NOT_VERIFIED'
    created_at=(Get-Date).ToString('o')
}
$Receipt | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $Record -Encoding UTF8 -NoNewline
Write-Output "Review-only Unreal window launched, PID $($Run.Id)."
Write-Output 'Controls: 1 = Centering (5 MP, 3 rounds); 2 = Resonant Pulse (3 MP).'
Write-Output 'No GPU, speaker, or keyboard acceptance is claimed until witnessed.'
Write-Output "Launch receipt: $Record"
