"""Engine-free PNG pixel integrity fixtures; not native Unreal image evidence."""
import struct
import sys
import unittest
import zlib
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / 'Tools'
sys.path.insert(0, str(TOOLS))
from verify_aureate_v4_png_pixels import PNG_SIG, inspect_png_pixels


def synthetic_png(blank=False):
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data +
                struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff))
    ihdr = struct.pack('>IIBBBBB', 1280, 720, 8, 2, 0, 0, 0)
    rows = []
    for y in range(720):
        row = bytearray()
        for x in range(1280):
            row.extend((0, 0, 0) if blank else
                       ((x + y) % 256, (2 * x + y) % 256, (x + 2 * y) % 256))
        rows.append(b'\0' + bytes(row))
    return (PNG_SIG + chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', zlib.compress(b''.join(rows), 6)) + chunk(b'IEND', b''))


class PixelContentIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = synthetic_png()
        cls.blank = synthetic_png(blank=True)

    def test_valid_synthetic_pixel_data_has_dynamic_range(self):
        metrics = inspect_png_pixels(self.good)
        self.assertGreater(metrics['distinct_luma_values'], 12)
        self.assertTrue(metrics['contrast_review_pending'])
        self.assertFalse(metrics['art_approved'])

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
