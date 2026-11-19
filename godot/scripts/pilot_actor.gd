extends CharacterBody2D
## Early Godot input/grounding proof; NOT approved character art or equipment canon.

@export var character_name: String = "Ender"
@export var player_controlled: bool = false
@export var walk_speed: float = 148.0

var walking_bounds: Rect2 = Rect2(Vector2(145, 410), Vector2(670, 112))
var near_leg_forward: bool = false
var walk_clock: float = 0.0

func _ready() -> void:
    var shape_node := CollisionShape2D.new()
    var shape := CircleShape2D.new()
    shape.radius = 10.0
    shape_node.shape = shape
    add_child(shape_node)
    queue_redraw()

func _physics_process(delta: float) -> void:
    if not player_controlled:
        return
    var direction := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    velocity = direction * walk_speed
    move_and_slide()
    global_position = global_position.clamp(walking_bounds.position, walking_bounds.end)
    if direction.length_squared() > 0.001:
        walk_clock += delta
        near_leg_forward = sin(walk_clock * 13.0) > 0.0
    queue_redraw()

func _draw() -> void:
    # Intentionally rudimentary silhouettes; DO NOT confuse with field-pack admission.
    var is_ionia := character_name == "Ionia"
    var coat := Color("#203d68") if is_ionia else Color("#47634c")
    var highlight := Color("#d7b56a") if is_ionia else Color("#dccbaa")
    var hair := Color("#e4b65f") if is_ionia else Color("#965936")
    draw_circle(Vector2(0, -3), 14.0, Color(0.05, 0.11, 0.19, 0.45))
    var step := 3.0 if near_leg_forward and player_controlled else 0.0
    draw_line(Vector2(-5, -19), Vector2(-7-step, -2), Color("#253344"), 6.0)
    draw_line(Vector2(5, -19), Vector2(6+step, -2), Color("#253344"), 6.0)
    draw_colored_polygon(PackedVector2Array([
        Vector2(-13, -43), Vector2(12, -43), Vector2(15, -15), Vector2(0, -21), Vector2(-17, -15)
    ]), coat)
    draw_line(Vector2(-12, -41), Vector2(6, -21), highlight, 2.0)
    draw_line(Vector2(12, -39), Vector2(-1, -24), highlight, 2.0)
    draw_circle(Vector2(0, -54), 11.0, Color("#efc1a0"))
    draw_arc(Vector2(0, -58), 12.0, 3.1, 6.3, 12, hair, 7.0)
    if is_ionia:
        # Shoulder-length curls; reference identity only, not a finished sprite.
        for i in range(4):
            draw_circle(Vector2(-11 + i * 7, -47), 4.0, hair)
    else:
        draw_line(Vector2(16, -87), Vector2(16, -2), Color("#806341"), 3.0)
        draw_line(Vector2(16, -83), Vector2(16, -66), Color("#cbb37b"), 4.0)
    draw_line(Vector2(-4, -55), Vector2(-2, -55), Color("#4d9f79"), 2.0)
    draw_line(Vector2(3, -55), Vector2(5, -55), Color("#4d9f79"), 2.0)
