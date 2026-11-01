extends SceneTree
## Isolated fixtures are deliberately illustrative; NOT approved game stats.
const Rankings = preload("res://scripts/combat/level_one_rank_review.gd")

func _initialize() -> void:
    var fixture: Dictionary = {
        "ender": {"level": 1, "max_hp": 101, "max_mp": 64, "mag": 27},
        "lyra": {"level": 1, "max_hp": 86, "max_mp": 52, "mag": 19},
        "ionia": {"level": 1, "max_hp": 112, "max_mp": 28, "mag": 8},
        "reson": {"level": 1, "max_hp": 123, "max_mp": 20, "mag": 9},
        "aepex": {"level": 1, "max_hp": 108, "max_mp": 38, "mag": 11}
    }
    var before: Dictionary = fixture.duplicate(true)
    if not Rankings.validate(fixture)["ok"]:
        _fail("valid five-protagonist provisional profile rejected")
        return
    if fixture != before:
        _fail("validation mutated fixture")
        return
    var bad: Dictionary = fixture.duplicate(true)
    bad["ender"]["mag"] = bad["lyra"]["mag"]
    if Rankings.validate(bad)["ok"]:
        _fail("tied magic unexpectedly accepted")
        return
    bad = fixture.duplicate(true)
    bad["lyra"]["max_mp"] = bad["aepex"]["max_mp"]
    if Rankings.validate(bad)["ok"]:
        _fail("tied Lyra/Aepex MP unexpectedly accepted")
        return
    bad = fixture.duplicate(true)
    bad["aepex"]["max_hp"] = bad["ender"]["max_hp"]
    if Rankings.validate(bad)["ok"]:
        _fail("tied Ender/Aepex HP unexpectedly accepted")
        return
    bad = fixture.duplicate(true)
    bad["ionia"]["max_hp"] = bad["lyra"]["max_hp"] - 1
    if Rankings.validate(bad)["ok"]:
        _fail("Ionia below Lyra HP unexpectedly accepted")
        return
    bad = fixture.duplicate(true)
    bad["reson"]["mag"] = bad["ender"]["mag"] + 1
    if Rankings.validate(bad)["ok"]:
        _fail("Reson above Ender MAG unexpectedly accepted")
        return
    bad = fixture.duplicate(true)
    bad.erase("lyra")
    if Rankings.validate(bad)["ok"]:
        _fail("missing Lyra unexpectedly accepted")
        return
    bad = fixture.duplicate(true)
    bad["talen"] = {"level": 1, "max_hp": 10, "max_mp": 10, "mag": 10}
    if Rankings.validate(bad)["ok"]:
        _fail("extra character unexpectedly accepted")
        return
    bad = fixture.duplicate(true)
    bad["ender"]["max_mp"] = "64"
    if Rankings.validate(bad)["ok"]:
        _fail("text MP unexpectedly accepted")
        return
    bad = fixture.duplicate(true)
    bad["ender"]["level"] = 20
    if Rankings.validate(bad)["ok"]:
        _fail("non-Level-1 profile unexpectedly accepted")
        return
    bad = fixture.duplicate(true)
    bad["ender"]["mag"] = -1
    if Rankings.validate(bad)["ok"]:
        _fail("negative MAG unexpectedly accepted")
        return
    if fixture != before:
        _fail("negative fixtures mutated original")
        return
    print("NATIVE_LEVEL_ONE_RANK_REVIEW_PASS")
    quit(0)

func _fail(reason: String) -> void:
    push_error("NATIVE_LEVEL_ONE_RANK_REVIEW_FAIL: " + reason)
    quit(1)
