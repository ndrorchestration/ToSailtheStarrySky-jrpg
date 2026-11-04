"""Pure Python tests: AABB warnings are not native collision/sweep clearance."""
import hashlib
import itertools
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "Tools"
sys.path.insert(0, str(TOOLS))
import audit_aureate_v4_habitation_envelopes as study


def corners(minimum, maximum):
    return tuple(itertools.product(*zip(minimum, maximum)))


# These are extracted from the known SHA-pinned private GLBs at the
# November 4 source review, using glTF x/y-up/z-side -> UE x/y-side/z-up.
# Not committed assets, a native collision shape, or a creator scale decision.
BRIDGE = corners(
    (-96.38508214512286, -57.3982370866649, -72.0),
    (96.38508214512286, 57.3982370866649, 53.89016124824566),
)
QUARTERS = corners(
    (-185.78162785981388, -61.25, 34.29805429479633),
    (262.44123523364243, 61.25, 84.501443890418),
)
WING = corners(
    (-16, -46.90255987161053, -9.1),
    (280.3656871108917, 46.90255987161053, 9.1),
)


class ReviewEnvelopeTests(unittest.TestCase):
    def test_authoring_stage_is_source_bound(self):
        study.verify_stage()
        self.assertEqual(len(study.FORE_WINGS), 2)
        self.assertEqual(study.REVIEW_MAP_SHA,
                         "14e896f532e898836c98d51b3acf33936faf7c43f907b0d0fa20f9cac4ca4362")

    def test_glb_accessor_reader_validates_a_three_material_mesh(self):
        gltf = {
            "materials": [{"name": str(i)} for i in range(3)],
            "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
            "accessors": [{"min": [0, -1, -2], "max": [2, 1, 2]}],
        }
        chunk = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
        chunk += b" " * (-len(chunk) % 4)
        data = struct.pack("<4sII", b"glTF", 2, 20 + len(chunk))
        data += struct.pack("<I4s", len(chunk), b"JSON") + chunk
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.glb"
            path.write_bytes(data)
            expected = hashlib.sha256(data).hexdigest()
            points = study.glb_aabb(path, expected)
            self.assertEqual(study.aabb(points), ((0, -200, -100), (200, 200, 100)))
            with self.assertRaisesRegex(study.EnvelopeAuditHold, "mismatched"):
                study.glb_aabb(path, "0" * 64)

    def test_one_pass_world_corner_iterators_keep_all_axes(self):
        result = study.aabb((p for p in ((-2, 5, 0), (4, -3, 7))))
        self.assertEqual(result, ((-2, -3, 0), (4, 5, 7)))
        with self.assertRaisesRegex(study.EnvelopeAuditHold, "Empty"):
            study.aabb(iter(()))

    def test_previously_unmeasured_at_rest_envelope_gap(self):
        data = study.calculate(BRIDGE, QUARTERS, WING)
        row = data["fore_wing_envelope_review"]["0.0"]
        for side in study.FORE_WINGS:
            self.assertFalse(row["bridge"][side]["conservative_aabb_overlap"])
            self.assertFalse(row["quarters"][side]["conservative_aabb_overlap"])
            self.assertAlmostEqual(row["bridge"][side]["axis_separations_cm"][1], 17.56, places=2)
            self.assertAlmostEqual(row["quarters"][side]["axis_separations_cm"][1], 13.708, places=2)

    def test_both_pivot_directions_overlap_fore_wing_envelopes(self):
        data = study.calculate(BRIDGE, QUARTERS, WING)
        checks = (
            ("-17.5", "FORE_PORT"),
            ("17.5", "FORE_STARBOARD"),
        )
        for degree, side in checks:
            with self.subTest(degree=degree, side=side):
                frame = data["fore_wing_envelope_review"][degree]
                self.assertTrue(frame["bridge"][side]["conservative_aabb_overlap"])
                self.assertTrue(frame["quarters"][side]["conservative_aabb_overlap"])
        for s, vals in data["first_conservative_aabb_overlap_magnitude_deg_not_a_safe_limit"].items():
            self.assertTrue(0 < vals["bridge"] <= 17.5, s)
            self.assertTrue(0 < vals["quarters"] <= 17.5, s)

    def test_headroom_gauge_is_not_canon_or_occupancy_proof(self):
        data = study.calculate(BRIDGE, QUARTERS, WING)
        self.assertAlmostEqual(
            data["nominal_vertical_bridge_top_over_quarters_shell_top_cm"], 102.389, places=2
        )
        self.assertEqual(data["crew_floor_height_and_occupiable_volume"], "UNDEFINED_NOT_MEASURED")
        self.assertFalse(data["full_3d_mesh_collision_or_swept_clearance_verified"])
        self.assertFalse(data["pressure_envelope_and_docking_seal_verified"])
        self.assertFalse(data["creator_visual_approval"])
        self.assertFalse(data["starbourne_player_unlocked"])
        self.assertIn("HOLD", data["status"])

    def test_source_sha_mutation_requires_reaudit(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "stage.py"
            p.write_bytes(study.STAGE.read_bytes().replace(b"\r\n", b"\n") + b"# mutation\n")
            with self.assertRaisesRegex(study.EnvelopeAuditHold, "re-audit"):
                study.verify_stage(p)

    def test_unknown_map_sha_refused_without_launching_unreal(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "wrong.umap"
            p.write_bytes(b"not the pinned map")
            with self.assertRaisesRegex(study.EnvelopeAuditHold, "map absent/drifted"):
                study.audit_files(p, p, p, p)

    def test_source_never_builds_or_runs_game_or_authorizes_clearance(self):
        source = (TOOLS / "audit_aureate_v4_habitation_envelopes.py").read_text(encoding="utf8")
        for disallowed in ("import unreal", "save_current_level(", "subprocess.run(", "npm install", "np.", "native_collision_pass"):
            self.assertNotIn(disallowed, source)
        self.assertIn("CONSERVATIVE_AABB_OVERLAP_REVIEW_HOLD", source)

    def test_hosted_source_ci_registers_new_document_and_test(self):
        workflow = (Path(__file__).resolve().parents[2] /
                    ".github/workflows/unreal-aureate-cinematic-v4.yml").read_text()
        self.assertIn("'unreal/Tools/audit_aureate_v4_habitation_envelopes.py'", workflow)
        self.assertIn("'unreal/Tests/test_aureate_v4_habitation_clearance_envelopes.py'", workflow)
        self.assertIn("'unreal/Docs/AUREATE_V4_HABITATION_WING_ENVELOPE_GATE_2026_11_04.md'", workflow)
        self.assertIn("test_aureate_v4_habitation_clearance_envelopes.py", workflow)


if __name__ == "__main__":
    unittest.main()
