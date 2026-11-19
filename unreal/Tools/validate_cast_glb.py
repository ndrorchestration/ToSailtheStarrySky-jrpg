"""Validate private, creator-directed First Wake cast references and rigged GLB files.

Source-only validation can run without Unreal. Unreal Editor review import is explicitly
opt-in and creates only new, isolated candidate assets. It never certifies artistic
approval, likeness, animation quality, combat readiness, or a release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

SCHEMA = "tstss-first-wake-cast-candidate-v1"
APPROVED_REFERENCE_DECISION = "creator-visual-reference-2026-10-30"
MAX_SOURCE_BYTES = 256 * 1024 * 1024
HEX256 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_CHARACTERS = frozenset({"ender", "ionia"})
GLB_JSON = 0x4E4F534A
GLB_BIN = 0x004E4942


class IntakeFailure(ValueError):
    pass


def _safe_file(root: Path, name: str, extension: tuple[str, ...]) -> Path:
    if not isinstance(name, str) or not name or "\x00" in name:
        raise IntakeFailure("Missing or invalid relative asset path")
    value = Path(name)
    if value.is_absolute() or any(part in ("..", ".") for part in value.parts):
        raise IntakeFailure("Absolute/traversal paths are not permitted")
    root = root.resolve(strict=True)
    source = (root / value).resolve(strict=True)
    if root not in source.parents or not source.is_file():
        raise IntakeFailure("Asset is not a normal file inside the private source root")
    if source.suffix.lower() not in extension or source.stat().st_size > MAX_SOURCE_BYTES:
        raise IntakeFailure("Unsupported file extension or oversized asset")
    return source


def _check_sha(value: str, actual: str) -> None:
    if not isinstance(value, str) or not HEX256.fullmatch(value) or value != actual:
        raise IntakeFailure("Source SHA-256 missing, malformed or does not match")


def _image_metadata(path: Path) -> dict:
    with path.open("rb") as file:
        prefix = file.read(24)
        if path.suffix.lower() == ".png":
            if prefix[:8] != b"\x89PNG\r\n\x1a\n" or prefix[12:16] != b"IHDR":
                raise IntakeFailure("Reference PNG header invalid")
            width, height = struct.unpack(">II", prefix[16:24])
        elif path.suffix.lower() in (".jpg", ".jpeg"):
            if not prefix.startswith(b"\xff\xd8\xff"):
                raise IntakeFailure("Reference JPEG header invalid")
            # JPEG dimensions are not authenticated here: image review is mandatory.
            return {"format": "JPEG", "dimensions": "REVIEW_REQUIRED"}
        else:
            raise IntakeFailure("Reference must be a PNG or JPEG")
    if not (256 <= width <= 16384 and 256 <= height <= 16384):
        raise IntakeFailure("Reference image dimensions outside review limits")
    return {"format": "PNG", "width": width, "height": height}


def inspect_glb(path: Path) -> dict:
    """Check GLB structural readiness; this is not a full glTF validator or rig QA."""
    data = path.read_bytes()
    if len(data) < 28 or data[:4] != b"glTF":
        raise IntakeFailure("Not a binary glTF (GLB) file")
    version, total = struct.unpack_from("<II", data, 4)
    if version != 2 or total != len(data) or total % 4:
        raise IntakeFailure("Unsupported GLB version, length, or alignment")
    pos, chunks = 12, []
    while pos < total:
        if pos + 8 > total:
            raise IntakeFailure("Truncated GLB chunk")
        length, kind = struct.unpack_from("<II", data, pos)
        pos += 8
        if length % 4 or pos + length > total:
            raise IntakeFailure("Invalid GLB chunk bounds or alignment")
        chunks.append((kind, data[pos:pos + length]))
        pos += length
    if len(chunks) != 2 or chunks[0][0] != GLB_JSON or chunks[1][0] != GLB_BIN:
        raise IntakeFailure("Require an embedded JSON and BIN GLB with no external blobs")
    try:
        doc = json.loads(chunks[0][1].rstrip(b" \t\r\n\0").decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntakeFailure("GLB JSON is malformed") from exc
    if not isinstance(doc, dict) or doc.get("asset", {}).get("version") != "2.0":
        raise IntakeFailure("Expected glTF asset 2.0")
    buffers = doc.get("buffers", [])
    if len(buffers) != 1 or "uri" in buffers[0] or not isinstance(buffers[0].get("byteLength"), int) or buffers[0]["byteLength"] > len(chunks[1][1]):
        raise IntakeFailure("GLB must contain exactly one embedded BIN buffer")
    for image in doc.get("images", []):
        if "uri" in image or "bufferView" not in image:
            raise IntakeFailure("Referenced textures must be embedded in GLB")
    nodes, skins, meshes = doc.get("nodes", []), doc.get("skins", []), doc.get("meshes", [])
    if not nodes or not skins or not meshes:
        raise IntakeFailure("GLB lacks nodes, rig skin or mesh geometry")
    joints = set()
    for skin in skins:
        ids = skin.get("joints", [])
        if not isinstance(ids, list) or not ids or any(type(i) is not int or not 0 <= i < len(nodes) for i in ids):
            raise IntakeFailure("Skin joint references are invalid")
        joints.update(ids)
    if len(joints) < 20:
        raise IntakeFailure("Insufficient named skeletal joints for a production hero candidate")
    joint_names = [str(nodes[j].get("name", "")).lower() for j in joints]
    if not any("head" in name for name in joint_names):
        raise IntakeFailure("Expected identifiable head joint for character review")
    skinned = any("skin" in node and "mesh" in node for node in nodes)
    required_attrs = {"POSITION", "NORMAL", "TEXCOORD_0", "JOINTS_0", "WEIGHTS_0"}
    complete_primitive = any(
        required_attrs.issubset(set(p.get("attributes", {})))
        for mesh in meshes for p in mesh.get("primitives", [])
    )
    if not skinned or not complete_primitive:
        raise IntakeFailure("Missing skinned geometry with normals, UVs and skin weights")
    animations = doc.get("animations", [])
    if not animations or not any(a.get("channels") and a.get("samplers") for a in animations):
        raise IntakeFailure("At least one keyed skeletal animation is required")
    if not doc.get("materials"):
        raise IntakeFailure("No material slots found")
    return {"joints": len(joints), "meshes": len(meshes), "materials": len(doc["materials"]),
            "animations": len(animations), "embedded_images": len(doc.get("images", [])),
            "glb_sha256": hashlib.sha256(data).hexdigest()}


def validate_manifest(manifest_path: Path, source_root: Path, require_both=False) -> dict:
    source_root = source_root.resolve(strict=True)
    try:
        pack = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntakeFailure("Invalid input manifest") from exc
    if not isinstance(pack, dict) or pack.get("schema") != SCHEMA:
        raise IntakeFailure("Unsupported manifest schema")
    reference = pack.get("creator_reference")
    if not isinstance(reference, dict) or reference.get("decision") != APPROVED_REFERENCE_DECISION:
        raise IntakeFailure("Missing creator decision reference; manifest does not itself grant approval")
    ref_path = _safe_file(source_root, reference.get("path"), (".png", ".jpg", ".jpeg"))
    _check_sha(reference.get("sha256"), hashlib.sha256(ref_path.read_bytes()).hexdigest())
    reference_info = _image_metadata(ref_path)
    models = pack.get("characters", [])
    if not isinstance(models, list) or not models or len(models) > 2:
        raise IntakeFailure("Provide one or two First Wake hero model candidates")
    observed = {}
    for item in models:
        if not isinstance(item, dict) or item.get("id") not in ALLOWED_CHARACTERS:
            raise IntakeFailure("Only Ender/Ionia have First Wake hero import slots")
        hero = item["id"]
        if hero in observed:
            raise IntakeFailure("Duplicate character import entry")
        file = _safe_file(source_root, item.get("model_path"), (".glb",))
        parsed = inspect_glb(file)
        _check_sha(item.get("model_sha256"), parsed["glb_sha256"])
        observed[hero] = {"source_model": str(file), "source_sha256": parsed["glb_sha256"],
                          "review_folder": f"/Game/TSTSS/Review/CastCandidates/{hero.title()}",
                          "structural_readiness": parsed}
    if require_both and set(observed) != ALLOWED_CHARACTERS:
        raise IntakeFailure("Both Ender and Ionia must have model candidates for the cast gate")
    return {"authority": "CANDIDATE_ONLY_NOT_CREATOR_ART_APPROVAL",
            "creator_decision": reference["decision"], "reference_sha256": reference["sha256"],
            "reference": reference_info, "characters": observed,
            "missing": sorted(ALLOWED_CHARACTERS - set(observed))}


def import_review(validated: dict) -> dict:
    """Run only inside the UE editor. Fails on any nonempty intended import folder."""
    try:
        import unreal
    except ImportError as exc:
        raise IntakeFailure("Unreal Editor Python is required for --import-review") from exc
    library = unreal.EditorAssetLibrary
    for entry in validated["characters"].values():
        path = entry["review_folder"]
        if library.does_directory_exist(path) and library.list_assets(path, recursive=True, include_folder=False):
            raise IntakeFailure("Review import destination is not empty: " + path)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    created = {}
    for hero, entry in validated["characters"].items():
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", entry["source_model"])
        task.set_editor_property("destination_path", entry["review_folder"])
        task.set_editor_property("automated", False)  # Let artist inspect Interchange pipeline choices.
        task.set_editor_property("replace_existing", False)
        task.set_editor_property("save", True)
        tools.import_asset_tasks([task])
        paths = list(task.get_editor_property("imported_object_paths"))
        if not paths:
            raise IntakeFailure(f"Unreal import returned no created assets for {hero}")
        objects = [unreal.load_asset(path) for path in paths]
        if not any(isinstance(obj, unreal.SkeletalMesh) for obj in objects if obj is not None):
            raise IntakeFailure(f"No SkeletalMesh imported for {hero}; review candidate assets manually")
        created[hero] = {"paths": paths, "status": "EDITOR_IMPORTED_NOT_ART_ACCEPTED"}
    return created


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--require-both", action="store_true")
    parser.add_argument("--import-review", action="store_true", help="Unreal Editor only; creates new candidate imports")
    args = parser.parse_args(argv)
    try:
        result = validate_manifest(args.manifest, args.source_root, args.require_both)
        if args.import_review:
            result["unreal_import"] = import_review(result)
        # Source paths and source material remain local; output contains only hashes/structural metrics.
        report = {k: v for k, v in result.items() if k != "characters"}
        report["characters"] = {hero: {k: value for k, value in entry.items() if k != "source_model"}
                                 for hero, entry in result["characters"].items()}
        print(json.dumps(report, indent=2))
    except (IntakeFailure, OSError, KeyError, TypeError, IndexError) as exc:
        parser.exit(1, "CAST INTAKE HOLD: " + str(exc) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
