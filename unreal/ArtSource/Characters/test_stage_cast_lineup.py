"""Engine-free regressions for the guarded native cast lineup intake."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from editor_intake import validate_sources, DEST_ROOT
from stage_cast_lineup import check_inputs, check_height_order, HEIGHT_RANK


class CastLineupInputTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.folder = self.project / "Saved" / "CharacterLookdev"
        self.folder.mkdir(parents=True)
        self.record = {
            "status": "IMPORT_PASS_REVIEW_PENDING",
            "kind": "STATIC_LOOKDEV_ONLY",
            "requested": "all",
            "imported": [
                {"name": r["name"], "sha256": r["sha256"],
                 "mesh": DEST_ROOT + "/" + r["name"] + "/" +
                         r["name"] + "/StaticMeshes/" + r["name"] + "." + r["name"]}
                for r in validate_sources()
            ],
        }
        self.write(self.record)

    def write(self, content):
        (self.folder / "unit_test.json").write_text(json.dumps(content), encoding="utf-8")

    def check(self):
        with mock.patch.dict("os.environ", {"TSTSS_CAST_INPUT_SESSION": "unit_test"}):
            return check_inputs(self.project)

    def test_accepts_exact_five_native_receipt(self):
        entries, path = self.check()
        self.assertEqual(len(entries), 5)
        self.assertEqual(path.name, "unit_test.json")

    def test_canonical_body_height_ranking(self):
        records = validate_sources()
        heights = check_height_order(records)
        self.assertEqual(HEIGHT_RANK, ("Reson", "Aepex", "Ender", "Ionia", "Lyra"))
        self.assertTrue(all(heights[a] > heights[b] for a, b in zip(HEIGHT_RANK, HEIGHT_RANK[1:])))

    def test_rejects_height_rank_violation(self):
        records = copy.deepcopy(validate_sources())
        for r in records:
            if r["name"] == "Lyra":
                r["height_m"] = 2.0
        with self.assertRaisesRegex(ValueError, "Canonical cast height order"):
            check_height_order(records)

    def test_rejects_nonfinite_body_height(self):
        records = copy.deepcopy(validate_sources())
        for r in records:
            if r["name"] == "Reson":
                r["height_m"] = float("nan")
        with self.assertRaisesRegex(ValueError, "Invalid intrinsic"):
            check_height_order(records)

    def test_requires_completed_native_import(self):
        for field, value in [("status", "FAILED"), ("kind", "RIGGED"), ("requested", "Ender")]:
            broken = copy.deepcopy(self.record)
            broken[field] = value
            self.write(broken)
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check()

    def test_rejects_missing_or_reordered_protagonist(self):
        for value in (self.record["imported"][:-1], list(reversed(self.record["imported"]))):
            broken = copy.deepcopy(self.record)
            broken["imported"] = value
            self.write(broken)
            with self.assertRaises(ValueError):
                self.check()

    def test_rejects_modified_source_hash(self):
        broken = copy.deepcopy(self.record)
        broken["imported"][0]["sha256"] = "0" * 64
        self.write(broken)
        with self.assertRaisesRegex(ValueError, "SHA"):
            self.check()

    def test_rejects_nonreview_asset(self):
        broken = copy.deepcopy(self.record)
        broken["imported"][0]["mesh"] = "/Game/Characters/Ender.Ender"
        self.write(broken)
        with self.assertRaisesRegex(ValueError, "isolated"):
            self.check()

    def test_refuses_malformed_session_name(self):
        with mock.patch.dict("os.environ", {"TSTSS_CAST_INPUT_SESSION": "../tamper"}):
            with self.assertRaisesRegex(ValueError, "session"):
                check_inputs(self.project)


if __name__ == "__main__":
    unittest.main()
