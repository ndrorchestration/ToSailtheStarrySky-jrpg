extends SceneTree
## Genuine native renderer images from the actual configured First Wake entry,
## real Area2D water contact and postflight actor scene. Local runner custody.
const Game = preload("res://scenes/first_wake_game.tscn")
var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("_capture")

func _advance(job) -> bool:
    for i in range(18):
        if not job.dialogue_open:
            return true
        if not job.interact():
            return false
    return not job.dialogue_open

func _private_preview_jpeg(frame: Image, label: String) -> void:
    # This art is public-safe. Low-resolution QA log only, not an artifact,
    # download, project asset or production visual acceptance receipt.
    if label == "03-reduced-motion-still-sea":
        return
    var reduced: Image = frame.duplicate()
    reduced.resize(480, 320, Image.INTERPOLATE_LANCZOS)
    var bytes: PackedByteArray = reduced.save_jpg_to_buffer(0.70)
    if bytes.is_empty() or bytes.size() > 180000:
        failures.append("bounded visual review JPEG was not encoded")
        return
    var encoded: String = Marshalls.raw_to_base64(bytes)
    print("TSTSS_POSTFLIGHT_PRIVATE_JPEG_BEGIN:" + label + ":480x320")
    for offset in range(0, encoded.length(), 3500):
        print("TSTSS_POSTFLIGHT_PRIVATE_JPEG_DATA:" + encoded.substr(offset, 3500))
    print("TSTSS_POSTFLIGHT_PRIVATE_JPEG_END:" + label)

func _photo(folder: String, name: String) -> Image:
    for frame in range(10):
        await process_frame
        await RenderingServer.frame_post_draw
    var image: Image = root.get_texture().get_image()
    if image == null or image.get_size() != Vector2i(960, 640):
        failures.append("native frame absent or resolution invalid: " + name)
        return null
    var path: String = folder.path_join(name + ".png")
    if image.save_png(path) != OK:
        failures.append("could not save real framebuffer " + name)
        return null
    print("TSTSS_CINEMATIC_DECK_FRAME: ", path)
    print("TSTSS_CINEMATIC_DECK_HASH: ", FileAccess.get_sha256(path))
    _private_preview_jpeg(image, name)
    return image

func _region_delta(left: Image, right: Image) -> float:
    if left == null or right == null:
        return 0.0
    var value: float = 0.0
    for y in range(302, 383, 5):
        for x in range(366, 482, 5):
            var a: Color = left.get_pixel(x, y)
            var b: Color = right.get_pixel(x, y)
            value += absf(a.r - b.r) + absf(a.g - b.g) + absf(a.b - b.b)
    return value

func _capture() -> void:
    if ProjectSettings.get_setting("application/run/main_scene") != "res://scenes/first_wake_game.tscn":
        failures.append("must enter through configured first-wake native game")
    var game = Game.instantiate()
    root.add_child(game)
    await process_frame
    var job = game.job
    if job == null:
        failures.append("actual Ender playable job scene absent")
    else:
        job.ender.position = job.FLYER_POSITION
        if not job.interact() or not _advance(job):
            failures.append("could not read authentic job notice")
        job.ender.position = job.IONIA_DOCK_POSITION
        if not job.interact() or not _advance(job):
            failures.append("Ionia-first recruitment did not complete")
        job.ender.position = job.GANGWAY_POSITION
        if not job.interact():
            failures.append("real gangway entry refused")
        for item in ["reference", "containment", "fuel"]:
            job.ender.position = job.ROOM_POSITIONS[item]
            if not job.interact() or not _advance(job):
                failures.append("real engineering evidence missing: " + item)
        job.ender.position = job.ROOM_POSITIONS["checklist"]
        if not job.interact() or not _advance(job) or not job.launch_flight_review():
            failures.append("authentic preflight refused")
        if failures.is_empty():
            var flight = job.flight_review
            if not flight.begin_short_test_flight():
                failures.append("real short flight failed")
            var warned: bool = false
            for tick in range(200):
                await process_frame
                if flight.phase == "warning":
                    warned = true
                    break
            if not warned or not flight.stabilize_for_water_descent():
                failures.append("real warning and abort were not observed")
            else:
                var waterborne: bool = false
                for tick in range(560):
                    await process_frame
                    if flight.phase == "waterborne":
                        waterborne = true
                        break
                if not waterborne or not flight.contact_observed or not flight.stable_float_verified:
                    failures.append("genuine Area2D water contact and float not established")
            for tick in range(120):
                await process_frame
                if game.game_stage == "postflight":
                    break
    if game.game_stage != "postflight" or game.postflight == null:
        failures.append("did not reach genuine player-controlled postflight scene")
    if not failures.is_empty():
        for error in failures:
            push_error("TSTSS_CINEMATIC_DECK_CAPTURE_FAIL: " + error)
        quit(1)
        return
    var deck = game.postflight
    if deck.cinematic_seascape == null or deck.ender == null:
        failures.append("cinematic environment not attached to actual playable deck")
    var folder: String = ProjectSettings.globalize_path("res://review-evidence/first-wake-cinematic-deck")
    if DirAccess.make_dir_recursive_absolute(folder) != OK:
        failures.append("native render evidence directory unavailable")
    var before: Image = await _photo(folder, "01-real-postflight-depleted-reserve")
    deck.ender.position = deck.RESERVE_STATION
    if not deck.interact_reserve():
        failures.append("Ender could not inspect real reserve")
    for line in range(deck.messages.size()):
        if not deck.interact_reserve():
            failures.append("interactive reserve dialogue failed")
            break
    if not deck.inspected_station or not game.session.can_checkpoint():
        failures.append("postflight reserve not actually inspected")
    var after: Image = await _photo(folder, "02-interactive-reserve-inspected")
    var pixel_delta: float = _region_delta(before, after)
    if pixel_delta < 6.0:
        failures.append("the rendered console did not visibly change after inspection")
    deck.set_reduced_motion(true)
    var still: Image = await _photo(folder, "03-reduced-motion-still-sea")
    if still == null or not deck.cinematic_seascape.reduced_motion:
        failures.append("reduced-motion scene was not captured")
    print("TSTSS_CINEMATIC_DECK_CONSOLE_DELTA: ", pixel_delta)
    game.queue_free()
    await process_frame
    if failures.is_empty():
        print("TSTSS_CINEMATIC_DECK_CAPTURE_PASS frames=3 native_gl=true",
            " real_ocean_contact=true interactive_console=true")
        quit(0)
    else:
        for error in failures:
            push_error("TSTSS_CINEMATIC_DECK_CAPTURE_FAIL: " + error)
        quit(1)
