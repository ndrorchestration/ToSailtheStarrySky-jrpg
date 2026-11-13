# Pure report validation for source-locked Unreal 5.8.4 automation evidence.
# Must not launch the Editor, create/delete report files or set release status.
# Dot-source this function from Verify-Unreal.ps1; synthetic CI fixtures reuse it.
function Assert-TSTSSNativeAutomationReport {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$ReportPath,
        [Parameter(Mandatory=$true)][string[]]$RequiredTests
    )
    if ($RequiredTests.Count -ne 38 -or @($RequiredTests | Select-Object -Unique).Count -ne 38) {
        throw "Expected exactly 38 unique required native test names"
    }
    if (-not (Test-Path -LiteralPath $ReportPath -PathType Leaf)) {
        throw "No automation JSON evidence; refusing to mark PASS"
    }
    try {
        $Report = Get-Content -LiteralPath $ReportPath -Raw -ErrorAction Stop |
            ConvertFrom-Json -ErrorAction Stop
    } catch {
        throw "Invalid automation JSON evidence; cannot claim PASS: $_"
    }
    if ($null -eq $Report -or $Report -isnot [pscustomobject]) {
        throw "Automation report root must be a JSON object"
    }
    foreach ($field in @('succeeded','failed','notRun')) {
        $property = $Report.PSObject.Properties[$field]
        if ($null -eq $property -or $null -eq $property.Value -or
            ($property.Value -isnot [int] -and $property.Value -isnot [long]) -or
            $property.Value -lt 0) {
            throw "Automation report invalid non-negative integer summary: $field"
        }
    }
    if ($Report.failed -ne 0 -or $Report.notRun -ne 0) {
        throw "Automation evidence incomplete: succeeded=$($Report.succeeded), failed=$($Report.failed), notRun=$($Report.notRun)"
    }
    if ($Report.succeeded -lt $RequiredTests.Count) {
        throw "Automation success count $($Report.succeeded) is below required test count $($RequiredTests.Count)"
    }
    $testsProperty = $Report.PSObject.Properties['tests']
    if ($null -eq $testsProperty -or $null -eq $testsProperty.Value -or
        $testsProperty.Value -isnot [array]) {
        throw "No per-test automation evidence; refusing aggregate-only PASS"
    }
    $Entries = @($testsProperty.Value)
    if ($Entries.Count -lt $RequiredTests.Count) {
        throw "Insufficient per-test automation evidence; refusing aggregate-only PASS"
    }
    $TestPaths = @{}
    $SuccessCount = 0
    foreach ($Entry in $Entries) {
        if ($null -eq $Entry -or $Entry -isnot [pscustomobject] -or
            $Entry.fullTestPath -isnot [string] -or
            [string]::IsNullOrWhiteSpace($Entry.fullTestPath) -or
            $Entry.state -isnot [string]) {
            throw "Invalid per-test entry schema; refusing native PASS"
        }
        if ($TestPaths.ContainsKey($Entry.fullTestPath)) {
            throw "Duplicate test path in native automation JSON: $($Entry.fullTestPath)"
        }
        $TestPaths[$Entry.fullTestPath] = $Entry.state
        if ($Entry.state -eq 'Success') {
            $SuccessCount++
        } else {
            throw "Native automation entry not successful: $($Entry.fullTestPath) ($($Entry.state))"
        }
    }
    if ($Report.succeeded -ne $SuccessCount) {
        throw "Native automation summary and per-test successes disagree: $($Report.succeeded) vs $SuccessCount"
    }
    foreach ($TestName in $RequiredTests) {
        if (-not $TestPaths.ContainsKey($TestName)) {
            throw "Required test missing from native automation JSON: $TestName"
        }
        if ($TestPaths[$TestName] -ne 'Success') {
            throw "Required test is not successful: $TestName"
        }
    }
    # Only an evidence check. Neither caller nor this function may infer PIE or art.
    [pscustomobject]@{
        Status = 'REPORTED_NATIVE_AUTOMATIONS_SUCCESS'
        RequiredTests = $RequiredTests.Count
        ReportedSuccesses = $SuccessCount
        GameplayPIE = 'NOT_TESTED_BY_THIS_CHECK'
    }
}
