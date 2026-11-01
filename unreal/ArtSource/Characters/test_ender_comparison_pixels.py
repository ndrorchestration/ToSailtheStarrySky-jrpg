"""Synthetic PNG controls for native paired-Ender visibility QA (stdlib only)."""
import struct
import tempfile
from pathlib import Path
import unittest
import zlib

from verify_ender_comparison_pixels import check_pair_coverage, decode_png_rgb


def chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload +
            struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff))


def make_png(width=160, height=120, rgba=False, left=True, right=True,
             background=(12, 14, 17), filter_method=0):
    channels = 4 if rgba else 3
    lines = []
    prior = bytes(width * channels)
    for y in range(height):
        pixels = bytearray()
        for x in range(width):
            rgb = background
            if left and 19 <= x <= 52 and 23 <= y <= 105:
                rgb = (180, 95, 74)
            if right and 107 <= x <= 141 and 23 <= y <= 105:
                rgb = (64, 174, 130)
            pixels.extend(rgb)
            if rgba:
                pixels.append(255)
        filtered = bytearray(len(pixels))
        for i, val in enumerate(pixels):
            left_val = pixels[i - channels] if i >= channels else 0
            above = prior[i]
            upper_left = prior[i - channels] if i >= channels else 0
            if filter_method == 0:
                predict = 0
            elif filter_method == 1:
                predict = left_val
            elif filter_method == 2:
                predict = above
            elif filter_method == 3:
                predict = (left_val + above) // 2
            else:
                p = left_val + above - upper_left
                ds = (abs(p - left_val), abs(p - above), abs(p - upper_left))
                predict = (left_val, above, upper_left)[ds.index(min(ds))]
            filtered[i] = (val - predict) & 255
        lines.append(bytes([filter_method]) + filtered)
        prior = bytes(pixels)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6 if rgba else 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(b"".join(lines), 6))
            + chunk(b"IEND", b""))


class PixelPairGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "capture.png"

    def check(self, data):
        self.path.write_bytes(data)
        return check_pair_coverage(self.path, expected=(160, 120))

    def test_rgb_pair_visible_but_not_approved(self):
        result = self.check(make_png())
        self.assertEqual(result["status"], "BOTH_IMAGE_HALVES_VISIBLE_NOT_LIKENESS_APPROVAL")
        self.assertFalse(result["creator_approved"])
        self.assertFalse(result["rigging_verified"])
        self.assertGreater(result["regions"]["EnderV1_left"]["foreground_fraction"], .05)
        self.assertGreater(result["regions"]["EnderV2_right"]["foreground_fraction"], .05)

    def test_rgba_pair_visible(self):
        self.check(make_png(rgba=True))

    def test_all_five_png_filters_decode(self):
        for method in range(5):
            with self.subTest(method=method):
                result = self.check(make_png(filter_method=method))
                self.assertGreater(result["regions"]["EnderV1_left"]["foreground_fraction"], .05)

    def test_one_sided_images_fail(self):
        for left, right in ((False, True), (True, False), (False, False)):
            with self.subTest(left=left, right=right):
                with self.assertRaisesRegex(ValueError, "appears missing"):
                    self.check(make_png(left=left, right=right))

    def test_white_clipped_scene_fails(self):
        with self.assertRaisesRegex(ValueError, "appears missing|overexposed"):
            self.check(make_png(background=(255, 255, 255), left=False, right=False))

    def test_dimensions_fail(self):
        self.path.write_bytes(make_png())
        with self.assertRaisesRegex(ValueError, "size mismatch"):
            check_pair_coverage(self.path, expected=(1280, 720))

    def test_crc_tamper_fails(self):
        blob = bytearray(make_png())
        blob[-6] ^= 1
        with self.assertRaisesRegex(ValueError, "CRC"):
            self.check(blob)

    def test_wrong_scanline_filter_fails(self):
        # Mutate a valid raw scanline filter, then build a CRC-correct PNG.
        blob = make_png()
        z = blob.find(b"IDAT")
        length = struct.unpack_from(">I", blob, z - 4)[0]
        raw = bytearray(zlib.decompress(blob[z + 4:z + 4 + length]))
        raw[0] = 6
        payload = zlib.compress(bytes(raw))
        ihdr = blob[8:33]
        tampered = b"\x89PNG\r\n\x1a\n" + ihdr + chunk(b"IDAT", payload) + chunk(b"IEND", b"")
        with self.assertRaisesRegex(ValueError, "scanline filter"):
            self.check(tampered)

    def test_non_png_rejected(self):
        with self.assertRaisesRegex(ValueError, "Not a PNG"):
            self.check(b"not-png")


if __name__ == "__main__":
    unittest.main()
