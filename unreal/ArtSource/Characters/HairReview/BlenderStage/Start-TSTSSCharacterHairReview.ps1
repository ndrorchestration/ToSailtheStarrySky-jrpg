# TSTSS Ender character DCC preflight. SAFE by default; no processes launched.
# Optional -Launch only after the owner-controlled Unreal session has closed
# naturally and free RAM/disk admission passes. Never terminates any process.
param([switch]$Launch)

$ErrorActionPreference='Stop'
$Blender='C:\TSTSS_Tools\BlenderPortable\blender-5.2.4-windows-x64\blender.exe'
$Script=Join-Path $PSScriptRoot 'build_ender_v3_review_scene.py'
$Output='C:\TSTSS_Tools\BlenderPortable\TSTSS_CharacterArt\ReviewOutput'
$Asset='C:\TSTSS_EnderHairNativeV1_20261104\unreal\ArtSource\Characters\HairReview\CandidatesV3\Ender_BroadLayerHair_V3_NONCANONICAL.glb'
$Receipt='C:\TSTSS_Tools\BlenderPortable\blender-5.2.4-windows-x64_source_receipt.json'
$Result=Join-Path $Output 'Ender_V3_Hair_EDITABLE_DCC_REVIEW_NONCANONICAL.blend'

foreach($path in @($Blender,$Script,$Asset,$Receipt)){
 if(!(Test-Path -LiteralPath $path -PathType Leaf)){
   Write-Output ('TSTSS_DCC_HOLD: missing '+$path); exit 2
 }
}
if(!(Test-Path -LiteralPath $Output -PathType Container)){
  Write-Output 'TSTSS_DCC_HOLD: review output folder missing';exit 2
}
if(Test-Path -LiteralPath $Result){
  Write-Output 'TSTSS_DCC_HOLD: existing .blend study would be overwritten';exit 2
}
$busy=@(Get-CimInstance Win32_Process | Where-Object {
 $_.Name -in @('UnrealEditor.exe','LiveCodingConsole.exe','UnrealBuildTool.exe','blender.exe')
})
if($busy.Count -gt 0){
 Write-Output 'TSTSS_DCC_HOLD: separately owned Unreal/Blender process is active; no competing renderer.'
 $busy | Select-Object ProcessId,Name | Format-Table | Out-String | Write-Output
 exit 2
}
$os=Get-CimInstance Win32_OperatingSystem
$ram=[double]$os.FreePhysicalMemory/1048576.0
$disk=[double](Get-PSDrive C).Free/1GB
if($ram -lt 6.5 -or $disk -lt 14.0){
 Write-Output ("TSTSS_DCC_HOLD: resource gate RAM={0:N2} GiB (<6.5) or disk={1:N2} GiB (<14)" -f $ram,$disk)
 exit 2
}
Write-Output ("TSTSS_DCC_READY: RAM={0:N2} GiB disk={1:N2} GiB source only" -f $ram,$disk)
if(!$Launch){
 Write-Output 'CHECK_ONLY_NO_BLENDER_LAUNCHED; To execute later: .\Start-TSTSSCharacterHairReview.ps1 -Launch'
 exit 0
}
Write-Output 'TSTSS_DCC_NATIVE_BLENDER_EXECUTING: creates only isolated editable .blend study, not a render.'
& $Blender --background --factory-startup --python $Script -- --outdir $Output
if($LASTEXITCODE -ne 0){
 Write-Output ('TSTSS_DCC_HOLD: Blender exit '+$LASTEXITCODE);exit $LASTEXITCODE
}
Write-Output 'TSTSS_DCC_RESULT_CREATED_BUT_ART_AND_UNREAL_GATES_OPEN'
