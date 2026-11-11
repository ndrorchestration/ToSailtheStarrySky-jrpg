#!/usr/bin/env python3
"""Test QA import safety and scene integration source boundaries; NOT UE-native QA."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_audio_preview_samples import generate, DURATIONS
import import_first_wake_audio_review as importer

UNREAL_ROOT = Path(__file__).resolve().parents[1]
SOURCES = UNREAL_ROOT / "Source" / "ToSailTheStarrySky"


class AudioReviewIntegrationSourceTests(unittest.TestCase):
    def test_original_review_receipt_allows_only_exact_ten_files(self):
        with tempfile.TemporaryDirectory() as temp:
            generated = generate(Path(temp) / "sound_review")
            self.assertEqual(set(DURATIONS),
                             {p.name for p in importer.verify_source(Path(temp) / "sound_review")})
            self.assertEqual(len(generated["files"]), 10)

    def test_tampered_wav_is_denied(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / "sound_review"
            generate(directory)
            wav = directory / "weather_gust.wav"
            payload = wav.read_bytes()
            wav.write_bytes(payload[:-1] + bytes([payload[-1] ^ 1]))
            with self.assertRaisesRegex(RuntimeError, "hash mismatch"):
                importer.verify_source(directory)

    def test_uncleared_or_unrecognized_manifest_denied(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "sound_review"
            generate(folder)
            receipt = folder / "audio_preview_receipt.json"
            d = json.loads(receipt.read_text())
            d["files"][0]["production_approved"] = True
            receipt.write_text(json.dumps(d))
            with self.assertRaisesRegex(RuntimeError, "approval scope"):
                importer.verify_source(folder)
            d["files"][0]["production_approved"] = False
            d["files"][0]["filename"] = "uncleared-sample.wav"
            receipt.write_text(json.dumps(d))
            with self.assertRaisesRegex(RuntimeError, "Unrecognized"):
                importer.verify_source(folder)

    def test_import_refuses_without_explicit_opt_in(self):
        with mock.patch.dict(os.environ, {"TSTSS_AUDIO_REVIEW_OPT_IN":"", "TSTSS_AUDIO_REVIEW_SOURCE":"x"}):
            with self.assertRaisesRegex(RuntimeError, "opt-in"):
                importer.main()

    def test_import_denies_insufficient_ram_before_unreal_import(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "source"
            generate(folder)
            with mock.patch.dict(os.environ, {
                "TSTSS_AUDIO_REVIEW_OPT_IN":importer.OPT_IN,
                "TSTSS_AUDIO_REVIEW_SOURCE":str(folder),
            }):
                with mock.patch.object(importer, "available_ram_bytes", return_value=0):
                    with self.assertRaisesRegex(RuntimeError, "RAM"):
                        importer.main()

    def test_environment_actor_is_optional_cosmetic_only(self):
        header = (SOURCES / "Public" / "TSTSSAudioEnvironmentDirector.h").read_text()
        impl = (SOURCES / "Private" / "TSTSSAudioEnvironmentDirector.cpp").read_text()
        self.assertIn("bool bHarborZoneAudible = false", header)
        self.assertEqual(impl.count("CreateDefaultSubobject<UAudioComponent>"), 6)
        self.assertIn("GetAtmosphereProfile()", impl)
        self.assertIn("GetCategoryVolume(ETSTSSAudioCategory::Ambience)", impl)
        self.assertIn("Audio->IsMuted()", impl)
        self.assertIn("FMath::FInterpTo", impl)
        for forbidden in ("AdvanceTo(", "ConfirmWaterContact(", "SaveGameToSlot(", "UnlockStarbourne("):
            self.assertNotIn(forbidden, impl)

    def test_spawned_loop_handles_auto_destroy_on_completion(self):
        engine = (SOURCES / "Private" / "TSTSSAudioSubsystem.cpp").read_text(encoding="utf-8")
        self.assertIn("nullptr, nullptr, true)", engine)
        self.assertIn("nullptr, false, true", engine)
        self.assertIn("ActiveLoops.Remove(EventId)", engine)
        self.assertIn("SILENT_SPAWN_FAILURE", engine)

    def test_harbor_zone_is_local_player_sound_only(self):
        zone = (SOURCES / "Private" / "TSTSSHarborAudioZone.cpp").read_text(encoding="utf-8")
        head = (SOURCES / "Public" / "TSTSSHarborAudioZone.h").read_text(encoding="utf-8")
        self.assertIn("SetCollisionEnabled(ECollisionEnabled::QueryOnly)", zone)
        self.assertIn("SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap)", zone)
        self.assertIn("Player->GetPawn() == OtherActor", zone)
        self.assertIn("SetHarborZoneAudible(true)", zone)
        self.assertIn("SetHarborZoneAudible(false)", zone)
        self.assertIn("TObjectPtr<ATSTSSAudioEnvironmentDirector>", head)
        for forbidden in ("AdvanceTo(", "InspectStation(", "ConfirmWaterContact("):
            self.assertNotIn(forbidden, zone)

    def test_grounded_surface_footstep_source_boundaries(self):
        cpp = (SOURCES / "Private" / "TSTSSFootstepAudioDirector.cpp").read_text(encoding="utf-8")
        header = (SOURCES / "Public" / "TSTSSFootstepAudioDirector.h").read_text(encoding="utf-8")
        self.assertIn("ATSTSSFootstepAudioDirector", cpp)
        self.assertIn("UGameplayStatics::GetPlayerPawn(World, 0)", cpp)
        self.assertIn("Movement->IsMovingOnGround()", cpp)
        self.assertIn("Velocity.Size2D() < MinimumGroundSpeedCmPerSec", cpp)
        self.assertIn("TravelCm > MaximumContinuityDeltaCm", cpp)
        self.assertIn("DistanceAccumulatorCm", cpp)
        self.assertIn("Params.bReturnPhysicalMaterial = true", cpp)
        self.assertIn("UPhysicalMaterial::DetermineSurfaceType", cpp)
        self.assertIn("World->LineTraceSingleByChannel", cpp)
        for suffix in ("wood", "sand", "stone", "metal"):
            self.assertIn("foley.footstep." + suffix, cpp)
        self.assertIn("return NAME_None", cpp)
        self.assertIn("ResetFootstepTracking()", cpp)
        self.assertIn("TEnumAsByte<EPhysicalSurface>", header)
        for forbidden in ("AddMovementInput(", "AdvanceTo(", "SaveGameToSlot(", "SetActorLocation("):
            self.assertNotIn(forbidden, cpp)

    def test_authoritative_gameplay_still_precedes_audio(self):
        milestone = (SOURCES / "Private" / "TSTSSMilestoneActor.cpp").read_text()
        atmosphere = (SOURCES / "Private" / "TSTSSAtmosphereDirector.cpp").read_text()
        self.assertLess(milestone.index("if (!bSucceeded) return false;"),
                        milestone.index("Audio->EmitCue("))
        self.assertLess(atmosphere.index("if (static_cast<uint8>(InWeather)"),
                        atmosphere.index("Audio->EmitCue("))
        self.assertIn("PreviousWeather != InWeather", atmosphere)


if __name__ == "__main__":
    unittest.main()
