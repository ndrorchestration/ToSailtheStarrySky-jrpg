param(
    [Parameter(Mandatory=$true)][string]$EngineRoot
)

# This wrapper preserves the existing strict verifier unchanged. UE 5.8
# generates two tracked .ini files during otherwise successful automation.
# Fail closed if any file already has an unexpected read-only state.
$ErrorActionPreference = 'Stop'
$Verifier = Join-Path $PSScriptRoot 'Verify-Unreal.ps1'
if (-not (Test-Path -LiteralPath $Verifier -PathType Leaf)) {
    throw 'Missing canonical strict verifier'
}

function Get-ConfigSha256([string]$Path) {
    $Hasher = [System.Security.Cryptography.SHA256]::Create()
    try {
        $Stream = [System.IO.File]::OpenRead($Path)
        try { return [System.BitConverter]::ToString($Hasher.ComputeHash($Stream)) }
        finally { $Stream.Dispose() }
    }
    finally { $Hasher.Dispose() }
}

$ConfigNames = @('DefaultEngine.ini', 'DefaultInput.ini')
$Guards = @()
foreach ($Name in $ConfigNames) {
    $Candidate = Join-Path $PSScriptRoot (Join-Path '../Config' $Name)
    $Resolved = (Resolve-Path -LiteralPath $Candidate -ErrorAction Stop).Path
    $Item = Get-Item -LiteralPath $Resolved -ErrorAction Stop
    if ($Item.IsReadOnly) {
        throw "Refusing to change an existing read-only config: $Name"
    }
    $Guards += [pscustomobject]@{
        Name = $Name
        Path = $Resolved
        InitialHash = (Get-ConfigSha256 $Resolved)
    }
}

$VerifyError = $null
$VerifyExit = 999
try {
    foreach ($Guard in $Guards) {
        (Get-Item -LiteralPath $Guard.Path).IsReadOnly = $true
    }
    # The canonical verifier still checks exact HEAD, clean Git tree,
    # native build, 29 required test identities and per-test JSON success.
    & $Verifier -EngineRoot $EngineRoot
    $VerifyExit = $LASTEXITCODE
}
catch {
    $VerifyError = $_
}
finally {
    # Only revert the two file attributes. Never restore or rewrite content.
    foreach ($Guard in $Guards) {
        (Get-Item -LiteralPath $Guard.Path).IsReadOnly = $false
    }
}

$Changed = @($Guards | Where-Object {
    (Get-ConfigSha256 $_.Path) -ne $_.InitialHash
})
if ($Changed.Count -gt 0) {
    throw "Protected tracked configuration content changed: $($Changed.Name -join ', ')"
}
if ($null -ne $VerifyError) { throw "Strict native verifier failed: $VerifyError" }
if ($VerifyExit -ne 0) { throw "Strict native verifier exit code: $VerifyExit" }
Write-Host 'PASS: strict UE native verification with two read-only config guards; original file hashes and attributes preserved.'
