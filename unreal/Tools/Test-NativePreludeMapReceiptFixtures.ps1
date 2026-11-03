# Exercise actual production map receipt validator. Pure PowerShell; no UE/PIE.
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Assert-NativePreludeMapReceipt.ps1')
$Head = 'a' * 40
$MapHash = 'b' * 64
$Passes = 0

$locations = [ordered]@{}
foreach ($name in @(
    'FlyerDiscovery', 'IoniaHiring', 'AureateBoarding', 'LiftStation',
    'PressureStation', 'ReserveStation', 'EngineeringApproval'
)) { $locations[$name] = @(200.0, 50.0, 15.0) }
$Valid = [ordered]@{
    status = 'NATIVE_EDITOR_MAP_AND_REAL_ACTORS_PASS_NOT_PIE'
    source_sha = $Head
    map_sha256 = $MapHash
    native_engine_version = '5.8.4-12345678'
    native_milestone_actor_count = 7
    engineering_inspection_mask = 7
    map_loaded_in_editor = $true
    all_seven_collision_targets_present = $true
    physical_review_floor = $true
    ocean_explicitly_visual_no_collision = $true
    actual_reflected_game_mode_pawn_present = $true
    real_actor_ordered_story_acceptance = $true
    wrong_order_and_duplicate_interactions_rejected = $true
    objective_text_reflected_and_correct = $true
    chapter_one_act_one = $false
    actual_pie_player_input_tested = $false
    actual_savegame_disk_roundtrip_tested = $false
    native_collision_line_trace_tested = $false
    render_or_water_physics_approved = $false
    character_or_ship_art_approved = $false
    source_bindings = [ordered]@{
        config_mapping_count = 9
        source_handlers_verified = $true
        player_keyboard_input_executed = $false
    }
    spawn_to_flyer_actor_origin_cm = 200.0
    stop_locations_world_cm = $locations
}
function Copy-Receipt {
    return (ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $Valid -Depth 16))
}
function MustReject {
    param([string]$Description, [psobject]$Report, [string]$ExpectedReason)
    $rejected = $false
    try {
        $null = Assert-TSTSSNativePreludeMapReceipt -Report $Report -ExpectedHead $Head -ExpectedMapSha $MapHash
    } catch {
        if ($_.Exception.Message -notmatch $ExpectedReason) {
            throw ("WRONG_REASON " + $Description + ": " + $_.Exception.Message)
        }
        $rejected = $true
    }
    if (-not $rejected) { throw "UNSAFE_MAP_REPORT_ACCEPTED $Description" }
    $script:Passes++
}

$accepted = Assert-TSTSSNativePreludeMapReceipt -Report (Copy-Receipt) -ExpectedHead $Head -ExpectedMapSha $MapHash
if ($accepted.Status -cne 'NATIVE_EDITOR_MAP_RECEIPT_SCHEMA_ACCEPTED_NOT_PIE' -or
    $accepted.P01_P13 -cne 'NOT_TESTED' -or
    $accepted.WaterPhysics -cne 'NOT_AUTHORIZED' -or
    $accepted.Release -cne 'NOT_AUTHORIZED') {
    throw 'Synthetic valid map receipt falsely granted gameplay/release approval'
}
$Passes++

$x = Copy-Receipt; $x.status = 'PLAYABLE_RELEASE_APPROVED'
MustReject 'false-status' $x 'bounded Editor admission'
$x = Copy-Receipt; $x.source_sha = 'c' * 40
MustReject 'wrong-source-commit' $x 'source commit'
$x = Copy-Receipt; $x.map_sha256 = 'c' * 64
MustReject 'wrong-map-digest' $x 'map digest'
$x = Copy-Receipt; $x.native_engine_version = '5.8.5'
MustReject 'wrong-engine-patch' $x 'engine'
$x = Copy-Receipt; $x.native_milestone_actor_count = 6
MustReject 'missing-actor' $x 'native_milestone_actor_count'
$x = Copy-Receipt; $x.native_milestone_actor_count = '7'
MustReject 'string-count' $x 'native_milestone_actor_count'
$x = Copy-Receipt; $x.engineering_inspection_mask = 3
MustReject 'wrong-inspection-mask' $x 'engineering_inspection_mask'
$x = Copy-Receipt; $x.map_loaded_in_editor = $false
MustReject 'map-not-loaded' $x 'map_loaded_in_editor'
$x = Copy-Receipt; $x.PSObject.Properties.Remove('all_seven_collision_targets_present')
MustReject 'omitted-collision-proof' $x 'all_seven_collision_targets_present'
$x = Copy-Receipt; $x.physical_review_floor = 'true'
MustReject 'string-truthy-floor' $x 'physical_review_floor'
$x = Copy-Receipt; $x.ocean_explicitly_visual_no_collision = $false
MustReject 'ocean-with-collision' $x 'ocean_explicitly_visual_no_collision'
$x = Copy-Receipt; $x.actual_reflected_game_mode_pawn_present = $false
MustReject 'missing-native-pawn' $x 'actual_reflected_game_mode_pawn_present'
$x = Copy-Receipt; $x.real_actor_ordered_story_acceptance = $false
MustReject 'story-order-not-verified' $x 'real_actor_ordered_story_acceptance'
$x = Copy-Receipt; $x.wrong_order_and_duplicate_interactions_rejected = $false
MustReject 'invalid-milestone-rejected-status' $x 'wrong_order_and_duplicate_interactions_rejected'
$x = Copy-Receipt; $x.objective_text_reflected_and_correct = $false
MustReject 'objective-not-verified' $x 'objective_text_reflected_and_correct'
$x = Copy-Receipt; $x.chapter_one_act_one = $true
MustReject 'false-chapter-one-pass' $x 'chapter_one_act_one'
$x = Copy-Receipt; $x.actual_pie_player_input_tested = $true
MustReject 'false-pie-claim' $x 'actual_pie_player_input_tested'
$x = Copy-Receipt; $x.actual_savegame_disk_roundtrip_tested = $true
MustReject 'false-save-claim' $x 'actual_savegame_disk_roundtrip_tested'
$x = Copy-Receipt; $x.native_collision_line_trace_tested = $true
MustReject 'false-ray-cast-claim' $x 'native_collision_line_trace_tested'
$x = Copy-Receipt; $x.render_or_water_physics_approved = $true
MustReject 'false-water-claim' $x 'render_or_water_physics_approved'
$x = Copy-Receipt; $x.character_or_ship_art_approved = $true
MustReject 'false-art-claim' $x 'character_or_ship_art_approved'
$x = Copy-Receipt; $x.source_bindings.config_mapping_count = 8
MustReject 'missing-input-mapping' $x 'config_mapping_count'
$x = Copy-Receipt; $x.source_bindings.source_handlers_verified = $false
MustReject 'missing-input-handler' $x 'source_handlers_verified'
$x = Copy-Receipt; $x.source_bindings.player_keyboard_input_executed = $true
MustReject 'fabricated-keyboard-proof' $x 'player_keyboard_input_executed'
$x = Copy-Receipt; $x.spawn_to_flyer_actor_origin_cm = 0
MustReject 'collapsed-actor-origins' $x 'locations collapsed'
$x = Copy-Receipt; $x.spawn_to_flyer_actor_origin_cm = '200'
MustReject 'string-distance' $x 'not numeric'
$x = Copy-Receipt; $x.stop_locations_world_cm.PSObject.Properties.Remove('IoniaHiring')
MustReject 'missing-stop-location' $x 'missing or extra'
$x = Copy-Receipt; $x.stop_locations_world_cm.FlyerDiscovery = @(12, 20)
MustReject 'incomplete-actor-position' $x 'three coordinates'
$x = Copy-Receipt; $x.stop_locations_world_cm.FlyerDiscovery = @('3', 4, 5)
MustReject 'non-numeric-position' $x 'not numeric'
$x = Copy-Receipt; $x.stop_locations_world_cm | Add-Member -NotePropertyName 'UnexpectedEighth' -NotePropertyValue @(1, 2, 3)
MustReject 'eighth-actor-location' $x 'missing or extra'
$x = Copy-Receipt; $x.PSObject.Properties.Remove('source_bindings')
MustReject 'omitted-input-source-provenance' $x 'source_bindings'

Write-Output "PASS: $Passes actual map-receipt validator cases (1 valid + fail-closed negative fixtures); NO UNREAL/PIE"
