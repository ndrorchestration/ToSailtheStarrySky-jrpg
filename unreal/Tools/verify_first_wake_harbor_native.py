#!/usr/bin/env python3
"""Independent UE 5.8.4 readback of newly staged First Wake Harbor V1.

Run only in a SEPARATE headless UnrealEditor.exe -NullRHI process AFTER staging. Read-only:
never call save_current_level(), alter actor transforms, or create new assets.
This is not a GPU screenshot, animation, physics or PIE acceptance.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

# Unreal -ExecutePythonScript may use the project root as its import cwd.
# Resolve this trusted sibling recipe in the exact disposable worktree.
TOOLS_DIR = str(Path(__file__).resolve().parent)
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)
import build_first_wake_harbor_environment as harbor


def fail(reason: str):
    raise RuntimeError("TSTSS_HARBOR_NATIVE_READBACK_HOLD: " + reason)


def verify_saved_harbor_world():
    import unreal
    project = Path(unreal.Paths.project_dir()).resolve()
    if project.name.lower() != "unreal" or project.parent.name != harbor.ROOT_NAME:
        fail("unapproved project root")
    if not unreal.SystemLibrary.get_engine_version().startswith("5.8.4"):
        fail("wrong Unreal build")
    parent = project / harbor.BASE_REL
    dest = project / harbor.DEST_REL
    stage_file = project / harbor.RECEIPT_REL
    result_file = project / "Saved/FirstWakeEnvironmentV1/independent_harbor_readback.json"
    if result_file.exists():
        fail("independent receipt already exists; no replacement")
    if not parent.is_file() or harbor.sha256(parent) != harbor.BASE_SHA256:
        fail("original parent map missing or mutated")
    if not dest.is_file() or not stage_file.is_file():
        fail("staged map or native stage receipt absent")
    stage = json.loads(stage_file.read_text(encoding="utf-8"))
    if stage.get("status") != "NATIVE_HARBOR_MAP_SAVED_PENDING_INDEPENDENT_READBACK":
        fail("stage receipt lacks required native status")
    if stage.get("map_sha256") != harbor.sha256(dest):
        fail("native staged map digest mismatch")
    if stage.get("previous_actor_count") != 34:
        fail("parent actor count unexpected")
    expected_added = {
        harbor.PREFIX + prop.name for prop in harbor.PROPS
    } | {
        harbor.PREFIX + suffix for suffix in
        ("NativeSkyAtmosphere", "CoastalHeightFog", "CoastalHeroCamera")
    }
    if set(stage.get("staged_actor_labels", [])) != expected_added:
        fail("native stage actor identities differ from recipe")
    if stage.get("new_actor_count") != len(expected_added) or len(expected_added) != 50:
        fail("exact scene actor count mismatch")
    world = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not world.load_level(harbor.DEST_MAP):
        fail("cannot reload saved harbor World")
    actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
    labels = [a.get_actor_label() for a in actors]
    if len(actors) != 84 or len(set(labels)) != len(actors):
        fail("saved World actor count or unique labels incorrect")
    index = {a.get_actor_label(): a for a in actors}
    if not expected_added.issubset(index):
        fail("missing staged harbor actor")
    if sum(isinstance(a, unreal.PlayerStart) for a in actors) != 1:
        fail("original PlayerStart lost or duplicated")
    for name in harbor.MILESTONES:
        label = "TSTSS_PRELUDE_REVIEW_" + name
        if label not in index or index[label].get_class().get_name() != "TSTSSMilestoneActor":
            fail("story milestone absent: " + label)
    if any("STARBOURNE" in n.upper() for n in labels):
        fail("Starbourne actor appeared in gated First Wake")
    paths = {}
    for spec in harbor.PROPS:
        label = harbor.PREFIX + spec.name
        actor = index[label]
        if not isinstance(actor, unreal.StaticMeshActor):
            fail("scenery actor not StaticMeshActor: " + label)
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is None:
            fail("scenery missing StaticMeshComponent: " + label)
        mesh = component.get_editor_property("static_mesh")
        if not isinstance(mesh, unreal.StaticMesh):
            fail("scenery missing real Unreal StaticMesh: " + label)
        expected_mesh = "/Engine/BasicShapes/" + spec.mesh
        got = mesh.get_path_name().split(".")[0]
        if got != expected_mesh:
            fail("wrong mesh for " + label + " got " + got)
        if actor.get_actor_enable_collision():
            fail("new scenery unexpectedly collides: " + label)
        if component.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
            fail("new scenery component collision drift: " + label)
        material = component.get_material(0)
        expected_mat = harbor.MATERIAL_DIR + "/M_" + spec.material
        if material is None or material.get_path_name().split(".")[0] != expected_mat:
            fail("wrong native material binding: " + label)
        paths[label] = {"mesh": got, "material": expected_mat}
    for suffix, cls in (
        ("NativeSkyAtmosphere", unreal.SkyAtmosphere),
        ("CoastalHeightFog", unreal.ExponentialHeightFog),
        ("CoastalHeroCamera", unreal.CameraActor),
    ):
        if not isinstance(index[harbor.PREFIX + suffix], cls):
            fail("native environment actor class drift " + suffix)
    for role in harbor.PALETTE:
        mat_path = harbor.MATERIAL_DIR + "/M_" + role
        material = unreal.load_asset(mat_path)
        if not isinstance(material, unreal.Material):
            fail("missing saved native material " + mat_path)
    suns = [a for a in actors if isinstance(a, unreal.DirectionalLight)]
    if len(suns) != 1:
        fail("scene must preserve exactly one directional sun")
    sun = suns[0].get_component_by_class(unreal.DirectionalLightComponent)
    if sun is None or not sun.get_editor_property("atmosphere_sun_light"):
        fail("native sky not linked to original sun")
    if harbor.sha256(dest) != stage["map_sha256"]:
        fail("readback changed staged World")
    if harbor.sha256(parent) != harbor.BASE_SHA256:
        fail("readback changed parent World")
    result = {
        "status": "INDEPENDENT_NATIVE_HARBOR_SAVED_WORLD_READBACK_PASS_NOT_PIE",
        "engine": unreal.SystemLibrary.get_engine_version(),
        "new_map": harbor.DEST_MAP,
        "new_map_sha256": stage["map_sha256"],
        "parent_sha256": harbor.BASE_SHA256,
        "total_actor_count": len(actors),
        "inherited_actor_count": 34,
        "new_collision_disabled_visual_meshes": len(harbor.PROPS),
        "new_atmosphere_fog_camera_actors": 3,
        "new_materials_verified": len(harbor.PALETTE),
        "milestones_verified": len(harbor.MILESTONES),
        "player_starts_verified": 1,
        "native_mesh_and_material_paths": paths,
        "actual_map_saved_during_readback": False,
        "real_player_input_verified": False,
        "native_gpu_capture_verified": False,
        "ocean_physics_verified": False,
        "creator_art_approved": False,
        "production_content_modified": False,
        "starbourne_unlocked": False,
    }
    with result_file.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
    unreal.log(
        "TSTSS_HARBOR_INDEPENDENT_READBACK_PASS_NOT_PIE " +
        json.dumps({"map_sha256": result["new_map_sha256"],
                    "total_actors": result["total_actor_count"]})
    )
    return result


if __name__ == "__main__":
    print(json.dumps(verify_saved_harbor_world(), indent=2, sort_keys=True))
