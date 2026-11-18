"""Source contract for one-shot PRIVATE Ender pawn continuity across VS02 review travel.

Engine-free tests inspect source authorization and mutation denial; they do NOT
run Unreal, private licensed packages, PIE possession, or a player playthrough.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "Source/ToSailTheStarrySky"
ROUTE = (ROOT / "Private/TSTSSReviewShoreTravelSubsystem.cpp").read_text(encoding="utf8")
HEADER = (ROOT / "Public/TSTSSReviewShoreTravelSubsystem.h").read_text(encoding="utf8")
PAWN = (ROOT / "Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")

PRIVATE_CLASS_SOURCE = (
    '"BP_EnderLocomotionPreview_NONCANONICAL."'
    '\n    "BP_EnderLocomotionPreview_NONCANONICAL_C"'
)
SUBSYSTEM_CALL = "Travel->TryResumePrivateEnderInShipRoom(this)"

def body(source, begin, end=None):
    start = source.index(begin)
    return source[start:source.index(end, start)] if end else source[start:]

def checks(header, route, pawn):
    problems = []
    def need(condition, message):
        if not condition:
            problems.append(message)
    queue = body(route, "bool UTSTSSReviewShoreTravelSubsystem::QueueShore(",
                 "bool UTSTSSReviewShoreTravelSubsystem::QueueOpticalInspection(")
    arrive = body(route, "bool UTSTSSReviewShoreTravelSubsystem::ConsumeShoreArrival(",
                  "bool UTSTSSReviewShoreTravelSubsystem::TryResumePrivateEnderInShipRoom(")
    resume = body(route, "bool UTSTSSReviewShoreTravelSubsystem::TryResumePrivateEnderInShipRoom(")
    tick = body(pawn, "void ATSTSSExplorerCharacter::Tick(",
                "void ATSTSSExplorerCharacter::MoveForward(") if (
                    "void ATSTSSExplorerCharacter::MoveForward(" in pawn
                    and pawn.index("void ATSTSSExplorerCharacter::MoveForward(") >
                        pawn.index("void ATSTSSExplorerCharacter::Tick(")
                ) else body(pawn, "void ATSTSSExplorerCharacter::Tick(",
                                 "void ATSTSSExplorerCharacter::EndPlay(")
    need("UPROPERTY(Transient)" in header and
         "TSubclassOf<ATSTSSExplorerCharacter> PendingPrivateEnderClass" in header,
         "transient strong pawn class custody")
    need(PRIVATE_CLASS_SOURCE in route and
         "SourcePawn->GetClass()->GetPathName() == PrivateEnderPawnClassPath" in queue,
         "source-class exact match")
    for token in ('World->WorldType == EWorldType::PIE',
                  'SourceMap == VisualReviewPreludeName',
                  'Destination == ShipPackage',
                  'SourcePawn->IsPlayerControlled()',
                  'bPending = true'):
        need(token in queue, "boarding gate: " + token)
    for token in ('bPending = false', 'PendingMapPackage.Reset()',
                  'bPrivateEnderArrivalReady = false',
                  'const bool bRestored = State->Restore(true, Beat, Mask)',
                  'bRestored && World->WorldType == EWorldType::PIE',
                  'Target == ShipPackage'):
        need(token in arrive, "one-use restored ticket: " + token)
    for token in ('bPrivateEnderArrivalReady = false',
                  'PendingPrivateEnderClass = nullptr',
                  'World->WorldType != EWorldType::PIE',
                  'World->GetNetMode() != NM_Standalone',
                  'TEXT("/Game/TSTSS/Review/VerticalSlice/")',
                  'UGameplayStatics::GetCurrentLevelName(World, true) != ShipName',
                  'PC->GetPawn() != DefaultPawn',
                  'DefaultPawn->GetClass() != ATSTSSExplorerCharacter::StaticClass()',
                  'PrivateClass->GetPathName() != PrivateEnderPawnClassPath',
                  'State->GetCurrentBeat() != ETSTSSFirstWakeBeat::BoardedAureateWake',
                  'Ender->GetFirstWakeState()->Restore(',
                  'PC->Possess(Ender)',
                  'PC->GetPawn() != Ender',
                  'PC->Possess(DefaultPawn)',
                  'DefaultPawn->Destroy()',
                  'TSTSS_PRIVATE_ENDER_VS02_REBIND_OK',
                  'save_mutation=0 map_unchanged=1'):
        need(token in resume, "rebind gate/rollback: " + token)
    consume = resume.find("bPrivateEnderArrivalReady = false")
    spawn = resume.find("World->SpawnActor<ATSTSSExplorerCharacter>")
    need(0 <= consume < spawn, "ticket consumed before reentrant spawn")
    need(resume.index("Ender->GetFirstWakeState()->Restore(") <
         resume.index("PC->Possess(Ender)") <
         resume.index("DefaultPawn->Destroy()"),
         "story restoration before possession; old pawn last")
    need(SUBSYSTEM_CALL in tick and
         "Scene == TEXT(\"VS02_AureateInteriors\")" in tick,
         "tick only resuming VS02")
    for forbidden in ("LoadClass<", "LoadObject<", "SaveGameToSlot(",
                      "UGameplayStatics::OpenLevel(", "QueueShore("):
        need(forbidden not in resume, "rebind may not access: " + forbidden)
    return problems

class ScopedPrivateEnderContinuity(unittest.TestCase):
    def test_source_contract(self):
        self.assertEqual(checks(HEADER, ROUTE, PAWN), [])

    def test_mutation_remove_private_class_check(self):
        damaged = ROUTE.replace(
            "SourcePawn->GetClass()->GetPathName() == PrivateEnderPawnClassPath",
            "SourcePawn->GetClass() != nullptr", 1)
        self.assertTrue(checks(HEADER, damaged, PAWN))

    def test_mutation_unsafe_editor_scope(self):
        # Mutate the rebind decision, not an unrelated earlier travel guard.
        start = ROUTE.index(
            "bool UTSTSSReviewShoreTravelSubsystem::TryResumePrivateEnderInShipRoom(")
        damaged = (ROUTE[:start] + ROUTE[start:].replace(
            "World->WorldType != EWorldType::PIE", "false", 1))
        self.assertTrue(checks(HEADER, damaged, PAWN))

    def test_mutation_unearned_ticket(self):
        damaged = ROUTE.replace("Target == ShipPackage", "true", 1)
        self.assertTrue(checks(HEADER, damaged, PAWN))

    def test_mutation_too_early_possession(self):
        damaged = ROUTE.replace(
            "PC->Possess(Ender);", "DefaultPawn->Destroy();\n    PC->Possess(Ender);", 1)
        self.assertTrue(checks(HEADER, damaged, PAWN))

    def test_mutation_remove_one_use_gate(self):
        damaged = ROUTE.replace("bPrivateEnderArrivalReady = false;\n    PendingPrivateEnderClass = nullptr;",
                               "// no ticket consumption\n    PendingPrivateEnderClass = nullptr;", 1)
        self.assertTrue(checks(HEADER, damaged, PAWN))

if __name__ == "__main__":
    unittest.main()
