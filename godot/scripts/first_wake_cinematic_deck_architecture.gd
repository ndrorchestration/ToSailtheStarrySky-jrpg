extends Node2D
## Original timber/brass vector stage dressing. The open-water splashdown is
## retained: no fabricated shore, tow, harbor or hidden vessel mode appears.
const DEEP := Color("#142533")
const TIMBER := Color("#745641")
const TIMBER_LIGHT := Color("#b18a61")
const BRASS := Color("#d9bb86")
const MINT := Color("#9dd7c4")
const WARN := Color("#eab078")
const STATION := Vector2(420, 351)

var reserve_inspected: bool = false

func set_reserve_inspected(value: bool) -> void:
    reserve_inspected = value
    queue_redraw()

func _poly(points: Array[Vector2], color: Color) -> void:
    draw_colored_polygon(PackedVector2Array(points), color)

func _draw() -> void:
    # The lower atmospheric horizon and deck do not disguise the ship at sea.
    draw_rect(Rect2(0, 381, 960, 19), Color(0.06, 0.18, 0.23, 0.58))
    for x in [28.0, 184.0, 791.0, 937.0]:
        draw_line(Vector2(x, 386), Vector2(x, 406), Color("#384e55"), 7.0)
        draw_circle(Vector2(x, 385), 4.0, BRASS.darkened(0.35))
    draw_line(Vector2(0, 392), Vector2(960, 392), Color("#947c62"), 7.0)
    draw_line(Vector2(0, 390), Vector2(960, 390), BRASS, 1.7)
    # Two diagonal structural spars frame the unobstructed crew activity lane.
    _poly([Vector2(0, 230), Vector2(22, 230), Vector2(115, 398), Vector2(96, 398)], Color("#3d3432"))
    _poly([Vector2(938, 229), Vector2(960, 229), Vector2(867, 398), Vector2(848, 398)], Color("#3d3432"))
    draw_line(Vector2(12, 230), Vector2(105, 394), TIMBER_LIGHT, 2.2)
    draw_line(Vector2(949, 230), Vector2(857, 394), TIMBER_LIGHT, 2.2)
    for pt in [Vector2(38, 283), Vector2(80, 356), Vector2(924, 283), Vector2(882, 356)]:
        draw_circle(pt, 3.0, BRASS)
    # The ship's timber foredeck: dark-underlit support, long-grain boards,
    # tapered seams, worn finish and independent fasteners in perspective.
    _poly([Vector2(0, 401), Vector2(960, 401), Vector2(960, 545), Vector2(0, 545)], Color("#302c2c"))
    _poly([Vector2(0, 400), Vector2(960, 400), Vector2(960, 531), Vector2(0, 531)], TIMBER)
    for row in range(9):
        var y0: float = 401.0 + float(row) * 15.0
        var y1: float = y0 + 15.0
        var tone: Color = Color("#88694d") if row % 2 == 0 else Color("#6b513f")
        _poly([Vector2(0, y0), Vector2(960, y0), Vector2(960, y1), Vector2(0, y1)], tone)
        draw_line(Vector2(0, y1), Vector2(960, y1), Color("#2a2929"), 1.5)
        draw_line(Vector2(0, y0 + 2), Vector2(960, y0 + 2), Color(0.99, 0.82, 0.60, 0.11), 1.0)
        for seam in range(1, 5):
            var xx: float = 46.0 + seam * 205.0 + 62.0 * float(row % 2)
            draw_line(Vector2(xx, y0 + 2), Vector2(xx - 3, y1 - 2), Color("#3e332f"), 1.5)
            draw_circle(Vector2(xx - 10, y0 + 5), 1.4, BRASS.darkened(0.45))
            draw_circle(Vector2(xx + 11, y0 + 5), 1.4, BRASS.darkened(0.45))
    draw_line(Vector2(0, 402), Vector2(960, 402), TIMBER_LIGHT, 3.0)
    draw_line(Vector2(0, 530), Vector2(960, 530), Color("#bd9b73"), 3.0)
    # Off-route ship furniture keeps the actor walk corridor legible.
    _poly([Vector2(42, 342), Vector2(131, 342), Vector2(146, 399), Vector2(27, 399)], Color("#3c3938"))
    draw_rect(Rect2(48, 349, 75, 42), Color("#465965"))
    draw_rect(Rect2(55, 354, 61, 3), Color("#98b4b0"))
    for y in [364.0, 377.0]:
        draw_line(Vector2(58, y), Vector2(113, y), Color("#bfbc9c"), 2.0)
    for x in [43.0, 132.0]:
        draw_line(Vector2(x, 341), Vector2(x, 398), BRASS.darkened(0.23), 3.0)
    _poly([Vector2(822, 353), Vector2(913, 353), Vector2(928, 399), Vector2(807, 399)], Color("#554638"))
    draw_line(Vector2(818, 355), Vector2(921, 355), BRASS, 3.0)
    for x in [826.0, 868.0, 910.0]:
        draw_line(Vector2(x, 356), Vector2(x + 7, 394), Color("#a68a64"), 2.0)
    # Reserve console: shallow extruded cabin fixture, inset bevel, metallic
    # ring, carefully bounded emissive-look glints (no bloom/postprocess claim).
    draw_rect(Rect2(347, 284, 147, 110), Color("#181f29"))
    _poly([Vector2(344, 285), Vector2(491, 285), Vector2(505, 394), Vector2(335, 394)], Color("#4c4141"))
    _poly([Vector2(354, 293), Vector2(484, 293), Vector2(490, 377), Vector2(346, 377)], Color("#203d49"))
    draw_line(Vector2(350, 289), Vector2(490, 289), BRASS, 3.0)
    draw_line(Vector2(351, 382), Vector2(490, 382), TIMBER_LIGHT, 4.0)
    for x in [355.0, 487.0]:
        for y in [298.0, 377.0]:
            draw_circle(Vector2(x, y), 2.4, BRASS.darkened(0.16))
    var glow: Color = MINT if reserve_inspected else WARN
    for k in range(7, 0, -1):
        var radius: float = 18.0 + k * 3.8
        draw_circle(STATION, radius, Color(glow.r, glow.g, glow.b, 0.010))
    draw_arc(STATION, 33.0, 0, TAU, 72, Color("#15242e"), 8.0, true)
    draw_arc(STATION, 28.0, 0, TAU, 72, BRASS.darkened(0.18), 3.0, true)
    draw_arc(STATION, 23.0, -PI * 0.7, PI * 0.8, 50, glow, 3.8, true)
    draw_line(STATION + Vector2(-17, -7), STATION + Vector2(17, -7), glow, 1.3, true)
    draw_line(STATION + Vector2(-12, 6), STATION + Vector2(12, 6), BRASS, 1.4, true)
    draw_circle(STATION, 4.0, glow)
    for x in [372.0, 391.0, 454.0, 471.0]:
        draw_rect(Rect2(x - 4, 302, 8, 4), BRASS.darkened(0.26))
    draw_string(ThemeDB.fallback_font, Vector2(366, 273),
        "HARMONIC RESERVE", HORIZONTAL_ALIGNMENT_LEFT, 120, 13, Color("#f5debb"))
    # Natural occluding rim, safe because it is below walkable character feet.
    draw_line(Vector2(0, 534), Vector2(960, 534), Color("#3b3734"), 7.0)
    draw_line(Vector2(0, 537), Vector2(960, 537), Color("#bc9f73"), 2.0)
    # Cinematic clear-contrast UI beds, behind live CanvasLayer labels.
    draw_rect(Rect2(0, 0, 960, 117), Color(0.035, 0.059, 0.092, 0.91))
    draw_line(Vector2(24, 110), Vector2(936, 110), Color("#d1ae7c"), 1.2)
    draw_rect(Rect2(0, 540, 960, 100), Color(0.035, 0.058, 0.083, 0.96))
    draw_line(Vector2(28, 547), Vector2(932, 547), Color("#d1ae7c"), 1.5)
    draw_line(Vector2(28, 626), Vector2(932, 626), Color(0.71, 0.79, 0.73, 0.22), 1.0)
    # Restrained contrast vignette at the left/right edges, never over text.
    for i in range(8):
        var alpha: float = (8.0 - float(i)) / 8.0 * 0.026
        draw_rect(Rect2(i * 7, 117, 7, 420), Color(0.03, 0.06, 0.09, alpha))
        draw_rect(Rect2(953 - i * 7, 117, 7, 420), Color(0.03, 0.06, 0.09, alpha))
