"""Source-only independent review of the opt-in multi-foe Pulse fixture.

This does NOT certify Unreal C++ compilation, real PIE, native automation,
visual quality, or player-driven damage. Production encounters remain untouched.
"""
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTOR = ROOT / "Source/ToSailTheStarrySky/Private/Review/TSTSSResonatorFocusReviewActor.cpp"
HEADER = ROOT / "Source/ToSailTheStarrySky/Public/Review/TSTSSResonatorFocusReviewActor.h"
COMBAT = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSBattleSkillSystem.cpp"
RADIUS = 600.0

PROXIES = ("EnderProxy", "IoniaProxy", "FoeProxy",
           "FoeHighProxy", "FoeOutsideProxy")
REQUIRED = {
    "EnderProxy": (0.0,-100.0,80.0),
    "IoniaProxy": (0.0,-390.0,80.0),
    "FoeProxy": (500.0,-190.0,80.0),
    "FoeHighProxy": (200.0,100.0,350.0),
    "FoeOutsideProxy": (680.0,-100.0,330.0),
}


def read_point(code, name):
    regex = rf'{name}->SetRelativeLocation\(FVector\(([^)]*)\)\);'
    match = re.search(regex, code)
    if not match:
        raise ValueError("Missing real-world proxy position: " + name)
    try:
        return tuple(float(v.strip().rstrip("f")) for v in match.group(1).split(","))
    except ValueError as e:
        raise ValueError("Non-numeric proxy position: " + name) from e


def check(code, header, combat):
    if "bool bMultiEnemyPulseProofReview=false;" not in header:
        raise ValueError("Multi-foe opt-in must default OFF")
    if '#if UE_BUILD_SHIPPING' not in code:
        raise ValueError("Review-only shipping deny missing")
    for name in PROXIES:
        point = read_point(code, name)
        if len(point) != 3 or not all(math.isfinite(x) for x in point):
            raise ValueError("Invalid 3D proxy point: " + name)
        if point != REQUIRED[name]:
            raise ValueError("Unexpected fixture geometry: " + name)
    caster = read_point(code, "EnderProxy")
    distances = {name: math.dist(caster, read_point(code, name)) for name in PROXIES}
    if not (distances["FoeProxy"] < RADIUS
            and distances["FoeHighProxy"] < RADIUS
            and distances["FoeOutsideProxy"] > RADIUS
            and distances["IoniaProxy"] < RADIUS):
        raise ValueError("Two-inside / one-outside / ally-in topology failed")
    for field in ("FoeHighProxy", "FoeOutsideProxy"):
        if f"TObjectPtr<UStaticMeshComponent> {field};" not in header:
            raise ValueError("Missing component owner: " + field)
        if f"{field}->SetCollisionEnabled(ECollisionEnabled::NoCollision)" in code:
            raise ValueError("Collision ownership drift: " + field)
        if f"{field}.Get()" not in code:
            raise ValueError("Component is not included in review source")
    for token in (
        "if (bMultiEnemyPulseProofReview)",
        "FoeHighProxy->SetVisibility(bMultiEnemyPulseProofReview)",
        "FoeOutsideProxy->SetVisibility(bMultiEnemyPulseProofReview)",
        "if (!bIoniaRecruitedForReview",
        "TSTSSPulseAreaMath::WithinSphere(",
        "FTSTSSBattleSkillSystem::ResonantPulseRadiusCm",
        "Inside(FoeProxy->GetComponentLocation())",
        "Inside(FoeHighProxy->GetComponentLocation())",
        "Inside(FoeOutsideProxy->GetComponentLocation())",
        "Inside(IoniaProxy->GetComponentLocation())",
        "Foes.Add(Elevated);",
        "Foes.Add(Outside);",
        "InitializeEncounter(Crew,Active,Foes)",
        "Positions.Add(Unit.CharacterId, FoeHighProxy->GetComponentLocation())",
        "Positions.Add(Unit.CharacterId, FoeOutsideProxy->GetComponentLocation())",
        "SubmitResonantPulseArea(Command, Positions)",
        "Actor==FocusOpponentHighId || Actor==FocusOpponentOutsideId",
    ):
        if token not in code:
            raise ValueError("Missing opt-in/authorization rule: " + token)
    if "Row->Admission!=ETSTSSBattleSkillAdmission::DesignOnly" not in code:
        raise ValueError("Unselected spell gate missing")
    if "TryUseValidatedRow(" not in combat or "Affected.Sort(" not in combat:
        raise ValueError("Atomic learned-skill area damage contract missing")
    return distances


class MultiFoeReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = ACTOR.read_text(encoding="utf8")
        cls.header = HEADER.read_text(encoding="utf8")
        cls.combat = COMBAT.read_text(encoding="utf8")

    def test_fixture_contains_two_enemies_inside_and_one_outside_in_3d(self):
        d = check(self.code,self.header,self.combat)
        self.assertGreater(d["FoeHighProxy"], 0)
        self.assertNotEqual(read_point(self.code,"FoeHighProxy")[2],
                            read_point(self.code,"EnderProxy")[2])

    def test_default_off_mutation_denied(self):
        with self.assertRaisesRegex(ValueError,"default OFF"):
            check(self.code,self.header.replace(
                "bMultiEnemyPulseProofReview=false",
                "bMultiEnemyPulseProofReview=true"),self.combat)

    def test_outside_enemy_moved_inside_denied(self):
        with self.assertRaisesRegex(ValueError,"fixture geometry"):
            check(self.code.replace("FVector(680.f,-100.f,330.f)",
                                    "FVector(580.f,-100.f,80.f)"),
                  self.header,self.combat)

    def test_enemy_uses_real_actor_positions_and_authority(self):
        with self.assertRaisesRegex(ValueError,"authorization rule"):
            check(self.code.replace("SubmitResonantPulseArea(Command, Positions)",
                                    "SubmitCommand(Command)"),
                  self.header,self.combat)

    def test_ally_inclusion_is_required_but_cannot_be_damaged(self):
        with self.assertRaisesRegex(ValueError,"authorization rule"):
            check(self.code.replace("Inside(IoniaProxy->GetComponentLocation())",
                                    "Inside(EnderProxy->GetComponentLocation())"),
                  self.header,self.combat)


if __name__=="__main__":
    unittest.main()
