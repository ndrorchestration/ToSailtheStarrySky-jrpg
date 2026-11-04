"""Stage existing imported draft art in a new First Wake gameplay-review level.

Must run only in isolated TSTSS_AssetAssembly_20261104 UE 5.8.4 worktree.
This creates a separate review map; it never edits the original seven-stop
Prelude, production maps, Story/SaveGame data, or the Starbourne player gate.
Native map save/readback is NOT PIE or cinematic art approval.
"""
import hashlib
import json
import traceback
from pathlib import Path
from datetime import datetime, timezone

import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
ROOT = PROJECT.parent
BASE_MAP = "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2"
DEST_MAP = "/Game/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3"
BASE_FILE = PROJECT / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"
DEST_FILE = PROJECT / "Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3.umap"
BASE_SHA = "4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80"
RECEIPT = PROJECT / "Saved/AssetAssemblyEvidence/first_wake_asset_scene_native_v3_20261104.json"
PREFIX = "TSTSS_ASSET_REVIEW_"
STOPS = ("FlyerDiscovery", "IoniaHiring", "AureateBoarding",
         "LiftStation", "PressureStation", "ReserveStation", "EngineeringApproval")
ASSETS = {
    "hull_trim": "/Game/TSTSS/Review/ShipArt/CinematicV4/AureateWake_SharedExteriorTrim_V4_REVIEW/StaticMeshes/AureateWake_SharedExteriorTrim_V4_REVIEW",
    "wing": "/Game/TSTSS/Review/ShipArt/WingCinematicCandidate_20261103/AureateWake_Wing_Lookdev/StaticMeshes/AureateWake_Wing_Lookdev",
    "bridge": "/Game/TSTSS/Review/ShipArt/CoupledHabitation_20261104/AureateWake_CoupledBridge_Geodesic_REVIEW/StaticMeshes/AureateWake_CoupledBridge_Geodesic_REVIEW",
    "quarters": "/Game/TSTSS/Review/ShipArt/CoupledHabitation_20261104/AureateWake_CurvedLivingQuarters_REVIEW/StaticMeshes/AureateWake_CurvedLivingQuarters_REVIEW",
    "ionia": "/Game/ArtLookdev/Characters/Ionia/Ionia/StaticMeshes/Ionia",
    "ender_v2": "/Game/ArtLookdev/Characters/EnderFidelityV2/Ender_ender_fidelity_v2/StaticMeshes/Ender_ender_fidelity_v2",
}
MIN_SLOTS = {"hull_trim": 4, "wing": 3, "bridge": 3, "quarters": 3,
             "ionia": 1, "ender_v2": 1}


def must(condition, message):
    if not condition:
        raise RuntimeError("ASSET_ASSEMBLY_HOLD: " + message)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def triples(point):
    return [float(point.x), float(point.y), float(point.z)]


report = {
    "status": "NOT_STARTED",
    "authority": "ISOLATED_NONCANONICAL_ASSET_SCENE_ONLY",
    "pie_input_verified": False,
    "cinematic_approval": False,
    "collision_or_water_physics_verified": False,
    "ender_rig_animation_verified": False,
    "starbourne_player_unlocked": False,
    "production_assets_modified": False,
    "original_map_modified": False,
}
try:
    must(ROOT.name == "TSTSS_AssetAssembly_20261104" and PROJECT.name.lower() == "unreal",
         "unexpected project root")
    must(unreal.SystemLibrary.get_engine_version().startswith("5.8."),
         "unexpected Unreal engine family")
    must(BASE_FILE.is_file() and digest(BASE_FILE) == BASE_SHA,
         "original Prelude asset digest changed")
    must(not DEST_FILE.exists() and not RECEIPT.exists(),
         "review map/receipt exists; cannot overwrite")
    save_root = PROJECT / "Saved/SaveGames"
    must(not save_root.exists() or not list(save_root.glob("*.sav")),
         "review SaveGame files present; cannot stage")
    config_paths = [PROJECT / "Config/DefaultEngine.ini", PROJECT / "Config/DefaultInput.ini"]
    config_hashes = {p.name: digest(p) for p in config_paths}

    meshes = {}
    for key, path in ASSETS.items():
        mesh = unreal.load_asset(path)
        must(isinstance(mesh, unreal.StaticMesh), "native mesh missing: " + key)
        slots = len(mesh.get_editor_property("static_materials"))
        must(slots >= MIN_SLOTS[key], "material sections missing: " + key)
        meshes[key] = mesh
    primitive = unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere")
    must(isinstance(primitive, unreal.StaticMesh), "engine hull review proxy missing")

    library = unreal.EditorAssetLibrary
    must(library.does_asset_exist(BASE_MAP), "original Unreal World not registered")
    must(not library.does_asset_exist(DEST_MAP), "target World already registered")
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    # One Unreal operation creates and opens the new map from the authored V2 template.
    # Duplicating then loading in a single Python frame caused a world-GC fatal in v1.
    must(bool(levels.new_level_from_template(DEST_MAP, BASE_MAP)),
         "Editor cannot create and open new World from V2 template")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    before = list(actors.get_all_level_actors())
    names = [a.get_actor_label() for a in before]
    for stop in STOPS:
        must(sum(1 for n in names if n == "TSTSS_PRELUDE_REVIEW_" + stop) == 1,
             "missing or duplicate original milestone: " + stop)
    must(sum(isinstance(a, unreal.PlayerStart) for a in before) == 1,
         "player start not preserved")
    must(not any(n.startswith(PREFIX) for n in names),
         "stage labels already present in duplicate")

    added = []
    def stage(label, mesh, position, angles=(0, 0, 0), scale=(1, 1, 1)):
        actor = actors.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(*position), unreal.Rotator(*angles))
        must(actor is not None, "actor spawn failed: " + label)
        comp = actor.static_mesh_component
        must(comp is not None and comp.set_static_mesh(mesh),
             "native mesh assignment failed: " + label)
        actor.set_actor_label(PREFIX + label)
        actor.set_actor_scale3d(unreal.Vector(*scale))
        actor.set_actor_enable_collision(False)
        comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        added.append(actor.get_actor_label())
        return actor

    def rel(base, delta):
        return tuple(a + b for a, b in zip(base, delta))

    # Preserve review route and reach: vessel is across the visual-only shoreline.
    origin = (-850, 980, 185)
    stage("AUREATE_HULL_PROXY_NOT_APPROVED", primitive, origin, scale=(7.9, 1.15, 0.55))
    stage("AUREATE_SHARED_V4_TRIM", meshes["hull_trim"], origin)
    stage("AUREATE_CURVED_QUARTERS", meshes["quarters"], origin)
    stage("AUREATE_GEODESIC_BRIDGE", meshes["bridge"], rel(origin, (170, 0, 133)))
    wings = (
        ("FORE_PORT", (145, -99, 55), (0, -80, -8)),
        ("FORE_STARBOARD", (145, 99, 55), (0, 80, 8)),
        ("AFT_PORT", (-180, -99, 53), (0, -102, -8)),
        ("AFT_STARBOARD", (-180, 99, 53), (0, 102, 8)),
    )
    for label, xyz, rpy in wings:
        stage("AUREATE_" + label + "_LEAF", meshes["wing"], rel(origin, xyz), rpy)
    stage("IONIA_STATIC_REVIEW_NOT_NPC", meshes["ionia"], (-1550, -150, 0),
          (0, 180, 0))
    stage("ENDER_STATIC_REVIEW_NOT_PAWN", meshes["ender_v2"], (-2770, -360, 0))
    must(len(added) == 10, "unexpected number of asset actors")
    must(bool(levels.save_current_level()), "new World save failed")
    must(DEST_FILE.is_file() and DEST_FILE.stat().st_size > 1000,
         "new level file absent or too small")

    # Do not reload the World while this Python frame still holds Actor references.
    # Independent saved-package readback must run in a separate Editor process.
    reloaded = [a.get_actor_label() for a in actors.get_all_level_actors()]
    must(all(reloaded.count(name) == 1 for name in added),
         "native map readback lost one or more staged assets")
    must(all(sum(n == "TSTSS_PRELUDE_REVIEW_" + stop for n in reloaded) == 1 for stop in STOPS),
         "native readback lost first-wake milestones")
    must(digest(BASE_FILE) == BASE_SHA, "original map changed during stage")
    must(all(digest(p) == config_hashes[p.name] for p in config_paths),
         "project config changed during stage")

    report.update({
        "status": "NATIVE_ASSET_WORLD_SAVED_PENDING_INDEPENDENT_READBACK",
        "engine": unreal.SystemLibrary.get_engine_version(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "base_map_sha256": BASE_SHA,
        "new_map_package": DEST_MAP,
        "new_map_sha256": digest(DEST_FILE),
        "staged_actor_labels": added,
        "original_milestone_count": len(STOPS),
        "original_player_start_count": 1,
        "native_stage_count": len(added),
        "native_mesh_paths": ASSETS,
        "config_hashes_preserved": config_hashes,
        "native_world_reload_successful": False,
        "original_map_modified": False,
    })
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    unreal.log("TSTSS_FIRST_WAKE_ASSET_ASSEMBLY_MAP_SAVED_PENDING_READBACK " +
               digest(DEST_FILE))
except Exception:
    report["status"] = "ASSET_STAGE_HOLD"
    report["error"] = traceback.format_exc()
    unreal.log_error("TSTSS_FIRST_WAKE_ASSET_ASSEMBLY_STAGE_HOLD " + report["error"])
    raise
