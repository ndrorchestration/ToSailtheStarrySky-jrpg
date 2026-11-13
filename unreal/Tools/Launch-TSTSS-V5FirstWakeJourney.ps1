param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [string]$ExpectedHead = '',
    [switch]$PrintOnly
)
# Review-only, non-destructive. Never merge, rewrite maps, save data or project defaults.
$ErrorActionPreference = 'Stop'
# Fail-closed receipt hashing without relying on Get-FileHash command registration.
# Some authenticated Neontic PowerShell hosts omit that otherwise standard cmdlet.
function Get-TSTSSReviewSHA256([string]$LiteralPath) {
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
            throw 'HOLD: invalid native report SHA-256'
        }
        return [System.BitConverter]::ToString($Digest).Replace('-', '').ToLowerInvariant()
    } finally {
        $Stream.Dispose()
    }
}
$Repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Project = Join-Path $Repo 'unreal\ToSailTheStarrySky.uproject'
$Editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$TitlePackage = '/Game/TSTSS/Review/Opening/L_FirstWake_TitleReview'
$TitleMode = '/Script/ToSailTheStarrySky.TSTSSOpeningReviewMode'
$RequiredMaps = @(
    'Opening\L_FirstWake_TitleReview.umap',
    'FirstWake_PreludeInteraction_V5_VisualReview.umap',
    'VerticalSlice\VS02_AureateInteriors.umap',
    'VerticalSlice\VS03_FirstWakeSky.umap',
    'VerticalSlice\VS04_SplashdownSea.umap',
    'VerticalSlice\VS05_DenithFuelShanty.umap',
    'MultipathV1\L_VS06_ShoreMagicEnemyGear_Review.umap'
)
function Git-Read([string[]]$GitArgs) {
    $Out = & git -C $Repo @GitArgs
    if ($LASTEXITCODE -ne 0) { throw 'HOLD: Git custody unavailable' }
    return ($Out | Out-String).Trim()
}
if (-not (Test-Path -LiteralPath $Project -PathType Leaf) -or
    -not (Test-Path -LiteralPath $Editor -PathType Leaf)) {
    throw 'HOLD: project or installed Unreal Editor missing'
}
$BuildVersion = Get-Content (Join-Path $EngineRoot 'Engine\Build\Build.version') -Raw | ConvertFrom-Json
if (('{0}.{1}.{2}' -f $BuildVersion.MajorVersion, $BuildVersion.MinorVersion, $BuildVersion.PatchVersion) -ne '5.8.4') {
    throw 'HOLD: UE 5.8.4 required'
}
if ([IO.Path]::GetFullPath((Git-Read -GitArgs @('rev-parse','--show-toplevel'))).TrimEnd('\') -ine
    [IO.Path]::GetFullPath($Repo).TrimEnd('\')) {
    throw 'HOLD: active repository root mismatch'
}
$Branch = Git-Read -GitArgs @('branch','--show-current')
$Head = Git-Read -GitArgs @('rev-parse','HEAD')
if (-not $Branch.StartsWith('review/') -or $Head -notmatch '^[0-9a-fA-F]{40}$' -or
    ($ExpectedHead -ne '' -and
        ($ExpectedHead -notmatch '^[0-9a-fA-F]{40}$' -or $Head -ine $ExpectedHead))) {
    throw 'HOLD: require an isolated review branch and exact source HEAD'
}
if (Git-Read -GitArgs @('status','--porcelain','-uall')) {
    throw 'HOLD: source worktree must be clean'
}
$MapFolder = Join-Path $Repo 'unreal\Content\TSTSS\Review'
foreach ($Map in $RequiredMaps) {
    if (-not (Test-Path -LiteralPath (Join-Path $MapFolder $Map) -PathType Leaf)) {
        throw "HOLD: required saved review map missing: $Map"
    }
}
# New Game must open the V5 interactive map; V2 and VS01 remain review history.
$Widget = Get-Content -LiteralPath (Join-Path $Repo 'unreal\Source\ToSailTheStarrySky\Private\TSTSSOpeningReviewWidget.cpp') -Raw
$EngineIni = Get-Content -LiteralPath (Join-Path $Repo 'unreal\Config\DefaultEngine.ini') -Raw
if (-not $Widget.Contains('/Game/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview') -or
    -not $Widget.Contains('UGameplayStatics::OpenLevel(Controller, FName(*PreludeMap))') -or
    -not $EngineIni.Contains('GlobalDefaultGameMode=/Script/ToSailTheStarrySky.TSTSSGameMode')) {
    throw 'HOLD: title New Game or subsequent Explorer GameMode contract drifted'
}
if ($PrintOnly) {
    Write-Output "SOURCE PLAN: New Game -> V5 seven E markers -> K Aureate interior -> K sky -> K physical sea -> E fuel -> K shore"
    Write-Output "Review HEAD: $Branch / $Head; all seven review map assets present"
    Write-Output 'No Unreal process started. Actual launch requires same-head full 38-native-test receipt and resource checks.'
    exit 0
}

# A parent PR's two native tests cannot authorize a newer source revision.
$Verifier = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'Verify-Unreal.ps1') -Raw
$Names = @([regex]::Matches($Verifier, "(?m)^\s*'(TSTSS\.[^']+)'") |
    ForEach-Object { $_.Groups[1].Value })
if ($Names.Count -ne 38 -or @($Names | Select-Object -Unique).Count -ne 38) {
    throw 'HOLD: live verifier requires 38 distinct native tests'
}
$Evidence = Join-Path $Repo 'unreal\Saved\MigrationEvidence'
if (-not (Test-Path -LiteralPath $Evidence -PathType Container)) {
    throw 'HOLD: no exact-head native build and automation evidence'
}
. (Join-Path $PSScriptRoot 'Assert-NativeAutomationReport.ps1')
$NativeAccepted = $false
foreach ($File in @(Get-ChildItem -LiteralPath $Evidence -Filter 'verified-native.json' -File -Recurse)) {
    try {
        $Receipt = Get-Content -LiteralPath $File.FullName -Raw | ConvertFrom-Json
        $ReportPath = Join-Path $File.DirectoryName 'AutomationReport\index.json'
        $HeadPath = Join-Path $File.DirectoryName 'head.txt'
        if ($Receipt.status -ne 'WIN64_EDITOR_BUILD_AND_NATIVE_AUTOMATIONS_PASS_CLEAN_SOURCE' -or
            $Receipt.source_sha -ine $Head -or $Receipt.unreal_version -ne '5.8.4' -or
            $Receipt.required_native_tests -ne 38 -or
            $Receipt.pie_player_input -ne 'NOT_TESTED' -or
            $Receipt.visual_approval -ne 'NOT_TESTED' -or
            -not (Test-Path -LiteralPath $HeadPath -PathType Leaf) -or
            -not (Test-Path -LiteralPath $ReportPath -PathType Leaf) -or
            (Get-Content -LiteralPath $HeadPath -Raw).Trim() -ine $Head -or
            (Get-TSTSSReviewSHA256 -LiteralPath $ReportPath) -ne $Receipt.report_sha256) {
            continue
        }
        $Check = Assert-TSTSSNativeAutomationReport -ReportPath $ReportPath -RequiredTests $Names
        if ($Check.Status -eq 'REPORTED_NATIVE_AUTOMATIONS_SUCCESS' -and $Check.RequiredTests -eq 38) {
            $NativeAccepted = $true
            break
        }
    } catch {
        # Malformed or stale evidence stays untouched and never grants admission.
        continue
    }
}
if (-not $NativeAccepted) { throw 'HOLD: no matching full 38-test native receipt at this source HEAD' }

# Do not interrupt simultaneous UE development work or bypass resource minimums.
$OtherEditors = @(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','LiveCodingConsole' -ErrorAction SilentlyContinue)
if ($OtherEditors.Count -gt 0) { throw 'HOLD: another Editor or Live Coding session is active' }
$OtherBuilds = @(Get-CimInstance Win32_Process -Filter "Name='cmd.exe' OR Name='dotnet.exe' OR Name='UnrealBuildTool.exe'" -ErrorAction Stop |
    Where-Object { $_.CommandLine -match '(?i)(?:UnrealBuildTool(?:\.dll|\.exe)?|[\\/]Build\.bat)' })
if ($OtherBuilds.Count -gt 0) { throw 'HOLD: another UnrealBuildTool build is active' }
$FreeKiB = (Get-CimInstance Win32_OperatingSystem -ErrorAction Stop).FreePhysicalMemory
$Disk = Get-PSDrive -Name C -ErrorAction Stop
if ($null -eq $FreeKiB -or $FreeKiB -lt 6815744 -or
    $null -eq $Disk.Free -or $Disk.Free -lt (14 * 1GB)) {
    throw 'HOLD: require 6.5 GiB free RAM and 14 GiB free C: disk'
}
if ((Git-Read -GitArgs @('rev-parse','HEAD')) -ine $Head -or
    (Git-Read -GitArgs @('status','--porcelain','-uall'))) {
    throw 'HOLD: source changed before native launch'
}

$TitleURL = $TitlePackage + '?game=' + $TitleMode
$Arguments = @(
    ('"{0}"' -f $Project),
    ('"{0}"' -f $TitleURL),
    '-game', '-windowed', '-ResX=1280', '-ResY=720', '-log'
)
Write-Output "Launching First Wake V5 title at exact HEAD $Head; no gameplay or visual acceptance implied."
$Child = Start-Process -FilePath $Editor -ArgumentList $Arguments -WorkingDirectory (Split-Path $Project) -PassThru
Write-Output "Native review launched, process ID $($Child.Id); launcher made no save or asset changes."
