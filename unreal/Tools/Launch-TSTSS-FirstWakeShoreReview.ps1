param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [switch]$PrintOnly
)
$ErrorActionPreference = 'Stop'
$Project = (Resolve-Path (Join-Path $PSScriptRoot '..\ToSailTheStarrySky.uproject')).Path
$Editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
if (-not (Test-Path $Editor -PathType Leaf)) { throw 'UnrealEditor.exe not found' }
$Version = Get-Content (Join-Path $EngineRoot 'Engine\Build\Build.version') -Raw | ConvertFrom-Json
if ("$($Version.MajorVersion).$($Version.MinorVersion).$($Version.PatchVersion)" -ne '5.8.4') {
    throw 'Review route requires Unreal 5.8.4'
}
$Level = '/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2'
$MapFolder = Join-Path (Split-Path $Project) 'Content\TSTSS\Review'
foreach ($Map in @(
    'VerticalSlice\VS03_FirstWakeSky.umap',
    'VerticalSlice\VS04_SplashdownSea.umap',
    'VerticalSlice\VS05_DenithFuelShanty.umap',
    'MultipathV1\L_VS06_ShoreMagicEnemyGear_Review.umap'
)) {
    if (-not (Test-Path (Join-Path $MapFolder $Map) -PathType Leaf)) {
        throw "Required native review map missing: $Map"
    }
}
$LaunchArguments = @(
    ('"{0}"' -f $Project),
    ('"{0}?game=/Script/ToSailTheStarrySky.TSTSSOpeningReviewMode"' -f $Level),
    '-game', '-windowed', '-ResX=1280', '-ResY=720', '-log'
)
if ($PrintOnly) {
    Write-Output 'Review route: title -> First Wake engineering -> K sky -> K physical sea -> K fuel shanty -> E reserves -> K shoreline'
    Write-Output 'Executable: UnrealEditor.exe (UE 5.8.4); four scene maps verified'
    Write-Output 'Source checks only: no native PIE, gameplay or visual acceptance claimed.'
    exit 0
}
if (@(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','LiveCodingConsole' -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'Another Unreal editor session is active: no launch'
}
$FreeKiB = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
$FreeDisk = (Get-PSDrive C).Free
if ($FreeKiB -lt 6815744 -or $FreeDisk -lt (14 * 1GB)) {
    throw 'Insufficient resources for interactive review: need 6.5 GiB RAM and 14 GiB C: free'
}
Write-Output 'Opening review-only First Wake; native gameplay and art quality unapproved.'
Start-Process -FilePath $Editor -ArgumentList $LaunchArguments -WorkingDirectory (Split-Path $Project)
