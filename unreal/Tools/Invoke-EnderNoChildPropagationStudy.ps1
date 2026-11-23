<#
Single-run, source-locked PRIVATE retargeter-duplicate experiment.
Never writes to existing retargeter or Ender animations; refuses overwrite.
Produces ignored local binaries. No gameplay/root motion release authorization.
#>
param([Parameter(Mandatory=$true)][string]$ExpectedHead)
$ErrorActionPreference='Stop'
$Repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Project=Join-Path $Repo 'unreal'
$Editor='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Up=Join-Path $Project 'ToSailTheStarrySky.uproject'
$Author=Join-Path $PSScriptRoot 'author_private_ender_nochildprop_study.py'
$Root=Join-Path $Project 'Content\TSTSS\Review\Characters\EnderRetarget_NONCANONICAL'
$Target=Join-Path $Root 'DirectionalNoChildPropV1_PRIVATE'
$NewRetarget=Join-Path $Root 'RTG_MannyToEnder_NoChildPropV1_PRIVATE.uasset'
function Need([bool]$ok,[string]$label){if(!$ok){throw ('HOLD_PRIVATE_NOCHILDPROP_'+$label)}}
function Sha([string]$file){
 $hasher=[System.Security.Cryptography.SHA256]::Create()
 try {return ([BitConverter]::ToString($hasher.ComputeHash([IO.File]::ReadAllBytes($file)))).Replace('-','').ToLowerInvariant()}
 finally {$hasher.Dispose()}
}
function Clean {return @(& git -C $Repo status --porcelain).Count -eq 0}
Need ($ExpectedHead -match '^[0-9a-f]{40}$' -and (git -C $Repo rev-parse HEAD) -eq $ExpectedHead) 'HEAD'
Need ((git -C $Repo branch --show-current) -eq 'review/ender-directional-spine-geometry-gate-20261123') 'BRANCH'
Need (Clean) 'SOURCE_DIRTY'
Need ((Test-Path $Editor) -and (Test-Path $Up) -and (Test-Path $Author)) 'NATIVE_INPUTS'
Need (!(Test-Path $Target) -and !(Test-Path $NewRetarget)) 'PRIVATE_OUTPUT_ALREADY_EXISTS'
Need (@(Get-Process UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool,LiveCodingConsole -ErrorAction SilentlyContinue).Count -eq 0) 'ENGINE_BUSY'
Need ((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1048576 -ge 6.5 -and (Get-PSDrive C).Free/1GB -ge 16.5) 'RESOURCES'
$Privates=@(Get-ChildItem $Root -Recurse -File -Filter '*.uasset' | Select-Object -ExpandProperty FullName)
Need ($Privates.Count -eq 18) 'ORIGINAL_ASSET_COUNT'
$Protected=@($Privates + $Up + (Join-Path $Project 'Content\TSTSS\Review\Characters\EnderRetarget_NONCANONICAL\BP_EnderPIEGameMode_NONCANONICAL.uasset'))|Sort-Object -Unique
$Hashes=@{};foreach($file in $Protected){Need (Test-Path $file) 'PROTECTED_FILE_MISSING';$Hashes[$file]=Sha $file}
foreach($name in @('MF_Unarmed_Walk_Bwd','MF_Unarmed_Walk_Left','MF_Unarmed_Walk_Right')){
 $f=Join-Path $Root ('MannequinWalkSources_PRIVATE\'+$name+'.uasset')
 Need (Test-Path $f) ('SOURCE_NOT_FOUND_'+$name)
 $p='unreal/Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/DirectionalNoChildPropV1_PRIVATE/'+$name+'_EnderNoChildPropV1_PRIVATE.uasset'
 git -C $Repo check-ignore --no-index -q $p
 Need ($LASTEXITCODE -eq 0) 'PRIVATE_OUTPUT_NOT_IGNORED'
}
$Run=Join-Path $Project ('Saved\MigrationEvidence\EnderNoChildPropStudy_'+$ExpectedHead.Substring(0,10)+'_'+(Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ'))
Need (!(Test-Path $Run)) 'EVIDENCE_COLLISION'
New-Item -Path $Run -ItemType Directory | Out-Null
$Receipt=Join-Path $Run 'native-result.json'
$Log=Join-Path $Run 'native-editor.log'
$env:TSTSS_NOCHILDPROP_EXPECTED_HEAD=$ExpectedHead
$env:TSTSS_NOCHILDPROP_RECEIPT=$Receipt
$env:TSTSS_PRIVATE_NOCHILDPROP_CREATE='1'
$ErrorActionPreference='Continue'
try {
 & $Editor $Up ('-ExecutePythonScript='+$Author) -nullrhi -unattended -nosplash -NoLiveCoding -nop4 ('-abslog='+$Log) 2>&1 | Select-Object -Last 5
 $Exit=$LASTEXITCODE
} finally {
 Remove-Item Env:\TSTSS_NOCHILDPROP_EXPECTED_HEAD -ErrorAction SilentlyContinue
 Remove-Item Env:\TSTSS_NOCHILDPROP_RECEIPT -ErrorAction SilentlyContinue
 Remove-Item Env:\TSTSS_PRIVATE_NOCHILDPROP_CREATE -ErrorAction SilentlyContinue
}
$ErrorActionPreference='Stop'
Need (@(Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue).Count -eq 0) 'EDITOR_LEFT_RUNNING'
$Allowed=@('unreal/Config/DefaultEngine.ini','unreal/Config/DefaultInput.ini')
$Drift=@(git -C $Repo diff --name-only)
Need (@($Drift|Where-Object{$_ -notin $Allowed}).Count -eq 0) 'UNEXPECTED_TRACKED_DRIFT'
foreach($name in $Drift){
 git -C $Repo restore --source=$ExpectedHead -- $name
 Need ($LASTEXITCODE -eq 0) 'CONFIG_RESTORE'
}
Need (Clean) 'SOURCE_DIRTY_AFTER'
foreach($file in $Protected){Need ((Test-Path $file) -and (Sha $file) -eq $Hashes[$file]) 'ORIGINAL_BINARY_MUTATED'}
Need ($Exit -eq 0 -and (Test-Path $Receipt)) 'EDITOR_OR_RECEIPT_ERROR'
$r=Get-Content $Receipt -Raw|ConvertFrom-Json
Need ($r.source_sha -eq $ExpectedHead -and @($r.created).Count -eq 3) 'CANDIDATE_COUNT'
foreach($item in $r.created){
 $file=Join-Path $Target ($item.name+'.uasset')
 Need ((Test-Path $file) -and (Sha $file) -eq $item.sha256) 'CANDIDATE_HASH'
}
Write-Output ('PRIVATE_NOCHILDPROP_NATIVE_STATUS='+$r.status+' count='+@($r.created).Count+' protected='+$Protected.Count+' exit='+$Exit)
Write-Output ('RESULT='+$Receipt)
# The result status can be a valid diagnosed hold; never promote automatically.
Need ($r.status -eq 'SPINE_GEOMETRY_SCREEN_PASS_NOT_VISUAL') 'GEOMETRY_REJECTED'
