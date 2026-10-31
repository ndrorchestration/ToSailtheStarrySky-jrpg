"""First Wake review-only UE 5.8 stage builder.

Run --validate with normal Python; run --build only inside an Unreal Editor
with Python Editor Script Plugin and the compiled TSTSS C++ module.
Does not alter gameplay maps, story state, saves, unlocks or released content.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass

MAP_PATH = "/Game/TSTSS/Review/FirstWake_Benchmark_V1"
SHIP_CLASS_PATH = "/Script/ToSailTheStarrySky.AureateWakePreviewActor"
LABEL_PREFIX = "TSTSS_REVIEW_"
# Centimeters, Unreal X-forward, Z-up; all geometry is noncanonical blockout.
@dataclass(frozen=True)
class MeshPiece:
    name: str
    primitive: str
    location: tuple[float, float, float]
    scale: tuple[float, float, float]

@dataclass(frozen=True)
class ReviewCamera:
    name: str
    location: tuple[float, float, float]
    target: tuple[float, float, float]

SHIP_POSITION = (1300.0, -500.0, 180.0)
# Ocean is presentation only: no water volume, buoyancy or story trigger.
PIECES = (
    MeshPiece("Ocean_VisualOnly", "Plane", (2800, 0, -55), (120, 120, 1)),
    MeshPiece("Harbor_Quay", "Cube", (-1400, -450, 45), (15, 18, 1.2)),
    MeshPiece("Harbor_Pier", "Cube", (-20, -500, 100), (14, 3.0, .4)),
    MeshPiece("Gangway_ReviewOnly", "Cube", (740, -500, 118), (4.3, 1.1, .15)),
    MeshPiece("Dock_Rail_Left_A", "Cube", (-450, -685, 155), (4, .12, .12)),
    MeshPiece("Dock_Rail_Left_B", "Cube", (130, -685, 155), (4, .12, .12)),
    MeshPiece("Dock_Rail_Right_A", "Cube", (-450, -315, 155), (4, .12, .12)),
    MeshPiece("Dock_Rail_Right_B", "Cube", (130, -315, 155), (4, .12, .12)),
    MeshPiece("Mooring_01", "Cube", (-480, -700, 150), (.35, .35, 1.2)),
    MeshPiece("Mooring_02", "Cube", (0, -700, 150), (.35, .35, 1.2)),
    MeshPiece("Mooring_03", "Cube", (500, -700, 150), (.35, .35, 1.2)),
    MeshPiece("Coast_Rock_01", "Cube", (-2070, 610, 105), (2.4, 1.6, 1.5)),
    MeshPiece("Coast_Rock_02", "Cube", (-1830, 920, 95), (1.8, 2.1, 1.1)),
    MeshPiece("Harbor_Building_Base", "Cube", (-1950, 360, 230), (4.3, 3.5, 3.5)),
    MeshPiece("Harbor_Building_Roof", "Cube", (-1950, 360, 425), (5.0, 4.1, .4)),
)
# Named markers (not stand-in performers); only Ender and Ionia appear in First Wake preflight.
IMPORT_SLOTS = (
    ("Ender_ApprovedCast_ImportSlot", (-1910, -400, 112)),
    ("Ionia_ApprovedCast_ImportSlot", (-1150, -400, 112)),
    ("Flyer_Interaction_ImportSlot", (-1730, -220, 145)),
    ("HarmonicEngine_ImportSlot", (1300, -500, 270)),
)
CAMERAS = (
    ReviewCamera("01_Harbor_Establishing", (-2850, -2700, 1030), (-100, -420, 130)),
    ReviewCamera("02_Wake_ThreeQuarter", (90, -2300, 680), SHIP_POSITION),
    ReviewCamera("03_Gangway", (-440, -1270, 340), (710, -490, 135)),
    ReviewCamera("04_SeaLanding_CompositionOnly", (2500, -2600, 970), SHIP_POSITION),
)

def look_at_rotation(eye, target):
    """Unreal Rotator Pitch/Yaw/Roll in degrees for a +X-facing camera."""
    dx, dy, dz = (target[i] - eye[i] for i in range(3))
    horizontal = math.hypot(dx, dy)
    if horizontal < 1e-6 and abs(dz) < 1e-6:
        raise ValueError("Camera eye and target coincide")
    return (math.degrees(math.atan2(dz, horizontal)),
            math.degrees(math.atan2(dy, dx)), 0.0)

def validate_plan():
    names = [p.name for p in PIECES]
    names += [n for n, _ in IMPORT_SLOTS]
    names += [c.name for c in CAMERAS]
    names += ["AureateWake", "KeySun", "SkyFill", "SkyAtmosphere", "SeaHaze"]
    assert len(names) == len(set(names)), "Duplicate review actor label"
    assert len(CAMERAS) == 4
    assert len(IMPORT_SLOTS) == 4
    assert {"Ender_ApprovedCast_ImportSlot", "Ionia_ApprovedCast_ImportSlot"} <= set(names)
    assert all(not any(bad in n.lower() for bad in ("lyra", "talen", "orbiter", "moon_bridge", "submersible")) for n in names)
    assert all(p.primitive in ("Cube", "Plane") and min(p.scale) > 0 for p in PIECES)
    assert all(math.isfinite(v) for p in PIECES for v in (*p.location, *p.scale))
    assert all(math.isfinite(v) for c in CAMERAS for v in (*c.location, *c.target))
    for c in CAMERAS:
        look_at_rotation(c.location, c.target)
    return {"map": MAP_PATH, "ship_class": SHIP_CLASS_PATH,
            "pieces": [asdict(p) for p in PIECES],
            "import_slots": [{"name": n, "position": xyz} for n, xyz in IMPORT_SLOTS],
            "cameras": [asdict(c) for c in CAMERAS],
            "authority": "REVIEW_ONLY_NO_GAMEPLAY_OR_WATER_AUTHORITY"}

def build_in_unreal():
    plan = validate_plan()
    try:
        import unreal
    except ImportError as exc:
        raise RuntimeError("--build requires the Unreal Editor Python environment") from exc

    # Fail before touching any current level or creating an asset.
    ship_class = unreal.load_class(None, SHIP_CLASS_PATH)
    if not ship_class:
        raise RuntimeError("Compile the TSTSS Unreal C++ module first; ship actor is missing")
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        raise RuntimeError("Review map already exists: refusing destructive overwrite at " + MAP_PATH)
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("Current editor has unsaved map changes; save or discard them manually first")
    meshes = {}
    for key in ("Cube", "Plane"):
        meshes[key] = unreal.load_asset("/Engine/BasicShapes/{0}.{0}".format(key))
        if not meshes[key]:
            raise RuntimeError("Missing required engine basic shape: " + key)

    world = unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
    if not world:
        raise RuntimeError("Unreal failed to create a blank review world")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    def vec(xyz):
        return unreal.Vector(*xyz)

    def spawn(cls, name, xyz, angles=(0, 0, 0)):
        actor = actors.spawn_actor_from_class(cls, vec(xyz), unreal.Rotator(*angles))
        if not actor:
            raise RuntimeError("Unable to spawn: " + name)
        actor.set_actor_label(LABEL_PREFIX + name)
        return actor

    for piece in PIECES:
        actor = spawn(unreal.StaticMeshActor, piece.name, piece.location)
        comp = actor.get_component_by_class(unreal.StaticMeshComponent)
        if not comp:
            raise RuntimeError("No StaticMeshComponent on " + piece.name)
        comp.set_static_mesh(meshes[piece.primitive])
        actor.set_actor_scale3d(vec(piece.scale))
        comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

    ship = spawn(ship_class, "AureateWake", SHIP_POSITION)
    # Deliberately do not RequestForm: actor defaults to Skyborne.
    # Never wire the water observer or fake SeaContact/FlotationConfirmed.

    for name, xyz in IMPORT_SLOTS:
        spawn(unreal.TargetPoint, name, xyz)

    for camera in CAMERAS:
        spawn(unreal.CineCameraActor, "Camera_" + camera.name,
              camera.location, look_at_rotation(camera.location, camera.target))

    spawn(unreal.DirectionalLight, "KeySun", (0, 0, 1600), (-32, -42, 0))
    spawn(unreal.SkyLight, "SkyFill", (0, 0, 250))
    spawn(unreal.SkyAtmosphere, "SkyAtmosphere", (0, 0, 0))
    spawn(unreal.ExponentialHeightFog, "SeaHaze", (0, 0, -150))

    unreal.EditorAssetLibrary.make_directory("/Game/TSTSS/Review")
    if not unreal.EditorLoadingAndSavingUtils.save_map(world, MAP_PATH):
        raise RuntimeError("Editor did not save review map " + MAP_PATH)
    unreal.log("TSTSS review-only First Wake benchmark map created: " + MAP_PATH)
    unreal.log("Validate native rendering and frame time. NO cinematic/art/physics/gameplay approval.")
    return plan

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate", action="store_true", help="Pure Python source plan validation; no Unreal required")
    mode.add_argument("--build", action="store_true", help="Author new review map inside the Unreal Editor")
    args = parser.parse_args()
    plan = build_in_unreal() if args.build else validate_plan()
    print(json.dumps({"map": plan["map"], "piece_count": len(plan["pieces"]),
                      "camera_count": len(plan["cameras"]), "import_slot_count": len(plan["import_slots"]),
                      "authority": plan["authority"]}, indent=2))

if __name__ == "__main__":
    main()
