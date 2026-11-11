# Synthetic, isolated replay of the native automation JSON acceptance rules.
# Uses the actual 30 names in Verify-Unreal.ps1, without launching Unreal.
$ErrorActionPreference = 'Stop'
$ToolDir = $PSScriptRoot
. (Join-Path $ToolDir 'Assert-NativeAutomationReport.ps1')
$VerifierSource = Get-Content -LiteralPath (Join-Path $ToolDir 'Verify-Unreal.ps1') -Raw
$NameMatches = [regex]::Matches($VerifierSource, "'(TSTSS\.[^']+)'")
$Required = @($NameMatches | ForEach-Object { $_.Groups[1].Value })
if ($Required.Count -ne 30 -or @($Required | Select-Object -Unique).Count -ne 30) {
    throw "Synthetic test cannot identify exactly 30 unique native test names"
}
$FixtureRoot = Join-Path ([IO.Path]::GetTempPath()) ("tstss-report-fixtures-" + [guid]::NewGuid().ToString('N'))
$PassedCases = 0
try {
    New-Item -Path $FixtureRoot -ItemType Directory -ErrorAction Stop | Out-Null
    $ReportPath = Join-Path $FixtureRoot 'index.json'
    function Save-Report([object]$Data) {
        ConvertTo-Json -InputObject $Data -Depth 10 | Set-Content -LiteralPath $ReportPath -Encoding utf8
    }
    function MustReject([string]$Name, [object]$Data, [string]$ExpectedReason) {
        Save-Report $Data
        $Rejected = $false
        try {
            $null = Assert-TSTSSNativeAutomationReport -ReportPath $ReportPath -RequiredTests $Required
        } catch {
            if ($_.Exception.Message -notmatch $ExpectedReason) {
                throw "$Name rejected for the wrong reason: $($_.Exception.Message)"
            }
            $Rejected = $true
        }
        if (-not $Rejected) { throw "${Name}: unsafe native report accepted" }
        $script:PassedCases++
    }
    function Clone-Report([object]$Data) {
        return ($Data | ConvertTo-Json -Depth 10 | ConvertFrom-Json)
    }
    $Valid = [pscustomobject]@{
        succeeded = 30
        failed = 0
        notRun = 0
        tests = @($Required | ForEach-Object {
            [pscustomobject]@{ fullTestPath = $_; state = 'Success' }
        })
    }
    Save-Report $Valid
    $Accepted = Assert-TSTSSNativeAutomationReport -ReportPath $ReportPath -RequiredTests $Required
    if ($Accepted.Status -ne 'REPORTED_NATIVE_AUTOMATIONS_SUCCESS' -or
        $Accepted.ReportedSuccesses -ne 30 -or
        $Accepted.GameplayPIE -ne 'NOT_TESTED_BY_THIS_CHECK') {
        throw 'Valid synthetic report accepted with incorrect summary or PIE claim'
    }
    $PassedCases++

    $Fake = Clone-Report $Valid; $Fake.succeeded = 31
    MustReject 'inflated-summary' $Fake 'summary and per-test successes disagree'
    $Fake = Clone-Report $Valid; $Fake.succeeded = '30'
    MustReject 'noninteger-summary' $Fake 'integer summary'
    $Fake = Clone-Report $Valid; $Fake.failed = 1
    MustReject 'failure-count' $Fake 'evidence incomplete'
    $Fake = Clone-Report $Valid; $Fake.notRun = 1
    MustReject 'not-run-count' $Fake 'evidence incomplete'
    $Fake = Clone-Report $Valid; $Fake.tests = @()
    MustReject 'empty-tests' $Fake 'Insufficient per-test'
    $Fake = Clone-Report $Valid; $Fake.tests[0].fullTestPath = $Fake.tests[1].fullTestPath
    MustReject 'duplicate-name' $Fake 'Duplicate test path'
    $Fake = Clone-Report $Valid; $Fake.tests[0].fullTestPath = 'TSTSS.Fictional.NotRegistered'
    MustReject 'missing-required' $Fake 'Required test missing'
    $Fake = Clone-Report $Valid; $Fake.tests[0].state = 'NotRun'
    MustReject 'not-success-state' $Fake 'entry not successful'
    $Fake = Clone-Report $Valid; $Fake.tests[0].state = $null
    MustReject 'missing-per-test-state' $Fake 'entry schema'
    $Fake = Clone-Report $Valid; $Fake.tests[0].fullTestPath = ''
    MustReject 'blank-name' $Fake 'entry schema'
    $Fake = Clone-Report $Valid; $Fake.PSObject.Properties.Remove('failed')
    MustReject 'missing-summary-field' $Fake 'integer summary'
    $Fake = Clone-Report $Valid; $Fake.succeeded = -1
    MustReject 'negative-summary' $Fake 'integer summary'
    $Fake = Clone-Report $Valid; $Fake.tests = 'aggregate-only fake'
    MustReject 'non-array-tests' $Fake 'aggregate-only PASS'

    $BadRequired = @($Required[0..28])
    $RequiredRejected = $false
    try {
        $null = Assert-TSTSSNativeAutomationReport -ReportPath $ReportPath -RequiredTests $BadRequired
    } catch {
        if ($_.Exception.Message -notmatch 'exactly 30') { throw }
        $RequiredRejected = $true
    }
    if (-not $RequiredRejected) { throw 'Shortened native test registry was accepted' }
    $PassedCases++

    Set-Content -LiteralPath $ReportPath -Value '{bad json' -Encoding utf8
    $ParseRejected = $false
    try {
        $null = Assert-TSTSSNativeAutomationReport -ReportPath $ReportPath -RequiredTests $Required
    } catch {
        if ($_.Exception.Message -notmatch 'Invalid automation JSON') { throw }
        $ParseRejected = $true
    }
    if (-not $ParseRejected) { throw 'Malformed JSON was accepted' }
    $PassedCases++
    Write-Output "PASS: $PassedCases synthetic native-report cases; no Unreal process, SaveGame or prior evidence touched"
} finally {
    if (Test-Path -LiteralPath $FixtureRoot) {
        Remove-Item -LiteralPath $FixtureRoot -Recurse -Force
    }
}
