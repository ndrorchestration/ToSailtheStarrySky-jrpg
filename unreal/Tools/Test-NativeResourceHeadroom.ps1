# Read-only, optional resource preflight for an isolated Unreal 5.8.4 review.
# Conservative thresholds are review policy, NOT Unreal hardware minimums.
param(
    [string]$Checkout = (Get-Location).Path,
    [double]$MinFreeDiskGiB = 25,
    [double]$MinFreeRamGiB = 6,
    [switch]$SelfTest
)
$ErrorActionPreference = 'Stop'
function Test-ResourceThreshold {
    param([double]$DiskGiB,[double]$RamGiB,[double]$NeedDiskGiB,[double]$NeedRamGiB)
    if ($DiskGiB -lt 0 -or $RamGiB -lt 0 -or $NeedDiskGiB -lt 0 -or $NeedRamGiB -lt 0) {
        throw 'Resource values and thresholds must be nonnegative'
    }
    return ($DiskGiB -ge $NeedDiskGiB -and $RamGiB -ge $NeedRamGiB)
}
if ($SelfTest) {
    $cases = @(
        @{disk=25;ram=6;expected=$true},
        @{disk=24.99;ram=6;expected=$false},
        @{disk=25;ram=5.99;expected=$false},
        @{disk=25;ram=6.01;expected=$true},
        @{disk=0;ram=0;expected=$false}
    )
    foreach ($case in $cases) {
        $got = Test-ResourceThreshold -DiskGiB $case.disk -RamGiB $case.ram -NeedDiskGiB 25 -NeedRamGiB 6
        if ($got -ne $case.expected) { throw "Resource fixture failed: $($case | Out-String)" }
    }
    try {
        [void](Test-ResourceThreshold -DiskGiB -1 -RamGiB 7 -NeedDiskGiB 25 -NeedRamGiB 6)
        throw 'Negative-resource fixture failed'
    } catch {
        if ($_.Exception.Message -notlike 'Resource values*') { throw }
    }
    Write-Output 'PASS: 6 deterministic resource-gate cases; no build or filesystem edits'
    exit 0
}
if ($MinFreeDiskGiB -lt 0 -or $MinFreeRamGiB -lt 0) { throw 'Thresholds must be nonnegative' }
if (-not (Test-Path -LiteralPath $Checkout -PathType Container)) { throw "Checkout path not found: $Checkout" }
$root = [IO.Path]::GetPathRoot([IO.Path]::GetFullPath($Checkout))
$drive = [IO.DriveInfo]::new($root)
$diskGiB = $drive.AvailableFreeSpace / 1GB
$os = Get-CimInstance -ClassName Win32_OperatingSystem
if (-not $os) { throw 'Cannot read available physical RAM' }
$ramGiB = ([double]$os.FreePhysicalMemory * 1KB) / 1GB
$accepted = Test-ResourceThreshold -DiskGiB $diskGiB -RamGiB $ramGiB -NeedDiskGiB $MinFreeDiskGiB -NeedRamGiB $MinFreeRamGiB
$state = if ($accepted) { 'READY_FOR_MANUAL_NATIVE_REVIEW' } else { 'HOLD_RESOURCE_HEADROOM' }
Write-Output ('Resource preflight: {0}; checkout={1}; freeDiskGiB={2:N2}; freeRamGiB={3:N2}; policyDiskGiB={4:N2}; policyRamGiB={5:N2}' -f $state, $Checkout, $diskGiB, $ramGiB, $MinFreeDiskGiB, $MinFreeRamGiB)
Write-Output 'This probe does not launch Unreal or grant build, PIE, art, or release approval.'
if (-not $accepted) { exit 2 }
exit 0
