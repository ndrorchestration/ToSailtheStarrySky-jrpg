"""Negative-control tests for native cast PNG proof; engine-free."""
import struct
import tempfile
import unittest
from pathlib import Path
import zlib
from verify_render_pngs import PNG_HEADER, inspect_png, EXPECTED

def chunk(kind, body):
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xffffffff)

def sample(width=9, height=7, blank=False):
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    rows = []
    for y in range(height):
        pixels = bytearray()
        for x in range(width):
            pixels.extend((0, 0, 0, 255) if blank else (x*17, y*23, (x+y)*8, 255))
        rows.append(b"\x00" + bytes(pixels))
    return PNG_HEADER + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(b"".join(rows))) + chunk(b"IEND", b"")

class RenderIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.path = Path(self.t.name) / "image.png"

    def check(self, data, dims=(9, 7)):
        self.path.write_bytes(data)
        return inspect_png(self.path, dims)

    def test_valid_png(self):
        r = self.check(sample())
        self.assertEqual((r["width"], r["height"]), (9, 7))
        self.assertEqual(len(r["sha256"]), 64)

    def test_wrong_dimensions_rejected(self):
        with self.assertRaisesRegex(ValueError, "dimensions"):
            self.check(sample(), (10, 7))

    def test_crc_corruption_rejected(self):
        d = bytearray(sample())
        d[-5] ^= 1
        with self.assertRaisesRegex(ValueError, "CRC"):
            self.check(d)

    def test_truncation_rejected(self):
        with self.assertRaises(ValueError):
            self.check(sample()[:-6])

    def test_blank_rejected(self):
        with self.assertRaisesRegex(ValueError, "variation"):
            self.check(sample(blank=True))

    def test_required_shots(self):
        self.assertEqual(len(EXPECTED), 5)
        self.assertEqual(EXPECTED["Five_cast_lineup"], (1600, 900))

if __name__ == "__main__":
    unittest.main()
