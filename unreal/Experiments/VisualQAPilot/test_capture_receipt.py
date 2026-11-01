"""Synthetic PNG structural positive/negative controls. NOT an Unreal render."""
import hashlib
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from check_capture import check, PRE_STRUT_SEABORNE_SHA256, PNG_MAGIC

def chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload +
            struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff))

def synthetic_png(width=1280, height=720):
    # Full, syntactically valid grayscale PNG produced by Python, NOT UE.
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    row = bytes([0]) + bytes(width)
    return (PNG_MAGIC + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(row * height, 9)) +
            chunk(b"IEND", b""))

def metadata(path, image):
    return {
        "source_sha": "a" * 40,
        "build_sha": "a" * 40,
        "capture_path": str(path),
        "capture_sha256": hashlib.sha256(image).hexdigest(),
        "engine_version": "5.8.4",
        "renderer": "D3D12",
        "map": "/Game/Review/SyntheticNotNative",
        "camera": "SyntheticTestCamera",
        "capture_utc": "2026-11-01T20:00:00Z",
        "form": "Seaborne",
        "pixel_width": 1280,
        "pixel_height": 720,
        "post_strut_build": True,
    }

class SyntheticPNGTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "synthetic.png"

    def test_structurally_valid_png_passes_integrity_only(self):
        png = synthetic_png()
        self.path.write_bytes(png)
        result = check(metadata(self.path, png))
        self.assertIn("NATIVE_RENDER_PROVENANCE_AND_VISUAL_REVIEW_PENDING", result)

    def test_bad_dimensions_rejected(self):
        png = synthetic_png(1279, 720)
        self.path.write_bytes(png)
        with self.assertRaisesRegex(ValueError, "dimensions"):
            check(metadata(self.path, png))

    def test_bad_crc_rejected_even_if_sha_updated(self):
        png = bytearray(synthetic_png())
        png[32] ^= 1
        modified = bytes(png)
        self.path.write_bytes(modified)
        with self.assertRaisesRegex(ValueError, "CRC"):
            check(metadata(self.path, modified))

    def test_missing_iend_rejected(self):
        png = synthetic_png()[:-12]
        self.path.write_bytes(png)
        with self.assertRaisesRegex(ValueError, "IEND"):
            check(metadata(self.path, png))

    def test_old_digest_fails_closed(self):
        png = synthetic_png()
        self.path.write_bytes(png)
        values = metadata(self.path, png)
        values["capture_sha256"] = PRE_STRUT_SEABORNE_SHA256
        with self.assertRaisesRegex(ValueError, "pre-strut"):
            check(values)

if __name__ == "__main__":
    unittest.main()
