extends Node2D
## Shader-backed source-native atmosphere behind the real postflight gameplay.
## Art may animate; it has no contact, collision, stage, save or story authority.
const SkyShader = preload("res://shaders/first_wake_cinematic_sky.gdshader")
const SeaShader = preload("res://shaders/first_wake_cinematic_sea.gdshader")
const Architecture = preload("res://scripts/first_wake_cinematic_deck_architecture.gd")
const SIZE := Vector2(960, 640)

var sky: ColorRect
var sea: ColorRect
var architecture
var reduced_motion: bool = false

func _ready() -> void:
    sky = _layer("StormbreakSky", Vector2.ZERO, Vector2(960, 401), SkyShader)
    sea = _layer("OceanSurface", Vector2(0, 286), Vector2(960, 115), SeaShader)
    architecture = Architecture.new()
    architecture.name = "ShipboardMaritimeArchitecture"
    add_child(architecture)
    set_reduced_motion(reduced_motion)

func _layer(label: String, at: Vector2, extent: Vector2, shader: Shader) -> ColorRect:
    var rect := ColorRect.new()
    rect.name = label
    rect.position = at
    rect.size = extent
    rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
    var surface := ShaderMaterial.new()
    surface.shader = shader
    rect.material = surface
    add_child(rect)
    return rect

func set_reduced_motion(enabled: bool) -> void:
    reduced_motion = enabled
    if sea != null and sea.material is ShaderMaterial:
        (sea.material as ShaderMaterial).set_shader_parameter(
            "motion_scale", 0.0 if enabled else 1.0)

func set_reserve_inspected(inspected: bool) -> void:
    if architecture != null:
        architecture.set_reserve_inspected(inspected)

func visual_snapshot() -> Dictionary:
    return {
        "cinematic_2d_preview": true,
        "real_native_sky_shader": sky != null and sky.material is ShaderMaterial,
        "real_native_sea_shader": sea != null and sea.material is ShaderMaterial,
        "maritime_architecture": architecture != null,
        "reduced_motion": reduced_motion,
        "story_authority": false,
        "collision_authority": false,
        "production_art_approved": false,
    }
