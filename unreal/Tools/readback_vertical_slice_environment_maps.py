#!/usr/bin/env python3
"""Read-only UE5 audit of the six newly saved First Wake environment levels."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_vertical_slice_environment_maps as source

EXPECTED = {
    "VS01_DenithHarbor": ("TSTSS_PRELUDE_REVIEW_FlyerDiscovery",
                          "TSTSS_PRELUDE_REVIEW_IoniaHiring",
                          "TSTSS_PRELUDE_REVIEW_LiftStation",
                          "TSTSS_VS_REVIEW_DENITH_HARBOR_Sign"),
    "VS02_AureateInteriors": ("TSTSS_VS_REVIEW_MainWalkableDeck",
                              "TSTSS_VS_REVIEW_GeodesicBridgeSilhouette_NotGlass",
                              "TSTSS_VS_REVIEW_HarmonicStation_LIFT",
                              "TSTSS_VS_REVIEW_DragonflyWing_3_Proxy"),
    "VS03_FirstWakeSky": ("TSTSS_VS_REVIEW_CloudShelf_00",
                           "TSTSS_VS_REVIEW_FlyingHull_NotActualFlightPawn",
                           "TSTSS_VS_REVIEW_AuroralPath_ReadabilityOnly"),
    "VS04_SplashdownSea": ("TSTSS_VS_REVIEW_OceanHorizon_Visual_NoCollision",
                            "TSTSS_VS_REVIEW_PhysicalWaterProbeVolume",
                            "TSTSS_VS_REVIEW_PhysicsHullReviewProxy_NotCanon"),
    "VS05_DenithFuelShanty": ("TSTSS_VS_REVIEW_CoastalPlatform",
                               "TSTSS_VS_REVIEW_FuelShantyCabin",
                               "TSTSS_VS_REVIEW_FuelPier"),
    "VS06_SplashdownShore": ("TSTSS_VS_REVIEW_SandCoast",
                              "TSTSS_VS_REVIEW_BasaltCliff_0",
                              "TSTSS_VS_REVIEW_ShoreBeatStaging"),
}


def readback():
    import unreal
    project = Path(unreal.Paths.project_dir()).resolve()
    if project.parent.name != source.SANDBOX:
        raise RuntimeError("HOLD: wrong sandbox")
    original = project / source.PARENT
    receipt = project / "Saved/VerticalSliceMaps/authoring_receipt.json"
    if not receipt.is_file():
        raise RuntimeError("HOLD: original native authoring receipt absent")
    expected = json.loads(receipt.read_text(encoding="utf-8"))
    if hashlib.sha256(original.read_bytes()).hexdigest() != expected["parent_sha256_unchanged"]:
        raise RuntimeError("HOLD: original Prelude changed")
    for name in source.PALETTE:
        obj_name = "M_VS_" + name.title().replace("_", "")
        material = unreal.load_asset(source.DEST + "/" + obj_name)
        if material is None:
            raise RuntimeError("HOLD: missing actual PBR material " + obj_name)
    actor_sys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    results = {}
    for name, _, _ in source.ORDER:
        if not unreal.EditorAssetLibrary.does_asset_exist(source.DEST + "/" + name):
            raise RuntimeError("HOLD: missing saved asset " + name)
        path = project / "Content/TSTSS/Review/VerticalSlice" / (name + ".umap")
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        if checksum != expected["native_map_staging"][name]["sha256"]:
            raise RuntimeError("HOLD: saved map bytes changed: " + name)
        world = unreal.EditorLoadingAndSavingUtils.load_map(source.DEST + "/" + name)
        if world is None:
            raise RuntimeError("HOLD: could not reopen " + name)
        actors = actor_sys.get_all_level_actors()
        by_label = {str(a.get_actor_label()): a for a in actors}
        for label in EXPECTED[name]:
            if label not in by_label:
                raise RuntimeError("HOLD: required native actor absent: " + label)
        for label, actor in by_label.items():
            if not label.startswith(source.PREFIX):
                continue
            mesh = actor.get_component_by_class(unreal.StaticMeshComponent)
            if mesh is not None and mesh.get_editor_property("static_mesh") is not None:
                if mesh.get_material(0) is None:
                    raise RuntimeError("HOLD: missing visual material: " + label)
        for label in ("MainWalkableDeck", "CoastalPlatform", "SandCoast"):
            whole = source.PREFIX + label
            if whole in by_label:
                mesh = by_label[whole].get_component_by_class(unreal.StaticMeshComponent)
                if mesh.get_collision_enabled() != unreal.CollisionEnabled.QUERY_AND_PHYSICS:
                    raise RuntimeError("HOLD: no walkable floor: " + whole)
        if name == "VS04_SplashdownSea":
            water = by_label[source.PREFIX + "PhysicalWaterProbeVolume"]
            hull = by_label[source.PREFIX + "PhysicsHullReviewProxy_NotCanon"]
            tags = [str(t) for t in water.get_editor_property("tags")]
            if "TSTSSWaterVolume" not in tags:
                raise RuntimeError("HOLD: missing native water authority tag")
            wm = water.get_component_by_class(unreal.StaticMeshComponent)
            hm = hull.get_component_by_class(unreal.StaticMeshComponent)
            if wm.get_collision_enabled() != unreal.CollisionEnabled.QUERY_ONLY:
                raise RuntimeError("HOLD: water overlap collision incorrect")
            if not bool(wm.get_editor_property("generate_overlap_events")):
                raise RuntimeError("HOLD: water overlap disabled")
            if bool(hm.is_simulating_physics()):
                raise RuntimeError("HOLD: hull prematurely simulating")
        if name == "VS01_DenithHarbor":
            inherited = [n for n in by_label if n.startswith("TSTSS_PRELUDE_REVIEW_")
                         and not n.startswith("TSTSS_PRELUDE_REVIEW_SIGN_")]
            if len(inherited) < 7:
                raise RuntimeError("HOLD: original seven stops missing")
        results[name] = {
            "source_sha256": checksum,
            "actor_count": len(actors),
            "required_actor_labels_read": len(EXPECTED[name]),
            "reopened_native": True,
        }
        unreal.log("TSTSS_VSLICE_READBACK_PASS " + name + " actors=" + str(len(actors)))
    output = project / "Saved/VerticalSliceMaps/independent_readback.json"
    output.write_text(json.dumps({"map_validation": results, "status":
                        "SIX_NATIVE_LEVELS_REOPENED_NOT_PIE_OR_RENDER_ACCEPTED"}, indent=2)
                      + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":
    print(json.dumps(readback(), indent=2))
