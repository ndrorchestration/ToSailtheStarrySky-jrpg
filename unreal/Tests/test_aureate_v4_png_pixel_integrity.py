"""Engine-free PNG pixel integrity fixtures; not native Unreal image evidence."""
import struct
import sys
import unittest
import zlib
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / 'Tools'
sys.path.insert(0, str(TOOLS))
from verify_aureate_v4_png_pixels import PNG_SIG, inspect_png_pixels


def synthetic_png(blank=False, dark_ratio=0.0):
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data +
                struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff))
    ihdr = struct.pack('>IIBBBBB', 1280, 720, 8, 2, 0, 0, 0)
    rows = []
    for y in range(720):
        row = bytearray()
        for x in range(1280):
            row.extend((0, 0, 0) if blank or x < int(1280 * dark_ratio) else
                       ((x + y) % 256, (2 * x + y) % 256, (x + 2 * y) % 256))
        rows.append(b'\0' + bytes(row))
    return (PNG_SIG + chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', zlib.compress(b''.join(rows), 6)) + chunk(b'IEND', b''))


class PixelContentIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = synthetic_png()
        cls.blank = synthetic_png(blank=True)
        cls.dark_majority = synthetic_png(dark_ratio=0.84)

    def test_valid_synthetic_pixel_data_has_dynamic_range(self):
        metrics = inspect_png_pixels(self.good)
        self.assertGreater(metrics['distinct_luma_values'], 12)
        self.assertTrue(metrics['contrast_review_pending'])
        self.assertFalse(metrics['art_approved'])
        self.assertEqual(metrics['atmosphere_review_flag'], 'NO_DARK_MAJORITY_FLAG')
        self.assertLess(metrics['deep_black_fraction_below_12'], 0.6)

    def test_skybourne_like_black_majority_emits_advisory_not_art_acceptance(self):
        metrics = inspect_png_pixels(self.dark_majority)
        self.assertGreater(metrics['deep_black_fraction_below_12'], 0.8)
        self.assertEqual(metrics['atmosphere_review_flag'], 'DARK_MAJORITY_REVIEW_REQUIRED')
        self.assertFalse(metrics['art_approved'])
        self.assertGreater(metrics['distinct_luma_values'], 12)

    def test_sampled_luminance_metrics_bounded(self):
        metrics = inspect_png_pixels(self.good)
        self.assertGreaterEqual(metrics['mean_sampled_luminance'], 0)
        self.assertLessEqual(metrics['mean_sampled_luminance'], 255)
        self.assertGreaterEqual(metrics['clipped_white_fraction_above_245'], 0)
        self.assertLessEqual(metrics['clipped_white_fraction_above_245'], 1)

    def test_blank_frame_rejected(self):
        with self.assertRaises(ValueError):
            inspect_png_pixels(self.blank)

    def test_crc_corruption_rejected(self):
        changed = bytearray(self.good)
        changed[50] ^= 2
        with self.assertRaisesRegex(ValueError, 'CRC'):
            inspect_png_pixels(bytes(changed))

    def test_trailing_data_rejected(self):
        with self.assertRaisesRegex(ValueError, 'trailing'):
            inspect_png_pixels(self.good + b'trailing')

    def test_wrong_dimensions_rejected(self):
        with self.assertRaisesRegex(ValueError, 'format'):
            inspect_png_pixels(self.good, (1024, 768))

    def test_truncated_frame_rejected(self):
        with self.assertRaises(ValueError):
            inspect_png_pixels(self.good[:350])


if __name__ == '__main__':
    unittest.main()
