"""UE 5.8 Editor-only, review-folder intake for static cast lookdev GLBs.

Run via Unreal's Python Script Plugin; default imports Ender only. A standard
Python --preflight-only mode checks the exact source bytes without Unreal.
"""
import hashlib
import json
import os
from pathlib import Path
import struct
import sys

NAMES = ("Ender", "Ionia", "Lyra", "Reson", "Aepex")
ROOT = Path(__file__).resolve().parent
SOURCES = Path(os.environ.get("TSTSS_CAST_SOURCE", ROOT / "Candidates"))
DEST_ROOT = "/Game/ArtLookdev/Characters"


def validate_sources(source_dir=SOURCES):
    manifest = json.loads((source_dir / "manifest.json").read_text(encoding="utf-8"))
    records = manifest["characters"]
    if tuple(record["name"] for record in records) != NAMES:
        raise ValueError("Unexpected cast manifest order or identities")
    for record in records:
        name = record["name"]
        path = source_dir / (name + ".glb")
        data = path.read_bytes()
        if (len(data) < 28 or data[:4] != b"glTF" or
                struct.unpack_from("<II", data, 4) != (2, len(data))):
            raise ValueError(name + ": invalid glTF 2.0 header/length")
        if hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError(name + ": source hash mismatch")
        json_size, json_type = struct.unpack_from("<I4s", data, 12)
        if json_type != b"JSON" or json_size % 4 or 20 + json_size + 8 > len(data):
            raise ValueError(name + ": malformed JSON chunk")
        doc = json.loads(data[20:20 + json_size])
        if (len(doc.get("meshes", [])) != 1 or len(doc.get("nodes", [])) != 1 or
                doc.get("skins") or doc.get("animations")):
            raise ValueError(name + ": expected one unrigged lookdev mesh")
        if len(doc["meshes"][0]["primitives"]) != record["material_sections"]:
            raise ValueError(name + ": material section count mismatch")
        binary_size, binary_type = struct.unpack_from("<I4s", data, 20 + json_size)
        if binary_type != b"BIN\x00" or 28 + json_size + binary_size != len(data):
            raise ValueError(name + ": malformed binary chunk")
    return records


def import_one(unreal, name, record, source_dir):
    destination = DEST_ROOT + "/" + name
    library = unreal.EditorAssetLibrary
    if library.does_directory_exist(destination) and library.list_assets(destination, recursive=True):
        raise RuntimeError(name + ": review folder already contains assets; no replacement allowed")
    task = unreal.AssetImportTask()
    for key, value in (("filename", str(source_dir / (name + ".glb"))),
                       ("destination_path", destination),
                       ("automated", True), ("replace_existing", False),
                       ("save", True)):
        task.set_editor_property(key, value)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    objects = list(task.get_objects())
    meshes = [obj for obj in objects if isinstance(obj, unreal.StaticMesh)]
    if len(meshes) != 1:
        raise RuntimeError(name + ": expected one StaticMesh, got " + str(len(meshes)))
    bounds = meshes[0].get_bounding_box()
    low, high = bounds.min, bounds.max
    xyz = [abs(getattr(high, axis) - getattr(low, axis)) for axis in ("x", "y", "z")]
    height_cm = max(xyz)
    if not 150 <= height_cm <= 230:
        raise RuntimeError(name + ": suspicious imported extent: " + str(xyz))
    return {"name": name, "sha256": record["sha256"],
            "mesh": meshes[0].get_path_name(), "bounds_cm": xyz,
            "all_imported_objects": [obj.get_path_name() for obj in objects]}


def main():
    records = validate_sources(SOURCES)
    if "--preflight-only" in sys.argv:
        print("TSTSS_CAST_PREFLIGHT_PASS " + ",".join(NAMES))
        return
    import unreal  # Available only inside the UE Editor with Python Script Plugin.
    selection = os.environ.get("TSTSS_CAST_IMPORT", "Ender")
    if selection not in NAMES and selection != "all":
        raise ValueError("TSTSS_CAST_IMPORT must be a protagonist name or all")
    chosen = records if selection == "all" else [next(r for r in records if r["name"] == selection)]
    receipt_dir = Path(unreal.Paths.project_dir()) / "Saved" / "CharacterLookdev"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    session = os.environ.get("TSTSS_CAST_SESSION", "manual")
    if not session.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Invalid session label")
    receipt_path = receipt_dir / (session + ".json")
    if receipt_path.exists():
        raise RuntimeError("Receipt already exists; use a new session label")
    result = {"status": "FAILED", "kind": "STATIC_LOOKDEV_ONLY", "requested": selection,
              "imported": [], "engine": unreal.SystemLibrary.get_engine_version()}
    try:
        for record in chosen:
            result["imported"].append(import_one(unreal, record["name"], record, SOURCES))
        result["status"] = "IMPORT_PASS_REVIEW_PENDING"
    except Exception as exc:
        result["error"] = str(exc)
        raise
    finally:
        receipt_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        unreal.log("TSTSS_CAST_RECEIPT " + str(receipt_path) + " " + result["status"])


if __name__ == "__main__":
    main()
