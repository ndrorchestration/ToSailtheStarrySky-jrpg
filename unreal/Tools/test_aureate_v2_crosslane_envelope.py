#!/usr/bin/env python3
"""Engine-free unit tests for V2 body/wing cross-lane AABB admission."""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audit_aureate_v2_crosslane_envelope import (
    APPROVED_REFERENCE_SHA, BRIDGE_NAME, HULL_NAME, STATUS_HOLD,
    STATUS_SCREEN, V2ReviewHold, evaluate, extents, require_exact_v2_artifacts
)


class CrossLaneV2AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.hull = self.folder / HULL_NAME
        self.bridge = self.folder / BRIDGE_NAME
        self.hull.write_bytes(b"test-hull")
        self.bridge.write_bytes(b"test-bridge")
        self.manifest = self.folder / "manifest.json"
        self.payload = {
            "status": "NONCANONICAL_REVIEW_NOT_ART_ACCEPTED",
            "original_creator_approved_reference_sha256": APPROVED_REFERENCE_SHA,
            "source_to_gltf_scale": 0.01,
            "axis_remap": "UE_X_FORWARD_Z_UP_TO_GLTF_Y_UP",
            "orbiter_authorized": False,
            "gameplay_modified": False,
            "creator_3d_art_approval": "NOT_GRANTED",
            "sha256": {
                HULL_NAME: hashlib.sha256(self.hull.read_bytes()).hexdigest(),
                BRIDGE_NAME: hashlib.sha256(self.bridge.read_bytes()).hexdigest(),
            }
        }
        self.persist()

    def tearDown(self):
        self.temp.cleanup()

    def persist(self):
        self.manifest.write_text(json.dumps(self.payload), encoding="utf-8")

    def check(self):
        # Local tiny fixtures stand in for the immutable generated V2 bytes.
        # Production inputs must use the frozen real GLB digests.
        with patch('audit_aureate_v2_crosslane_envelope.EXPECTED_V2_GLB_HASHES', self.payload['sha256']):
            return require_exact_v2_artifacts(self.manifest, self.hull, self.bridge)

    def test_exact_manifest_and_files_are_accepted(self):
        self.assertEqual(self.check(), self.payload["sha256"])

    def test_rewritten_manifest_cannot_change_pinned_source_hashes(self):
        # Even if content and its manifest are both rewritten consistently,
        # they cannot inherit the original V2 candidate's reviewed source SHA.
        self.hull.write_bytes(b"tampered")
        self.payload["sha256"][HULL_NAME] = hashlib.sha256(self.hull.read_bytes()).hexdigest()
        self.persist()
        with self.assertRaisesRegex(V2ReviewHold, "differs from approved-review source hashes"):
            require_exact_v2_artifacts(self.manifest, self.hull, self.bridge)

    def test_changed_glb_bytes_hold(self):
        self.hull.write_bytes(b"tampered")
        with self.assertRaisesRegex(V2ReviewHold, "SHA mismatch"):
            self.check()

    def test_authority_mutations_fail_closed(self):
        for key, value in (
            ("orbiter_authorized", True),
            ("gameplay_modified", True),
            ("creator_3d_art_approval", "GRANTED"),
            ("source_to_gltf_scale", 100),
            ("original_creator_approved_reference_sha256", "wrong"),
        ):
            with self.subTest(key=key):
                original = self.payload[key]
                self.payload[key] = value
                self.persist()
                with self.assertRaisesRegex(V2ReviewHold, "provenance"):
                    self.check()
                self.payload[key] = original

    def test_v2_filename_and_manifest_entries_are_pinned(self):
        self.payload["sha256"]["unexpected.glb"] = "abc"
        self.persist()
        with self.assertRaisesRegex(V2ReviewHold, "names or SHA entries"):
            self.check()

    def test_extents_preserve_actor_translation(self):
        self.assertEqual(extents([(0, -2, -5), (4, 3, 8)], (240, 0, 95)),
                         ((240, -2, 90), (244, 3, 103)))

    def test_broad_phase_overlap_yields_hold_not_false_pass(self):
        # A root at x155/y112/z48 is enclosed by this surrogate V2 box.
        result = evaluate([(0., 0., 0.)],
                          ((140., 100., 30.), (170., 130., 60.)),
                          ((5000., 5000., 5000.), (6000., 6000., 6000.)),
                          steps=20)
        self.assertEqual(result["status"], STATUS_HOLD)
        self.assertIn("Wing/proxy clearance", result["first_broad_phase_hold"])

    def test_clear_separated_surrogate_remains_screen_only(self):
        result = evaluate([(0., 0., 0.)],
                          ((5000., 5000., 5000.), (6000., 6000., 6000.)),
                          ((-6000., -6000., -6000.), (-5000., -5000., -5000.)),
                          steps=20)
        self.assertEqual(result["status"], STATUS_SCREEN)

    def test_low_sampling_budget_fails_closed(self):
        with self.assertRaisesRegex(V2ReviewHold, "20 intervals"):
            evaluate([(0., 0., 0.)], ((0,0,0), (1,1,1)),
                     ((100,100,100), (101,101,101)), steps=10)


if __name__ == "__main__":
    unittest.main()
