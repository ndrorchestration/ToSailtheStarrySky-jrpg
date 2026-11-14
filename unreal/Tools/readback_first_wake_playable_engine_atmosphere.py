#!/usr/bin/env python3
"""Fresh-editor, read-only audit of the isolated First Wake VS02 atmosphere stage.

No game-level or source writes. The only output is a receipt under Saved/.
Run after native map authoring in a NEW Unreal Editor process, before PIE.
This checks the actual persisted level after reopen; source fixtures alone
do not count as native gameplay or cinematic quality evidence.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stage_first_wake_playable_engine_atmosphere as stage  # noqa: E402
import first_wake_surface_textures as surface  # noqa: E402

RECEIPT = stage.PROJECT / "Saved/EngineFocusGameplayV1/map_atmosphere_readback.json"
DIRECTOR = stage.LABEL
LIGHTS = tuple(
    "TSTSS_SURFACE_REVIEW_VS02_AureateInteriors_Practical_" + str(i)
    for i in range(2)
)
GAUGE = "TSTSS_VS_REVIEW_InstrumentCore_LIFT"
ENGINE = "TSTSS_VS_REVIEW_MainHarmonicLevitationEngine_Proxy"
EXPECTED_TOTAL = stage.EXPECTED_ORIGINAL_ACTORS - len(stage.ORIGINAL_LIGHTS) + 3


def inventory_contract(rows: list[tuple[str, str]]) -> dict:
    """Pure, fail-closed review of actor label and native class names."""
    labels = [label for label, _ in rows]
    stage.require(len(rows) == EXPECTED_TOTAL, "persisted map actor count drift")
    stage.require(len(labels) == len(set(labels)), "duplicate persisted actor label")
    for name in (*stage.ORIGINAL_LIGHTS,):
        stage.require(name not in labels, "obsolete sky actor survived: " + name)
    for name in (DIRECTOR, *LIGHTS, GAUGE, ENGINE):
        stage.require(labels.count(name) == 1,
                      "missing/duplicate persisted actor: " + name)
    directors = [
        name for name, cls in rows if cls == "TSTSSAtmosphereDirector"
    ]
    stage.require(directors == [DIRECTOR],
                  "persisted weather owner missing, relabeled or duplicated")
    for name in LIGHTS:
        stage.require((name, "PointLight") in rows,
                      "authored practical lost PointLight class: " + name)
    return {
        "actor_count": len(rows), "weather_authority_count": len(directors),
        "director_label": directors[0],
        "practical_labels": list(LIGHTS),
        "gauge_present": True, "old_sky_actor_count": 0,
    }


def self_test() -> dict:
    others = [
        ("TSTSS_UNRELATED_REVIEW_ACTOR_%02d" % i, "StaticMeshActor")
        for i in range(EXPECTED_TOTAL - 5)
    ]
    correct = [
        (DIRECTOR, "TSTSSAtmosphereDirector"),
        (LIGHTS[0], "PointLight"), (LIGHTS[1], "PointLight"),
        (GAUGE, "StaticMeshActor"), (ENGINE, "StaticMeshActor"),
        *others,
    ]
    assert inventory_contract(correct)["weather_authority_count"] == 1
    negative = [
        correct[:-1],
        [*correct, correct[0]],
        [("WrongDirector", "TSTSSAtmosphereDirector") if x[0] == DIRECTOR
         else x for x in correct],
        [(DIRECTOR, "StaticMeshActor") if x[0] == DIRECTOR else x
         for x in correct],
        [(LIGHTS[0], "StaticMeshActor") if x[0] == LIGHTS[0] else x
         for x in correct],
        [(GAUGE + "_renamed", x[1]) if x[0] == GAUGE else x
         for x in correct],
        [(stage.ORIGINAL_LIGHTS[0], x[1]) if x[0] == others[0][0] else x
         for x in correct],
    ]
    for rows in negative:
        try:
            inventory_contract(rows)
        except RuntimeError:
            continue
        raise AssertionError("readback negative fixture was accepted")
    return {
        "status": "PLAYABLE_ENGINE_NATIVE_READBACK_OFFLINE_FIXTURES_PASS",
        "positive_cases": 1, "negative_cases": len(negative),
        "native_editor_opened": False, "pie": "NOT_RUN",
    }


def native_readback() -> dict:
    stage.require(sys.platform == "win32",
                  "native readback requires Windows editor")
    stage.require(stage.ROOT.name == stage.WORKTREE,
                  "wrong review feature worktree")
    stage.require(os.getenv("TSTSS_GAMEPLAY_ENGINE_READBACK_EXPLICIT") == "1",
                  "explicit native readback opt-in absent")
    expected = os.getenv("TSTSS_GAMEPLAY_ENGINE_EXPECTED_HEAD", "").strip().lower()
    stage.require(bool(re.fullmatch("[0-9a-f]{40}", expected)),
                  "missing exact review source head")
    stage.require(stage.git("rev-parse", "HEAD").lower() == expected,
                  "source head drift from exact readback request")
    stage.require(stage.RECEIPT.is_file(),
                  "native authoring receipt not present")
    stage.require(not RECEIPT.exists(),
                  "native readback receipt already occupies target")
    before = json.loads(stage.RECEIPT.read_text(encoding="utf-8"))
    stage.require(before.get("status")
                  == "NATIVE_GAMEPLAY_MAP_AUTHORED_NOT_PIE_OR_APPROVED",
                  "native authoring receipt is not accepted source evidence")
    stage.require(before.get("exact_head") == expected,
                  "stage and readback heads disagree")
    stage.require(before.get("original_sha256")
                  == stage.EXPECTED_ORIGINAL_SHA,
                  "original source map provenance drift")
    map_hash = stage.digest(stage.MAP_FILE)
    stage.require(before.get("new_gameplay_map_sha256") == map_hash,
                  "actual persisted map hash differs from authoring receipt")
    status = stage.git("status", "--porcelain", "-uall").splitlines()
    map_path = "unreal/Content/TSTSS/Review/VerticalSlice/VS02_AureateInteriors.umap"
    stage.require(status == [" M " + map_path],
                  "unexpected working tree changes beyond one staged VS02 .umap")
    for config in stage.PROTECTED_CONFIG:
        stage.require(stage.digest(stage.PROJECT / "Config" / config)
                      == before["config_sha256"][config],
                      "protected project config differs from authoring receipt")
    import unreal as u
    stage.require(u.SystemLibrary.get_engine_version().startswith("5.8.4"),
                  "actual UE 5.8.4 native Editor required")
    stage.require(not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
                  and not u.EditorLoadingAndSavingUtils.get_dirty_content_packages(),
                  "unsaved editor assets present before readback")
    world = u.EditorLoadingAndSavingUtils.load_map(stage.MAP_ASSET)
    stage.require(world is not None,
                  "persisted playable VS02 could not be reopened")
    sysactors = u.get_editor_subsystem(u.EditorActorSubsystem)
    stage.require(sysactors is not None, "native actor subsystem unavailable")
    actors = list(sysactors.get_all_level_actors())
    audit = inventory_contract([
        (a.get_actor_label(), a.get_class().get_name())
        for a in actors
    ])
    bylabel = {a.get_actor_label(): a for a in actors}
    director = bylabel[DIRECTOR]
    stage.require(director.get_editor_property("initial_weather")
                  == surface.weather_enum_value(u, "Clear"),
                  "reopened director initial weather drift")
    stage.require(abs(float(director.get_editor_property("initial_clock_hours"))
                      - 17.1) < 0.01,
                  "reopened weather owner initial clock drift")
    stage.require(not director.get_editor_property("autoplay_review_cycle"),
                  "reopened atmosphere has automatic cycling enabled")
    stage.require(not director.get_editor_property("reduced_motion"),
                  "reopened review atmosphere reduced-motion default drift")
    lamp_rows = []
    for i, values in enumerate(surface.PRACTICAL_LAMPS[stage.SCENE]):
        actor = bylabel[LIGHTS[i]]
        component = actor.get_component_by_class(u.PointLightComponent)
        stage.require(component is not None, "native practical component absent")
        actual = actor.get_actor_location()
        stage.require(max(
            abs(float(actual.x) - values[0]),
            abs(float(actual.y) - values[1]),
            abs(float(actual.z) - values[2]),
        ) < 0.01, "reopened practical position differs from existing recipe")
        stage.require(abs(float(component.get_editor_property("intensity"))
                          - float(values[3])) < 0.01,
                      "reopened practical luminous intensity drift")
        lamp_rows.append({
            "label": LIGHTS[i], "location_cm": list(values[:3]),
            "lumens": float(values[3]),
        })
    stage.require(stage.digest(stage.MAP_FILE) == map_hash,
                  "readback mutated the actual gameplay .umap")
    for config in stage.PROTECTED_CONFIG:
        stage.require(stage.digest(stage.PROJECT / "Config" / config)
                      == before["config_sha256"][config],
                      "config drift after native reloading")
    result = {
        "schema": "tstss.firstwake.playable_engine.native_map_readback.v1",
        "status": "NATIVE_VS02_MAP_REOPEN_ATMOSPHERE_PASS_NOT_PIE",
        "exact_head": expected,
        "map": stage.MAP_ASSET,
        "map_sha256": map_hash,
        **audit,
        "weather": "Clear",
        "initial_clock_hours": 17.1,
        "practicals": lamp_rows,
        "source_dirty_scope": status,
        "native_pie": "NOT_RUN",
        "player_camera_input_test": "NOT_RUN",
        "visual_approval": "NOT_ESTABLISHED",
        "merged": False,
        "map_saved_by_readback": False,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    with RECEIPT.open("x", encoding="utf-8") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    u.log("TSTSS_PLAYABLE_ENGINE_NATIVE_VS02_REOPEN_PASS_NOT_PIE " + map_hash)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--readback", action="store_true")
    args = parser.parse_args()
    try:
        output = self_test() if args.self_test else native_readback()
        print(json.dumps(output, indent=2))
    except RuntimeError as err:
        print(str(err), file=sys.stderr)
        raise SystemExit(2) from err
