#!/usr/bin/env python3
"""Source-only, reversible tests for six synthetic QA harbor/atmosphere loops."""
from __future__ import annotations
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
import wave

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_audio_harbor_loops import DURATION, LOOPS, RATE, generate, pcm_for, verify

class HarborOriginalQAOnlyTests(unittest.TestCase):
    def test_six_unique_original_samples_are_seam_joined(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"loops"
            receipt=generate(path)
            self.assertEqual(len(receipt["files"]),6)
            self.assertEqual({p.name for p in verify(path)},set(LOOPS))
            self.assertEqual(receipt["status"],"ORIGINAL_HARBOR_LOOP_QA_ONLY_NOT_NATIVE_AUDITIONED")
            for name in LOOPS:
                with wave.open(str(path/name),"rb") as f:
                    self.assertEqual((f.getnchannels(),f.getsampwidth(),f.getframerate()),
                                     (1,2,RATE))
                    self.assertEqual(f.getnframes(),int(RATE*DURATION))
                pcm=pcm_for(name)
                self.assertEqual(pcm[:2],pcm[-2:])
                self.assertEqual(len(pcm), int(RATE*DURATION)*2)

    def test_sample_deterministic(self):
        h=lambda name:hashlib.sha256(pcm_for(name)).hexdigest()
        self.assertEqual(h("harbor_surf_loop.wav"),h("harbor_surf_loop.wav"))
        self.assertNotEqual(h("harbor_surf_loop.wav"),h("weather_rain_loop.wav"))

    def test_rights_and_sha_tampering_denied(self):
        with tempfile.TemporaryDirectory() as d:
            import json
            path=Path(d)/"loops"
            generate(path)
            report=path/"harbor_loop_receipt.json"
            receipt=json.loads(report.read_text())
            receipt["files"][0]["production_approved"]=True
            report.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError,"release or loop status"):
                verify(path)
            receipt["files"][0]["production_approved"]=False
            report.write_text(json.dumps(receipt))
            target=path/LOOPS[0]
            data=target.read_bytes()
            target.write_bytes(data[:-1]+bytes((data[-1]^1,)))
            with self.assertRaisesRegex(ValueError,"checksum mismatch"):
                verify(path)

    def test_refuses_asset_tree_and_unregistered_noise(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"inside Content or assets"):
                generate(Path(d)/"Content"/"Music")
            with self.assertRaisesRegex(ValueError,"Unregistered"):
                pcm_for("licensed_field_recording.wav")
            folder=Path(d)/"original"
            generate(folder)
            with self.assertRaisesRegex(ValueError,"overwrite populated"):
                generate(folder)

if __name__=="__main__":
    unittest.main()
