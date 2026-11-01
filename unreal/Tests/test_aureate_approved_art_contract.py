"""Source-only guard for approved four-form Aureate Wake visual reference.

This checks creator approval provenance and safe optional Unreal actor binding.
It does NOT demonstrate native Unreal compilation, aesthetic fidelity or physics.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"ArtSource"/"ShipReview"
sys.path.insert(0,str(ART))
from verify_aureate_reference import ArtReferenceHold, verify_reference

CONTRACT=ART/"aureate_wake_approved_art_contract.json"
HEADER=ROOT/"Source"/"ToSailTheStarrySky"/"Public"/"AureateWakePreviewActor.h"
SOURCE=ROOT/"Source"/"ToSailTheStarrySky"/"Private"/"AureateWakePreviewActor.cpp"
DOC=ROOT/"Docs"/"AUREATE_WAKE_APPROVED_ART_REFERENCE_2026-11-01.md"


class ApprovedShipArtContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.art=json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.h=HEADER.read_text(encoding="utf-8")
        cls.cpp=SOURCE.read_text(encoding="utf-8")

    def test_original_approval_fingerprint_is_exact(self):
        im=self.art["approved_image"]
        self.assertEqual(im["filename"],"Aureate Wake_ Four Configurations.png")
        self.assertEqual((im["width_px"],im["height_px"]),(1536,1024))
        self.assertEqual(im["size_bytes"],3837524)
        self.assertEqual(im["sha256"],"03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13")
        self.assertFalse(im["committed_original_bytes"])
        self.assertIn(im["sha256"],DOC.read_text(encoding="utf-8"))
        self.assertEqual(self.art["authority"],"CREATOR_APPROVED_VISUAL_REFERENCE")
        self.assertEqual(self.art["model_acceptance"],"NOT_YET_ESTABLISHED")

    def test_one_vessel_four_configurations_and_story_gates(self):
        self.assertEqual(self.art["canonical_consistency"]["principal_wing_count"],4)
        self.assertEqual(self.art["canonical_consistency"]["forms"],
                         ["Skyborne","Seaborne","Submersible","Orbiter"])
        self.assertEqual(self.art["story_lock"]["first_wake_allows"],["Skyborne","Seaborne"])
        self.assertTrue(self.art["story_lock"]["orbiter_locked"])
        self.assertTrue(self.art["story_lock"]["moon_bridge_locked"])
        self.assertIn("hydrofoils",self.art["form_must_have"]["Seaborne"][1])
        self.assertIn("visibl",str(self.art["form_must_have"]["Submersible"]))
        self.assertIn("radial",str(self.art["form_must_have"]["Orbiter"]))
        self.assertTrue(self.art["prototype_dimensions_are_not_canon"])

    def test_review_body_optin_disabled_and_unbound_by_default(self):
        self.assertIn("bool bUseAuthoredBodyReview = false;",self.h)
        self.assertIn("TObjectPtr<UStaticMesh> AuthoredHullReviewMesh;",self.h)
        self.assertIn("TObjectPtr<UStaticMesh> AuthoredBridgeDomeReviewMesh;",self.h)
        self.assertIn("bool RefreshBodyReviewMeshes();",self.h)
        self.assertIn("RefreshBodyReviewMeshes();",self.cpp)
        self.assertEqual(len(re.findall(r"bool AAureateWakePreviewActor::RefreshBodyReviewMeshes\s*\(",self.cpp)),1)

    def test_review_binding_rejects_partial_and_wrong_folders(self):
        section=self.cpp.split("bool AAureateWakePreviewActor::RefreshBodyReviewMeshes()",1)[1].split(
            "void AAureateWakePreviewActor::RefreshWingMeshes()",1)[0]
        self.assertIn("if (!NewHull || !NewBridge ||",section)
        self.assertIn('/Game/TSTSS/Review/ShipArt/HullCandidateV1/',section)
        self.assertIn('/Game/TSTSS/Review/ShipArt/BridgeDomeCandidateV1/',section)
        self.assertLess(section.index("if (!NewHull || !NewBridge ||"),section.index("Hull->SetStaticMesh(NewHull)"))
        self.assertIn("return false; // Fail closed without modifying either mesh.",section)
        self.assertNotIn("RequestForm(",section)
        self.assertNotIn("SetCollisionEnabled(",section)
        self.assertNotRegex(section, r"(?m)^\s*CurrentForm\s*=(?!=)")

    def test_reversion_preserves_existing_placeholder_and_scale(self):
        section=self.cpp.split("bool AAureateWakePreviewActor::RefreshBodyReviewMeshes()",1)[1].split(
            "void AAureateWakePreviewActor::RefreshWingMeshes()",1)[0]
        self.assertIn("OriginalCubeWingMesh.Get()",section)
        self.assertIn("Hull->SetRelativeScale3D(FVector(8.f, 1.5f, .65f))",section)
        self.assertIn("ForwardBridge->SetRelativeScale3D(FVector(2.1f, 1.1f, 1.1f))",section)
        self.assertIn("ForwardBridge->SetRelativeLocation(FVector(240.f, 0.f, 95.f))",section)

    def test_authorized_lookdev_never_unlocks_orbiter(self):
        self.assertIn("bAllowOrbiterPreview = false",self.h)
        self.assertIn("(bUseAuthoredBodyReview && (RequestedForm == EAureateWakeForm::Orbiter ||",self.cpp)
        self.assertIn("CurrentForm == EAureateWakeForm::Orbiter))",self.cpp)
        self.assertIn("CurrentForm == EAureateWakeForm::Orbiter",self.cpp)
        self.assertIn('WingRootSupports.Add(Support);',self.cpp)
        self.assertIn('DragonflyWing_%d',self.cpp)

    def test_verify_reference_rejects_wrong_size_without_reading_pixels(self):
        with tempfile.TemporaryDirectory() as td:
            img=Path(td)/self.art["approved_image"]["filename"]
            img.write_bytes(b"\x89PNG\r\n\x1a\n"+b"\x00"*32)
            with self.assertRaisesRegex(ArtReferenceHold,"size"):
                verify_reference(img)

    def test_original_reference_verifier_rejects_modified_file_sha(self):
        # Construct a complete lightweight fake PNG header with correct
        # dimensions and expected length. SHA must still fail closed.
        meta=self.art["approved_image"]
        with tempfile.TemporaryDirectory() as td:
            img=Path(td)/meta["filename"]
            head=(b"\x89PNG\r\n\x1a\n"+struct.pack(">I",13)+b"IHDR"+
                  struct.pack(">II",1536,1024))
            img.write_bytes(head+b"\x00"*(meta["size_bytes"]-len(head)))
            with self.assertRaisesRegex(ArtReferenceHold,"checksum mismatch"):
                verify_reference(img)

    def test_no_automatic_canonical_asset_promotion(self):
        self.assertFalse(self.art["approved_image"]["committed_original_bytes"])
        self.assertEqual(self.art["current_review_provenance"]["prior_body_candidate"],
                         "NONCANONICAL_SOURCE_LOOKDEV_NOT_APPROVED")
        self.assertEqual(self.art["current_review_provenance"]["creator_model_approval"],
                         "PENDING")
        self.assertGreaterEqual(len(self.art["native_implementation_gates"]),7)


if __name__ == "__main__":
    unittest.main()
