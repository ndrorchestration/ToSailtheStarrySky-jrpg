<#
Host-controlled first-time generation of three PRIVATE Ender directional walk
AnimSequences from installed UE5.8 mannequin template assets. Creates ignored
binaries only; no pawn binding, no scene save, no merge/release, no overwrite.
Retains evidence and partial output on failure for independent inspection.
#>
param([Parameter(Mandatory=$true)][string]$ExpectedHead,
      [string]$EngineRoot='C:\Program Files\Epic Games\UE_5.8')
$ErrorActionPreference='Stop'
$Repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Project=Join-Path $Repo 'unreal'
$Editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Uproject=Join-Path $Project 'ToSailTheStarrySky.uproject'
$Author=Join-Path $PSScriptRoot 'author_private_ender_directional_walk.py'
$SourceRoot=Join-Path $EngineRoot 'Templates\TemplateResources\High\Characters\Content\Mannequins\Anims\Unarmed\Walk'
$PrivateRoot=Join-Path $Project 'Content\TSTSS\Review\Characters\EnderRetarget_NONCANONICAL'
$SourceDir=Join-Path $PrivateRoot 'MannequinWalkSources_PRIVATE'
$OutputDir=Join-Path $PrivateRoot 'DirectionalWalkV1_PRIVATE'
$CandidateNames=@('MF_Unarmed_Walk_Bwd','MF_Unarmed_Walk_Left','MF_Unarmed_Walk_Right')
$ShaTable=@{
 MF_Unarmed_Walk_Bwd='ae0c2ee1c1178fd1b9493f6c327e52d10a3d6bbde29eae54dcb07c13a27dcf46'
 MF_Unarmed_Walk_Left='81500e4fcdd9ae9aa6433e652e67dea8f9dd9fa7b9ef1714e29f6ab0a1bb9d97'
 MF_Unarmed_Walk_Right='f5922b4e632351353224b32f719af97e85512ab4f6553b15315cf14ad04f675f'
}
function Need([bool]$good,[string]$why){if(!$good){throw ('HOLD_DIRECTIONAL_AUTHOR_'+$why)}}
function Sha([string]$filename){
  $hasher=[System.Security.Cryptography.SHA256]::Create()
  try {return ([BitConverter]::ToString($hasher.ComputeHash([System.IO.File]::ReadAllBytes($filename)))).Replace('-','').ToLowerInvariant()}
  finally {$hasher.Dispose()}
}
function TrackedClean{
  return @(& git -C $Repo status --porcelain).Count -eq 0
}
Need ((git -C $Repo rev-parse HEAD) -eq $ExpectedHead -and
      $ExpectedHead -match '^[a-f0-9]{40}$') 'WRONG_COMMIT'
Need ((git -C $Repo branch --show-current) -eq 'review/ender-directional-walk-retarget-20261123') 'BRANCH'
Need (TrackedClean) 'DIRTY_SOURCE'
Need ((Test-Path $Editor) -and (Test-Path $Author) -and (Test-Path $Uproject)) 'EDITOR_OR_AUTHOR_MISSING'
Need (@(Get-Process UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool,LiveCodingConsole -ErrorAction SilentlyContinue).Count -eq 0) 'ENGINE_BUSY'
Need ((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1048576 -ge 6.5) 'RAM'
Need ((Get-PSDrive C).Free/1GB -ge 16.5) 'DISK'
Need (!(Test-Path $SourceDir) -and !(Test-Path $OutputDir)) 'PRIVATE_SOURCE_OR_OUTPUT_ALREADY_EXISTS'
$Protected=@(
  (Get-ChildItem $PrivateRoot -Recurse -File -Filter '*.uasset' | Select-Object -ExpandProperty FullName)
  ) + @(
  $Uproject,
  (Join-Path $Project 'Config\DefaultEngine.ini'),
  (Join-Path $Project 'Config\DefaultInput.ini')
)
$Protected=$Protected | Where-Object {$_ -and (Test-Path $_)} | Sort-Object -Unique
Need ($Protected.Count -ge 10) 'PROTECTED_ASSET_BASELINE_TOO_SMALL'
$Before=@{}
foreach($item in $Protected){$Before[$item]=Sha $item}
foreach($name in $CandidateNames){
 $origin=Join-Path $SourceRoot ($name+'.uasset')
 Need ((Test-Path $origin) -and (Sha $origin) -eq $ShaTable[$name]) ('INPUT_HASH_'+$name)
 $relativeSource='unreal/Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/MannequinWalkSources_PRIVATE/'+$name+'.uasset'
 $relativeOutput='unreal/Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/DirectionalWalkV1_PRIVATE/'+$name+'_EnderDirectionalV1_PRIVATE.uasset'
 & git -C $Repo check-ignore --no-index -q $relativeSource
 Need ($LASTEXITCODE -eq 0) 'SOURCE_NOT_IGNORED'
 & git -C $Repo check-ignore --no-index -q $relativeOutput
 Need ($LASTEXITCODE -eq 0) 'OUTPUT_NOT_IGNORED'
}
$RunDir=Join-Path $Project ('Saved\MigrationEvidence\EnderDirectionalWalk_'+$ExpectedHead.Substring(0,10)+'_'+(Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ'))
Need (!(Test-Path $RunDir)) 'EVIDENCE_COLLISION'
New-Item -Path $RunDir -ItemType Directory | Out-Null
New-Item -Path $SourceDir -ItemType Directory | Out-Null
$Staged=@()
foreach($name in $CandidateNames){
 $from=Join-Path $SourceRoot ($name+'.uasset')
 $to=Join-Path $SourceDir ($name+'.uasset')
 Need (!(Test-Path $to)) 'STAGED_ALREADY_EXISTS'
 [System.IO.File]::Copy($from,$to,$false)
 Need ((Sha $to) -eq $ShaTable[$name]) ('COPY_HASH_'+$name)
 $Staged += $to
}
$Log=Join-Path $RunDir 'native-editor.log'
$Receipt=Join-Path $RunDir 'author-receipt.json'
$env:TSTSS_DIRECTIONAL_EXPECTED_HEAD=$ExpectedHead
$env:TSTSS_DIRECTIONAL_RECEIPT=$Receipt
$env:TSTSS_PRIVATE_DIRECTIONAL_CREATE='1'
$ErrorActionPreference='Continue'
try{
  & $Editor $Uproject ('-ExecutePythonScript='+$Author) -ddc=InstalledNoZenLocalFallback -nullrhi -unattended -nosplash -NoLiveCoding -nop4 ('-abslog='+$Log) 2>&1 | Select-Object -Last 7
  $Exit=$LASTEXITCODE
}finally{
  Remove-Item Env:\TSTSS_DIRECTIONAL_EXPECTED_HEAD -ErrorAction SilentlyContinue
  Remove-Item Env:\TSTSS_DIRECTIONAL_RECEIPT -ErrorAction SilentlyContinue
  Remove-Item Env:\TSTSS_PRIVATE_DIRECTIONAL_CREATE -ErrorAction SilentlyContinue
}
$ErrorActionPreference='Stop'
Need (@(Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue).Count -eq 0) 'EDITOR_LEFT_RUNNING'
$OnlyConfig=@('unreal/Config/DefaultEngine.ini','unreal/Config/DefaultInput.ini')
$Dirty=@(git -C $Repo diff --name-only)
Need (@($Dirty|Where-Object{$_ -notin $OnlyConfig}).Count -eq 0) 'UNEXPECTED_TRACKED_CHANGE'
foreach($file in $Dirty){
 Need (@($OnlyConfig -contains $file).Count -eq 1) 'UNEXPECTED_CONFIG'
 & git -C $Repo restore --source=$ExpectedHead -- $file
 Need ($LASTEXITCODE -eq 0) 'CONFIG_RESTORE'
}
Need (TrackedClean) 'SOURCE_DIRTY_AFTER'
foreach($item in $Protected){
 Need ((Test-Path $item) -and (Sha $item) -eq $Before[$item]) ('PROTECTED_ASSET_CHANGED_'+[IO.Path]::GetFileName($item))
}
Need ($Exit -eq 0 -and (Test-Path $Receipt)) 'EDITOR_OR_RECEIPT_MISSING'
$Result=Get-Content $Receipt -Raw | ConvertFrom-Json
Need ($Result.status -eq 'PRIVATE_DIRECTIONAL_RETARGET_CREATED_NOT_PLAYBACK_ACCEPTED' -and
      $Result.source_sha -eq $ExpectedHead -and @($Result.created).Count -eq 3) 'BATCH_NOT_ACCEPTED'
foreach($record in @($Result.created)){
 $file=Join-Path $OutputDir ($record.name+'.uasset')
 Need ((Test-Path $file) -and (Sha $file) -eq $record.sha256) 'NEW_ASSET_HASH'
}
Write-Output ('NATIVE_PRIVATE_DIRECTIONAL_RETARGET_PASS '+$ExpectedHead+' sources=3 outputs=3 protected='+$Protected.Count)
Write-Output ('RECEIPT='+$Receipt)
Write-Output ('TRACKED_CLEAN='+(TrackedClean))
