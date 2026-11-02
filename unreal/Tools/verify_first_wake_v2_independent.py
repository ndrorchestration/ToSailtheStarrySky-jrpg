"""Independent, read-only V2 Prelude map and isolated save-service QA.

Run in Unreal Editor Python ONLY from the named disposable checkout. The map
is a tracked byte-identical review artifact; never resave it. This exercises
actual reflected C++ First Wake actors and a separate temporary SaveGame slot,
but does NOT inject keyboard input, run PIE, or simulate ship water physics.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXPECTED_PARENT = "TSTSS_PreludeV2_IndependentReview_20261101"
MAP_PACKAGE = "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2"
MAP_RELATIVE = "Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"
MAP_SHA256 = "4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80"
SLOT = "tstss_prelude_v2_independent_qa"
ACTOR_PREFIX = "TSTSS_PRELUDE_REVIEW_"
STOPS = (
    ("FlyerDiscovery", "FlyerDiscovered", ""),
    ("IoniaHiring", "IoniaHired", ""),
    ("AureateBoarding", "BoardedAureateWake", ""),
    ("LiftStation", "", "Lift"),
    ("PressureStation", "", "Pressure"),
    ("ReserveStation", "", "Reserve"),
    ("EngineeringApproval", "EngineeringChecked", ""),
)
EXPECTED_MAPPINGS = {
    ("MoveForward", "W", "1.000000"),
    ("MoveForward", "S", "-1.000000"),
    ("MoveRight", "D", "1.000000"),
    ("MoveRight", "A", "-1.000000"),
    ("Turn", "MouseX", "1.000000"),
    ("LookUp", "MouseY", "-1.000000"),
}
EXPECTED_ACTIONS = {"Interact": "E", "QuickSave": "F5", "QuickLoad": "F9"}


def project_guard(project_directory: str) -> Path:
    p = Path(project_directory).resolve()
    if p.name.lower() != "unreal" or p.parent.name != EXPECTED_PARENT:
        raise RuntimeError("Refusing to inspect outside unique independent V2 sandbox")
    if not (p / MAP_RELATIVE).is_file():
        raise RuntimeError("Required V2 map absent")
    if sha(p / MAP_RELATIVE) != MAP_SHA256:
        raise RuntimeError("V2 .umap SHA differs from committed source")
    return p


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_input_source(project: Path) -> dict:
    """Source config and C++ wiring check, NOT real keyboard input execution."""
    import re
    config = (project / "Config/DefaultInput.ini").read_text(encoding="utf-8")
    axes = set(re.findall(
        r'AxisMappings=\(AxisName="([^"]+)",Scale=([-0-9.]+),Key=([^)]*)\)',
        config,
    ))
    axis_matches = {(name, key, scale) for name, scale, key in axes}
    if not EXPECTED_MAPPINGS.issubset(axis_matches):
        raise RuntimeError("WASD/mouse mapping drift")
    actions = dict(re.findall(
        r'ActionMappings=\(ActionName="([^"]+)",Key=([^)]*)\)', config))
    for name, key in EXPECTED_ACTIONS.items():
        if actions.get(name) != key:
            raise RuntimeError("Missing gameplay input action: " + name)
    cpp = (project / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
    for axis in ("MoveForward", "MoveRight", "Turn", "LookUp"):
        if 'BindAxis(TEXT("' + axis + '")' not in cpp:
            raise RuntimeError("Missing native controller axis binder " + axis)
    for action in EXPECTED_ACTIONS:
        if 'BindAction(TEXT("' + action + '")' not in cpp:
            raise RuntimeError("Missing native controller action binder " + action)
    if "LineTraceSingleByChannel" not in cpp or "FVector::DistSquared" not in cpp:
        raise RuntimeError("Pawn interaction trace or world-distance gate absent")
    if "SaveFirstWake(TEXT(\"first_wake_quick\"))" not in cpp or "LoadFirstWake(TEXT(\"first_wake_quick\"))" not in cpp:
        raise RuntimeError("F5/F9 native handler drift")
    return {"config_mapping_count": len(EXPECTED_MAPPINGS) + len(EXPECTED_ACTIONS),
            "source_handlers_verified": True, "player_keyboard_input_executed": False}


def native_verify() -> dict:
    import unreal
    project = project_guard(unreal.Paths.project_dir())
    settings_before = {p: sha(project / "Config" / p)
                       for p in ("DefaultEngine.ini", "DefaultInput.ini")}
    input_result = inspect_input_source(project)

    asset = project / MAP_RELATIVE
    if not unreal.EditorAssetLibrary.does_asset_exist(MAP_PACKAGE):
        raise RuntimeError("Unreal asset registry lacks V2 map")
    world = unreal.EditorLoadingAndSavingUtils.load_map(MAP_PACKAGE)
    if world is None:
        raise RuntimeError("Unreal failed to open V2 map")

    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    by_name = {}
    for actor in subsystem.get_all_level_actors():
        label = actor.get_actor_label()
        if label.startswith(ACTOR_PREFIX):
            if label in by_name:
                raise RuntimeError("Duplicate review actor label: " + label)
            by_name[label] = actor

    for label, beat, station in STOPS:
        obj = by_name.get(ACTOR_PREFIX + label)
        if obj is None or not isinstance(obj, unreal.TSTSSMilestoneActor):
            raise RuntimeError("Missing actual native actor: " + label)
        if bool(obj.get_editor_property("is_inspection_station")) != bool(station):
            raise RuntimeError("Wrong station flag: " + label)
        part = obj.get_component_by_class(unreal.StaticMeshComponent)
        if not part or part.get_collision_enabled() == unreal.CollisionEnabled.NO_COLLISION:
            raise RuntimeError("Interaction mesh cannot be traced: " + label)

    if sum(isinstance(a, unreal.TSTSSMilestoneActor)
           for a in subsystem.get_all_level_actors()) != len(STOPS):
        raise RuntimeError("Unexpected extra C++ milestone actor")

    player_start = by_name.get(ACTOR_PREFIX + "PlayerStart_Ender_REVIEW_PROXY")
    if not isinstance(player_start, unreal.PlayerStart):
        raise RuntimeError("Ender player start missing")
    floor = by_name.get(ACTOR_PREFIX + "Harbor_TraversalFloor")
    ocean = by_name.get(ACTOR_PREFIX + "Ocean_VISUAL_ONLY_NO_BUOYANCY")
    if not floor or not ocean:
        raise RuntimeError("Required harbor floor or visual ocean missing")
    ground_mesh = floor.get_component_by_class(unreal.StaticMeshComponent)
    sea_mesh = ocean.get_component_by_class(unreal.StaticMeshComponent)
    if not ground_mesh or ground_mesh.get_collision_enabled() != unreal.CollisionEnabled.QUERY_AND_PHYSICS:
        raise RuntimeError("Review floor lacks blocking collision")
    if not sea_mesh or sea_mesh.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
        raise RuntimeError("Decorative ocean must have zero collision")
    if str(sea_mesh.get_collision_profile_name()).lower() != "nocollision":
        raise RuntimeError("Ocean profile is not NoCollision")

    mode = unreal.get_default_object(unreal.TSTSSGameMode)
    pawn_cls = mode.get_editor_property("default_pawn_class")
    if pawn_cls is None or "TSTSSExplorerCharacter" not in str(pawn_cls):
        raise RuntimeError("Default game mode no longer spawns native explorer pawn")

    state = unreal.new_object(unreal.TSTSSFirstWakeState)
    by_stop = {label: by_name[ACTOR_PREFIX + label] for label, _, _ in STOPS}
    if by_stop["IoniaHiring"].try_activate(state):
        raise RuntimeError("Unauthorized Ionia pre-flyer shortcut")
    if by_stop["EngineeringApproval"].try_activate(state):
        raise RuntimeError("Premature engineer signoff")
    for label in ("FlyerDiscovery", "IoniaHiring", "AureateBoarding"):
        if not by_stop[label].try_activate(state):
            raise RuntimeError("Progression rejected valid stop: " + label)
    if by_stop["EngineeringApproval"].try_activate(state):
        raise RuntimeError("Signoff allowed before inspections")
    for label in ("LiftStation", "PressureStation", "ReserveStation"):
        if not by_stop[label].try_activate(state):
            raise RuntimeError("Valid engineering check rejected: " + label)
        if by_stop[label].try_activate(state):
            raise RuntimeError("Duplicate engineering check accepted: " + label)
    if not by_stop["EngineeringApproval"].try_activate(state):
        raise RuntimeError("Complete engineering signoff rejected")
    if state.is_chapter_one_act_one():
        raise RuntimeError("Prelude improperly advanced to Splashdown")
    if int(state.get_inspection_mask()) != 7:
        raise RuntimeError("Three separate inspections not accumulated")

    # Native persistence round-trip in a dedicated disposable save slot.
    # This exercises the real SaveGame service, not an F5/F9 keypress or PIE.
    if unreal.GameplayStatics.does_save_game_exist(SLOT, 0):
        raise RuntimeError("Dedicated review save already exists; refuse overwrite")
    saved = False
    try:
        save = unreal.new_object(unreal.TSTSSSaveGame)
        save.set_editor_property("first_wake_started", True)
        save.set_editor_property("first_wake_beat", state.get_current_beat())
        save.set_editor_property("inspection_mask", 7)
        if not unreal.TSTSSPersistence.save_progress(SLOT, save):
            raise RuntimeError("Real Unreal SaveGame service refused review save")
        saved = True
        readback = unreal.TSTSSPersistence.load_progress(SLOT)
        if not readback:
            raise RuntimeError("Real Unreal SaveGame service could not reload")
        if (not readback.get_editor_property("first_wake_started")
                or readback.get_editor_property("inspection_mask") != 7
                or readback.get_editor_property("first_wake_beat") != state.get_current_beat()):
            raise RuntimeError("First Wake native SaveGame roundtrip mismatch")
    finally:
        if saved and not unreal.GameplayStatics.delete_game_in_slot(SLOT, 0):
            raise RuntimeError("Could not remove isolated review test save")

    if sha(asset) != MAP_SHA256:
        raise RuntimeError("V2 map changed during read-only native verification")
    if any(sha(project / "Config" / n) != digest
           for n, digest in settings_before.items()):
        raise RuntimeError("Editor modified tracked project config during read-only verification")

    receipt = {
        "status": "NATIVE_V2_MAP_AND_SAVE_SERVICE_PASS_NOT_PLAYER_INPUT_PROOF",
        "git_source_map_sha256": MAP_SHA256,
        "native_engine_version": unreal.SystemLibrary.get_engine_version(),
        "real_cpp_milestone_actors": 7,
        "real_game_mode_explorer_pawn": True,
        "ordered_story_and_engineering_pass": True,
        "premature_and_duplicate_checks_rejected": True,
        "native_savegame_round_trip_pass": True,
        "isolated_test_slot_deleted": True,
        "source_input_bindings": input_result,
        "pie_keyboard_e_f5_f9_tested": False,
        "render_and_physics_approved": False,
        "actual_character_art_approved": False,
        "chapter_one_act_one": False,
    }
    output = project / "Saved" / "PreludeV2IndependentQA" / "v2_native_validation.json"
    if output.exists():
        raise RuntimeError("Independent V2 evidence already exists; refuse overwrite")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    unreal.log("TSTSS_PRELUDE_V2_INDEPENDENT_NATIVE_QA_PASS " + json.dumps(receipt))
    return receipt


if __name__ == "__main__":
    if "--source" in sys.argv:
        path = Path(sys.argv[sys.argv.index("--source") + 1])
        print(json.dumps({"map_sha256": MAP_SHA256, "inputs": inspect_input_source(path),
                          "native_execution": False}, indent=2))
    elif "--native" in sys.argv:
        print(json.dumps(native_verify(), indent=2))
    else:
        raise SystemExit("HOLD: choose explicit --source or --native")
