[CmdletBinding()]
param(
    [switch]$Install,
    [switch]$AcceptPackageAgreements
)
$ErrorActionPreference = 'Stop'
$Manifest = Join-Path $PSScriptRoot 'TSTSS-UE58.vsconfig'
if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) {
    throw "Required C++ toolchain manifest not found: $Manifest"
}
$Config = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
$Required = @(
    'Microsoft.VisualStudio.Workload.VCTools',
    'Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
    'Microsoft.VisualStudio.Component.Windows11SDK.26100'
)
foreach ($Item in $Required) {
    if ($Config.components -notcontains $Item) {
        throw "Missing approved free native C++ component: $Item"
    }
}
$Command = Get-Command winget -ErrorAction SilentlyContinue
if (-not $Command) { throw "Windows Package Manager (winget) unavailable" }
$Overrides = '--passive --norestart --config "' + $Manifest + '"'
$Arguments = @(
    'install', '--exact', '--id', 'Microsoft.VisualStudio.BuildTools',
    '--source', 'winget', '--override', $Overrides
)
$Plan = [ordered]@{
    authority = 'PREPARATION_ONLY_UNLESS_EXPLICIT_INSTALL'
    free_tool = 'Visual Studio Build Tools (stable)'
    required_components = $Required
    config_path = $Manifest
    install_requested = [bool]$Install
    ue_installation_is_separate = $true
    notes = @(
        'The UE5.8.4 Epic installation is managed separately and is not touched.',
        'Review remaining C: disk capacity before committing to a large toolchain download.',
        'Administrator/UAC approval may be needed for Microsoft installation.'
    )
}
$Plan | ConvertTo-Json -Depth 5
if (-not $Install) { exit 0 }
if (-not $AcceptPackageAgreements) {
    throw 'Explicit -AcceptPackageAgreements is required for toolchain installation'
}
$Arguments += @('--accept-package-agreements', '--accept-source-agreements')
& $Command.Source @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "Visual Studio Build Tools setup failed or was cancelled ($LASTEXITCODE)"
}
Write-Host 'Build Tools installer returned success. Re-run Check-UnrealHost.ps1; no Unreal build or editor render has run.'
