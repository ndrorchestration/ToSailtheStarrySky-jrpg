extends Node2D
## Isolated TURN-BASED and SEPARATE-SCENE architecture probe, NOT migrated combat.

const FirstWake = preload("res://scenes/first_wake.tscn")
var hero_hp: int = 100
var dummy_hp: int = 35
var guard_next: bool = false
var completed: bool = false
var status: Label

func _ready() -> void:
    var ui := CanvasLayer.new()
    add_child(ui)
    status = Label.new()
    status.position = Vector2(80, 505)
    status.add_theme_font_size_override("font_size", 24)
    ui.add_child(status)
    _refresh_status()

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, Vector2(960, 640)), Color("#1f2d44"))
    draw_colored_polygon(PackedVector2Array([
        Vector2(0, 420), Vector2(960, 420), Vector2(850, 550), Vector2(110, 550)
    ]), Color("#395a5c"))
    draw_circle(Vector2(310, 345), 48, Color("#447d66"))
    draw_circle(Vector2(660, 345), 48, Color("#9b7464"))
    draw_string(ThemeDB.fallback_font, Vector2(170, 95), "Godot training arena — turn-based, separate from exploration", HORIZONTAL_ALIGNMENT_LEFT, -1, 23, Color.WHITE)

func _unhandled_key_input(event: InputEvent) -> void:
    if not (event is InputEventKey) or not event.pressed or event.echo:
        return
    if event.keycode == KEY_ESCAPE or event.keycode == KEY_R:
        get_tree().change_scene_to_packed(FirstWake)
        return
    if completed:
        return
    if event.keycode == KEY_1:
        dummy_hp = maxi(0, dummy_hp - 12)
        if dummy_hp == 0:
            completed = true
        else:
            _enemy_turn(0)
    elif event.keycode == KEY_2:
        guard_next = true
        _enemy_turn(0)
    _refresh_status()

func _enemy_turn(_delta: int) -> void:
    var damage := 5 if guard_next else 10
    hero_hp = maxi(0, hero_hp - damage)
    guard_next = false
    if hero_hp == 0:
        completed = true

func _refresh_status() -> void:
    if completed:
        status.text = "Training only. HP %d · Dummy %d   |   R: return" % [hero_hp, dummy_hp]
    else:
        status.text = "HP %d · Dummy %d   |   1: strike   2: guard   R: return" % [hero_hp, dummy_hp]
