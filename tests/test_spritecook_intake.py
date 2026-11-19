"""Offline regression tests for the SpriteCook candidate-art intake."""
import argparse
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from scripts.spritecook_intake import IntakeError, inspect_png, stage


def sample_png(rgba=True, damaged=False):
    def chunk(kind, body):
        crc = zlib.crc32(kind + body) & 0xffffffff
        if damaged and kind == b'IDAT':
            crc ^= 1
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', crc)
    pixel = b'\x00\x00\x00\x00\x00' if rgba else b'\x00\x00\x00\x00'
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 6 if rgba else 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(pixel)) + chunk(b'IEND', b''))


class SpriteCookIntakeTests(unittest.TestCase):
    def test_good_png(self):
        info = inspect_png(sample_png())
        self.assertEqual(info['width'], 1)
        self.assertTrue(info['alpha_capable'])

    def test_crc_rejection(self):
        with self.assertRaises(IntakeError):
            inspect_png(sample_png(damaged=True))

    def make_args(self, root):
        root = Path(root)
        image = root / 'input.png'
        image.write_bytes(sample_png())
        prompt = root / 'prompt.txt'
        prompt.write_text('Public-safe brass engineering glyph.', encoding='utf-8')
        return argparse.Namespace(
            png=str(image), slug='engineering-glyph', asset_id='verified-id',
            source_url='https://app.spritecook.ai/assets/verified-id',
            prompt_file=str(prompt), dest=str(root / 'staged'),
            credit_cost=8, balance_before=40, balance_after=32,
            max_per_asset=12, allow_opaque=False
        )

    def test_stage_and_prevent_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            args = self.make_args(root)
            result = stage(args)
            receipt = json.loads(Path(result['manifest']).read_text())
            self.assertEqual(receipt['status'], 'CANDIDATE_NOT_APPROVED')
            self.assertTrue(receipt['credit_debit_verified_by_before_after_balance'])
            self.assertEqual(receipt['credit_cost_reported'], 8)
            with self.assertRaises(IntakeError):
                stage(args)

    def test_mismatched_balance_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            args = self.make_args(root)
            args.balance_after = 31
            with self.assertRaises(IntakeError):
                stage(args)

    def test_opaque_flag_needed(self):
        self.assertFalse(inspect_png(sample_png(rgba=False))['alpha_capable'])


if __name__ == '__main__':
    unittest.main()
