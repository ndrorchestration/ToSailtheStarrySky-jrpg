"""Source-bound checks for opt-in private Ender boarding continuity.

Real runtime behavior and visual acceptance require separate Unreal evidence.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "Source/ToSailTheStarrySky"
PAWN = (ROOT / "Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
ROUTE = (ROOT / "Private/TSTSSReviewShoreTravelSubsystem.cpp").read_text(encoding="utf8")
HEADER = (ROOT / "Public/TSTSSReviewShoreTravelSubsystem.h").read_text(encoding="utf8")

def section(src, start, end):
    return src.split(start, 1)[1].split(end, 1)[0]

def safe(pawn, route, header):
    try:
        world = section(route, "bool IsPrivateEnderStandaloneWorld(", "\n}")
        queue = section(route, "bool UTSTSSReviewShoreTravelSubsystem::QueueShore(", "\nbool UTSTSSReviewShoreTravelSubsystem::QueueOpticalInspection(")
        arrival = section(route, "bool UTSTSSReviewShoreTravelSubsystem::ConsumeShoreArrival(", "\nbool UTSTSSReviewShoreTravelSubsystem::TryResumePrivateEnderInShipRoom(")
        resume = route.split("bool UTSTSSReviewShoreTravelSubsystem::TryResumePrivateEnderInShipRoom(",1)[1]
        shipworld = section(pawn, "bool IsPrivateEnderStandaloneShip(", "\nbool IsPrivateEnderShipBinding(")
        visual = section(pawn, "bool IsPrivateEnderShipBinding(", "\nvoid ApplyCoastalRecoveryReviewSignage")
        binding = section(pawn, "void ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()", "\nvoid ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview")
        tick = section(pawn, "void ATSTSSExplorerCharacter::Tick(", "\nvoid ATSTSSExplorerCharacter::EndPlay(")
    except (IndexError, ValueError):
        return False
    req = [
        all(x in world for x in ("World->WorldType == EWorldType::Game", "World->GetNetMode() == NM_Standalone",
                                 'TEXT("TSTSSPrivateEnderLowMemReview")', "World->GetOutermost()->GetName() == ExpectedPackage")),
        'IsPrivateEnderStandaloneWorld(World, PrivatePreludePackage)' in queue,
        'SourcePawn->GetClass()->GetPathName() == PrivateEnderPawnClassPath' in queue,
        'SourcePawn->IsPlayerControlled()' in queue,
        'IsPrivateEnderStandaloneWorld(World, ShipPackage)' in arrival,
        'Target == ShipPackage' in arrival and 'bRestored' in arrival,
        'IsPrivateEnderStandaloneWorld(World, ShipPackage)' in resume,
        'PrivateClass->GetPathName() != PrivateEnderPawnClassPath' in resume,
        all(x in shipworld for x in ('World->WorldType == EWorldType::Game',
                                    'World->GetNetMode() == NM_Standalone',
                                    'TEXT("TSTSSPrivateEnderLowMemReview")',
                                    'TEXT("/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors")')),
        'IsPrivateEnderStandaloneShip(World)' in visual,
        'Pawn->GetClass()->GetPathName() !=' in visual,
        'IsPrivateEnderShipSpawnInProgress()' in visual,
        'IsPrivateEnderShipBinding(World, this)' in binding,
        'IsPrivateEnderStandaloneShip(World)' in tick,
        'bool bPrivateEnderShipSpawnInProgress = false;' in header,
        all(x in resume for x in ('bPrivateEnderArrivalReady = false;',
                                  'bPrivateEnderShipSpawnInProgress = true;',
                                  'bPrivateEnderShipSpawnInProgress = false;',
                                  'World->SpawnActor<ATSTSSExplorerCharacter>',
                                  'PC->Possess(DefaultPawn)', 'DefaultPawn->Destroy()'))
    ]
    if not all(req): return False
    return (resume.index('bPrivateEnderArrivalReady = false;') <
            resume.index('bPrivateEnderShipSpawnInProgress = true;') <
            resume.index('World->SpawnActor<ATSTSSExplorerCharacter>') <
            resume.index('bPrivateEnderShipSpawnInProgress = false;') <
            resume.index('PC->Possess(Ender)') < resume.index('DefaultPawn->Destroy()'))

class StandaloneShipTests(unittest.TestCase):
    def test_exact_opt_in_one_use_ticket_and_spawn_lease(self):
        self.assertTrue(safe(PAWN, ROUTE, HEADER))

    def test_each_critical_gate_and_cleanup_mutation_is_detected(self):
        for token in ('IsPrivateEnderStandaloneWorld(World, PrivatePreludePackage)',
                      'SourcePawn->IsPlayerControlled()',
                      'IsPrivateEnderStandaloneWorld(World, ShipPackage)',
                      'bPrivateEnderShipSpawnInProgress = false;',
                      'PrivateClass->GetPathName() != PrivateEnderPawnClassPath'):
            with self.subTest(token=token):
                self.assertFalse(safe(PAWN, ROUTE.replace(token, 'REMOVED_GATE', 1), HEADER))
        for token in ('IsPrivateEnderShipSpawnInProgress()', 'IsPrivateEnderShipBinding(World, this)',
                      'IsPrivateEnderStandaloneShip(World)'):
            with self.subTest(token=token):
                if token == 'IsPrivateEnderStandaloneShip(World)':
                    tick = section(PAWN, "void ATSTSSExplorerCharacter::Tick(", "\nvoid ATSTSSExplorerCharacter::EndPlay(")
                    self.assertIn(token, tick)
                    damaged = PAWN.replace(tick, tick.replace(token, 'REMOVED_GATE', 1), 1)
                else:
                    damaged = PAWN.replace(token, 'REMOVED_GATE', 1)
                self.assertFalse(safe(damaged, ROUTE, HEADER))

if __name__ == "__main__": unittest.main()
