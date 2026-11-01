#!/usr/bin/env python3
"""Offline, stdlib-only GLB clearance intake tests. No Unreal engine is invoked."""
import json
import math
import struct
import tempfile
import unittest
from pathlib import Path
from audit_aureate_wing_clearance import GeometryHold, read_vertices


def make_glb(path: Path, counts=(100, 2, 2), *, shorten_view=False,
             invalid_stride=False, nonfinite=False, node_override=None,
             scene_override=None, accessor_override=None,
             morph_targets=False):
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
    }
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
