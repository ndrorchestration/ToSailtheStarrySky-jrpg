"""Offline security/structural checks; fixtures do not represent approved art."""
import hashlib
import importlib.util
import json
import pathlib
import struct
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Tools" / "validate_cast_glb.py"
spec = importlib.util.spec_from_file_location("validate_cast_glb", SCRIPT)
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)


def fake_glb(*, skin=True, animation=True, head=True, uv=True, embedded=True):
    nodes = [{"name": ("head" if i == 8 and head else f"bone_{i}")}
             for i in range(24)]
    nodes.append({"name": "character_mesh", "mesh": 0, "skin": 0})
    attributes = {a: 0 for a in ("POSITION", "NORMAL", "JOINTS_0", "WEIGHTS_0")}
    if uv:
        attributes["TEXCOORD_0"] = 0
    doc = {
        "asset": {"version": "2.0"},
        "buffers": [{"byteLength": 4}],
        "nodes": nodes,
        "meshes": [{"primitives": [{"attributes": attributes}]}],
        "skins": [{"joints": list(range(24))}] if skin else [],
        "materials": [{"name": "M_Candidate"}],
        "images": [{"bufferView": 0, "mimeType": "image/png"}] if embedded else [{"uri": "missing.png"}],
        "animations": [{"samplers": [{"input": 0, "output": 0}],
                        "channels": [{"sampler": 0, "target": {"node": 0, "path": "rotation"}}]}] if animation else [],
    }
    json_chunk = json.dumps(doc, separators=(",", ":")).encode("utf-8")
    json_chunk += b" " * (-len(json_chunk) % 4)
    bin_chunk = b"\0" * 4
    total = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
    return (struct.pack("<4sII", b"glTF", 2, total) +
            struct.pack("<II", len(json_chunk), validator.GLB_JSON) + json_chunk +
            struct.pack("<II", len(bin_chunk), validator.GLB_BIN) + bin_chunk)


class CastIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        # Header-only fixture for minimal source identification test.
        self.picture = self.root / "cast.png"
        self.picture.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I4sIIBBBBB", 13, b"IHDR", 1024, 1024, 8, 6, 0, 0, 0))
        self.glb = self.root / "ender.glb"
        self.glb.write_bytes(fake_glb())
        self.pack = {
            "schema": validator.SCHEMA,
            "creator_reference": {
                "decision": validator.APPROVED_REFERENCE_DECISION,
                "path": "cast.png",
                "sha256": hashlib.sha256(self.picture.read_bytes()).hexdigest(),
            },
            "characters": [{
                "id": "ender",
                "model_path": "ender.glb",
                "model_sha256": hashlib.sha256(self.glb.read_bytes()).hexdigest(),
            }],
        }
        self.manifest = self.root / "review.json"
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.pack), encoding="utf-8")

    def test_source_only_intake_requires_real_matching_bytes(self):
        r = validator.validate_manifest(self.manifest, self.root)
        self.assertEqual(set(r["characters"]), {"ender"})
        self.assertEqual(r["missing"], ["ionia"])
        self.assertEqual(r["characters"]["ender"]["structural_readiness"]["joints"], 24)
        self.assertEqual(r["authority"], "CANDIDATE_ONLY_NOT_CREATOR_ART_APPROVAL")

    def test_full_first_wake_cast_gate_fails_when_ionia_missing(self):
        with self.assertRaises(validator.IntakeFailure):
            validator.validate_manifest(self.manifest, self.root, require_both=True)

    def test_bad_image_checksum_fails_closed(self):
        self.pack["creator_reference"]["sha256"] = "0" * 64
        self.save()
        with self.assertRaises(validator.IntakeFailure):
            validator.validate_manifest(self.manifest, self.root)

    def test_bad_model_checksum_fails_closed(self):
        self.pack["characters"][0]["model_sha256"] = "0" * 64
        self.save()
        with self.assertRaises(validator.IntakeFailure):
            validator.validate_manifest(self.manifest, self.root)

    def test_traversal_rejected_before_read(self):
        self.pack["characters"][0]["model_path"] = "../elsewhere.glb"
        self.save()
        with self.assertRaises(validator.IntakeFailure):
            validator.validate_manifest(self.manifest, self.root)

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            escaped = pathlib.Path(other) / "remote.glb"
            escaped.write_bytes(fake_glb())
            link = self.root / "link.glb"
            try:
                link.symlink_to(escaped)
            except OSError:
                self.skipTest("Symlinks unavailable on this host")
            self.pack["characters"][0]["model_path"] = link.name
            self.save()
            with self.assertRaises(validator.IntakeFailure):
                validator.validate_manifest(self.manifest, self.root)

    def test_duplicate_character_rejected(self):
        self.pack["characters"].append(dict(self.pack["characters"][0]))
        self.save()
        with self.assertRaises(validator.IntakeFailure):
            validator.validate_manifest(self.manifest, self.root)

    def test_non_preflight_cast_rejected(self):
        self.pack["characters"][0]["id"] = "lyra"
        self.save()
        with self.assertRaises(validator.IntakeFailure):
            validator.validate_manifest(self.manifest, self.root)

    def test_glb_structure_rejects_missing_rig_animation_uv(self):
        for config in ({"skin": False}, {"animation": False}, {"head": False},
                       {"uv": False}, {"embedded": False}):
            with self.subTest(config=config):
                self.glb.write_bytes(fake_glb(**config))
                with self.assertRaises(validator.IntakeFailure):
                    validator.inspect_glb(self.glb)

    def test_glb_header_rejects_tampering(self):
        self.glb.write_bytes(fake_glb()[:-4])
        with self.assertRaises(validator.IntakeFailure):
            validator.inspect_glb(self.glb)

    def test_existing_unreal_import_folder_blocks_before_modification(self):
        import types
        validated = validator.validate_manifest(self.manifest, self.root)
        class FakeLibrary:
            @staticmethod
            def does_directory_exist(path):
                return True
            @staticmethod
            def list_assets(path, recursive=True, include_folder=False):
                return ["existing_creator_asset"]
        class FakeHelpers:
            @staticmethod
            def get_asset_tools():
                raise AssertionError("Asset tools must never be contacted")
        old = sys.modules.get("unreal")
        sys.modules["unreal"] = types.SimpleNamespace(
            EditorAssetLibrary=FakeLibrary, AssetToolsHelpers=FakeHelpers)
        try:
            with self.assertRaises(validator.IntakeFailure):
                validator.import_review(validated)
        finally:
            if old is None:
                sys.modules.pop("unreal", None)
            else:
                sys.modules["unreal"] = old

    def test_both_heroes_structurally_valid_still_not_art_approved(self):
        second = self.root / "ionia.glb"
        second.write_bytes(fake_glb())
        self.pack["characters"].append({
            "id": "ionia", "model_path": "ionia.glb",
            "model_sha256": hashlib.sha256(second.read_bytes()).hexdigest(),
        })
        self.save()
        result = validator.validate_manifest(self.manifest, self.root, require_both=True)
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["authority"], "CANDIDATE_ONLY_NOT_CREATOR_ART_APPROVAL")

    def test_unreal_import_separate_from_validation(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("replace_existing", source)
        self.assertIn("does_directory_exist(path)", source)
        self.assertIn("SkeletalMesh", source)
        self.assertIn("if args.import_review:", source)
        self.assertIn("automated\", False", source)
        self.assertNotIn("APPROVED_PRODUCTION", source)


if __name__ == "__main__":
    unittest.main()
