#!/usr/bin/env python3
"""Additive UE 5.8.4 cross-path SHORE review stage; NEVER a playable encounter.

--plan is engine-free and read-only. Native authoring is only entered by an
explicitly gated host launcher. All saved assets go into a new Review path.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "unreal"
WORKTREE = "TSTSS_AllPaths_Integration_20261110"
BRANCH = "review/ue58-multipath-convergence-20261110"
SOURCE_NAME = "VS06_SplashdownShore"
SOURCE_PACKAGE = "/Game/TSTSS/Review/VerticalSlice/" + SOURCE_NAME
DEST_ROOT = "/Game/TSTSS/Review/MultipathV1"
DEST_MAP = DEST_ROOT + "/L_VS06_ShoreMagicEnemyGear_Review"
OBJ_DEST = DEST_ROOT + "/ObjectImports"
MATERIAL_CUE = "/Game/TSTSS/Magic/M_ResonatorGlow"
SAVED_RECEIPT = PROJECT / "Saved/MultipathV1/shore_stage_receipt.json"
PREFIX = "TSTSS_MP_REVIEW_"
MAP_FILE = PROJECT / "Content/TSTSS/Review/VerticalSlice/VS06_SplashdownShore.umap"
SOURCE_READBACK = PROJECT / "Docs/Evidence/vertical_slice_map_readback_20261110.json"
OBJECTS = PROJECT / "ArtSource/VerticalSliceObjectsV1"
EQUIPMENT = PROJECT / "ArtSource/PartyEquipment"
MAGIC = PROJECT / "DataSource/Magic/EnderResonator.vertical_slice.review.json"
INTEGRATION = PROJECT / "DataSource/Integration/FirstWakeMultipath.review.json"

REVIEW_OBJECTS = (
    "MooringBollard", "HarborLantern", "CargoCrate", "RopeCoil",
    "EngineeringWorkbench", "EmergencyBeacon", "FlotationBuoy",
    "HarmonicEngineCore",
)
GEAR_SHOWCASE = ("Ender.ResonanceStaff", "Ionia.CaptainSaber", "Lyra.WaterFocus")
ENEMY_KINDS = ("HarmonicShear", "AetherLeakWisp", "DockSkitter")
LEGACY_ENV_LABELS = (
    "TSTSS_VS_REVIEW_SunKey", "TSTSS_VS_REVIEW_SkyAmbient",
    "TSTSS_VS_REVIEW_Atmosphere", "TSTSS_VS_REVIEW_AerialFog",
)

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def evidence_plan() -> dict:
    integration = json.loads(INTEGRATION.read_text(encoding="utf-8"))
    if integration.get("schema") != "tstss.firstwake.multipath.v1":
        raise RuntimeError("HOLD: crosspath authority manifest missing or changed")
    if integration.get("native_at_integrated_head") != "NOT_TESTED":
        raise RuntimeError("HOLD: do not reuse altered native evidence state")
    readback = json.loads(SOURCE_READBACK.read_text(encoding="utf-8"))
    row = readback["map_validation"][SOURCE_NAME]
    if (readback.get("status") != "SIX_NATIVE_LEVELS_REOPENED_NOT_PIE_OR_RENDER_ACCEPTED"
            or row.get("reopened_native") is not True
            or row.get("actor_count") != 21
            or digest(MAP_FILE) != row.get("source_sha256")):
        raise RuntimeError("HOLD: source native shore map hash/readback drift")
    original = json.loads((OBJECTS / "manifest.json").read_text(encoding="utf-8"))
    entries = original["original_objects"]
    if len(entries) != 22 or len({p["name"] for p in entries}) != 22:
        raise RuntimeError("HOLD: 22-object inventory drift")
    for item in entries:
        name = item["name"]
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
            raise RuntimeError("HOLD: unsafe original object name")
        blob = OBJECTS / (name + ".glb")
        if not blob.is_file() or digest(blob) != item["sha256"]:
            raise RuntimeError("HOLD: original object source SHA mismatch: " + name)
    if not set(REVIEW_OBJECTS).issubset({p["name"] for p in entries}):
        raise RuntimeError("HOLD: review object sources missing")
    gear = json.loads((EQUIPMENT / "party_equipment_manifest.review.json").read_text(encoding="utf-8"))
    pieces = gear["entries"]
    if len(pieces) != 14 or gear.get("automatic_item_grants") is not False:
        raise RuntimeError("HOLD: equipment authorization or source drift")
    if gear.get("creator_approved") is not False:
        raise RuntimeError("HOLD: equipment not review-only")
    ids = set()
    for entry in pieces:
        ident = entry["id"]
        if ident in ids or entry["owner"] not in ("Ender", "Ionia", "Lyra", "Shared"):
            raise RuntimeError("HOLD: duplicate/unknown equipment")
        ids.add(ident)
        raw = entry["relative_path"]
        if not re.fullmatch(r"Generated/[A-Za-z0-9_]+\.glb", raw):
            raise RuntimeError("HOLD: unsafe equipment source path")
        source = EQUIPMENT / raw
        if not source.is_file() or digest(source) != entry["sha256"]:
            raise RuntimeError("HOLD: equipment source SHA mismatch: " + ident)
        if entry.get("runtime_equippable") or entry.get("creator_approved"):
            raise RuntimeError("HOLD: equipment visual source accidentally promoted")
    if not set(GEAR_SHOWCASE).issubset(ids):
        raise RuntimeError("HOLD: three showcase equipment assets missing")
    spells = json.loads(MAGIC.read_text(encoding="utf-8"))
    if (len(spells) != 9 or len({r["VfxCueId"] for r in spells}) != 9
            or not all(str(s["SkillId"]).startswith("Ender_") for s in spells)):
        raise RuntimeError("HOLD: source magic cue list drift")
    if len(ENEMY_KINDS) != 3 or len(set(ENEMY_KINDS)) != 3:
        raise RuntimeError("HOLD: enemy review kinds changed")
    return {
        "schema": "tstss.shore.multipath.review.v1",
        "engine": "UE 5.8.4",
        "source_package": SOURCE_PACKAGE,
        "source_sha256": row["source_sha256"],
        "new_map": DEST_MAP,
        "original_object_imports": len(entries),
        "showcase_object_actors": len(REVIEW_OBJECTS),
        "catalogued_gear": len(pieces),
        "showcase_gear_actors": len(GEAR_SHOWCASE),
        "preview_vfx_actors": len(spells),
        "enemy_silhouette_actors": len(ENEMY_KINDS),
        "atmosphere_actor": 1,
        "total_new_review_actors": 1 + len(REVIEW_OBJECTS) + len(GEAR_SHOWCASE) + len(spells) + len(ENEMY_KINDS) + 2,
        "review_only": True,
        "real_combat_executed": False,
        "runtime_transition_implemented": False,
        "spell_mastery_granted": False,
        "equipment_granted": False,
        "lyra_recruited": False,
        "live_quest_modified": False,
        "PIE_verified": False,
        "visual_approved": False,
        "native_staged": False,
    }

def git(*args) -> str:
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                       text=True, timeout=30, check=False)
    if r.returncode:
        raise RuntimeError("HOLD: git custody command failed")
    return r.stdout.strip()

def check_native_custody() -> dict:
    if (ROOT.name != WORKTREE or PROJECT.name.lower() != "unreal"
            or sys.platform != "win32"):
        raise RuntimeError("HOLD: requires dedicated Windows integration worktree")
    expected = os.environ.get("TSTSS_MP_EXPECTED_HEAD", "")
    if not re.fullmatch(r"[a-fA-F0-9]{40}", expected):
        raise RuntimeError("HOLD: exact-head variable required")
    if (git("branch", "--show-current") != BRANCH
            or git("rev-parse", "HEAD").lower() != expected.lower()
            or git("status", "--porcelain")):
        raise RuntimeError("HOLD: dirty or changed exact-head integration checkout")
    if os.environ.get("TSTSS_MP_STAGE_EXPLICIT") != "1":
        raise RuntimeError("HOLD: explicit host permission required")
    if (PROJECT / "Saved/SaveGames").is_dir() and list((PROJECT / "Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: existing SaveGames in review project")
    if SAVED_RECEIPT.exists() or (PROJECT / "Content/TSTSS/Review/MultipathV1").exists():
        raise RuntimeError("HOLD: existing native destination/receipt; never overwrite")
    return evidence_plan()

def gear_package(entry: dict) -> str:
    filename = Path(entry["relative_path"]).stem
    return ("/Game/TSTSS/Review/PartyEquipment/" + entry["owner"] + "/"
            + filename + "/StaticMeshes/" + filename)

def build_native_shore() -> dict:
    plan = check_native_custody()
    import unreal as u
    if not u.SystemLibrary.get_engine_version().startswith("5.8.4"):
        raise RuntimeError("HOLD: UE 5.8.4 required")
    if (u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
            or u.EditorLoadingAndSavingUtils.get_dirty_content_packages()):
        raise RuntimeError("HOLD: Editor contains unsaved changes")
    if u.EditorAssetLibrary.does_directory_exist(DEST_ROOT):
        raise RuntimeError("HOLD: review destination already exists")
    if not u.EditorAssetLibrary.does_asset_exist(SOURCE_PACKAGE):
        raise RuntimeError("HOLD: native source map package not loadable")
    cue_material_missing = not u.EditorAssetLibrary.does_asset_exist(MATERIAL_CUE)
    # Source #797 owns this specific emissive REVIEW material authoring path.
    # Only create it if absent; never replace an existing asset.
    if cue_material_missing and u.EditorAssetLibrary.does_directory_exist("/Game/TSTSS/Magic"):
        raise RuntimeError("HOLD: partial magic review namespace requires manual inspection")
    actor_classes = {
        name: u.load_class(None, "/Script/ToSailTheStarrySky." + name)
        for name in ("TSTSSAtmosphereDirector", "TSTSSSliceEnemyActor", "TSTSSResonatorVfxActor")
    }
    if any(cls is None for cls in actor_classes.values()):
        raise RuntimeError("HOLD: one or more integrated C++ review actors lack a verified native build")
    import unreal as ue
    if not hasattr(ue, "ETSTSSSliceEnemyKind"):
        raise RuntimeError("HOLD: C++ native enemy enum is not reflected")
    enum_kinds = {}
    for kind in ENEMY_KINDS:
        label = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", kind).upper()
        value = getattr(ue.ETSTSSSliceEnemyKind, label, None)
        if value is None:
            raise RuntimeError("HOLD: native enemy enum missing: " + label)
        enum_kinds[kind] = value
    gear = json.loads((EQUIPMENT / "party_equipment_manifest.review.json").read_text(encoding="utf-8"))
    showcased = {item["id"]: item for item in gear["entries"] if item["id"] in GEAR_SHOWCASE}
    imported_gear = {}
    for ident, entry in showcased.items():
        mesh = u.load_asset(gear_package(entry))
        if mesh is None or not isinstance(mesh, u.StaticMesh):
            raise RuntimeError("HOLD: native imported equipment asset missing: " + ident)
        imported_gear[ident] = mesh
    cloud = u.load_asset("/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst")
    if cloud is None:
        raise RuntimeError("HOLD: required original EngineSky cloud asset missing")
    config_names = ("DefaultEngine.ini", "DefaultInput.ini")
    config_hashes = {name: digest(PROJECT / "Config" / name) for name in config_names}
    source_sha = digest(MAP_FILE)
    if cue_material_missing:
        # Uses the already reviewed, isolated Ender-material generator from #797.
        from build_ender_resonator_preview import make_material
        created = make_material()
        if created is None or not u.EditorAssetLibrary.does_asset_exist(MATERIAL_CUE):
            raise RuntimeError("HOLD: emissive material creation failed")
    if not isinstance(u.load_asset(MATERIAL_CUE), u.MaterialInterface):
        raise RuntimeError("HOLD: cue material is not a native material asset")
    if not u.EditorAssetLibrary.make_directory(DEST_ROOT):
        raise RuntimeError("HOLD: cannot create disposable review namespace")
    if not u.EditorAssetLibrary.make_directory(OBJ_DEST):
        raise RuntimeError("HOLD: cannot create new review-only prop namespace")
    object_rows = json.loads((OBJECTS / "manifest.json").read_text(encoding="utf-8"))["original_objects"]
    tasks = []
    for item in object_rows:
        # Unique namespace per authored GLB: shared PBR material identifiers
        # must never collide silently across different object imports.
        object_path = OBJ_DEST + "/" + item["name"]
        if not u.EditorAssetLibrary.make_directory(object_path):
            raise RuntimeError("HOLD: cannot isolate imported GLB materials " + item["name"])
        task = u.AssetImportTask()
        task.set_editor_property("filename", str(OBJECTS / (item["name"] + ".glb")))
        task.set_editor_property("destination_path", object_path)
        task.set_editor_property("destination_name", item["name"])
        task.set_editor_property("automated", True)
        task.set_editor_property("replace_existing", False)
        task.set_editor_property("save", True)
        tasks.append(task)
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    imports = {}
    for item, task in zip(object_rows, tasks):
        found = [u.load_asset(path) for path in task.get_editor_property("imported_object_paths")]
        meshes = [asset for asset in found if isinstance(asset, u.StaticMesh)]
        if len(meshes) != 1:
            raise RuntimeError("HOLD: original GLB did not resolve to one UE StaticMesh: " + item["name"])
        imports[item["name"]] = meshes[0]
    if not u.EditorAssetLibrary.duplicate_asset(SOURCE_PACKAGE, DEST_MAP):
        raise RuntimeError("HOLD: failed to duplicate source into new review map")
    world = u.EditorLoadingAndSavingUtils.load_map(DEST_MAP)
    if world is None:
        raise RuntimeError("HOLD: duplicated native map cannot be opened")
    editor = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = editor.get_all_level_actors()
    if len(actors) != 21 or any(a.get_actor_label().startswith(PREFIX) for a in actors):
        raise RuntimeError("HOLD: source actor inventory/duplicate changed")
    removed = []
    for actor in actors:
        if actor.get_actor_label() in LEGACY_ENV_LABELS:
            label = actor.get_actor_label()
            if not editor.destroy_actor(actor):
                raise RuntimeError("HOLD: original light removal failed in COPY")
            removed.append(label)
    if not {"TSTSS_VS_REVIEW_SunKey", "TSTSS_VS_REVIEW_SkyAmbient"}.issubset(set(removed)):
        raise RuntimeError("HOLD: original review sky/sun inventory changed")
    def spawn(cls, label, xyz):
        instance = editor.spawn_actor_from_class(cls, u.Vector(*xyz), u.Rotator(0, 0, 0))
        if instance is None:
            raise RuntimeError("HOLD: failed to spawn " + label)
        instance.set_actor_label(PREFIX + label)
        return instance
    atmosphere = spawn(actor_classes["TSTSSAtmosphereDirector"], "CoastalAtmosphere", (0, 0, 0))
    atmosphere.set_editor_property("volumetric_cloud_material", cloud)
    atmosphere.set_editor_property("initial_clock_hours", 17.0)
    atmosphere.set_editor_property("autoplay_review_cycle", False)
    atmosphere.set_editor_property("reduced_motion", True)
    for i, name in enumerate(REVIEW_OBJECTS):
        mesh = imports[name]
        obj = spawn(u.StaticMeshActor, "OriginalProp_" + name,
                    (-4500 + (i % 4) * 1200, 1700 + (i // 4) * 920, 160))
        obj.static_mesh_component.set_static_mesh(mesh)
        obj.set_actor_enable_collision(False)
        obj.static_mesh_component.set_collision_profile_name("NoCollision")
    for i, ident in enumerate(GEAR_SHOWCASE):
        actor = spawn(u.StaticMeshActor, "StaticGear_NotEquipped_" + ident.replace(".", "_"),
                      (-3800 + i * 1400, 500, 220))
        actor.static_mesh_component.set_static_mesh(imported_gear[ident])
        actor.set_actor_enable_collision(False)
        actor.static_mesh_component.set_collision_profile_name("NoCollision")
    for i, kind in enumerate(ENEMY_KINDS):
        actor = spawn(actor_classes["TSTSSSliceEnemyActor"], "EnemyVisual_NoEncounter_" + kind,
                      (-3500 + i * 1150, -1350 - i * 350, 150))
        actor.set_editor_property("kind", enum_kinds[kind])
        actor.set_editor_property("instance_id", "MP_ReviewEnemy_%02d" % (i + 1))
        actor.set_editor_property("reduced_motion", True)
        actor.set_actor_enable_collision(False)
    for i, row in enumerate(json.loads(MAGIC.read_text(encoding="utf-8"))):
        actor = spawn(actor_classes["TSTSSResonatorVfxActor"],
                      "NoAuthorizedCast_" + row["SkillId"],
                      (1000 + (i % 3) * 1200, -650 - (i // 3) * 950, 160))
        actor.set_editor_property("preview_cue_id", row["VfxCueId"])
        actor.set_editor_property("preview_target_offset", u.Vector(300, 0, 80))
        actor.set_editor_property("loop_review", True)
        actor.set_actor_enable_collision(False)
    camera = spawn(u.CameraActor, "Overview_NotGameplayCamera", (-5300, -6200, 2850))
    camera.set_actor_rotation(u.Rotator(-18, 45, 0), False)
    caption = spawn(u.TextRenderActor, "UnapprovedVisualsNotice", (-3550, 2850, 500))
    text_component = caption.get_component_by_class(u.TextRenderComponent)
    if text_component is None:
        raise RuntimeError("HOLD: reviewer-visible noncanonical warning unavailable")
    text_component.set_text("REVIEW ONLY: NO UNLOCKED SKILLS / NO STORY ENCOUNTER")
    after = editor.get_all_level_actors()
    labels = [actor.get_actor_label() for actor in after]
    review_labels = [label for label in labels if label.startswith(PREFIX)]
    if (len(review_labels) != plan["total_new_review_actors"]
            or len(set(review_labels)) != len(review_labels)
            or len(after) != 21 - len(removed) + len(review_labels)):
        raise RuntimeError("HOLD: composed actor inventory/identity mismatch")
    if not u.EditorLoadingAndSavingUtils.save_map(world, DEST_MAP):
        raise RuntimeError("HOLD: cannot save new review map")
    dest_file = PROJECT / "Content/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review.umap"
    if not dest_file.is_file() or digest(MAP_FILE) != source_sha:
        raise RuntimeError("HOLD: new map missing or original source map mutated")
    if any(digest(PROJECT / "Config" / n) != config_hashes[n] for n in config_names):
        raise RuntimeError("HOLD: protected source config changed")
    if SAVED_RECEIPT.exists():
        raise RuntimeError("HOLD: old native receipt present; no evidence overwrite")
    receipt = {**plan, "native_staged": True, "status": "NATIVE_REVIEW_MAP_SAVED_NOT_PIE_OR_VISUAL_APPROVED",
               "source_head": git("rev-parse", "HEAD"),
               "new_map_sha256": digest(dest_file), "new_map_bytes": dest_file.stat().st_size,
               "saved_actor_count": len(after),
               "new_unique_review_actors": len(review_labels),
               "removed_duplicate_only_environment_actors": sorted(removed)}
    SAVED_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    SAVED_RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    u.log("TSTSS_MULTIPATH_SHORE_NATIVE_SAVED_NOT_PIE " + receipt["new_map_sha256"])
    return receipt

if __name__ == "__main__":
    if os.environ.get("TSTSS_MP_STAGE_EXPLICIT") == "1":
        result = build_native_shore()
    elif len(sys.argv) == 2 and sys.argv[1] == "--plan":
        result = evidence_plan()
    else:
        raise SystemExit("HOLD: use --plan for source-only review; native requires guarded host opt-in")
    print(json.dumps(result, indent=2))
