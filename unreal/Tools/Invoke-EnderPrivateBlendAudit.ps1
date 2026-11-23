<#
Exact-commit, read-only native Unreal 5.8.4 Ender asset audit.
Checks graph and binary custody without altering either saved private asset.
Authoring/recreation of assets is deliberately NOT authorized by this command.
#>
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [string]$ExpectedHead
)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$project=Join-Path $root 'unreal\ToSailTheStarrySky.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$script=Join-Path $PSScriptRoot 'audit_ender_private_blend_assets.py'
$head=(git -C $root rev-parse HEAD).Trim()
if(!$ExpectedHead){$ExpectedHead=$head}
function Need([bool]$condition,[string]$token){
  if(!$condition){throw ('HOLD_ENDER_PRIVATE_ASSET_AUDIT_'+$token)}
}
Need ($head -eq $ExpectedHead -and $ExpectedHead -match '^[a-f0-9]{40}$') 'WRONG_HEAD'
Need (@(git -C $root status --porcelain).Count -eq 0) 'SOURCE_DIRTY'
Need ((Test-Path $project) -and (Test-Path $editor) -and (Test-Path $script)) 'INPUT_MISSING'
Need (@(Get-Process UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool,LiveCodingConsole -ErrorAction SilentlyContinue).Count -eq 0) 'ENGINE_BUSY'
Need ((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1048576 -ge 6.5) 'RAM_LOW'
Need ((Get-PSDrive C).Free/1GB -ge 16.5) 'DISK_LOW'
$evidence=Join-Path $root ('unreal\Saved\MigrationEvidence\EnderAssetAudit_'+$head.Substring(0,10)+'_'+(Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ'))
Need (!(Test-Path $evidence)) 'RECEIPT_FOLDER_COLLISION'
New-Item -Path $evidence -ItemType Directory | Out-Null
$receipt=Join-Path $evidence 'asset-audit.json'
$log=Join-Path $evidence 'native-audit.log'
$env:TSTSS_ENDER_AUDIT_EXPECTED_HEAD=$ExpectedHead
$env:TSTSS_ENDER_AUDIT_RECEIPT=$receipt
$ErrorActionPreference='Continue'
try{
  & $editor $project ('-ExecutePythonScript='+$script) -ddc=InstalledNoZenLocalFallback -nullrhi -unattended -nosplash -NoLiveCoding -nop4 ('-abslog='+$log) 2>&1 | Select-Object -Last 5
  $exit=$LASTEXITCODE
}finally{
  Remove-Item Env:\TSTSS_ENDER_AUDIT_EXPECTED_HEAD -ErrorAction SilentlyContinue
  Remove-Item Env:\TSTSS_ENDER_AUDIT_RECEIPT -ErrorAction SilentlyContinue
}
$modified=@(git -C $root diff --name-only)
$allowed=@('unreal/Config/DefaultEngine.ini','unreal/Config/DefaultInput.ini')
Need (@($modified | Where-Object {$_ -notin $allowed}).Count -eq 0) 'UNEXPECTED_SOURCE_MODIFICATION'
Need (@(Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue).Count -eq 0) 'ENGINE_LEFT_RUNNING'
if($modified.Count -gt 0){
    git -C $root restore --source=$ExpectedHead -- 'unreal/Config/DefaultEngine.ini' 'unreal/Config/DefaultInput.ini'
    Need ($LASTEXITCODE -eq 0) 'CONFIG_RESTORE_FAILED'
}
Need ((git -C $root rev-parse HEAD).Trim() -eq $ExpectedHead) 'HEAD_CHANGED'
Need (@(git -C $root status --porcelain).Count -eq 0) 'DIRTY_AFTER_AUDIT'
Need ($exit -eq 0 -and (Test-Path $receipt)) 'NATIVE_EXECUTION_FAILED'
$result=Get-Content $receipt -Raw | ConvertFrom-Json
Need ($result.status -eq 'EXACT_HEAD_NATIVE_PRIVATE_ASSET_AUDIT_PASS' -and
      $result.source_sha -eq $ExpectedHead -and $result.private_assets.Count -eq 2) 'RECEIPT_INVALID'
Write-Output ('ENDER_PRIVATE_AUDIT_PASS '+$ExpectedHead+' assets=2 verified_links='+$result.verified_graph_links.Count)
Write-Output ('EVIDENCE='+$receipt)
