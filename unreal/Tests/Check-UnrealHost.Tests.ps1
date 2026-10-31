# Standalone Windows PowerShell version-gate regression; no UE installation needed.
$ErrorActionPreference = 'Stop'
$Gate = Join-Path $PSScriptRoot '..\Tools\Check-UnrealHost.ps1'
$Temp = Join-Path ([IO.Path]::GetTempPath()) ('TSTSS_UERunGate_' + [Guid]::NewGuid().ToString('N'))
$EngineFolder = Join-Path $Temp 'FakeEngine'
$BuildFolder = Join-Path $EngineFolder 'Engine\Build'
$BatchFolder = Join-Path $BuildFolder 'BatchFiles'
$BinFolder = Join-Path $EngineFolder 'Engine\Binaries\Win64'
try {
    New-Item -ItemType Directory -Force -Path $BatchFolder,$BinFolder | Out-Null
    foreach ($File in @((Join-Path $BatchFolder 'Build.bat'),
                        (Join-Path $BinFolder 'UnrealEditor.exe'),
                        (Join-Path $BinFolder 'UnrealEditor-Cmd.exe'))) {
        Set-Content -LiteralPath $File -Value 'FAKE VERSION TEST ONLY'
    }
    $VersionPath = Join-Path $BuildFolder 'Build.version'
    $Cases = @(
        @{ Name = 'old 5.7'; Major = 5; Minor = 7; Patch = 9; Valid = $false },
        @{ Name = 'old 5.8.3'; Major = 5; Minor = 8; Patch = 3; Valid = $false },
        @{ Name = 'current 5.8.4'; Major = 5; Minor = 8; Patch = 4; Valid = $true },
        @{ Name = 'future 5.8.6'; Major = 5; Minor = 8; Patch = 6; Valid = $true },
        @{ Name = 'other 6.0'; Major = 6; Minor = 0; Patch = 0; Valid = $false }
    )
    $Count = 0
    foreach ($Case in $Cases) {
        $Json = @{ MajorVersion = $Case.Major; MinorVersion = $Case.Minor; PatchVersion = $Case.Patch } |
            ConvertTo-Json -Compress
        Set-Content -LiteralPath $VersionPath -Value $Json
        $Result = (& $Gate -EngineRoot $EngineFolder) | Out-String | ConvertFrom-Json
        if ([bool]$Result.engine_version_manifest_valid -ne $Case.Valid) {
            throw ("Case {0} failed: {1}" -f $Case.Name,($Result | ConvertTo-Json -Compress))
        }
        if ($Result.ready_for_native_build_attempt) {
            throw "Fake engine was incorrectly classified as a real build-ready machine"
        }
        $Count++
    }
    Set-Content -LiteralPath $VersionPath -Value 'invalid json'
    $Bad = (& $Gate -EngineRoot $EngineFolder) | Out-String | ConvertFrom-Json
    if ($Bad.engine_version_manifest_valid -or -not $Bad.version_error) {
        throw 'Corrupt Build.version was not rejected'
    }
    $Count++
    $Strict = (& $Gate -EngineRoot $EngineFolder -RequireReady) | Out-String | ConvertFrom-Json
    if ($LASTEXITCODE -ne 2 -or $Strict.ready_for_native_build_attempt) {
        throw "Strict native gate failed to hold; exit code was $LASTEXITCODE"
    }
    $Count++
    Write-Output "PASS: $Count Windows PowerShell engine-version and strict HOLD cases"
    # The deliberate -RequireReady rejection sets LASTEXITCODE=2; clear it only
    # after every asserted case completed. Real failures still throw above.
    $global:LASTEXITCODE = 0
} finally {
    if (Test-Path -LiteralPath $Temp) {
        Remove-Item -LiteralPath $Temp -Force -Recurse
    }
}
