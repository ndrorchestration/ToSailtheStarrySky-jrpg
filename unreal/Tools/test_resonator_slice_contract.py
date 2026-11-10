#!/usr/bin/env python3
"""Engine-free source integrity for Ender's Resonator vertical-slice job.
This is NOT a native Unreal DataTable import, compile, or gameplay test.
"""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "DataSource/Jobs/Resonator.vertical_slice.review.json"
HEADER = ROOT / "Source/ToSailTheStarrySky/Public/TSTSSJobClassSystem.h"
NATIVE = ROOT / "Source/ToSailTheStarrySky/Private/Tests/TSTSSJobDataTableReadbackTests.cpp"
FAMILIES = {"ResonanceHarmonic", "Correspondence", "PsychicPsion", "Synergy"}

class ResonatorSliceSourceContract(unittest.TestCase):
    def setUp(self):
        self.rows = json.loads(FILE.read_text(encoding="utf-8"))

    def test_identity_and_admission(self):
        self.assertEqual(len(self.rows), 1)
        row = self.rows[0]
        self.assertEqual(row["Name"], "Resonator")
        self.assertEqual(row["JobId"], row["Name"])
        self.assertEqual(row["DisplayName"], "Resonator")
        self.assertEqual(row["ReviewStatus"], "ReviewSelectable")
        self.assertIs(row["bPrimaryEligible"], True)
        self.assertIs(row["bSecondaryEligible"], False)

    def test_exact_creator_curriculum(self):
        families = self.rows[0]["CurriculumFamilies"]
        self.assertEqual(len(families), 4)
        self.assertEqual(set(families), FAMILIES)

    def test_no_auto_granted_skills_mastery_or_innate_magic(self):
        self.assertEqual(set(self.rows[0]), {
            "Name", "JobId", "DisplayName", "ReviewStatus",
            "bPrimaryEligible", "bSecondaryEligible", "CurriculumFamilies"
        })

    def test_unreal_source_links_to_same_authoring_file(self):
        hdr = HEADER.read_text(encoding="utf-8")
        native = NATIVE.read_text(encoding="utf-8")
        self.assertIn("TArray<FName> CurriculumFamilies", hdr)
        self.assertIn("Resonator.vertical_slice.review.json", native)
        self.assertIn("TryReadJobDefinitionsForReview", native)
        self.assertIn("creator choice cannot bypass explicit character job unlock", native)
        self.assertIn("Resonator does not grant an unlearned Psion spell", native)
        self.assertIn("review approval revocation fails closed", native)

if __name__ == "__main__":
    unittest.main()
