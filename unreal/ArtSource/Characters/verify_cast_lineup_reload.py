"""Read-only fresh-editor verification of the persisted TSTSS five-cast lookdev map."""
import json
from pathlib import Path
import unreal

MAP = "/Game/ArtLookdev/ReviewMaps/TSTSS_CastLineup_Review"
EXPECTED = ("Ender", "Ionia", "Lyra", "Reson", "Aepex")
world = unreal.EditorLoadingAndSavingUtils.load_map(MAP)
if world is None:
    raise RuntimeError("Cannot reopen persisted review map")
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = sub.get_all_level_actors()
labels = [a.get_actor_label() for a in actors]
missing = ["LOOKDEV_STATIC_"+n for n in EXPECTED if "LOOKDEV_STATIC_"+n not in labels]
if missing or labels.count("CALIBRATION_180CM_NONCANON") != 1:
    raise RuntimeError("Expected actors not found: " + str(missing) + "; labels: " + str(labels))
if len([l for l in labels if l.startswith("LOOKDEV_STATIC_")]) != 5:
    raise RuntimeError("Unexpected number of cast mesh actors")
records = []
for a in actors:
    label = a.get_actor_label()
    if label.startswith("LOOKDEV_STATIC_"):
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        mesh = c.get_editor_property("static_mesh") if c else None
        if mesh is None:
            raise RuntimeError(label + ": missing StaticMeshComponent asset")
        if not mesh.get_path_name().startswith("/Game/ArtLookdev/Characters/"):
            raise RuntimeError(label + ": unexpected content source")
        records.append({"actor": label, "mesh": mesh.get_path_name()})
output = Path(unreal.Paths.project_dir()) / "Saved" / "CharacterLookdev" / "cast_lineup_reload.json"
if output.exists():
    raise RuntimeError("Readback receipt already exists")
output.write_text(json.dumps({
    "status":"FRESH_EDITOR_MAP_READ_PASS",
    "map": MAP,
    "engine":unreal.SystemLibrary.get_engine_version(),
    "actors":records,
    "calibration": "CALIBRATION_180CM_NONCANON",
    "visual_rendered":False,
    "user_art_approval":False,
}, indent=2) + "\n", encoding="utf-8")
print("TSTSS_CAST_FRESH_REOPEN_PASS " + str(output))
