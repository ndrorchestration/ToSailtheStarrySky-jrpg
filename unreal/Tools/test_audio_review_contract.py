#!/usr/bin/env python3
"""First Wake audio source tests: not a native Unreal compile or listening receipt."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import wave

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_audio_preview_samples import DURATIONS, RATE, generate

CATALOG = Path(__file__).resolve().parents[1] / "DataSource" / "Audio" / "FirstWakeAudioEvents.review.json"
HISTORY = CATALOG.with_name("HistoricalMusicCandidates.review.json")

class TestAudioSourceContract(unittest.TestCase):
    def test_unique_gated_events_and_truth(self):
        d = json.loads(CATALOG.read_text(encoding="utf-8"))
        events = d["events"]
        ids = [e["event_id"] for e in events]
        self.assertEqual(len(ids), 56)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(d["event_count"], len(ids))
        for event in events:
            self.assertIn(event["scope"], ("SLICE", "FUTURE"))
            self.assertEqual(event["runtime_status"], "NOT_NATIVE_VERIFIED")
            self.assertNotEqual(event["source_status"], "RELEASE_CLEARED")
            if event["event_id"].startswith(("magic.", "combat.", "ship.starbourne", "story.lyra")):
                self.assertTrue(event["requires_authoritative_gate"])
        self.assertIn("repair.station_inspect.success", ids)
        self.assertIn("weather.storm.begin", ids)
        self.assertIn("water.splashdown", ids)
        self.assertEqual(next(e for e in events if e["event_id"] == "ship.starbourne.transition")["scope"], "FUTURE")
        self.assertEqual(sum(bool(e["preview_file"]) for e in events), len(DURATIONS))

    def test_historical_rights_fail_closed(self):
        d = json.loads(HISTORY.read_text(encoding="utf-8"))
        self.assertEqual(len(d["tracks"]), 5)
        self.assertTrue(all(t["license"] == "NOT_VERIFIED" for t in d["tracks"]))
        self.assertTrue(all(not t["approved_for_shipping"] for t in d["tracks"]))
        self.assertTrue(all(not t["integrated_in_current_unreal"] for t in d["tracks"]))

    def test_generated_preview_is_deterministic_original_wav(self):
        with tempfile.TemporaryDirectory() as left, tempfile.TemporaryDirectory() as right:
            a, b = generate(left), generate(right)
            self.assertEqual(a, b)
            self.assertEqual(len(a["files"]), 6)
            for item in a["files"]:
                name = item["filename"]
                path = Path(left) / name
                self.assertEqual(item["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
                with wave.open(str(path),"rb") as wav:
                    self.assertEqual((wav.getnchannels(), wav.getsampwidth(),wav.getframerate()), (1,2,RATE))
                    self.assertGreater(wav.getnframes(), 1000)
                    self.assertTrue(any(x for x in wav.readframes(wav.getnframes())))
                self.assertFalse(item["production_approved"])

    def test_no_raw_audio_in_shipping_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            for forbidden in ("Content", "assets"):
                with self.assertRaises(ValueError):
                    generate(Path(temp) / forbidden / "TSTSS")

if __name__ == "__main__":
    unittest.main()
