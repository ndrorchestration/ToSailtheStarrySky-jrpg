# Pure PowerShell 5.1+ validation of an actual Unreal Editor Prelude map QA JSON.
# No UE process, filesystem mutation, Player SaveGame access or approval action.
# Validate all fields, not just a status string or the number of actors.
function Assert-TSTSSNativePreludeMapReceipt {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][psobject]$Report,
        [Parameter(Mandatory=$true)][string]$ExpectedHead,
        [Parameter(Mandatory=$true)][string]$ExpectedMapSha
    )
    if ($ExpectedHead -notmatch '^[a-fA-F0-9]{40}$' -or
        $ExpectedMapSha -notmatch '^[a-fA-F0-9]{64}$') {
        throw 'HOLD: invalid expected source/map SHA for map receipt'
    }
    function Require-Field {
        param([object]$Record, [string]$Field)
        if ($null -eq $Record -or $Record -isnot [pscustomobject]) {
            throw "HOLD: malformed map receipt object at $Field"
        }
        $prop = $Record.PSObject.Properties[$Field]
        if ($null -eq $prop -or $null -eq $prop.Value) {
            throw "HOLD: missing map receipt field: $Field"
        }
        return $prop.Value
    }
    function Require-Boolean {
        param([object]$Record, [string]$Field, [bool]$Expected)
        $actual = Require-Field $Record $Field
        if ($actual -isnot [bool] -or $actual -ne $Expected) {
            throw "HOLD: map receipt boolean invalid or contradictory: $Field"
        }
    }
    function Require-Integer {
        param([object]$Record, [string]$Field, [int]$Expected)
        $actual = Require-Field $Record $Field
        if (($actual -isnot [int] -and $actual -isnot [long]) -or
            $actual -ne $Expected) {
            throw "HOLD: map receipt integer invalid or contradictory: $Field"
        }
    }
    function Require-Finite {
        param([object]$Number, [string]$Field)
        if ($null -eq $Number -or
            ($Number -isnot [int] -and $Number -isnot [long] -and
             $Number -isnot [double] -and $Number -isnot [single] -and
             $Number -isnot [decimal])) {
            throw "HOLD: map receipt coordinate not numeric: $Field"
        }
        $asDouble = [double]$Number
        if ([double]::IsNaN($asDouble) -or [double]::IsInfinity($asDouble)) {
            throw "HOLD: map receipt nonfinite coordinate: $Field"
        }
        return $asDouble
    }

    $status = Require-Field $Report 'status'
    if ($status -isnot [string] -or
        $status -cne 'NATIVE_EDITOR_MAP_AND_REAL_ACTORS_PASS_NOT_PIE') {
        throw 'HOLD: native map receipt does not establish bounded Editor admission'
    }
    $sourceSha = Require-Field $Report 'source_sha'
    $mapSha = Require-Field $Report 'map_sha256'
    if ($sourceSha -isnot [string] -or $sourceSha -cne $ExpectedHead -or
        $mapSha -isnot [string] -or $mapSha -cne $ExpectedMapSha) {
        throw 'HOLD: map receipt source commit or map digest mismatches expected bytes'
    }
    $version = Require-Field $Report 'native_engine_version'
    if ($version -isnot [string] -or $version -notmatch '^5\.8\.4(?:$|[^0-9])') {
        throw 'HOLD: map receipt native engine is not Unreal 5.8.4'
    }
    Require-Integer $Report 'native_milestone_actor_count' 7
    Require-Integer $Report 'engineering_inspection_mask' 7
    foreach ($field in @(
        'map_loaded_in_editor',
        'all_seven_collision_targets_present',
        'physical_review_floor',
        'ocean_explicitly_visual_no_collision',
        'actual_reflected_game_mode_pawn_present',
        'real_actor_ordered_story_acceptance',
        'wrong_order_and_duplicate_interactions_rejected',
        'objective_text_reflected_and_correct',
        'world_layout_matches_authoring_plan',
        'all_marker_footprints_on_floor',
        'first_marker_initially_out_of_interaction_reach'
    )) { Require-Boolean $Report $field $true }
    foreach ($field in @(
        'chapter_one_act_one',
        'actual_pie_player_input_tested',
        'actual_savegame_disk_roundtrip_tested',
        'native_collision_line_trace_tested',
        'render_or_water_physics_approved',
        'character_or_ship_art_approved'
    )) { Require-Boolean $Report $field $false }

    $bindings = Require-Field $Report 'source_bindings'
    Require-Integer $bindings 'config_mapping_count' 9
    Require-Boolean $bindings 'source_handlers_verified' $true
    Require-Boolean $bindings 'player_keyboard_input_executed' $false

    $spawnDistance = Require-Finite (Require-Field $Report 'spawn_to_flyer_actor_origin_cm') 'spawn_to_flyer_actor_origin_cm'
    if ($spawnDistance -le 0) {
        throw 'HOLD: map receipt spawn/flyer actor locations collapsed'
    }
    $edgeDistance = Require-Finite (Require-Field $Report 'spawn_to_flyer_nearest_xy_edge_cm') 'spawn_to_flyer_nearest_xy_edge_cm'
    if ($edgeDistance -le 300 -or $edgeDistance -ge $spawnDistance) {
        throw 'HOLD: map receipt first marker does not establish safe initial interaction reach'
    }

    $coordinates = Require-Field $Report 'stop_locations_world_cm'
    if ($coordinates -isnot [pscustomobject]) {
        throw 'HOLD: map receipt milestone locations must be keyed JSON object'
    }
    $expectedStops = @(
        'FlyerDiscovery', 'IoniaHiring', 'AureateBoarding',
        'LiftStation', 'PressureStation', 'ReserveStation', 'EngineeringApproval'
    )
    $names = @($coordinates.PSObject.Properties.Name)
    if ($names.Count -ne 7) {
        throw 'HOLD: map receipt missing or extra milestone coordinates'
    }
    foreach ($name in $expectedStops) {
        $location = Require-Field $coordinates $name
        if ($location -isnot [array] -or $location.Count -ne 3) {
            throw "HOLD: map receipt location must contain three coordinates: $name"
        }
        foreach ($coord in $location) {
            $null = Require-Finite $coord $name
        }
    }

    # Independent UI and physics gates always stay held, even on PASS here.
    [pscustomobject]@{
        Status = 'NATIVE_EDITOR_MAP_RECEIPT_SCHEMA_ACCEPTED_NOT_PIE'
        SourceSha = $ExpectedHead
        NativeMilestones = 7
        P01_P13 = 'NOT_TESTED'
        WaterPhysics = 'NOT_AUTHORIZED'
        Release = 'NOT_AUTHORIZED'
    }
}
