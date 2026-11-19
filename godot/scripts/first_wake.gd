extends Node2D
## Small native-engine technical proof: First Wake dock contact, talk interaction,
## and transition to a SEPARATE turn-based training arena. No canon promotion.

const Actor = preload("res://scripts/pilot_actor.gd")
const TrainingArena = preload("res://scenes/training_arena.tscn")
const WALKABLE_DECK = Rect2(Vector2(145, 410), Vector2(670, 112))

var ender: CharacterBody2D
var ionia: CharacterBody2D
var dialogue: Label
var status: Label
var dialogue_open: bool = false

func _ready() -> void:
    var actors := Node2D.new()
    actors.name = "YSortedActors"
    actors.y_sort_enabled = true
    add_child(actors)

    var player = Actor.new()
    player.name = "EnderPilot"
    player.character_name = "Ender"
    player.player_controlled = true
    player.walking_bounds = WALKABLE_DECK
    player.position = Vector2(350, 462)
    actors.add_child(player)
    ender = player

    var captain = Actor.new()
    captain.name = "IoniaPilot"
    captain.character_name = "Ionia"
    captain.walking_bounds = WALKABLE_DECK
    captain.position = Vector2(570, 458)
    actors.add_child(captain)
    ionia = captain

    var ui := CanvasLayer.new()
    add_child(ui)
    status = Label.new()
    status.position = Vector2(28, 28)
    status.add_theme_font_size_override("font_size", 19)
    status.text = "AETHERWAKE  /  GODOT PILOT   ·   Arrows: move   E: speak   B: arena"
    ui.add_child(status)
    dialogue = Label.new()
    dialogue.position = Vector2(100, 555)
    dialogue.add_theme_font_size_override("font_size", 23)
    dialogue.text = "Ionia: Candidate dock encounter. Visual and story acceptance pending."
    dialogue.visible = false
    ui.add_child(dialogue)
    queue_redraw()

func _draw() -> void:
    # Pilot-only support geometry, NOT a representation of accepted world topology.
    draw_rect(Rect2(Vector2.ZERO, Vector2(960, 640)), Color("#78a8c6"))
    draw_colored_polygon(PackedVector2Array([
        Vector2(0, 260), Vector2(280, 180), Vector2(470, 328), Vector2(620, 206),
        Vector2(960, 320), Vector2(960, 393), Vector2(0, 393)
    ]), Color("#879d80"))
    draw_rect(Rect2(Vector2(0, 393), Vector2(960, 247)), Color("#396f8b"))
    draw_colored_polygon(PackedVector2Array([
        Vector2(125, 404), Vector2(830, 404), Vector2(885, 534), Vector2(75, 534)
    ]), Color("#725744"))
    for plank in range(0, 10):
        var y := 407 + plank * 14
        draw_line(Vector2(136, y), Vector2(836, y), Color("#ba9164"), 2.0)
    for post in [170, 400, 660, 805]:
        draw_rect(Rect2(Vector2(post, 365), Vector2(13, 65)), Color("#5a4939"))
        draw_line(Vector2(post + 6, 375), Vector2(post + 6, 424), Color("#e0b977"), 2.0)
    draw_line(Vector2(174, 375), Vector2(816, 375), Color("#cba776"), 6.0)
    draw_rect(Rect2(Vector2(95, 542), Vector2(780, 86)), Color(0.04, 0.08, 0.18, 0.72))
    draw_string(ThemeDB.fallback_font, Vector2(26, 94), "Native Godot/GDScript technical slice — NOT an accepted gameplay capture", HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color("#172a45"))

func _unhandled_key_input(event: InputEvent) -> void:
    if not (event is InputEventKey) or not event.pressed or event.echo:
        return
    if event.keycode == KEY_E and ender.global_position.distance_to(ionia.global_position) <= 110.0:
        dialogue_open = not dialogue_open
        dialogue.visible = dialogue_open
    elif event.keycode == KEY_B:
        get_tree().change_scene_to_packed(TrainingArena)
    elif event.keycode == KEY_ESCAPE:
        dialogue_open = false
        dialogue.visible = false
