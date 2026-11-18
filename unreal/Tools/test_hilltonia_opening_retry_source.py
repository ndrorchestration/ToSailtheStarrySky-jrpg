"""Hilltonia forest-edge admission: source-only fail-closed retry and road geometry.

This neither launches Unreal nor proves that a runtime WorldStatic instance
is registered, that the human can traverse the road, or that E/Enter works.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "Source/ToSailTheStarrySky"
PAWN = (ROOT / "Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
HEADER = (ROOT / "Public/TSTSSExplorerCharacter.h").read_text(encoding="utf8")
TOWN = (ROOT / "Private/TSTSSHilltoniaReviewExtension.cpp").read_text(encoding="utf8")


def segment(source, start, end):
    begin = source.index(start)
    return source[begin:source.index(end, begin + len(start))]


def source_problems(pawn, header, town):
    problems = []
    def need(condition, name):
        if not condition:
            problems.append(name)

    attempt = segment(pawn, "if (bTryHilltoniaOpening)",
                      "if (bFirstWakeBokehReview)")
    start = segment(pawn, "bool ATSTSSExplorerCharacter::StartHilltoniaOpening(",
                    "bool ATSTSSExplorerCharacter::IsHilltoniaFlyerHit(")
    road = segment(town, "for (int32 Step = 0; Step < 11; ++Step)",
                   "// A perpendicular accessible woodland lane")

    need("uint8 HilltoniaOpeningAttemptCount = 0;" in header,
         "per-pawn bounded-attempt state missing")
    need("bool StartHilltoniaOpening(UWorld* World);" in header,
         "success/failure return missing")
    need("HilltoniaOpeningAttemptCount = 0;" in pawn,
         "begin-play attempts not reset")
    need("constexpr uint8 MaxForestSpawnAttempts = 90;" in attempt,
         "missing attempt bound")
    need("if (StartHilltoniaOpening(World))" in attempt,
         "no success admission")
    need("bTryHilltoniaOpening = false;" in attempt and
         "else if (++HilltoniaOpeningAttemptCount >= MaxForestSpawnAttempts)" in attempt,
         "no fail-closed terminal hold")
    need("TSTSS_HILLTONIA_OPENING_HOLD bounded_attempts=" in attempt,
         "missing bounded hold evidence")
    need("TSTSS_HILLTONIA_OPENING_ADMISSION_READY" in attempt,
         "missing success evidence")
    need("!HasSupportedReviewFooting(World, Spawn)" in start,
         "five-point footing check missing")
    need("!TeleportTo(Spawn, FRotator::ZeroRotator)" in start,
         "real pawn teleport not verified")
    need(start.index("HasSupportedReviewFooting(World, Spawn)") <
         start.index("TeleportTo(Spawn, FRotator::ZeroRotator)"),
         "teleport before footing validation")
    need("OldFlyer->SetActorHiddenInGame(true)" in start and
         start.index("TeleportTo(Spawn, FRotator::ZeroRotator)") <
         start.index("OldFlyer->SetActorHiddenInGame(true)"),
         "legacy marker retired before valid spawn")
    need("return true;" in start and
         "AdvanceTo(" not in start and
         "SaveGameToSlot(" not in start,
         "initial spawning granted story/save authority")
    need("WestRoad, -9650.f - 600.f * Step, RoadCenterY, -30.f" in road and
         "6.2f, 7.8f, .6f" in road,
         "west road geometry no longer established")
    need("bSolid ? ECC_WorldStatic : ECC_WorldDynamic" in town,
         "road WorldStatic collision classification missing")
    need("bSolid ? ECollisionEnabled::QueryAndPhysics" in town,
         "road collision has been disabled")
    return problems


def west_road_supports_spawn(town):
    # Source-locked constants, not a claim about registered physics bodies.
    flat = " ".join(town.split())
    if ("constexpr float RoadCenterY = -150.f;" not in flat or
        "Place(WestRoad, -9650.f - 600.f * Step, RoadCenterY, -30.f, 6.2f, 7.8f, .6f);" not in flat):
        return False
    x, y = -14650.0, -150.0
    points = [(x, y), (x + 35, y), (x - 35, y),
              (x, y + 35), (x, y - 35)]
    return all(any(
        abs(px - (-9650.0 - k * 600.0)) < 310.0 and
        abs(py - y) < 390.0
        for k in range(11)) for px, py in points)

class HilltoniaSpawnAdmission(unittest.TestCase):
    def test_source_contract(self):
        self.assertEqual(source_problems(PAWN, HEADER, TOWN), [])

    def test_spawn_five_point_road_coverage_in_source(self):
        self.assertTrue(west_road_supports_spawn(TOWN))

    def test_negative_removes_bounded_retry(self):
        broken = PAWN.replace(
            "else if (++HilltoniaOpeningAttemptCount >= MaxForestSpawnAttempts)",
            "else if (false)", 1)
        self.assertTrue(source_problems(broken, HEADER, TOWN))

    def test_negative_removes_footing_guard(self):
        broken = PAWN.replace("!HasSupportedReviewFooting(World, Spawn)", "false", 1)
        self.assertTrue(source_problems(broken, HEADER, TOWN))

    def test_negative_retires_flyer_before_spawn(self):
        token = "OldFlyer->SetActorHiddenInGame(true);"
        begin = PAWN.index("bool ATSTSSExplorerCharacter::StartHilltoniaOpening(")
        broken = PAWN[:begin] + PAWN[begin:].replace(
            token, "OldFlyer->SetActorHiddenInGame(true);", 1)
        # Change order by moving only the *first* marker retirement line.
        loc = broken.index(token, begin)
        broken = broken[:loc] + broken[loc+len(token):]
        at = broken.index("    if (!TeleportTo(Spawn, FRotator::ZeroRotator))", begin)
        broken = broken[:at] + "    " + token + "\\n" + broken[at:]
        self.assertTrue(source_problems(broken, HEADER, TOWN))

    def test_negative_disables_worldstatic(self):
        broken = TOWN.replace("bSolid ? ECC_WorldStatic : ECC_WorldDynamic",
                              "ECC_WorldDynamic", 1)
        self.assertTrue(source_problems(PAWN, HEADER, broken))

    def test_negative_road_coverage_shift(self):
        broken = TOWN.replace("WestRoad, -9650.f - 600.f * Step",
                              "WestRoad, -3500.f - 600.f * Step", 1)
        self.assertFalse(west_road_supports_spawn(broken))

    def test_negative_no_spawning_story_progress(self):
        begin = PAWN.index("bool ATSTSSExplorerCharacter::StartHilltoniaOpening(")
        ret = PAWN.index("    return true;", begin)
        broken = (PAWN[:ret] +
                  "    FirstWakeState->AdvanceTo(ETSTSSFirstWakeBeat::FlyerDiscovered);\\n" +
                  PAWN[ret:])
        self.assertTrue(source_problems(broken, HEADER, TOWN))


if __name__ == "__main__":
    unittest.main()
