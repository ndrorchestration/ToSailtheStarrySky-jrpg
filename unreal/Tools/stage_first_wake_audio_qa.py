#!/usr/bin/env python3
"""Explicitly opt-in, editor-only First Wake audio QA scene stage.

Never called by CI. Creates a NEW review map and QA-only imported SoundWaves
in a disposable, detached, exact-head local checkout. Never changes source maps.
The result is a review candidate, NOT native audible acceptance or shipping art.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from import_first_wake_audio_review import (
    DESTINATION, EXPECTED, OPT_IN as IMPORT_OPT_IN, MIN_DISK_BYTES,
    MIN_RAM_BYTES, available_ram_bytes, verify_source,
)

STAGE_OPT_IN = "I_APPROVE_DISPOSABLE_QA_MAP_ONLY"
SOURCE_MAP = "/Game/TSTSS/Review/VerticalSlice/VS01_DenithHarbor"
DEST_MAP = "/Game/TSTSS/Audio/QAReview/VS01_DenithHarbor_OriginalQATest"
CUES = {
    "ui_confirm.wav": "ui.confirm",
    "repair_attuned.wav": "repair.station_inspect.success",
    "engine_warning.wav": "ship.engine.unstable",
    "mystery_echo.wav": "mystery.ship.reply",
    "weather_gust.wav": "weather.wind.gust",
    "splashdown_review.wav": "water.splashdown",
    "footstep_wood.wav": "foley.footstep.wood",
    "footstep_sand.wav": "foley.footstep.sand",
    "footstep_stone.wav": "foley.footstep.stone",
    "footstep_metal.wav": "foley.footstep.metal",
}

def _git(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args],
                       text=True, capture_output=True, timeout=20, check=True)
    return p.stdout.strip()

def preflight(project_dir: Path):
    if os.environ.get("TSTSS_AUDIO_STAGE_OPT_IN") != STAGE_OPT_IN:
        raise RuntimeError("Isolated audio-map staging opt-in missing")
    if os.environ.get("TSTSS_AUDIO_REVIEW_OPT_IN") != IMPORT_OPT_IN:
        raise RuntimeError("Independent QA WAV import opt-in missing")
    expected_sha = os.environ.get("TSTSS_AUDIO_EXPECTED_SOURCE_SHA", "").lower()
    if len(expected_sha) != 40 or any(c not in "0123456789abcdef" for c in expected_sha):
        raise RuntimeError("Full explicit source SHA required")
    project_dir = project_dir.resolve(strict=True)
    if project_dir.name.lower() != "unreal":
        raise RuntimeError("Expected a project named unreal within isolated worktree")
    root = project_dir.parent
    if "audioreview" not in root.name.lower():
        raise RuntimeError("Refusing a non-AudioReview worktree")
    if not (project_dir / "ToSailTheStarrySky.uproject").is_file():
        raise RuntimeError("Missing exact TSTSS Unreal project")
    if _git(root, "rev-parse", "HEAD").lower() != expected_sha:
        raise RuntimeError("Local source differs from explicit expected commit")
    ref_check = subprocess.run(
        ["git", "-C", str(root), "symbolic-ref", "-q", "HEAD"],
        text=True, capture_output=True, timeout=20, check=False,
    )
    if ref_check.returncode == 0:
        raise RuntimeError("Staging requires a detached review worktree")
    if ref_check.returncode != 1:
        raise RuntimeError("Could not establish detached source custody")
    if _git(root, "status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("Tracked source is dirty; refused")
    if available_ram_bytes() < MIN_RAM_BYTES:
        raise RuntimeError("Below minimum 6.5 GiB free RAM")
    if shutil.disk_usage(root).free < MIN_DISK_BYTES:
        raise RuntimeError("Below minimum 14 GiB free C: disk")
    source = os.environ.get("TSTSS_AUDIO_REVIEW_SOURCE", "")
    if not source:
        raise RuntimeError("Missing audio review source directory")
    paths = verify_source(Path(source))
    if {x.name for x in paths} != EXPECTED or set(CUES) != EXPECTED:
        raise RuntimeError("QA WAV source list and cue bindings disagree")
    return root, paths, expected_sha

def stage():
    import unreal  # editor-only, after import/rights/resource guard
    project = Path(unreal.Paths.project_dir())
    root, paths, sha = preflight(project)
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assets = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    if level.is_in_play_in_editor():
        raise RuntimeError("Cannot author assets while PIE is active")
    if not assets.does_asset_exist(SOURCE_MAP):
        raise RuntimeError("Missing source Denith Harbor map")
    if assets.does_asset_exist(DEST_MAP):
        raise RuntimeError("Disposable audio map exists; never overwrite")
    for path in paths:
        if assets.does_asset_exist(DESTINATION + "/QA_" + path.stem):
            raise RuntimeError("QA imported SoundWave already exists; refuse overwrite")

    # Always source original synthetic QA WAVs through Unreal's import task.
    # Interchange may ignore destination_name, so validate actual paths.
    tasks = []
    for file in sorted(paths):
        task = unreal.AssetImportTask()
        task.filename = str(file)
        task.destination_path = DESTINATION
        task.destination_name = "QA_" + file.stem
        task.automated = True
        task.replace_existing = False
        task.save = False
        tasks.append(task)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    actual = [str(obj) for task in tasks for obj in task.imported_object_paths]
    if len(actual) != len(EXPECTED):
        raise RuntimeError("Incorrect QA SoundWave import count; stop without map edits")

    sound_by_filename = {}
    for task, file in zip(tasks, sorted(paths)):
        obj_paths = [str(p) for p in task.imported_object_paths]
        if len(obj_paths) != 1 or not obj_paths[0].startswith(DESTINATION + "/"):
            raise RuntimeError("Imported source outside isolated QA directory")
        sound = assets.load_asset(obj_paths[0])
        if sound is None or not isinstance(sound, unreal.SoundWave):
            raise RuntimeError("Imported asset is not a SoundWave: " + file.name)
        sound_by_filename[file.name] = sound

    # No source map is opened or saved. Copy to the guaranteed-absent QA path
    # via 5.8 LevelEditorSubsystem (not the legacy duplicate+load route).
    if not level.new_level_from_template(DEST_MAP, SOURCE_MAP):
        raise RuntimeError("Could not create disposable map from Denith source")
    starts = [
        actor for actor in actors.get_all_level_actors()
        if isinstance(actor, unreal.PlayerStart)
    ]
    if not starts:
        raise RuntimeError("Audio QA map lacks a PlayerStart; no arbitrary placement")
    origin = starts[0].get_actor_location()
    rotation = unreal.Rotator(0.0, 0.0, 0.0)

    def add(class_name, label):
        clazz = unreal.load_class(None, "/Script/ToSailTheStarrySky." + class_name)
        if clazz is None:
            raise RuntimeError("Uncompiled C++ audio class: " + class_name)
        placed = actors.spawn_actor_from_class(clazz, origin, rotation, False)
        if placed is None:
            raise RuntimeError("Failed to place QA actor " + class_name)
        placed.set_actor_label(label)
        return placed

    bank = add("TSTSSAudioCueBankActor", "TSTSS_AUDIO_QA_CueBank")
    mix = add("TSTSSAudioEnvironmentDirector", "TSTSS_AUDIO_QA_HarborMix")
    zone = add("TSTSSHarborAudioZone", "TSTSS_AUDIO_QA_HarborZone")
    add("TSTSSFootstepAudioDirector", "TSTSS_AUDIO_QA_Footsteps")

    entries = []
    for filename, event_id in sorted(CUES.items()):
        cue = unreal.TSTSSAudioCue()
        cue.set_editor_property("event_id", unreal.Name(event_id))
        cue.set_editor_property("sound", sound_by_filename[filename])
        cue.set_editor_property("gain", 0.4)
        entries.append(cue)
    bank.set_editor_property("cues", entries)
    zone.set_editor_property("harbor_audio", mix)
    # Ambience fields remain empty rather than pretending the ten review
    # samples contain real surf/gulls/market loops or cleared music.

    # Save only QA audio source packages before their referring map package.
    # This avoids saving a map referencing still-unsaved SoundWaves.
    for filename in sorted(CUES):
        path = DESTINATION + "/QA_" + Path(filename).stem
        if not assets.save_asset(path, False):
            raise RuntimeError("QA-only SoundWave save failed: " + filename)
    if not level.save_current_level():
        raise RuntimeError("QA map save failed; no native playable claim")
    receipt = {
        "status": "STAGED_QA_UNAUDITIONED_NOT_RELEASE_AUTHORIZED",
        "source_sha": sha,
        "review_map": DEST_MAP,
        "placed_actors": 4,
        "soundwave_count": len(CUES),
        "audio_monitoring": "NOT_TESTED",
        "gameplay_physics": "UNCHANGED",
        "sample_rights": "ORIGINAL_SYNTHETIC_QA_ONLY",
    }
    report = root / "unreal" / "Saved" / "AudioNativeReview" / "qa-scene-stage.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    unreal.log("TSTSS isolated audio map STAGED ONLY, no listening verified: " + str(report))
    return receipt

if __name__ == "__main__":
    result = stage()
    print(json.dumps(result, indent=2))
