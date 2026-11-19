extends SceneTree
## Shader/native node-level QA. Does NOT impersonate an ocean landing or grant story.
const DeckEnvironment = preload("res://scripts/first_wake_cinematic_seascape.gd")
var failures: Array[String] = []
var checks: int = 0

func _initialize() -> void:
    call_deferred("_run")

func verify(ok: bool, what: String) -> void:
    checks += 1
    if not ok:
        failures.append(what)

func _run() -> void:
    var stage := DeckEnvironment.new()
    root.add_child(stage)
    await process_frame
    var snap: Dictionary = stage.visual_snapshot()
    verify(snap.get("real_native_sky_shader", false), "real native sky material required")
    verify(snap.get("real_native_sea_shader", false), "real native sea material required")
    verify(snap.get("maritime_architecture", false), "actual ship deck geometry required")
    verify(snap.get("cinematic_2d_preview", false), "this is visual stage dressing")
    verify(snap.get("story_authority", true) == false, "art has no story authority")
    verify(snap.get("collision_authority", true) == false, "art has no collision authority")
    verify(snap.get("production_art_approved", true) == false, "technical QA is not art approval")
    verify(stage.sky.size == Vector2(960, 401), "sky covers authored viewport")
    verify(stage.sea.position == Vector2(0, 286), "sea begins below horizon")
    verify(stage.sea.size == Vector2(960, 115), "sea stays behind actual open-air deck")
    var sea_material := stage.sea.material as ShaderMaterial
    verify(sea_material != null and sea_material.shader != null, "actual GPU water shader exists")
    stage.set_reduced_motion(true)
    verify(stage.reduced_motion
        and sea_material.get_shader_parameter("motion_scale") == 0.0,
        "reduced motion stops shader animation")
    stage.set_reduced_motion(false)
    verify(not stage.reduced_motion
        and sea_material.get_shader_parameter("motion_scale") == 1.0,
        "motion toggle is reversible")
    stage.set_reserve_inspected(true)
    verify(stage.architecture.reserve_inspected, "reserve light changes only via explicit state")
    stage.set_reserve_inspected(false)
    verify(not stage.architecture.reserve_inspected, "reserve state can be restored")
    verify(stage.get_child_count() == 3, "only sky, water and physical-free stage art")
    stage.queue_free()
    await process_frame
    if failures.is_empty():
        print("TSTSS_FIRST_WAKE_CINEMATIC_DECK_PASS checks=", checks,
            " native_shaders=true motion_accessibility=true story_unchanged=true")
        quit(0)
    else:
        for error in failures:
            push_error("TSTSS_FIRST_WAKE_CINEMATIC_DECK_FAIL: " + error)
        quit(1)
