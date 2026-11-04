"""Independent read-only Unreal asset-world verification; not gameplay or art acceptance."""
from pathlib import Path
import hashlib
import json
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
EVIDENCE = PROJECT / "Saved/AssetAssemblyEvidence"
STAGE_FILE = EVIDENCE / "first_wake_asset_scene_native_v3_20261104.json"
OUT = EVIDENCE / "first_wake_asset_scene_readback_v3_20261104.json"
MAP_FILE = PROJECT / "Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3.umap"
BASE_FILE = PROJECT / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"
BASE_SHA = "4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80"
STOPS = ("FlyerDiscovery","IoniaHiring","AureateBoarding","LiftStation",
         "PressureStation","ReserveStation","EngineeringApproval")


def fail_if(value, message):
    if value:
        raise RuntimeError("INDEPENDENT_ASSET_MAP_READBACK_HOLD: " + message)


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


fail_if(PROJECT.name.lower() != "unreal" or PROJECT.parent.name != "TSTSS_AssetAssembly_20261104",
        "invalid project")
fail_if(OUT.exists(), "immutable readback receipt already exists")
fail_if(not STAGE_FILE.is_file() or not MAP_FILE.is_file() or not BASE_FILE.is_file(),
        "stage manifest, map or source template absent")
stage = json.loads(STAGE_FILE.read_text(encoding="utf-8"))
fail_if(stage.get("status") != "NATIVE_ASSET_WORLD_SAVED_PENDING_INDEPENDENT_READBACK",
        "stage source not accepted")
fail_if(stage.get("new_map_sha256") != sha(MAP_FILE), "staged map bytes drifted")
fail_if(sha(BASE_FILE) != BASE_SHA, "base map digest changed")
fail_if(stage.get("new_map_package") !=
        "/Game/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3",
        "map package mismatch")
fail_if(len(stage.get("staged_actor_labels",[])) != 10, "not 10 asset stage labels")

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
fail_if(not level.load_level(stage["new_map_package"]), "native saved map reload failed")
all_actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
labels = [a.get_actor_label() for a in all_actors]
label_index = {}
for actor in all_actors:
    label = actor.get_actor_label()
    fail_if(label in label_index, "duplicate actor labels")
    label_index[label] = actor
for stop in STOPS:
    name = "TSTSS_PRELUDE_REVIEW_" + stop
    fail_if(name not in label_index or
            label_index[name].get_class().get_name() != "TSTSSMilestoneActor",
            "missing original reflected milestone: " + name)
starts = [a for a in all_actors if isinstance(a, unreal.PlayerStart)]
fail_if(len(starts) != 1, "expected exactly one original PlayerStart")
added = stage["staged_actor_labels"]
fail_if(any(labels.count(label) != 1 for label in added), "missing/duplicated staged art")
paths = stage["native_mesh_paths"]
spec = {
    "TSTSS_ASSET_REVIEW_AUREATE_HULL_PROXY_NOT_APPROVED": "/Engine/BasicShapes/Sphere",
    "TSTSS_ASSET_REVIEW_AUREATE_SHARED_V4_TRIM": paths["hull_trim"],
    "TSTSS_ASSET_REVIEW_AUREATE_CURVED_QUARTERS": paths["quarters"],
    "TSTSS_ASSET_REVIEW_AUREATE_GEODESIC_BRIDGE": paths["bridge"],
    "TSTSS_ASSET_REVIEW_AUREATE_FORE_PORT_LEAF": paths["wing"],
    "TSTSS_ASSET_REVIEW_AUREATE_FORE_STARBOARD_LEAF": paths["wing"],
    "TSTSS_ASSET_REVIEW_AUREATE_AFT_PORT_LEAF": paths["wing"],
    "TSTSS_ASSET_REVIEW_AUREATE_AFT_STARBOARD_LEAF": paths["wing"],
    "TSTSS_ASSET_REVIEW_IONIA_STATIC_REVIEW_NOT_NPC": paths["ionia"],
    "TSTSS_ASSET_REVIEW_ENDER_STATIC_REVIEW_NOT_PAWN": paths["ender_v2"],
}
fail_if(set(spec) != set(added), "unexpected staged actor identity set")
resolved = {}
for label, asset_path in spec.items():
    actor = label_index[label]
    fail_if(not isinstance(actor, unreal.StaticMeshActor),
            "staged art is not static mesh: " + label)
    comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    fail_if(not comp, "missing mesh component: " + label)
    mesh = comp.get_editor_property("static_mesh")
    fail_if(not isinstance(mesh, unreal.StaticMesh), "missing native mesh: " + label)
    actual = mesh.get_path_name().split(".")[0]
    fail_if(actual != asset_path, "wrong imported mesh path for " + label + ": " + actual)
    fail_if(actor.get_actor_enable_collision(), "asset stage unexpectedly collides: " + label)
    resolved[label] = actual
fail_if(any("STARBOURNE" in label.upper() for label in labels),
        "gated form visible as actor in First Wake")
fail_if(sha(MAP_FILE) != stage["new_map_sha256"], "map changed during readback")
fail_if(sha(BASE_FILE) != BASE_SHA, "original map changed during readback")
report = {
    "status": "INDEPENDENT_NATIVE_SAVED_WORLD_READBACK_PASS_NOT_PIE",
    "engine": unreal.SystemLibrary.get_engine_version(),
    "map_package": stage["new_map_package"],
    "map_sha256": sha(MAP_FILE),
    "base_map_sha256": BASE_SHA,
    "total_actor_count": len(all_actors),
    "milestone_count": len(STOPS),
    "player_start_count": len(starts),
    "imported_asset_actor_count": len(spec),
    "asset_paths_verified": resolved,
    "actor_collision_disabled": True,
    "native_map_saved_during_readback": False,
    "real_player_input_verified": False,
    "cinematic_art_approved": False,
    "native_gpu_screenshot_produced": False,
    "starbourne_player_unlocked": False,
}
OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
unreal.log("TSTSS_FIRST_WAKE_ASSET_MAP_INDEPENDENT_READBACK_PASS " + json.dumps({
    "map_sha256": report["map_sha256"],
    "total_actor_count": report["total_actor_count"],
    "asset_actor_count": len(spec)}))
