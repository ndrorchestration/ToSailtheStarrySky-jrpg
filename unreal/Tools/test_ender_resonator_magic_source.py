"""Engine-free, fail-closed Ender Resonator review-catalog consistency checks."""
import json
from pathlib import Path
import re
import unittest

UE = Path(__file__).resolve().parents[1]
SOURCE = UE / "DataSource/Magic/EnderResonator.vertical_slice.review.json"
CPP = UE / "Source/ToSailTheStarrySky/Private/TSTSSResonatorVfxActor.cpp"
HEADER = UE / "Source/ToSailTheStarrySky/Public/TSTSSResonatorVfxActor.h"
SKILLS = UE / "Source/ToSailTheStarrySky/Private/TSTSSBattleSkillSystem.cpp"
JOBS = UE / "DataSource/Jobs/Resonator.vertical_slice.review.json"
FAMILIES = {"ResonanceHarmonic", "Correspondence", "PsychicPsion"}
EXPECTED_IDS = {
    "Ender_ResonantPulse", "Ender_TuningLance", "Ender_EchoMend",
    "Ender_CorrespondenceThread", "Ender_LatticeBreak", "Ender_MindRipple",
    "Ender_FocusHarmonic", "Ender_ConcordanceBurst", "Ender_ThoughtChord",
}

def validate(rows):
    errors = []
    names, cues = set(), set()
    if len(rows) != len(EXPECTED_IDS):
        errors.append("not exactly nine reviewed Ender spells")
    for r in rows:
        sid, cue = r.get("SkillId"), r.get("VfxCueId")
        if not isinstance(sid, str) or sid not in EXPECTED_IDS or sid in names:
            errors.append("invalid/duplicated spell identifier")
        names.add(sid)
        if r.get("Name") != sid: errors.append("DataTable row name != skill id")
        if not isinstance(cue, str) or not cue.startswith("VFX.Ender.") or cue in cues:
            errors.append("invalid/duplicated visual cue")
        cues.add(cue)
        if r.get("Kind") != "Spell" or r.get("Admission") != "ReviewExecutable":
            errors.append("invalid isolated review admission")
        if r.get("RequiredSchool") not in FAMILIES:
            errors.append("school out of creator Resonator curriculum")
        if type(r.get("RequiredMasteryRank")) is not int or not 1 <= r["RequiredMasteryRank"] <= 5:
            errors.append("missing mastery gate")
        if r.get("Target") not in {"Enemy", "Ally", "Self"}: errors.append("invalid target")
        if r.get("bHealing") and r.get("Target") == "Enemy": errors.append("heal enemy")
        for k, low, high in [("Power", 0, 99), ("ResourceCost", 1, 99),
                             ("CooldownActorTurns", 0, 10)]:
            if type(r.get(k)) is not int or not low <= r[k] <= high:
                errors.append("invalid bounded value: " + k)
        sec = r.get("RequiredSecondarySchool")
        if sec:
            if sec not in FAMILIES or sec == r.get("RequiredSchool") or (
                type(r.get("RequiredSecondaryRank")) is not int or
                not 1 <= r["RequiredSecondaryRank"] <= 5):
                errors.append("illegal synergy gate")
        elif r.get("RequiredSecondaryRank", 0) != 0:
            errors.append("orphan secondary rank")
    if names != EXPECTED_IDS: errors.append("missing or extra spell IDs")
    if len(cues) != 9: errors.append("not nine distinct cues")
    return errors

class ResonatorReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.cpp = CPP.read_text(encoding="utf-8")
        cls.header = HEADER.read_text(encoding="utf-8")
        cls.executor = SKILLS.read_text(encoding="utf-8")

    def test_unreal_datatable_import_has_explicit_optional_fields(self):
        # Missing JSON fields generate Unreal CSVImportFactory warnings even when native C++ defaults exist.
        for row in self.rows:
            for field in ("RequiredSecondarySchool", "RequiredSecondaryRank",
                          "RequiredWeaponClass", "AnimationCueId"):
                self.assertIn(field, row, row["SkillId"])
            self.assertEqual("", row["RequiredWeaponClass"])
            self.assertEqual("", row["AnimationCueId"])
            if not row["RequiredSecondarySchool"]:
                self.assertEqual(0, row["RequiredSecondaryRank"])

    def test_exact_review_catalog(self):
        self.assertEqual([], validate(self.rows))

    def test_every_row_has_own_rendered_cue_mapping(self):
        mappings = re.findall(
            r'\{TEXT\("(Ender_[A-Za-z]+)"\), TEXT\("(VFX\.Ender\.[A-Za-z]+)"\)', self.cpp)
        self.assertEqual({(r["SkillId"], r["VfxCueId"]) for r in self.rows}, set(mappings))

    def test_all_creator_curricula_covered_with_explicit_synergy(self):
        schools = {r["RequiredSchool"] for r in self.rows}
        secondaries = {r["RequiredSecondarySchool"] for r in self.rows
                       if r.get("RequiredSecondarySchool")}
        self.assertEqual(FAMILIES, schools)
        self.assertIn("Correspondence", secondaries)
        self.assertIn("PsychicPsion", secondaries)

    def test_visuals_cannot_spend_mp_or_unlock_skills(self):
        self.assertIn("SpawnFromAcceptedCue", self.cpp)
        self.assertIn("IsAcceptedEnderCue", self.cpp)
        for forbidden in ["LearnedByActor.Add", "MasteryByActor.Add",
                          "FTSTSSCombatAbilities::TryUse", "NextAllowedTurnByActorAndSkill.Add"]:
            self.assertNotIn(forbidden, self.cpp)
        self.assertIn("Row.Admission != ETSTSSBattleSkillAdmission::ReviewExecutable", self.executor)
        self.assertIn("Knowledge.LearnedByActor.Find", self.executor)

    def test_invalid_mastery_fails(self):
        bad = [dict(r) for r in self.rows]
        bad[0]["RequiredMasteryRank"] = 0
        self.assertTrue(validate(bad))

    def test_invalid_duplicate_cue_fails(self):
        bad = [dict(r) for r in self.rows]
        bad[1]["VfxCueId"] = bad[0]["VfxCueId"]
        self.assertTrue(validate(bad))

    def test_invalid_synergy_fails(self):
        bad = [dict(r) for r in self.rows]
        bad[-1]["RequiredSecondarySchool"] = "ResonanceHarmonic"
        self.assertTrue(validate(bad))

    def test_invalid_enemy_heal_fails(self):
        bad = [dict(r) for r in self.rows]
        bad[0]["bHealing"] = True
        self.assertTrue(validate(bad))

    def test_review_catalog_never_grants_mastery(self):
        for r in self.rows:
            self.assertNotIn("LearnedByActor", r)
            self.assertNotIn("GrantedMastery", r)
        if JOBS.exists():
            job_rows = json.loads(JOBS.read_text(encoding="utf-8"))
            self.assertFalse(any(row.get("StartingSkills") for row in job_rows))
        self.assertIn("TryUseDataTable", self.executor)

if __name__ == "__main__":
    unittest.main()
