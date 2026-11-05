"""First Wake Prelude: native, traversable review-only interaction level.

Builds a *new* Unreal .umap using actual existing TSTSS Explorer and Milestone
C++ classes. Does not modify runtime game code, global startup maps, any saved
game, approved art, Orbiter gate or the authority of physical sea contact.
This is an early-harbor / engineering-inspection review slice, not Chapter I.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

REVIEW_MAP = "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2"
REVIEW_ONLY_PROJECT_PARENT = "TSTSS_FirstWakePreludeSandbox_20261101"
AUTHORING_PREFIX = "TSTSS_PRELUDE_REVIEW_"
MILESTONE_CLASS = "/Script/ToSailTheStarrySky.TSTSSMilestoneActor"
PLAYER_CLASS = "/Script/ToSailTheStarrySky.TSTSSExplorerCharacter"
GAMEMODE_CLASS = "/Script/ToSailTheStarrySky.TSTSSGameMode"
EXPECTED_FACING_YAW = 0.0
# All centimeters. Real chapter art and physics remain out of scope.

@dataclass(frozen=True)
class ReviewStop:
    label: str
    x: float
    y: float
    phase: str
    milestone: str = ""
    inspection: str = ""
    caption: str = ""


STOPS = (
    ReviewStop("FlyerDiscovery", -2200, 0, "Prelude", milestone="FlyerDiscovered",
               caption="01  Discover Captain Ionia's flyer  [E]"),
    ReviewStop("IoniaHiring", -1550, 0, "Prelude", milestone="IoniaHired",
               caption="02  Meet Captain Ionia  [E]   [REVIEW MARKER]"),
    ReviewStop("AureateBoarding", -900, 0, "Prelude", milestone="BoardedAureateWake",
               caption="03  Board the Aureate Wake  [E]   [REVIEW MARKER]"),
    ReviewStop("LiftStation", -250, 0, "Engineering", inspection="Lift",
               caption="04  Harmonic lift inspection  [E]"),
    ReviewStop("PressureStation", 225, 0, "Engineering", inspection="Pressure",
               caption="05  Pressure inspection  [E]"),
    ReviewStop("ReserveStation", 700, 0, "Engineering", inspection="Reserve",
               caption="06  Reserve inspection  [E]"),
    ReviewStop("EngineeringApproval", 1175, 0, "Prelude", milestone="EngineeringChecked",
               caption="07  Confirm all three checks  [E]"),
)

# Distinct platform silhouettes and visual-only waterside context.
# A collision floor is mandatory; the ocean plane is purely presentation.
FLOOR_LOCATION = (-600.0, 0.0, -100.0)
FLOOR_SCALE = (63.0, 14.0, 2.0)
OCEAN_LOCATION = (-500.0, 2100.0, -65.0)
OCEAN_SCALE = (95.0, 75.0, 1.0)
PLAYER_SPAWN = (-2780.0, 0.0, 130.0)
REVIEW_CAMERA = (-2650.0, -1800.0, 720.0)
REVIEW_CAMERA_YAW = 25.0
# Source-only reviewer geometry. UE BasicShapes Cube is 100 cm wide before
# the explicit milestone scale of (.75,.75,1.6). This cannot prove PIE hits.
REVIEW_MARKER_HALF_WIDTH_CM = 37.5
REVIEW_INTERACTION_REACH_CM = 300.0


def validate_spatial_review_plan() -> dict:
    """Validate a continuous floor footprint and honest first E-range.

    Only authoring-world XY plan geometry; not native UE collision, LOS,
    camera occlusion, navigation meshes, dynamic obstacles or PIE movement.
    """
    values = (
        *PLAYER_SPAWN, *FLOOR_LOCATION, *FLOOR_SCALE,
        REVIEW_MARKER_HALF_WIDTH_CM, REVIEW_INTERACTION_REACH_CM,
        *(coordinate for stop in STOPS for coordinate in (stop.x, stop.y)),
    )
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("Nonfinite Prelude path or collision dimensions")
    if any(s <= 0 for s in FLOOR_SCALE):
        raise ValueError("Review floor dimensions must be positive")
    if REVIEW_INTERACTION_REACH_CM <= 0 or REVIEW_MARKER_HALF_WIDTH_CM <= 0:
        raise ValueError("Review marker width and interaction distance must be positive")

    # The blockout traversal floor is a scaled 100cm BasicShapes cube.
    floor_min_x = FLOOR_LOCATION[0] - FLOOR_SCALE[0] * 50
    floor_max_x = FLOOR_LOCATION[0] + FLOOR_SCALE[0] * 50
    floor_min_y = FLOOR_LOCATION[1] - FLOOR_SCALE[1] * 50
    floor_max_y = FLOOR_LOCATION[1] + FLOOR_SCALE[1] * 50
    floor_top_z = FLOOR_LOCATION[2] + FLOOR_SCALE[2] * 50
    if abs(floor_top_z) > 5:
        raise ValueError("Review traversal floor top has drifted from height zero")

    # The initial pawn and the full marker footprints must fit on the
    # continuous floor. AABB coverage is necessary, not sufficient for PIE.
    x, y, z = PLAYER_SPAWN
    if not (floor_min_x < x < floor_max_x and floor_min_y < y < floor_max_y):
        raise ValueError("First Wake player start is outside traversal floor")
    if z < floor_top_z:
        raise ValueError("Review player start is below the floor collision top")
    for stop in STOPS:
        if not (floor_min_x < stop.x - REVIEW_MARKER_HALF_WIDTH_CM and
                stop.x + REVIEW_MARKER_HALF_WIDTH_CM < floor_max_x and
                floor_min_y < stop.y - REVIEW_MARKER_HALF_WIDTH_CM and
                stop.y + REVIEW_MARKER_HALF_WIDTH_CM < floor_max_y):
            raise ValueError("Review interaction marker outside traversal floor: " + stop.label)

    # Spawn must be far enough away that the flyer cannot be activated
    # immediately from the starting pawn position even at its nearest edge.
    first = STOPS[0]
    nearest_x = max(abs(first.x - x) - REVIEW_MARKER_HALF_WIDTH_CM, 0.0)
    nearest_y = max(abs(first.y - y) - REVIEW_MARKER_HALF_WIDTH_CM, 0.0)
    spawn_to_flyer_nearest_edge = math.hypot(nearest_x, nearest_y)
    if spawn_to_flyer_nearest_edge <= REVIEW_INTERACTION_REACH_CM:
        raise ValueError("Flyer review marker is already within 300cm of player spawn")

    return {
        "floor_x_cm": [floor_min_x, floor_max_x],
        "floor_y_cm": [floor_min_y, floor_max_y],
        "floor_top_z_cm": floor_top_z,
        "spawn_to_flyer_nearest_xy_edge_cm": round(spawn_to_flyer_nearest_edge, 2),
        "all_seven_marker_footprints_on_floor": True,
        "native_visibility_or_pie_tested": False,
    }


def validate_plan() -> dict:
    names = [s.label for s in STOPS]
    if len(names) != len(set(names)) or len(STOPS) != 7:
        raise ValueError("Prelude review requires seven unique interaction stops")
    milestones = [s.milestone for s in STOPS if s.milestone]
    if milestones != ["FlyerDiscovered", "IoniaHired",
                      "BoardedAureateWake", "EngineeringChecked"]:
        raise ValueError("Opening narrative order changed")
    stations = [s.inspection for s in STOPS if s.inspection]
    if stations != ["Lift", "Pressure", "Reserve"]:
        raise ValueError("Three separate engineering inspections required")
    if any(s.inspection and s.milestone for s in STOPS):
        raise ValueError("A milestone cannot double as an inspection")
    if any(forbidden in (" ".join(names + milestones + stations)).lower()
           for forbidden in ("seacontact", "flotationconfirmed", "orbiter",
                             "submersible", "lyra", "talen", "reson", "aepex")):
        raise ValueError("Story/physics gate or premature party member in review stage")
    if any(STOPS[i].x >= STOPS[i + 1].x for i in range(len(STOPS) - 1)):
        raise ValueError("Interaction path must be ordered and traversable")
    if STOPS[0].x - PLAYER_SPAWN[0] < 250:
        raise ValueError("Player spawn must precede flyer interaction")
    geometry = validate_spatial_review_plan()
    return {
        "status": "REVIEW_ONLY_TRAVERSABLE_PRELUDE_NO_GAMEPLAY_PROOF",
        "map": REVIEW_MAP,
        "stops": [asdict(s) for s in STOPS],
        "player_start_cm": PLAYER_SPAWN,
        "authoring_geometry_only": geometry,
        "floor_location_cm": FLOOR_LOCATION,
        "floor_scale": FLOOR_SCALE,
        "ocean_is_visual_only": True,
        "water_physics_events_issued": False,
        "launch_progression_issued": False,
        "canon_cast_art_present": False,
        "automatic_party_recruitment": False,
        "orbiter_unlocked": False,
        "production_map_modified": False,
        "approved_gameplay": False,
        "controls": "WASD mouse look, E interact, F5 quicksave, F9 quickload",
    }


def assert_disposable_project(project_dir: str) -> Path:
    path = Path(project_dir).resolve()
    if path.name.lower() != "unreal" or path.parent.name != REVIEW_ONLY_PROJECT_PARENT:
        raise RuntimeError("Refusing to author anywhere outside isolated First Wake Prelude sandbox")
    return path


def build_in_unreal() -> dict:
    plan = validate_plan()
    import unreal
    project = assert_disposable_project(unreal.Paths.project_dir())
    if unreal.EditorAssetLibrary.does_asset_exist(REVIEW_MAP):
        raise RuntimeError("Review map exists: never overwrite a map")
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("Existing dirty Editor map: refuse to discard changes")

    actor_class = unreal.load_class(None, MILESTONE_CLASS)
    pawn_class = unreal.load_class(None, PLAYER_CLASS)
    game_mode_class = unreal.load_class(None, GAMEMODE_CLASS)
    if any(cls is None for cls in (actor_class, pawn_class, game_mode_class)):
        raise RuntimeError("Actual C++ milestone/pawn/GameMode classes must compile before staging")
    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    plane = unreal.load_asset("/Engine/BasicShapes/Plane.Plane")
    if cube is None or plane is None:
        raise RuntimeError("Required engine BasicShapes missing")
    if not unreal.EditorAssetLibrary.does_directory_exist("/Game/TSTSS/Review"):
        unreal.EditorAssetLibrary.make_directory("/Game/TSTSS/Review")

    world = unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
    if world is None:
        raise RuntimeError("Could not create the isolated review world")
    editor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    def spawn(cls, name, xyz):
        obj = editor.spawn_actor_from_class(cls, unreal.Vector(*xyz),
                                            unreal.Rotator(pitch=0, yaw=0, roll=0))
        if obj is None:
            raise RuntimeError("Could not spawn "+name)
        obj.set_actor_label(AUTHORING_PREFIX + name)
        return obj

    def set_mesh(actor, mesh, scale, collision):
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is None:
            raise RuntimeError("Expected native StaticMeshComponent")
        component.set_static_mesh(mesh)
        actor.set_actor_scale3d(unreal.Vector(*scale))
        component.set_collision_enabled(
            unreal.CollisionEnabled.QUERY_AND_PHYSICS if collision
            else unreal.CollisionEnabled.NO_COLLISION)
        # The component collision_enabled call alone does not persist for
        # BasicShapes Plane in a saved .umap; V1 reloaded as BlockAll.
        # Persist the named profile, then confirm the runtime mode.
        component.set_collision_profile_name("BlockAll" if collision else "NoCollision")
        component.set_collision_enabled(
            unreal.CollisionEnabled.QUERY_AND_PHYSICS if collision
            else unreal.CollisionEnabled.NO_COLLISION)
        if component.get_collision_enabled() != (
                unreal.CollisionEnabled.QUERY_AND_PHYSICS if collision
                else unreal.CollisionEnabled.NO_COLLISION):
            raise RuntimeError("Unreal collision assignment was not applied")

    ground = spawn(unreal.StaticMeshActor, "Harbor_TraversalFloor",
                   FLOOR_LOCATION)
    set_mesh(ground, cube, FLOOR_SCALE, True)

    sea = spawn(unreal.StaticMeshActor, "Ocean_VISUAL_ONLY_NO_BUOYANCY",
                OCEAN_LOCATION)
    set_mesh(sea, plane, OCEAN_SCALE, False)

    # In-world harbor context. Nothing in this visual-only prop list is a
    # canon model for Ionia, Ender or Aureate Wake.
    for n, location, scale in (
        ("QuaysideWall", (-2200, -720, 75), (15, 1, 1.5)),
        ("GangwayVisualMarker", (-1050, 800, 35), (6, 3, .7)),
        ("EngineBayVisualMarker", (250, 750, 120), (4, 2, 2.4)),
        ("HarborStorehouseBlockout", (-3200, 650, 350), (5, 4, 7)),
    ):
        prop = spawn(unreal.StaticMeshActor, n, location)
        set_mesh(prop, cube, scale, False)

    def reflected_enum_member(enum_type, canonical_name):
        # UE Python exposes UENUM values with its own underscored name policy
        # (e.g. FLYER_DISCOVERED, not FLYERDISCOVERED). Resolve by comparing
        # normalized tokens without guessing numbering or bypassing canon.
        target = canonical_name.replace("_", "").upper()
        matched = [getattr(enum_type, name) for name in dir(enum_type)
                   if name.isupper() and name.replace("_", "") == target]
        if len(matched) != 1:
            raise RuntimeError("Unknown or ambiguous native enum name: " + canonical_name)
        return matched[0]

    for stop in STOPS:
        actor = spawn(actor_class, stop.label, (stop.x, stop.y, 90))
        set_mesh(actor, cube, (.75, .75, 1.6), True)
        if stop.inspection:
            actor.set_editor_property("is_inspection_station", True)
            actor.set_editor_property(
                "inspection_station",
                reflected_enum_member(unreal.TSTSSInspectionStation, stop.inspection))
        else:
            actor.set_editor_property(
                "milestone",
                reflected_enum_member(unreal.TSTSSFirstWakeBeat, stop.milestone))
        # If signage fails we fail the staging operation; no invisible
        # instruction markers should be represented as a playable proof.
        sign = spawn(unreal.TextRenderActor, "SIGN_" + stop.label,
                     (stop.x - 175.0, stop.y + 100.0, 250.0))
        text_comp = sign.get_component_by_class(unreal.TextRenderComponent)
        if text_comp is None:
            raise RuntimeError("Required TextRenderComponent missing")
        text_comp.set_text(stop.caption)
        text_comp.set_editor_property("world_size", 45.0)

    start = spawn(unreal.PlayerStart, "PlayerStart_Ender_REVIEW_PROXY", PLAYER_SPAWN)
    start.set_actor_rotation(unreal.Rotator(pitch=0, yaw=EXPECTED_FACING_YAW, roll=0), False)

    # Lighting and a fixed review angle. These do not save a movie or
    # emulate any approved cinematic moment.
    spawn(unreal.DirectionalLight, "ReviewDirectionalLight", (0, 0, 1800))
    spawn(unreal.SkyLight, "ReviewSkyFill", (0, 0, 800))
    camera = spawn(unreal.CameraActor, "PreludeOverview_Camera", REVIEW_CAMERA)
    camera.set_actor_rotation(unreal.Rotator(pitch=-12, yaw=REVIEW_CAMERA_YAW, roll=0), False)

    if not unreal.EditorLoadingAndSavingUtils.save_map(world, REVIEW_MAP):
        raise RuntimeError("Unreal could not save the new isolated Prelude review level")
    receipt_dir = project / "Saved" / "PreludeInteractionV2"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    saved = project / "Content" / "TSTSS" / "Review" / "FirstWake_PreludeInteraction_V2.umap"
    if not saved.is_file():
        raise RuntimeError("Expected native .umap was not saved")
    plan["status"] = "NATIVE_REVIEW_MAP_SAVED_NOT_PLAYTESTED"
    plan["map_sha256"] = hashlib.sha256(saved.read_bytes()).hexdigest()
    plan["map_bytes"] = saved.stat().st_size
    result = receipt_dir / "native_staging_receipt.json"
    if result.exists():
        raise RuntimeError("Review staging receipt exists: refuse overwrite")
    result.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    unreal.log("TSTSS_PRELUDE_REVIEW_NATIVE_STAGE_SAVED " + str(saved))
    return plan


def main(argv=None):
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--validate", action="store_true")
    modes.add_argument("--build", action="store_true")
    args = parser.parse_args(argv)
    result = build_in_unreal() if args.build else validate_plan()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
