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
             zero_count=False, invalid_stride=False, nonfinite=False):
    accessors = []
    views = []
    primitives = []
    binary = bytearray()
    for index, count in enumerate(counts):
        start = len(binary)
        for number in range(count):
            value = float(number) / 100.
            if nonfinite and index == 0 and number == count - 1:
                value = math.nan
            binary.extend(struct.pack("<fff", value, float(index), 0.0))
        length = count * 12
        if shorten_view and index == 0:
            length -= 12
        view = {"buffer": 0, "byteOffset": start, "byteLength": length}
        if invalid_stride and index == 0:
            view["byteStride"] = 8
        views.append(view)
        accessors.append({"bufferView": index, "componentType": 5126,
                          "count": count, "type": "VEC3"})
        primitives.append({"attributes": {"POSITION": index}})
    document = {
        "asset": {"version": "2.0"},
        "extras": {"sourceToGltfScale": 0.01},
        "meshes": [{"primitives": primitives}],
        "bufferViews": views,
        "accessors": accessors,
    }
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


if __name__ == "__main__":
    unittest.main()
