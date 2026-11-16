"""READ-ONLY Unreal Editor script: dump actor transforms and mesh bounds of one review map.

Runs under UnrealEditor-Cmd `-ExecutePythonScript` (see
run_aureate_envelope_export_native.py). Writes exactly one NEW snapshot JSON in
`aureate_envelope_snapshot_v1` format; judgement, tolerances and fail-closed
rules live in aureate_envelope_records.py, which this script does not import so
that it stays a dumb recorder.

Contract (asserted by test_aureate_envelope_export_source_contract.py):
- never saves a level, asset or package; never spawns, deletes or moves actors;
- refuses to overwrite an existing output file;
- refuses a map that is not under /Game/TSTSS/Review/ or an unsupported engine version;
- records the on-disk map SHA-256 taken BEFORE and AFTER loading and refuses if they differ;
- does not touch Starbourne content; creator art approval is not implied.

Inputs (environment): TSTSS_ENVELOPE_MAP (/Game/... path), TSTSS_ENVELOPE_FORM
(display form name), TSTSS_ENVELOPE_OUT (new .json path).
"""
import hashlib
import json
import os
import traceback
from pathlib import Path

import unreal

EXPECTED_ENGINE_PREFIX = "5.8"
ALLOWED_MAP_PREFIX = "/Game/TSTSS/Review/"
SCHEMA = "aureate_envelope_snapshot_v1"


def must(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def map_file(game_path):
    project_dir = Path(unreal.Paths.project_dir())
    relative = game_path[len("/Game/"):]
    return project_dir / "Content" / (relative + ".umap")


def vec(v):
    return [float(v.x), float(v.y), float(v.z)]


def actor_record(actor):
    components = actor.get_components_by_class(unreal.StaticMeshComponent)
    # Exactly one mesh component, else no local bounds: the converter then refuses the actor.
    local_bounds = None
    if len(components) == 1 and components[0].static_mesh is not None:
        bounds = components[0].static_mesh.get_bounds()
        local_bounds = {"origin": vec(bounds.origin), "extent": vec(bounds.box_extent)}
    transform = actor.get_actor_transform()
    quat = transform.rotation
    origin, extent = actor.get_actor_bounds(False)
    return {
        "label": actor.get_actor_label(),
        "location": vec(transform.translation),
        "rotation_quat": [float(quat.w), float(quat.x), float(quat.y), float(quat.z)],
        "scale": vec(transform.scale3d),
        "local_bounds": local_bounds,
        "world_aabb": {"origin": vec(origin), "extent": vec(extent)},
        "static_mesh_component_count": len(components),
    }


def main():
    report = {"state": "EXPORT_HOLD", "read_only": True}
    out_path = None
    try:
        game_map = os.environ.get("TSTSS_ENVELOPE_MAP", "")
        form = os.environ.get("TSTSS_ENVELOPE_FORM", "")
        out_path = Path(os.environ.get("TSTSS_ENVELOPE_OUT", ""))
        must(game_map.startswith(ALLOWED_MAP_PREFIX), "Map must be under " + ALLOWED_MAP_PREFIX)
        must(".." not in game_map and "." not in game_map.rsplit("/", 1)[-1], "Bad map path")
        must(bool(form), "TSTSS_ENVELOPE_FORM is required")
        must(str(out_path) not in ("", "."), "TSTSS_ENVELOPE_OUT is required")
        must(not out_path.exists(), "Refusing to overwrite an existing snapshot")
        version = unreal.SystemLibrary.get_engine_version()
        must(version.startswith(EXPECTED_ENGINE_PREFIX), "Unsupported engine version " + version)
        source = map_file(game_map)
        must(source.is_file(), "Map file missing on disk")
        before = sha256(source)
        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        must(bool(levels.load_level(game_map)), "Cannot load map")
        actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
        records = [actor_record(a) for a in actors]
        after = sha256(source)
        must(before == after, "Map file changed while exporting")
        snapshot = {"schema": SCHEMA, "ue_version": version, "map_path": game_map,
                    "map_sha256": before, "form": form, "units": "cm", "actors": records}
        out_path.write_text(json.dumps(snapshot, sort_keys=True, indent=2) + "\n", encoding="utf8")
        report.update({"state": "EXPORT_PASS_UNVERIFIED", "actors": len(records), "out": str(out_path)})
    except Exception as exc:  # noqa: BLE001 - recorder must report, never crash silently
        report["state"] = "EXPORT_HOLD"
        report["error"] = str(exc)
        report["traceback"] = traceback.format_exc()[-3000:]
    unreal.log("AUREATE_ENVELOPE_EXPORT " + json.dumps(report, sort_keys=True))
    if report["state"] != "EXPORT_PASS_UNVERIFIED":
        raise RuntimeError(report.get("error", "Envelope export held"))


main()
