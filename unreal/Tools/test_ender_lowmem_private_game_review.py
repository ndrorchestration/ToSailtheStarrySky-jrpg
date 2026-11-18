"""Strict source-only contract for editor-built -game PRIVATE Ender preview.
Does NOT establish real GPU rendering, physical keys, skeletal animation
deformation, creator acceptance, or production readiness.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
HDR = (ROOT / "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf8")
PRIVATE = "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
NAME = "FirstWake_PreludeInteraction_V5_VisualReview"


def section(start: str, stop: str, source: str = CPP) -> str:
    assert start in source, f"Missing section start: {start}"
    return source.split(start, 1)[1].split(stop, 1)[0]


def helper(source=CPP) -> str:
    return section("bool IsPrivateEnderLowMemGameReview(const UWorld* World)",
                   "void ApplyCoastalRecoveryReviewSignage(UWorld* World)", source)


def tick(source=CPP) -> str:
    return section("// Lower-RAM graphical fallback for the exact PRIVATE Ender review map.",
                   "// Only scoped review worlds advertise live interaction.", source)


def appearance(source=CPP) -> str:
    return section("void ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()",
                   "void ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview", source)


def preview(source=CPP) -> str:
    return section("void ATSTSSExplorerCharacter::TryEnderPIELocomotionPreview(uint8 MotionBand)",
                   "void ATSTSSExplorerCharacter::ToggleFirstWakeBokehReview()", source)


REQUIRED_HELPER = (
    "World->WorldType == EWorldType::Game",
    "World->GetNetMode() == NM_Standalone",
    'TEXT("TSTSSPrivateEnderLowMemReview")',
    "World->GetOutermost()",
    'World->GetOutermost()->GetName() ==',
    f'TEXT("{PRIVATE}/{NAME}")',
)
REQUIRED_TICK = (
    "bReviewNamespace && IsPrivateEnderLowMemGameReview(World)",
    'GetClass()->GetName() == TEXT("BP_EnderLocomotionPreview_NONCANONICAL_C")',
    "bFirstWakeThirdPersonReview",
    "World->GetNetMode() == NM_Standalone",
    f'Scene == TEXT("{NAME}")',
    "Body->GetSkeletalMeshAsset() == EnderSliceReviewBody.Get()",
    "GetCharacterMovement()->IsMovingOnGround()",
    "TryEnderPIELocomotionPreview(MotionBand);",
    "render_NOT_VERIFIED",
    "art_NOT_APPROVED",
)
REQUIRED_BRIDGE = (
    "IsPrivateEnderLowMemGameReview(World)",
    'GetClass()->GetName() == TEXT("BP_EnderLocomotionPreview_NONCANONICAL_C")',
    "(World->WorldType != EWorldType::PIE && !bPrivateGame)",
    "World->GetNetMode() != NM_Standalone",
    'TEXT("/Game/TSTSS/Review/")',
    "EnderSliceReviewBody.IsNull()",
)


class LowMemoryPrivateEnderSourceContracts(unittest.TestCase):
    def test_unique_exact_world_and_explicit_launch_flag(self):
        self.assertIn("#if WITH_EDITOR\n// The full Unreal Editor GUI", CPP)
        for gate in REQUIRED_HELPER:
            with self.subTest(gate=gate):
                self.assertIn(gate, helper())
        self.assertEqual(helper().count("TSTSSPrivateEnderLowMemReview"), 1)
        self.assertNotIn("EndsWith(", helper())
        self.assertNotIn("StartsWith(", helper())
        self.assertNotIn("SaveGameToSlot(", helper())

    def test_runtime_only_private_pawn_and_true_grounded_clips(self):
        for gate in REQUIRED_TICK:
            with self.subTest(gate=gate):
                self.assertIn(gate, tick())
        self.assertIn("bEnableEnderPIELocomotionPreview = false", HDR)
        self.assertIn("bEnableEnderPIEWalkRunControls = false", HDR)
        self.assertIn("Body->PlayAnimation(Next, true)", preview())
        self.assertIn("GetCharacterMovement()->IsMovingOnGround()", preview())
        # The existing Game Tick path already owns one speed update, and
        # the PIE path the other. An additional lowmem call would duplicate
        # the speed lease update and break the existing source contract.
        whole_tick = section(
            "void ATSTSSExplorerCharacter::Tick(float DeltaSeconds)",
            "void ATSTSSExplorerCharacter::EndPlay(",
        )
        self.assertEqual(whole_tick.count("TryEnderPIEWalkRunControls();"), 2)
        self.assertNotIn("TryEnderPIEWalkRunControls();", tick())

    def test_body_and_triplet_admission_refuse_normal_game(self):
        for method in (appearance(), preview()):
            for gate in REQUIRED_BRIDGE:
                with self.subTest(gate=gate, method=method[:65]):
                    self.assertIn(gate, method)
            self.assertIn("bPrivateGame", method)
            self.assertNotIn("SaveGameToSlot(", method)
            self.assertNotIn("OpenLevel(", method)
            self.assertNotIn("SetActorLocation(", method)

    def test_negative_gate_mutations_fail_closed(self):
        h = helper()
        t = tick()
        for gate in REQUIRED_HELPER:
            with self.subTest(removed_world_guard=gate):
                damaged = h.replace(gate, "REMOVED_GUARD", 1)
                # A nested property expression contains a second textual
                # occurrence of World->GetOutermost(); compare counts, not
                # mere presence, so removing the standalone null guard fails.
                self.assertFalse(all(
                    damaged.count(g) == h.count(g) for g in REQUIRED_HELPER
                ))
        for gate in REQUIRED_TICK:
            with self.subTest(removed_tick_guard=gate):
                damaged = t.replace(gate, "REMOVED_GUARD", 1)
                self.assertFalse(all(
                    damaged.count(g) == t.count(g) for g in REQUIRED_TICK
                ))

    def test_no_unsafe_world_or_asset_changes_in_new_runtime_section(self):
        for forbidden in (
            "SaveGameToSlot(", "LoadGameFromSlot(", "SetActorLocation(",
            "OpenLevel(", "SpawnActor<", "AdvanceTo(", "SetAnimation(",
            "SetSkeletalMeshAsset(", "PlayAnimation(", "SetMovementMode(",
            "SetActorTransform(", "TeleportTo(",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, helper())
                self.assertNotIn(forbidden, tick())
        self.assertIn("World->WorldType == EWorldType::PIE", CPP)
        self.assertIn("TryEnderPIELocomotionPreview(MotionBand);", CPP)


if __name__ == "__main__":
    unittest.main()
