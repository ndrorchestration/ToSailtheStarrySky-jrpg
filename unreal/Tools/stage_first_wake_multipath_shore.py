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
PREPARE_RECEIPT = PROJECT / "Saved/MultipathV1/shore_prepare_receipt.json"
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
# Immutable visual scope of the HISTORIC 222-file native shoreline snapshot:
# nine fixed spell-cue silhouettes, not an ever-growing live spell catalog.
# Centering belongs only in the new, independent interactive focus review.
LEGACY_PREVIEW_SKILL_IDS = (
    "Ender_ResonantPulse", "Ender_TuningLance", "Ender_EchoMend",
    "Ender_CorrespondenceThread", "Ender_LatticeBreak",
    "Ender_MindRipple", "Ender_FocusHarmonic",
    "Ender_ConcordanceBurst", "Ender_ThoughtChord",
)
LEGACY_ENV_LABELS = (
    "TSTSS_VS_REVIEW_SunKey", "TSTSS_VS_REVIEW_SkyAmbient",
    "TSTSS_VS_REVIEW_Atmosphere", "TSTSS_VS_REVIEW_AerialFog",
)

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def legacy_magic_preview_rows() -> list[dict]:
    """Maintain exact 9 spell actor identities for the original shoreline map.

    The new Centering ability can appear as a tenth catalog row, but may not
    rewrite this exact-hash historical map, raise its actor count, or promote
    older DesignOnly abilities. Unknown extra rows fail closed.
    """
    spells = json.loads(MAGIC.read_text(encoding="utf-8"))
    if not isinstance(spells, list):
        raise RuntimeError("HOLD: invalid magic catalog")
    ids = [row.get("SkillId") for row in spells if isinstance(row, dict)]
    cues = [row.get("VfxCueId") for row in spells if isinstance(row, dict)]
    if (len(ids) != len(spells) or len(set(ids)) != len(spells)
            or len(set(cues)) != len(spells)
            or any(not isinstance(s, str) or not s.startswith("Ender_") for s in ids)):
        raise RuntimeError("HOLD: duplicate or malformed magic catalog")
    legacy = [r for r in spells if r["SkillId"] in LEGACY_PREVIEW_SKILL_IDS]
    if len(legacy) != 9 or {r["SkillId"] for r in legacy} != set(LEGACY_PREVIEW_SKILL_IDS):
        raise RuntimeError("HOLD: legacy shoreline nine-cue roster drift")
    extras = [r for r in spells if r["SkillId"] not in LEGACY_PREVIEW_SKILL_IDS]
    if extras:
        if len(extras) != 1:
            raise RuntimeError("HOLD: unsupported additional legacy-stage cues")
        added = extras[0]
        if (added.get("SkillId") != "Ender_Centering"
                or added.get("VfxCueId") != "VFX.Ender.Centering"
                or added.get("Admission") != "ReviewExecutable"
                or added.get("RequiredSchool") != "ResonanceHarmonic"
                or added.get("RequiredMasteryRank") != 1
                or added.get("Target") != "Self"
                or added.get("ResourceCost") != 5
                or added.get("Power") != 0
                or added.get("bPartyPhysicalDefenseBuff") is not True
                or added.get("PhysicalDefenseBuffPercent") != 15
                or added.get("BuffDurationRounds") != 3):
            raise RuntimeError("HOLD: Centering cannot contaminate historical preview")
        if {r["SkillId"] for r in spells if r.get("Admission")=="ReviewExecutable"} != {
                "Ender_Centering","Ender_ResonantPulse"}:
            raise RuntimeError("HOLD: non-focus magic gained review execution")
    return legacy


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
    spells = legacy_magic_preview_rows()
    if len(spells)!=9:
        raise RuntimeError("HOLD: historic shoreline review has nine cues exactly")
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

def assert_source_custody_for_phase(phase: str) -> None:
    """All tracked source must remain clean. Generated native assets are narrow.

    Preparer starts with a fully clean checkout. Composer/readback may see
    ONLY the new M_ResonatorGlow and isolated MultipathV1 review asset trees.
    A tracked config change or unrelated untracked path is always rejected.
    """
    status = git("status", "--porcelain", "-uall").splitlines()
    if phase == "prepare":
        if status:
            raise RuntimeError("HOLD: preparation requires entirely clean source")
        return
    if phase != "compose":
        raise RuntimeError("HOLD: unknown source custody phase")
    prefixes = (
        "?? unreal/Content/TSTSS/Magic/M_ResonatorGlow.uasset",
        "?? unreal/Content/TSTSS/Review/MultipathV1/",
    )
    for line in status:
        if not ((line == prefixes[0]) or line.startswith(prefixes[1])):
            raise RuntimeError("HOLD: unexpected tracked/untracked source mutation")


def check_native_custody(phase: str = "prepare") -> dict:
    if phase not in ("prepare", "compose"):
        raise RuntimeError("HOLD: unknown native staging phase")
    if (ROOT.name != WORKTREE or PROJECT.name.lower() != "unreal"
            or sys.platform != "win32"):
        raise RuntimeError("HOLD: requires dedicated Windows integration worktree")
    expected = os.environ.get("TSTSS_MP_EXPECTED_HEAD", "")
    if not re.fullmatch(r"[a-fA-F0-9]{40}", expected):
        raise RuntimeError("HOLD: exact-head variable required")
    if (git("branch", "--show-current") != BRANCH
            or git("rev-parse", "HEAD").lower() != expected.lower()):
        raise RuntimeError("HOLD: changed exact-head integration checkout")
    assert_source_custody_for_phase(phase)
    if os.environ.get("TSTSS_MP_STAGE_EXPLICIT") != "1":
        raise RuntimeError("HOLD: explicit host permission required")
    if (PROJECT / "Saved/SaveGames").is_dir() and list((PROJECT / "Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: existing SaveGames in review project")
    target_exists = (PROJECT / "Content/TSTSS/Review/MultipathV1").exists()
    if SAVED_RECEIPT.exists():
        raise RuntimeError("HOLD: final native receipt already exists")
    if phase == "prepare" and (PREPARE_RECEIPT.exists() or target_exists):
        raise RuntimeError("HOLD: existing prepared assets; no overwrite")
    if phase == "compose" and (not PREPARE_RECEIPT.is_file() or not target_exists):
        raise RuntimeError("HOLD: first-process preparation evidence missing")
    return evidence_plan()

def gear_package(entry: dict) -> str:
    filename = Path(entry["relative_path"]).stem
    return ("/Game/TSTSS/Review/PartyEquipment/" + entry["owner"] + "/"
            + filename + "/StaticMeshes/" + filename)

def resolve_native_enemy_kinds(unreal_module) -> dict:
    """Resolve the Blueprint-reflected UENUM using UE Python's E-prefix removal.

    C++ ETSTSSSliceEnemyKind becomes unreal.TSTSSSliceEnemyKind. Never fall
    back to a different enum or an integer cast: missing values are a HOLD.
    """
    enum_type = getattr(unreal_module, "TSTSSSliceEnemyKind", None)
    if enum_type is None:
        raise RuntimeError("HOLD: native TSTSSSliceEnemyKind not exposed to Python")
    values = {}
    for kind in ENEMY_KINDS:
        member = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", kind).upper()
        value = getattr(enum_type, member, None)
        if value is None:
            raise RuntimeError("HOLD: native enemy enum missing " + member)
        values[kind] = value
    if len(values) != 3 or len(set(map(str, values.values()))) != 3:
        raise RuntimeError("HOLD: enemy Python enum values duplicated or incomplete")
    return values

def set_required_review_bool(actor, name: str, enabled: bool) -> str:
    """Set a C++ review bool across UE Python's b-prefix spelling variants.

    UE-generated property names are not guaranteed to preserve the leading b.
    Every necessary review setting must be confirmed after writing; never
    silently skip reduced-motion / non-autoplay safeguards.
    """
    for prop in (name, "b_" + name):
        try:
            actor.get_editor_property(prop)
        except Exception:
            continue
        actor.set_editor_property(prop, enabled)
        if actor.get_editor_property(prop) is not enabled:
            raise RuntimeError("HOLD: review actor boolean did not stick: " + prop)
        return prop
    raise RuntimeError("HOLD: native review actor boolean missing: " + name)


def build_native_shore(phase: str) -> dict:
    plan = check_native_custody(phase)
    import unreal as u
    if not u.SystemLibrary.get_engine_version().startswith("5.8.4"):
        raise RuntimeError("HOLD: UE 5.8.4 required")
    if (u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
            or u.EditorLoadingAndSavingUtils.get_dirty_content_packages()):
        raise RuntimeError("HOLD: Editor contains unsaved changes")
    if phase == "prepare" and u.EditorAssetLibrary.does_directory_exist(DEST_ROOT):
        raise RuntimeError("HOLD: review destination already exists")
    if phase == "compose" and not u.EditorAssetLibrary.does_directory_exist(DEST_ROOT):
        raise RuntimeError("HOLD: prepared review namespace missing")
    if not u.EditorAssetLibrary.does_asset_exist(SOURCE_PACKAGE):
        raise RuntimeError("HOLD: native source map package not loadable")
    cue_material_missing = not u.EditorAssetLibrary.does_asset_exist(MATERIAL_CUE)
    # Source #797 owns this specific emissive REVIEW material authoring path.
    # Only create it if absent; never replace an existing asset.
    if phase == "prepare" and cue_material_missing and u.EditorAssetLibrary.does_directory_exist("/Game/TSTSS/Magic"):
        raise RuntimeError("HOLD: partial magic review namespace requires manual inspection")
    actor_classes = {
        name: u.load_class(None, "/Script/ToSailTheStarrySky." + name)
        for name in ("TSTSSAtmosphereDirector", "TSTSSSliceEnemyActor", "TSTSSResonatorVfxActor")
    }
    if any(cls is None for cls in actor_classes.values()):
        raise RuntimeError("HOLD: one or more integrated C++ review actors lack a verified native build")
    enum_kinds = resolve_native_enemy_kinds(u)
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
    object_rows = json.loads((OBJECTS / "manifest.json").read_text(encoding="utf-8"))["original_objects"]
    dest_file = PROJECT / "Content/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review.umap"
    if phase == "prepare":
        if cue_material_missing:
            # Load only the reviewed material helper, never its __main__ scene.
            import importlib.util
            helper = PROJECT / "Tools/build_ender_resonator_preview.py"
            spec = importlib.util.spec_from_file_location("tstss_review_material_source", helper)
            if spec is None or spec.loader is None:
                raise RuntimeError("HOLD: material helper source not loadable")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            created = module.make_material()
            if created is None or not u.EditorAssetLibrary.does_asset_exist(MATERIAL_CUE):
                raise RuntimeError("HOLD: emissive material creation failed")
        if not isinstance(u.load_asset(MATERIAL_CUE), u.MaterialInterface):
            raise RuntimeError("HOLD: cue material is not native")
        if not u.EditorAssetLibrary.make_directory(DEST_ROOT):
            raise RuntimeError("HOLD: cannot create disposable review namespace")
        if not u.EditorAssetLibrary.make_directory(OBJ_DEST):
            raise RuntimeError("HOLD: cannot create review object import namespace")
        tasks = []
        for item in object_rows:
            object_path = OBJ_DEST + "/" + item["name"]
            if not u.EditorAssetLibrary.make_directory(object_path):
                raise RuntimeError("HOLD: import namespace collision " + item["name"])
            task = u.AssetImportTask()
            task.set_editor_property("filename", str(OBJECTS / (item["name"] + ".glb")))
            task.set_editor_property("destination_path", object_path)
            task.set_editor_property("destination_name", item["name"])
            task.set_editor_property("automated", True)
            task.set_editor_property("replace_existing", False)
            task.set_editor_property("save", True)
            tasks.append(task)
        u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        for item, task in zip(object_rows, tasks):
            imported = [u.load_asset(path) for path in task.get_editor_property("imported_object_paths")]
            if len([x for x in imported if isinstance(x, u.StaticMesh)]) != 1:
                raise RuntimeError("HOLD: GLB import did not yield one mesh " + item["name"])
        # Important: do NOT duplicate a UWorld through EditorAssetLibrary.
        # UE-177376 / UE-109253 and our exact-head EditorServer.cpp:2544
        # failure show that UWorld asset duplication can leak or retain
        # references, even when the new World appears to exist.
        # Instead load the source map and use Unreal's proper Save Map As
        # path to re-home the level script into a separate target package.
        # Exit this child before loading the new copy in phase two.
        source_world = u.EditorLoadingAndSavingUtils.load_map(SOURCE_PACKAGE)
        if source_world is None:
            raise RuntimeError("HOLD: cannot load canonical review shore source map")
        source_actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
        if len(source_actors) != 21:
            raise RuntimeError("HOLD: native source shore actor count changed")
        if not u.EditorLoadingAndSavingUtils.save_map(source_world, DEST_MAP):
            raise RuntimeError("HOLD: Save Map As failed to produce independent review copy")
        if not dest_file.is_file() or digest(MAP_FILE) != source_sha:
            raise RuntimeError("HOLD: source-map digest or saved copy missing")
        if any(digest(PROJECT / "Config" / n) != config_hashes[n] for n in config_names):
            raise RuntimeError("HOLD: protected project config modified in preparation")
        receipt = {**plan, "status": "REVIEW_ASSETS_AND_BASE_MAP_PREPARED_NOT_PIE",
                   "native_staged": False, "source_head": git("rev-parse", "HEAD"),
                   "base_map_sha256": digest(dest_file), "prepared_object_meshes": len(tasks)}
        PREPARE_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        with PREPARE_RECEIPT.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2)
            stream.write("\n")
        u.log("TSTSS_MULTIPATH_SHORE_PREPARED_NOT_PIE " + receipt["base_map_sha256"])
        return receipt
    # Phase two is a completely FRESH Editor process. It cannot retain a
    # standalone duplicated UWorld reference from process one.
    if cue_material_missing:
        raise RuntimeError("HOLD: preparation magic material absent")
    if not PREPARE_RECEIPT.is_file() or not dest_file.is_file():
        raise RuntimeError("HOLD: no first-process preparation/map receipt")
    prepared = json.loads(PREPARE_RECEIPT.read_text(encoding="utf-8"))
    if (prepared.get("status") != "REVIEW_ASSETS_AND_BASE_MAP_PREPARED_NOT_PIE"
            or prepared.get("source_head") != git("rev-parse", "HEAD")
            or prepared.get("source_sha256") != source_sha
            or prepared.get("base_map_sha256") != digest(dest_file)
            or prepared.get("prepared_object_meshes") != 22
            or prepared.get("PIE_verified") is not False
            or prepared.get("visual_approved") is not False):
        raise RuntimeError("HOLD: stale/incorrect first-phase preparation receipt")
    imports = {}
    for item in object_rows:
        name = item["name"]
        path = OBJ_DEST + "/" + name + "/" + name + "/StaticMeshes/" + name
        mesh = u.load_asset(path)
        if mesh is None or not isinstance(mesh, u.StaticMesh):
            raise RuntimeError("HOLD: imported review prop mesh unavailable: " + name)
        imports[name] = mesh
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
    set_required_review_bool(atmosphere, "autoplay_review_cycle", False)
    set_required_review_bool(atmosphere, "reduced_motion", True)
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
        set_required_review_bool(actor, "reduced_motion", True)
        actor.set_actor_enable_collision(False)
    for i, row in enumerate(legacy_magic_preview_rows()):
        actor = spawn(actor_classes["TSTSSResonatorVfxActor"],
                      "NoAuthorizedCast_" + row["SkillId"],
                      (1000 + (i % 3) * 1200, -650 - (i // 3) * 950, 160))
        actor.set_editor_property("preview_cue_id", row["VfxCueId"])
        actor.set_editor_property("preview_target_offset", u.Vector(300, 0, 80))
        set_required_review_bool(actor, "loop_review", True)
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
        result = build_native_shore(os.environ.get("TSTSS_MP_PHASE", ""))
    elif len(sys.argv) == 2 and sys.argv[1] == "--plan":
        result = evidence_plan()
    else:
        raise SystemExit("HOLD: use --plan for source-only review; native requires guarded host opt-in")
    print(json.dumps(result, indent=2))
