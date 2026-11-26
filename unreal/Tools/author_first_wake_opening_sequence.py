"""Private native Sequencer authoring. Run in UE Editor Python, never commandlet.
Requires the reviewed stage map and actual placed camera/scene anchors.
Does not generate replacement art, edit existing maps, or overwrite an asset.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = json.loads((ROOT / "first_wake_opening_shots.json").read_text(encoding="utf-8"))

def validate_spec(spec):
    fps = spec["fps"]
    duration = spec["duration_seconds"]
    shots = spec["shots"]
    assert fps == 24 and duration == 86
    assert shots[0]["start"] == 0 and shots[-1]["end"] == duration
    assert len({s["id"] for s in shots}) == len(shots)
    for i, shot in enumerate(shots):
        assert 0 <= shot["start"] < shot["end"] <= duration
        assert shot["lens_mm"] > 0
        if i:
            assert shots[i-1]["end"] == shot["start"]
    previous = 0
    for i, voice in enumerate(spec["voice_windows"]):
        assert voice["cue"] == i+1
        assert previous <= voice["start"] < voice["end"] <= duration
        previous = voice["end"]

def transform_values(actor):
    loc = actor.get_actor_location()
    rot = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    values = [loc.x, loc.y, loc.z, rot.roll, rot.pitch, rot.yaw,
              scale.x, scale.y, scale.z]
    if not all(math.isfinite(v) for v in values):
        raise RuntimeError("Nonfinite camera transform")
    return values

def author():
    import unreal as u
    validate_spec(SPEC)
    asset_path = SPEC["sequence"]
    stage_map = SPEC["stage_map"]
    fps = SPEC["fps"]
    level = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    if not level or level.get_path_name().split(".")[0] != stage_map:
        raise RuntimeError("HOLD: open the exact isolated opening-stage map")
    if u.EditorAssetLibrary.does_asset_exist(asset_path):
        raise RuntimeError("HOLD: sequence exists; inspect rather than overwrite")
    actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    labels = {}
    for actor in actors:
        labels.setdefault(actor.get_actor_label(), []).append(actor)
    def unique(label):
        matches = labels.get(label, [])
        if len(matches) != 1:
            raise RuntimeError("HOLD: expected exactly one stage actor: " + label)
        return matches[0]
    for label in SPEC["required_stage_labels"]:
        unique(label)
    pairs = []
    for shot in SPEC["shots"]:
        first = unique("FW_CAM_" + shot["id"] + "_START")
        last = unique("FW_CAM_" + shot["id"] + "_END")
        if not isinstance(first, u.CineCameraActor) or not isinstance(last, u.CineCameraActor):
            raise RuntimeError("HOLD: camera markers must be CineCameraActors")
        if first.get_attach_parent_actor() or last.get_attach_parent_actor():
            raise RuntimeError("HOLD: camera markers must use world transforms")
        a, b = transform_values(first), transform_values(last)
        if a == b:
            raise RuntimeError("HOLD: identical start/end camera transforms: " + shot["id"])
        for axis in (3, 4, 5):
            b[axis] = a[axis] + (b[axis] - a[axis] + 180) % 360 - 180
        pairs.append((shot, first, a, b))
    voices = []
    for v in SPEC["voice_windows"]:
        path = "/Game/TSTSS/Review/Cinematics/Voice_PRIVATE/SW_EnderOpening_%02d" % v["cue"]
        sound = u.EditorAssetLibrary.load_asset(path)
        if not isinstance(sound, u.SoundWave):
            raise RuntimeError("HOLD: missing voice asset " + path)
        seconds = float(sound.get_editor_property("duration"))
        if not 0 < seconds <= v["end"] - v["start"]:
            raise RuntimeError("HOLD: voice exceeds assigned cue window " + path)
        voices.append((v, sound))
    # All inputs checked before creating any new asset. Camera bindings are
    # possessables of the isolated map, not global actors or gameplay pawns.
    directory, name = asset_path.rsplit("/", 1)
    seq = u.AssetToolsHelpers.get_asset_tools().create_asset(
        name, directory, u.LevelSequence, u.LevelSequenceFactoryNew())
    if not seq:
        raise RuntimeError("HOLD: sequence creation failed")
    try:
        seq.set_display_rate(u.FrameRate(fps, 1))
        seq.set_playback_start(0)
        seq.set_playback_end(SPEC["duration_seconds"] * fps)
        cuts = seq.add_track(u.MovieSceneCameraCutTrack)
        for shot, actor, start, end in pairs:
            lo, hi = shot["start"] * fps, shot["end"] * fps
            binding = seq.add_possessable(actor)
            if not binding.is_valid():
                raise RuntimeError("Camera binding failed")
            section = binding.add_track(u.MovieScene3DTransformTrack).add_section()
            section.set_range(lo, hi)
            channels = section.get_all_channels()
            if len(channels) != 9 or not all(isinstance(c, u.MovieSceneScriptingDoubleChannel) for c in channels):
                raise RuntimeError("Unexpected transform channel schema")
            for channel, a, b in zip(channels, start, end):
                channel.add_key(u.FrameNumber(lo), a)
                channel.add_key(u.FrameNumber(hi-1), b)
            cut = cuts.add_section()
            cut.set_range(lo, hi)
            cut.set_camera_binding_id(seq.get_binding_id(binding))
        audio = seq.add_track(u.MovieSceneAudioTrack)
        for v, sound in voices:
            section = audio.add_section()
            section.set_sound(sound)
            section.set_looping(False)
            section.set_suppress_subtitles(True)
            section.set_range(v["start"] * fps, v["end"] * fps)
        if seq.get_playback_start() != 0 or seq.get_playback_end() != 2064:
            raise RuntimeError("Playback range readback mismatch")
        if len(cuts.get_sections()) != 8 or len(audio.get_sections()) != 10:
            raise RuntimeError("Track section readback mismatch")
        if not u.EditorAssetLibrary.save_loaded_asset(seq, only_if_is_dirty=False):
            raise RuntimeError("Sequence save failed")
    except Exception:
        # A failed partial asset is never auto-deleted or declared admitted.
        u.log_error("FIRST_WAKE_OPENING_AUTHOR_HOLD: inspect unsaved private candidate")
        raise
    u.log("FIRST_WAKE_OPENING_AUTHOR_SAVED: 8 cuts, 10 voice sections, 2064 frames; native playback/visual gate OPEN")

if __name__ == "__main__":
    author()
