"""Build a reversible native Unreal static-cast lineup review map.

Requires previous successful editor_intake.py -- TSTSS_CAST_IMPORT=all.
This is a visualization/staging map only, never production character art.
"""
import json
import math
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from editor_intake import validate_sources, NAMES, DEST_ROOT

MAP_PATH = "/Game/ArtLookdev/ReviewMaps/TSTSS_CastLineup_Review"
# Creator-locked ranking, not a claim that the numerical lookdev heights are canon.
HEIGHT_RANK = ("Reson", "Aepex", "Ender", "Ionia", "Lyra")

def check_height_order(records):
    heights = {r["name"]: r.get("height_m") for r in records}
    if any(type(heights[n]) not in (int, float) or not math.isfinite(heights[n])
           or heights[n] <= 0 for n in HEIGHT_RANK):
        raise ValueError("Invalid intrinsic cast body height")
    if any(heights[a] <= heights[b] for a, b in zip(HEIGHT_RANK, HEIGHT_RANK[1:])):
        raise ValueError("Canonical cast height order violated")
    return heights

def check_inputs(project_dir):
    records = validate_sources()
    check_height_order(records)
    expected = {r["name"]: r["sha256"] for r in records}
    label = os.environ.get("TSTSS_CAST_INPUT_SESSION", "five_cast_20261101_a")
    if not label.replace("_", "").replace("-", "").isalnum():
        raise ValueError("Invalid source session")
    path = Path(project_dir) / "Saved" / "CharacterLookdev" / (label + ".json")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    if (receipt.get("status") != "IMPORT_PASS_REVIEW_PENDING" or
        receipt.get("kind") != "STATIC_LOOKDEV_ONLY" or
        receipt.get("requested") != "all"):
        raise ValueError("Cannot stage without full successful native intake")
    imported = receipt.get("imported", [])
    if [x.get("name") for x in imported] != list(NAMES):
        raise ValueError("Expected all five cast identities in order")
    for entry in imported:
        name = entry["name"]
        if entry.get("sha256") != expected[name]:
            raise ValueError(name + ": source SHA does not match checked-in manifest")
        asset = entry.get("mesh", "")
        if not asset.startswith(DEST_ROOT + "/" + name + "/") or not asset.endswith("." + name):
            raise ValueError(name + ": mesh is not in the isolated lookdev folder")
    return imported, path

def main():
    import unreal
    project_dir = unreal.Paths.project_dir()
    entries, source_receipt = check_inputs(project_dir)
    output = Path(project_dir) / "Saved" / "CharacterLookdev" / "cast_lineup_stage.json"
    if output.exists():
        raise RuntimeError("Staging receipt already exists; do not overwrite")
    if not unreal.SystemLibrary.get_engine_version().startswith("5.8."):
        raise RuntimeError("Native review validated only for UE 5.8")
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        raise RuntimeError("Refusing to replace an existing review map")
    meshes = []
    for entry in entries:
        asset = unreal.load_asset(entry["mesh"])
        if not isinstance(asset, unreal.StaticMesh):
            raise RuntimeError(entry["name"] + ": missing native StaticMesh")
        meshes.append(asset)
    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if not isinstance(cube, unreal.StaticMesh):
        raise RuntimeError("Engine calibration cube is unavailable")
    if not hasattr(unreal.EditorLevelLibrary, "new_level"):
        raise RuntimeError("EditorLevelLibrary.new_level is not exposed in this engine")
    if not unreal.EditorLevelLibrary.new_level(MAP_PATH):
        raise RuntimeError("Could not create the isolated review map")
    staged = []
    for i, (name, mesh) in enumerate(zip(NAMES, meshes)):
        actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
            mesh, unreal.Vector(0, (i - 2) * 230, 0), unreal.Rotator(0, 0, 0))
        if actor is None:
            raise RuntimeError(name + ": actor staging failed")
        actor.set_actor_label("LOOKDEV_STATIC_" + name)
        staged.append({"name": name, "actor": actor.get_actor_label(), "mesh": mesh.get_path_name()})
    marker = unreal.EditorLevelLibrary.spawn_actor_from_object(
        cube, unreal.Vector(0, 690, 90), unreal.Rotator(0, 0, 0))
    if marker is None:
        raise RuntimeError("Scale marker staging failed")
    marker.set_actor_label("CALIBRATION_180CM_NONCANON")
    marker.set_actor_scale3d(unreal.Vector(.05, .05, 1.8))
    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("Could not save the review map")
    result = {"status": "STAGED_STATIC_REVIEW_ONLY", "engine": unreal.SystemLibrary.get_engine_version(),
              "map": MAP_PATH, "source_receipt": str(source_receipt),
              "protagonists": staged, "marker": "180 cm Engine BasicShapes cube",
              "visual_approval": False, "rigging": False, "animation": False}
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("TSTSS_CAST_LINEUP_STAGE_PASS " + str(output))

if __name__ == "__main__":
    main()
