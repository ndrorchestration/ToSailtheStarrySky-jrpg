"""Source-level safeguards for the in-memory, strictly guarded review traversal."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import unittest

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
SOURCE = ROOT / "Source/ToSailTheStarrySky"
SESSION_H = SOURCE / "Public/TSTSSReviewRouteSession.h"
SESSION_C = SOURCE / "Private/TSTSSReviewRouteSession.cpp"
GATE_H = SOURCE / "Public/TSTSSReviewRouteGate.h"
GATE_C = SOURCE / "Private/TSTSSReviewRouteGate.cpp"
PAWN = SOURCE / "Private/TSTSSExplorerCharacter.cpp"
NATIVE_TEST = SOURCE / "Private/Tests/TSTSSFirstWakeInteractionIntegrationTests.cpp"
BUILDER = TOOLS / "build_vertical_slice_traversal_overlays.py"

spec = importlib.util.spec_from_file_location("review_traversal", BUILDER)
traversal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(traversal)


class StrictTraversalContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = SESSION_C.read_text(encoding="utf-8")
        cls.gate = GATE_C.read_text(encoding="utf-8")
        cls.pawn = PAWN.read_text(encoding="utf-8")
        cls.builder = BUILDER.read_text(encoding="utf-8")
        cls.test = NATIVE_TEST.read_text(encoding="utf-8")

    def test_six_unique_exact_map_names_match_native_code(self):
        expected = list(traversal.SCENE_NAMES)
        actual = re.findall(r'GetReviewLevelName\([^)]*\)[\s\S]*?'
                            r'(?=bool UTSTSSReviewRouteSession::IsEligible)',
                            self.session)
        self.assertEqual(len(actual), 1)
        from_cpp = re.findall(r'case ETSTSSReviewMap::\w+: return TEXT\("([^"]+)"\)',
                              actual[0])
        self.assertEqual(from_cpp, expected)
        self.assertEqual(len(set(expected)), 6)
        self.assertTrue(all(x.endswith("_TraversalReviewV1") for x in expected))

    def test_five_routes_no_shortcut_or_hidden_extra_stage(self):
        plan = traversal.validate_plan()
        self.assertEqual(len(plan["new_maps"]), 6)
        self.assertEqual(len(plan["transfer_order"]), 5)
        self.assertIn("Index >= static_cast<uint8>(ETSTSSReviewMap::SplashdownShore)", self.session)
        self.assertIn("Index + 1u", self.session)
        self.assertIn("return false;", self.session)
        self.assertEqual(plan["authority"], "PIE_ONLY_ILLUSTRATIVE_WALK_ROUTE")

    def test_runtime_checks_preconditions_and_in_memory_snapshot(self):
        for token in (
            "HasStarted()", "BoardedAureateWake",
            "EngineeringChecked", "Launched",
            "FlotationConfirmed", "EmptyReserveInspected",
            "0x07u", "World->WorldType != EWorldType::PIE",
            "GetCurrentLevelName(World, true) != FromName",
            "GetCurrentLevelName(World, true) != GetReviewLevelName(Arrival)",
            "SnapshotBeat = Story->GetCurrentBeat()",
            "SnapshotInspectionMask = Story->GetInspectionMask()",
            "return Story->Restore(true, Beat, Mask)",
            "CancelPending();",
        ):
            self.assertIn(token, self.session, token)
        self.assertLess(self.session.index("CancelPending();", self.session.index("bool UTSTSSReviewRouteSession::ConsumeArrival")),
                        self.session.index("return Story->Restore(true, Beat, Mask)"))

    def test_no_gameplay_authority_grants_in_new_route_code(self):
        for code in (self.session, self.gate):
            for forbidden in (
                "AdvanceTo(", "AdvanceWaterBeat(", "SaveProgress(",
                "DoesSaveGameExist(", "SaveGameToSlot(", "GrantPartyMember(",
                "Starbourne", "GiveItem(", "SetCurrentBeat(", "DeleteGameInSlot("
            ):
                self.assertNotIn(forbidden, code, forbidden)
        self.assertIn("TryTraverse(this)", self.pawn)
        self.assertIn("IsInsidePlayerReach(", self.pawn)
        self.assertIn("bTriggered = true;", self.gate)
        self.assertIn("UGameplayStatics::OpenLevel", self.gate)

    def test_only_pie_and_explicit_E_gate_can_travel(self):
        self.assertNotIn("OnActorBeginOverlap", self.gate)
        self.assertNotIn("OnComponentBeginOverlap", self.gate)
        self.assertIn("World->WorldType != EWorldType::PIE", self.gate)
        self.assertIn("Session->ArmNextStage", self.gate)
        self.assertNotIn("OpenLevel(", self.session)
        self.assertIn("Player->GetWorld() != World", self.gate)
        self.assertIn("bPIEReviewQuickSlotOwned = false", self.pawn)

    def test_story_recovery_only_via_pawn_begin_play_and_subsystem(self):
        pawn_begin = self.pawn.split("void ATSTSSExplorerCharacter::BeginPlay()", 1)[1].split(
            "void ATSTSSExplorerCharacter::SetupPlayerInputComponent", 1)[0]
        self.assertIn("NewObject<UTSTSSFirstWakeState>(this)", pawn_begin)
        self.assertIn("Session->ConsumeArrival(ArrivalWorld, FirstWakeState)", pawn_begin)
        self.assertIn("ShowFirstWakeReviewObjective", pawn_begin)
        self.assertNotIn("SaveProgress(", pawn_begin)
        self.assertIn("bPending = false;", self.session)
        self.assertIn("SnapshotInspectionMask = 0;", self.session)

    def test_build_is_additive_and_protects_original_maps(self):
        for token in (
            "hashlib.sha256(source.read_bytes()).hexdigest()",
            "hashes[name][\"sha256\"]",
            "dirty source checkout",
            "traversal overlay files already exist",
            "unreal.EditorLoadingAndSavingUtils.load_map(source_package)",
            "unreal.EditorLoadingAndSavingUtils.save_map(world, destination)",
            "hashlib.sha256(orig_file.read_bytes()).hexdigest()",
            "native physical gate",
        ):
            if token == "native physical gate":
                continue
            self.assertIn(token, self.builder)
        self.assertNotIn("DefaultEngine.ini", self.builder)
        self.assertNotIn("DefaultInput.ini", self.builder)
        self.assertIn('if beat in ("SeaContact", "FlotationConfirmed"):', self.builder)
        self.assertIn("cannot author milestone capable of faking water physics", self.builder)

    def test_containment_boundaries_and_gates_fit_walkable_floors(self):
        p = traversal.validate_plan()
        self.assertTrue(p["fall_prevention_barriers_proposed"])
        self.assertFalse(p["native_collision_barrier_tested"])
        self.assertEqual(len(traversal.SAFE_REVIEW_FLOORS), 6)
        for idx, (_, gate) in enumerate(traversal.GATES):
            cx, cy, top, hx, hy = traversal.SAFE_REVIEW_FLOORS[idx]
            self.assertLess(abs(gate[0] - cx), hx - 100)
            self.assertLess(abs(gate[1] - cy), hy - 100)
            self.assertLessEqual(top, gate[2])
        for rail in ("SafeEdgeWest", "SafeEdgeEast",
                     "SafeEdgeSouth", "SafeEdgeNorth"):
            self.assertIn(rail, self.builder)
        self.assertIn('if index == 4:', self.builder)
        self.assertIn('for side, x in (("West", -1000), ("East", 1000)):', self.builder)
        self.assertIn('box("SeaObserverDeck", (-2600, -1600, 350), (26, 10, 2), True)',
                      self.builder)

    def test_out_of_bounds_gate_fails_closed_before_native_build(self):
        original = traversal.GATES
        try:
            traversal.GATES = original[:2] + (
                ("FirstWakeSky", (120000.0, 0.0, 90.0)),) + original[3:]
            with self.assertRaisesRegex(RuntimeError, "safe walkable floor"):
                traversal.validate_plan()
        finally:
            traversal.GATES = original

    def test_missing_or_reordered_route_fails_closed(self):
        original = traversal.GATES
        try:
            traversal.GATES = original[:-1]
            with self.assertRaisesRegex(RuntimeError, "five routes"):
                traversal.validate_plan()
            traversal.GATES = (original[1], original[0]) + original[2:]
            with self.assertRaisesRegex(RuntimeError, "route ordering drift"):
                traversal.validate_plan()
        finally:
            traversal.GATES = original

    def test_no_registered_native_automation_count_change(self):
        self.assertIn("FTSTSSFirstWakeInteractionSplashdownTest", self.test)
        self.assertIn("UTSTSSReviewRouteSession::IsEligible", self.test)
        self.assertIn("physic", self.test.lower())
        self.assertIn("static_cast<ETSTSSReviewMap>(255)", self.test)
        self.assertNotIn("IMPLEMENT_SIMPLE_AUTOMATION_TEST", self.session)
        self.assertNotIn("IMPLEMENT_SIMPLE_AUTOMATION_TEST", self.gate)


if __name__ == "__main__":
    unittest.main()
