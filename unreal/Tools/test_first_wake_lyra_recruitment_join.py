"""Cross-lane Lyra recruitment authority checks (source only, not live UE).

Protects the three-stage equipment fixture and its provenance when other
First Wake branches are composed. A source PASS is not story SaveGame or PIE.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "Source/ToSailTheStarrySky/Public/TSTSSPartySliceReviewEquipment.h"
CPP = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSPartySliceReviewEquipment.cpp"
NATIVE_TEST = ROOT / "Source/ToSailTheStarrySky/Private/Tests/TSTSSPartySliceEquipmentTests.cpp"
MANIFEST = ROOT / "DataSource/Integration/FirstWakeMultipath.review.json"
EXPECTED_STAGES = ("FirstWake", "AfterSplashdown", "LyraRecruited")


def validate(header: str, cpp: str, native_test: str, manifest: dict) -> list[str]:
    errors = []
    match = re.search(
        r"enum\s+class\s+ETSTSSPartySliceReviewStage\s*:\s*uint8\s*\{([^}]+)\}",
        header, re.S,
    )
    names = tuple(re.findall(r"\b(?:FirstWake|AfterSplashdown|LyraRecruited)\b",
                             match.group(1))) if match else ()
    if names != EXPECTED_STAGES or "UENUM(BlueprintType)" not in header:
        errors.append("three-stage native review enum missing or reordered")
    if "Review-stage authority is NOT proof of actual story recruitment" not in header:
        errors.append("review-fixture cannot assert actual Lyra story recruitment")

    key = "bool FTSTSSPartySliceReviewEquipment::IsMemberAvailable("
    next_key = "bool FTSTSSPartySliceReviewEquipment::TryBuildEquippedReviewFixture("
    if cpp.count(key) != 1 or cpp.count(next_key) != 1:
        return errors + ["C++ party gate function boundaries changed"]
    availability = cpp.split(key, 1)[1].split(next_key, 1)[0]
    fixture = cpp.split(next_key, 1)[1]
    if not re.search(
        r'CharacterId\s*==\s*TEXT\("Lyra"\)\s*&&\s*'
        r'Stage\s*==\s*ETSTSSPartySliceReviewStage::LyraRecruited',
        availability,
    ):
        errors.append("Lyra member eligibility must require distinct recruitment")
    if not re.search(
        r'Stage\s*==\s*ETSTSSPartySliceReviewStage::LyraRecruited\s*&&'
        r'\s*\(!AddAndEquip\(Candidate,\s*TEXT\("Lyra"\)',
        fixture,
    ) or fixture.count('AddAndEquip(Candidate, TEXT("Lyra")') != 3:
        errors.append("Lyra equipment fixture must be guarded by recruitment")
    if "Stage != ETSTSSPartySliceReviewStage::AfterSplashdown" not in fixture:
        errors.append("splashdown without recruitment must remain an admissible two-person stage")
    for token in (
        'TestFalse(TEXT("Splashdown alone does not recruit Lyra")',
        'TestTrue(TEXT("Lyra becomes eligible only after distinct recruitment")',
        'TestFalse(TEXT("splashdown does not grant Lyra equipment")',
        'Sea.OwnedInstances.Num(), 6',
        'After.OwnedInstances.Num(), 9',
        'TryBuildEquippedReviewFixture(Recruited, After)',
    ):
        if token not in native_test:
            errors.append("native test lacks distinct recruitment negative/positive gate: " + token)

    gate = manifest.get("lyra_equipment_gate", {})
    if gate != {
        "after_sea_contact_stage": "AfterSplashdown",
        "requires_distinct_recruitment": True,
        "recruited_stage": "LyraRecruited",
        "automatic_item_grants": False,
        "runtime_recruitment_verified": False,
    }:
        errors.append("cross-lane Lyra authority/gating projection drift")
    if manifest.get("pre_splashdown_party") != ["Ender", "Ionia"] or (
        manifest.get("post_splashdown_before_recruitment_party") != ["Ender", "Ionia"]
    ) or manifest.get("post_splashdown_first_recruit") != "Lyra":
        errors.append("First Wake roster chronology drift")
    if manifest.get("disallowed_slice_party") != ["Reson", "Aepex"]:
        errors.append("later party must not be recruited in this slice")
    return errors


def load():
    return (
        HEADER.read_text(encoding="utf-8"),
        CPP.read_text(encoding="utf-8"),
        NATIVE_TEST.read_text(encoding="utf-8"),
        json.loads(MANIFEST.read_text(encoding="utf-8")),
    )


class LyraRecruitmentGateReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.header, cls.cpp, cls.native, cls.manifest = load()

    def failures(self, **kw):
        args = dict(header=self.header, cpp=self.cpp, native_test=self.native,
                    manifest=self.manifest)
        args.update(kw)
        return validate(**args)

    def assert_fails(self, needle, **kw):
        result = self.failures(**kw)
        self.assertTrue(any(needle in r for r in result), result)

    def test_three_stage_integrated_source(self):
        self.assertEqual([], self.failures())

    def test_splashdown_cannot_implicitly_admit_lyra(self):
        changed = self.cpp.replace(
            "Stage == ETSTSSPartySliceReviewStage::LyraRecruited);",
            "Stage == ETSTSSPartySliceReviewStage::AfterSplashdown);", 1)
        self.assert_fails("eligibility", cpp=changed)

    def test_splashdown_cannot_grant_lyra_items(self):
        changed = self.cpp.replace(
            "if (Stage == ETSTSSPartySliceReviewStage::LyraRecruited &&",
            "if (Stage == ETSTSSPartySliceReviewStage::AfterSplashdown &&", 1)
        self.assert_fails("equipment fixture", cpp=changed)

    def test_native_recruitment_rejection_cannot_disappear(self):
        changed = self.native.replace(
            'TestFalse(TEXT("Splashdown alone does not recruit Lyra")',
            'TestTrue(TEXT("Splashdown alone does not recruit Lyra")', 1)
        self.assert_fails("native test lacks", native_test=changed)

    def test_late_party_cannot_join(self):
        changed = dict(self.manifest, disallowed_slice_party=["Aepex"])
        self.assert_fails("later party", manifest=changed)

    def test_runtime_verification_not_inferred(self):
        changed = dict(self.manifest, lyra_equipment_gate={
            **self.manifest["lyra_equipment_gate"], "runtime_recruitment_verified": True,
        })
        self.assert_fails("authority/gating", manifest=changed)

    def test_no_automatic_equipment_grants(self):
        changed = dict(self.manifest, lyra_equipment_gate={
            **self.manifest["lyra_equipment_gate"], "automatic_item_grants": True,
        })
        self.assert_fails("authority/gating", manifest=changed)

    def test_three_stage_enum_cannot_collapse(self):
        changed = self.header.replace("    LyraRecruited\n", "    AfterSplashdown\n", 1)
        self.assert_fails("enum", header=changed)


if __name__ == "__main__":
    unittest.main()
