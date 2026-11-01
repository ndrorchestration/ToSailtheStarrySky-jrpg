#!/usr/bin/env python3
"""Offline, stdlib-only GLB clearance intake tests. No Unreal engine is invoked."""
import json
import math
import struct
import tempfile
import unittest
from pathlib import Path
from audit_aureate_wing_clearance import (
    DEFAULT_MAX_VERTICES_PER_PRIMITIVE, GeometryHold, audit, read_vertices
)
from author_aureate_wing_glb import build as build_authored_review_wing


def make_glb(path: Path, counts=(100, 2, 2), *, shorten_view=False,
             invalid_stride=False, nonfinite=False, node_override=None,
             scene_override=None, accessor_override=None,
             view_override=None, buffer_override=None, morph_targets=False):
    accessors = []
    views = []
    primitives = []
    binary = bytearray()
    for index, count in enumerate(counts):
        start = len(binary)
        exported = []
        for number in range(count):
            value = float(number) / 100.
            if nonfinite and index == 0 and number == count - 1:
                value = math.nan
            exported.append((value, float(index), 0.0))
            binary.extend(struct.pack("<fff", value, float(index), 0.0))
        length = count * 12
        if shorten_view and index == 0:
            length -= 12
        view = {"buffer": 0, "byteOffset": start, "byteLength": length}
        if invalid_stride and index == 0:
            view["byteStride"] = 8
        views.append(view)
        finite = [p for p in exported if all(math.isfinite(v) for v in p)]
        extrema_min = [min(p[a] for p in finite) for a in range(3)] if finite else [0.] * 3
        extrema_max = [max(p[a] for p in finite) for a in range(3)] if finite else [0.] * 3
        accessors.append({"bufferView": index, "componentType": 5126,
                          "count": count, "type": "VEC3",
                          "min": extrema_min, "max": extrema_max})
        primitives.append({"attributes": {"POSITION": index}})
    if accessor_override:
        accessors[0].update(accessor_override)
    if view_override:
        views[0].update(view_override)
    if morph_targets:
        primitives[0]["targets"] = [{"POSITION": 0}]
    document = {
        "asset": {"version": "2.0"},
        "extras": {"sourceToGltfScale": 0.01},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "AureateWake_ArtReviewWing"}],
        "meshes": [{"primitives": primitives}],
        "bufferViews": views,
        "accessors": accessors,
        "buffers": [{"byteLength": len(binary)}],
    }
    if buffer_override:
        document["buffers"][0].update(buffer_override)
    if node_override:
        document["nodes"][0].update(node_override)
    if scene_override:
        document.update(scene_override)
    json_bytes = json.dumps(document, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * ((-len(json_bytes)) % 4)
    bin_bytes = bytes(binary) + b"\x00" * ((-len(binary)) % 4)
    total = 12 + 8 + len(json_bytes) + 8 + len(bin_bytes)
    payload = (b"glTF" + struct.pack("<II", 2, total)
               + struct.pack("<I4s", len(json_bytes), b"JSON") + json_bytes
               + struct.pack("<I4s", len(bin_bytes), b"BIN\x00") + bin_bytes)
    path.write_bytes(payload)


class CompleteVertexClearanceIntake(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "review.glb"

    def tearDown(self):
        self.temp.cleanup()

    def test_full_position_accessor_coverage_includes_extreme_vertex(self):
        make_glb(self.path)
        positions, sizes = read_vertices(self.path, per_primitive=100)
        self.assertEqual(sizes, [100, 2, 2])
        self.assertEqual(len(positions), 104)
        self.assertAlmostEqual(max(point[0] for point in positions), 99.0, places=2)

    def test_rejects_partial_vertex_sampling_even_when_budget_positive(self):
        make_glb(self.path, counts=(101, 2, 2))
        with self.assertRaisesRegex(GeometryHold, "Partial vertex coverage forbidden"):
            read_vertices(self.path, per_primitive=100)

    def test_rejects_zero_length_position_accessor(self):
        make_glb(self.path, counts=(0, 2, 2))
        with self.assertRaisesRegex(GeometryHold, "Empty or invalid position accessor"):
            read_vertices(self.path, per_primitive=100)

    def test_rejects_position_access_beyond_declared_view(self):
        make_glb(self.path, shorten_view=True)
        with self.assertRaisesRegex(GeometryHold, "vertex access out of bounds"):
            read_vertices(self.path, per_primitive=100)

    def test_rejects_short_stride(self):
        make_glb(self.path, invalid_stride=True)
        with self.assertRaisesRegex(GeometryHold, "Invalid GLB position view/stride"):
            read_vertices(self.path, per_primitive=100)

    def test_rejects_nonfinite_position(self):
        make_glb(self.path, nonfinite=True)
        with self.assertRaisesRegex(GeometryHold, "Nonfinite GLB geometry"):
            read_vertices(self.path, per_primitive=100)

    def test_real_generator_glb_full_coverage_fits_safe_default(self):
        # Exercise the *actual* source generator rather than relying only on
        # tiny synthetic GLBs. The venation primitive has 14,770 positions:
        # the old 3,000 cap would refuse this artist-authored review source.
        glb, _, manifest = build_authored_review_wing()
        self.path.write_bytes(glb)
        decoded, counts = read_vertices(self.path)
        self.assertEqual(counts, [292, 14770, 78])
        self.assertEqual(len(decoded), sum(counts))
        self.assertEqual(
            counts, [section["vertices"] for section in manifest["topology"]])
        self.assertLessEqual(max(counts), DEFAULT_MAX_VERTICES_PER_PRIMITIVE)
        self.assertEqual(DEFAULT_MAX_VERTICES_PER_PRIMITIVE, 20_000)

    def test_real_generator_six_directed_ordinary_routes_sampled(self):
        # Run the actual model through a discrete-time AABB screen, not merely
        # the GLB parser. Collision/under-clearance must FAIL this review test.
        # Exercise the auditor's default twenty intervals (126 poses total).
        glb, _, _ = build_authored_review_wing()
        self.path.write_bytes(glb)
        decoded, counts = read_vertices(self.path)
        self.assertEqual(counts, [292, 14770, 78])
        result = audit(decoded, steps=20)
        self.assertEqual(result["checked_directed_transitions"], 6)
        self.assertEqual(result["time_samples_per_transition"], 21)
        self.assertEqual(result["checked_poses"], 126)
        self.assertEqual(result["mesh_sample_points"], 15140)
        self.assertGreaterEqual(result["minimum_proxy_aabb_clearance_cm"], 10)
        self.assertGreaterEqual(result["minimum_interwing_aabb_clearance_cm"], 10)

    def test_rejects_unbounded_budget(self):
        make_glb(self.path)
        with self.assertRaisesRegex(GeometryHold, "maximum vertices"):
            read_vertices(self.path, per_primitive=99999)

    def test_rejects_translated_rotated_scaled_nodes(self):
        variants = [
            {"translation": [0.0, 100.0, 0.0]},
            {"rotation": [0.0, 0.70710678, 0.0, 0.70710678]},
            {"scale": [1.0, 2.0, 1.0]},
            {"matrix": [1.0] * 16},
        ]
        for node in variants:
            with self.subTest(node=node):
                make_glb(self.path, node_override=node)
                with self.assertRaisesRegex(GeometryHold, "Scene-graph transform"):
                    read_vertices(self.path, per_primitive=100)

    def test_rejects_nested_scene_skinning_and_extensions(self):
        variants = [
            {"node_override": {"children": [1]}},
            {"node_override": {"skin": 0}},
            {"scene_override": {"scenes": [{"nodes": [0, 0]}]}},
            {"scene_override": {"nodes": [{"mesh": 0}, {"mesh": 0}]}},
            {"scene_override": {"skins": [{"joints": [0]}]}},
            {"scene_override": {"extensionsUsed": ["KHR_some_extension"]}},
            {"scene_override": {"animations": [{"channels": [], "samplers": []}]}},
        ]
        for variant in variants:
            with self.subTest(variant=variant):
                make_glb(self.path, **variant)
                with self.assertRaisesRegex(GeometryHold, "Scene-graph transform"):
                    read_vertices(self.path, per_primitive=100)

    def test_rejects_sparse_and_morphed_position_data(self):
        for override in ({"sparse": {"count": 1}},
                         {"normalized": True},
                         {"extensions": {"KHR_unknown": {}}}):
            with self.subTest(accessor=override):
                make_glb(self.path, accessor_override=override)
                with self.assertRaisesRegex(GeometryHold, "position accessor format"):
                    read_vertices(self.path, per_primitive=100)
        make_glb(self.path, morph_targets=True)
        with self.assertRaisesRegex(GeometryHold, "Morph targets"):
            read_vertices(self.path, per_primitive=100)

    def test_rejects_accessor_before_declared_view_start(self):
        # The first decoded vertex exists in BIN, but a negative accessor
        # offset would make it lie BEFORE the declared view's own first byte.
        # The old combined-offset/end check incorrectly admitted this.
        make_glb(self.path,
                 view_override={"byteOffset": 12, "byteLength": 1212},
                 accessor_override={"byteOffset": -12})
        with self.assertRaisesRegex(GeometryHold, "Invalid GLB position view"):
            read_vertices(self.path, per_primitive=100)

    def test_rejects_negative_view_offset_cancelled_by_accessor(self):
        make_glb(self.path,
                 view_override={"byteOffset": -12, "byteLength": 1212},
                 accessor_override={"byteOffset": 12})
        with self.assertRaisesRegex(GeometryHold, "Invalid GLB position view"):
            read_vertices(self.path, per_primitive=100)

    def test_rejects_view_extending_beyond_embedded_bin(self):
        # Even a small accessor must not inherit a malformed declared view.
        make_glb(self.path, view_override={"byteLength": 100000})
        with self.assertRaisesRegex(GeometryHold, "view exceeds declared logical buffer"):
            read_vertices(self.path, per_primitive=100)

    def test_rejects_noninteger_and_unaligned_glb_offsets(self):
        variants = [
            {"view_override": {"byteOffset": True}},
            {"view_override": {"byteOffset": 2}},
            {"view_override": {"byteLength": True}},
            {"view_override": {"byteStride": 13}},
            {"accessor_override": {"byteOffset": True}},
            {"accessor_override": {"byteOffset": "12"}},
            {"accessor_override": {"byteOffset": 2}},
        ]
        for variant in variants:
            with self.subTest(variant=variant):
                make_glb(self.path, **variant)
                with self.assertRaisesRegex(GeometryHold, "Invalid GLB position view"):
                    read_vertices(self.path, per_primitive=100)

    def test_rejects_positions_inside_bin_but_outside_logical_buffer(self):
        # A view can appear physically valid in padded BIN bytes while
        # extending beyond glTF buffers[0].byteLength. Importers may reject
        # those bytes: the offline screen must fail closed too.
        make_glb(self.path, buffer_override={"byteLength": 1247})
        with self.assertRaisesRegex(GeometryHold, "view exceeds declared logical buffer"):
            read_vertices(self.path, per_primitive=100)

    def test_rejects_malformed_logical_buffer_declarations(self):
        for override in ({"byteLength": True},
                         {"byteLength": -1},
                         {"byteLength": 100},
                         {"byteLength": 1250},
                         {"uri": "external.bin"},
                         {"extensions": {"KHR_unknown": {}}}):
            with self.subTest(buffer=override):
                make_glb(self.path, buffer_override=override)
                with self.assertRaisesRegex(GeometryHold, "Invalid GLB declared logical buffer"):
                    read_vertices(self.path, per_primitive=100)
        for replacement in ({"buffers": []},
                            {"buffers": [{"byteLength": 1248}, {"byteLength": 0}]}):
            with self.subTest(scene=replacement):
                make_glb(self.path, scene_override=replacement)
                with self.assertRaisesRegex(GeometryHold, "Invalid GLB declared logical buffer"):
                    read_vertices(self.path, per_primitive=100)

    def test_rejects_boolean_accessor_vertex_count(self):
        make_glb(self.path, accessor_override={"count": True})
        with self.assertRaisesRegex(GeometryHold, "Empty or invalid position accessor"):
            read_vertices(self.path, per_primitive=100)

    def test_rejects_position_view_bound_to_nonembedded_buffer(self):
        # If the view says buffer 1, reading raw bytes from embedded buffer 0
        # could falsely clear wing geometry that Unreal resolves differently.
        make_glb(self.path, view_override={"buffer": 1})
        with self.assertRaisesRegex(GeometryHold, "unsupported buffer"):
            read_vertices(self.path, per_primitive=100)

    def test_rejects_multiple_meshes(self):
        make_glb(self.path, scene_override={"nodes": [{"mesh": 0}],
                    "meshes": [{"primitives": [{}, {}, {}]}, {"primitives": []}]})
        with self.assertRaisesRegex(GeometryHold, "exactly one local-space"):
            read_vertices(self.path, per_primitive=100)

    def test_rejects_missing_or_false_position_extrema(self):
        for bad in ({"min": None},
                    {"max": [0.0, 0.0, 0.0]},
                    {"min": [0.0, 0.0]},
                    {"max": [float("nan"), 1.0, 1.0]}):
            with self.subTest(accessor_override=bad):
                make_glb(self.path, accessor_override=bad)
                with self.assertRaisesRegex(
                        GeometryHold, "declared POSITION min/max|POSITION min/max disagrees"):
                    read_vertices(self.path, per_primitive=100)


if __name__ == "__main__":
    unittest.main()
