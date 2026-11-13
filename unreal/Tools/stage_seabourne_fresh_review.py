"""UE 5.8: stage an isolated new blank Seabourne geometry review map only.

Never duplicate or load an existing map in this process. Preserve VS05 bytes.
Not approved ship art, navigation, first wake quest, or gameplay evidence.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unreal

project = Path(unreal.Paths.project_dir()).resolve()
if project.parent.name != "TSTSS_V5ObjectIntegration_20261112":
    raise RuntimeError("HOLD: wrong sandbox")

source = project / "Content/TSTSS/Review/VerticalSlice/VS05_DenithFuelShanty.umap"
expected_sha = "5c83e7125eb97aa42d951e89ff1b530600bcc1738287b441f681d44bfaf963bd"
sha = lambda b: hashlib.sha256(b).hexdigest()
if not source.is_file() or sha(source.read_bytes()) != expected_sha:
    raise RuntimeError("HOLD: VS05 source hash drifted")

target = "/Game/TSTSS/Review/SeabourneRecovery/L_CoastalShip_SeabourneReview"
target_file = project / "Content/TSTSS/Review/SeabourneRecovery/L_CoastalShip_SeabourneReview.umap"
if target_file.exists() or unreal.EditorAssetLibrary.does_asset_exist(target):
    raise RuntimeError("HOLD: isolated target already occupied; never overwrite")

ship_cls = unreal.load_class(None, "/Script/ToSailTheStarrySky.AureateWakePreviewActor")
if ship_cls is None:
    raise RuntimeError("HOLD: native preview actor class unavailable")

cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
plane = unreal.load_asset("/Engine/BasicShapes/Plane.Plane")
if cube is None or plane is None:
    raise RuntimeError("HOLD: engine geometry unavailable")

materials = {}
for name in ("Ocean", "Sand", "Timber", "Brass", "Stone"):
    asset = unreal.load_asset("/Game/TSTSS/Review/VerticalSlice/M_VS_" + name)
    if asset is None:
        raise RuntimeError("HOLD: missing source-bound review material " + name)
    materials[name] = asset

world = unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
if world is None:
    raise RuntimeError("HOLD: couldn't create an independent blank map")
actor_sys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if actor_sys is None:
    raise RuntimeError("HOLD: no editor actor subsystem")

def spawn(cls, label, loc, rotation=(0, 0, 0)):
    actor = actor_sys.spawn_actor_from_class(
        cls, unreal.Vector(*loc),
        unreal.Rotator(pitch=rotation[0], yaw=rotation[1], roll=rotation[2]))
    if actor is None:
        raise RuntimeError("HOLD: spawn failed " + label)
    actor.set_actor_label("TSTSS_SEABOURNE_REVIEW_" + label)
    return actor

def mesh_actor(label, mesh, loc, scale, material, solid):
    actor = spawn(unreal.StaticMeshActor, label, loc)
    comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    if comp is None:
        raise RuntimeError("HOLD: static mesh missing " + label)
    comp.set_static_mesh(mesh)
    comp.set_material(0, materials[material])
    comp.set_collision_profile_name("BlockAll" if solid else "NoCollision")
    comp.set_collision_enabled(
        unreal.CollisionEnabled.QUERY_AND_PHYSICS if solid
        else unreal.CollisionEnabled.NO_COLLISION)
    actor.set_actor_scale3d(unreal.Vector(*scale))
    return actor

# Single light-review environment: dock, coast, ocean, readable review text.
mesh_actor("OceanNoCollision", plane, (0, 2000, -110), (150, 150, 1), "Ocean", False)
mesh_actor("CoastalGround", cube, (0, -2600, -75), (40, 35, 1), "Sand", True)
mesh_actor("WalkablePier", cube, (0, -120, -45), (5, 40, 1), "Timber", True)
for side in (-1, 1):
    mesh_actor("PierRail" + str(side), cube, (side * 280, -150, 90),
               (0.12, 39, 1.7), "Brass", False)

ship = spawn(ship_cls, "AureateWakeVisualProxy", (0, 2600, 0), (0, 90, 0))
ship.set_editor_property("editor_review_pose", unreal.AureateWakeForm.SEABORNE)
if not ship.apply_editor_review_pose():
    raise RuntimeError("HOLD: native editor ship posing was refused")
if ship.get_current_form() != unreal.AureateWakeForm.SEABORNE:
    raise RuntimeError("HOLD: native preview was not posed Seabourne")
if ship.get_editor_property("editor_review_pose") != unreal.AureateWakeForm.SEABORNE:
    raise RuntimeError("HOLD: cannot apply Seabourne editor review pose")

spawn(unreal.PlayerStart, "ReviewPlayerStart", (0, -2650, 150), (0, 90, 0))
sun = spawn(unreal.DirectionalLight, "ReviewSun", (0, 0, 2500), (-38, 25, 0))
spawn(unreal.SkyLight, "ReviewSkyAmbient", (0, 0, 1800))

def text(label, content, loc):
    actor = spawn(unreal.TextRenderActor, label, loc, (0, -90, 0))
    comp = actor.get_component_by_class(unreal.TextRenderComponent)
    if comp is None:
        raise RuntimeError("HOLD: text renderer missing " + label)
    comp.set_text(content)
    comp.set_editor_property("world_size", 55.0)

text("Notice", "COASTAL RECOVERY | SEABOURNE REVIEW", (-200, -2100, 250))
text("Provenance", "DRAFT GEOMETRY - NO CANON ART APPROVAL", (-250, -1750, 250))
text("Navigation", "NO PLAYABLE SHIP NAVIGATION YET", (-250, -1350, 250))

# Save only this new map; never load or duplicate a second world here.
if not unreal.EditorLoadingAndSavingUtils.save_map(world, target):
    raise RuntimeError("HOLD: failed to save disposable map")
if not target_file.is_file():
    raise RuntimeError("HOLD: destination .umap not written")
if sha(source.read_bytes()) != expected_sha:
    raise RuntimeError("HOLD: source VS05 changed unexpectedly")

receipt = {
    "authority": "NONCANON_UNAPPROVED_GEOMETRY_REVIEW",
    "target": target,
    "target_sha256": sha(target_file.read_bytes()),
    "source_vs05_sha256_unchanged": expected_sha,
    "preview_ship_count_expected": 1,
    "ship_editor_pose": "Seabourne",
    "ship_position_cm": [0, 2600, 0],
    "source_map_duplicate": False,
    "gameplay_sailing": False,
    "in_editor_visual_approval": False,
}
(project / "Saved/SeabourneFreshStagingReceipt_20261113.json").write_text(
    json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
unreal.log("TSTSS_SEABOURNE_FRESH_STAGE_PASS " + json.dumps(receipt))