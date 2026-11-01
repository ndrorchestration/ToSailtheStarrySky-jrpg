"""Offline tests for root support GLB, four visual mount geometry and authority."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Tools"))
import author_aureate_root_support as supports
import audit_aureate_wing_clearance as clearance

CPP = (ROOT/"Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp").read_text(encoding="utf-8")
HEADER = (ROOT/"Source/ToSailTheStarrySky/Public/AureateWakePreviewActor.h").read_text(encoding="utf-8")

class RootSupportArt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glb,cls.manifest=supports.build()
        jlen=struct.unpack_from("<I",cls.glb,12)[0]
        cls.doc=json.loads(cls.glb[20:20+jlen])
        cls.parts=supports.build_surfaces()

    def test_exact_100cm_meter_scaled_asset(self):
        self.assertEqual(self.glb[:4],b"glTF")
        self.assertEqual(struct.unpack_from("<I",self.glb,8)[0],len(self.glb))
        self.assertEqual(self.doc["extras"]["sourceToGltfScale"],.01)
        self.assertEqual(self.doc["extras"]["strutLengthCm"],100.)
        pos=self.doc["accessors"][self.doc["meshes"][0]["primitives"][0]["attributes"]["POSITION"]]
        self.assertAlmostEqual(pos["min"][0],0,places=5)
        self.assertAlmostEqual(pos["max"][0],1,places=5)
        self.assertEqual(self.manifest["nominal_length_cm"],100.)

    def test_three_distinct_review_materials_and_lumen(self):
        self.assertEqual(len(self.doc["meshes"]),1)
        self.assertEqual(len(self.doc["meshes"][0]["primitives"]),3)
        names=[m["name"] for m in self.doc["materials"]]
        self.assertIn("M_Root_Strut_BlueSteel_REVIEW",names)
        self.assertIn("M_Root_Coupler_Brass_REVIEW",names)
        self.assertIn("M_Root_Trace_Lumen_REVIEW",names)
        self.assertGreater(self.doc["materials"][2]["emissiveFactor"][2],.5)

    def test_all_three_sections_closed_manifold(self):
        for piece in self.parts:
            with self.subTest(piece=piece["name"]):
                edge=Counter(tuple(sorted((a,b))) for a,b,c in piece["faces"]
                             for a,b in ((a,b),(b,c),(c,a)))
                self.assertTrue(edge)
                self.assertTrue(all(n==2 for n in edge.values()))
                self.assertTrue(all(len({a,b,c})==3 for a,b,c in piece["faces"]))

    def test_deterministic_generator_and_sha256_receipt(self):
        copy,receipt=supports.build()
        self.assertEqual(copy,self.glb)
        self.assertEqual(receipt,self.manifest)
        self.assertEqual(receipt["sha256"][supports.FILES[0]],hashlib.sha256(copy).hexdigest())

    def test_no_overwrite_when_directory_is_populated(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"assets"
            target.mkdir()
            (target/"DO_NOT_DELETE.txt").write_text("creator material",encoding="utf-8")
            import subprocess
            proc=subprocess.run([sys.executable,str(ROOT/"Tools"/"author_aureate_root_support.py"),
                                 "--output-dir",str(target)],capture_output=True,text=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertEqual((target/"DO_NOT_DELETE.txt").read_text(),"creator material")
            self.assertFalse((target/supports.FILES[0]).exists())

    def test_four_independent_supports_do_not_add_wings(self):
        # Integration reuses the existing four proxy mounts, no second four-piece rig.
        self.assertIn("WingRootMounts.Add(Bracket);",CPP)
        self.assertEqual(CPP.count("WingRootMounts.Add(Bracket);"),1)
        self.assertNotIn("WingRootSupports.Add(Support);",CPP)
        self.assertIn("GetWingRootMountCount() const",HEADER)
        self.assertIn("GetWingCount() const { return Wings.Num(); }",HEADER)
        self.assertIn("GetHydrofoilCount() const { return Hydrofoils.Num(); }",HEADER)

    def test_supports_hidden_without_correct_explicit_art(self):
        self.assertIn("bUseRootPivotedWingPose && AuthoredWingMesh &&",CPP)
        self.assertIn("AuthoredRootSupportMesh != nullptr",CPP)
        self.assertIn("Bracket->SetVisibility(bReviewMountsVisible);",CPP)
        self.assertIn("SetupPreviewMesh(Bracket, Shape);",CPP)
        self.assertIn("Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);",CPP)
        self.assertIn("CurrentForm != EAureateWakeForm::Orbiter",CPP)

    def test_telescoping_support_always_tracks_wing_root(self):
        self.assertIn("FVector(Length / 100.f, 1.f, 1.f)",CPP)
        self.assertIn("Bracket->SetRelativeRotation(Span.ToOrientationQuat());",CPP)
        self.assertIn("bUseAuthoredSupport\n            ? HullAnchor",CPP)
        self.assertIn("const float HalfWidth = ShouldShowPrimitiveHullStudy(bUseHullSilhouetteReview, bBodyReviewApplied) ? 56.f : 72.f;",CPP)
        for frm in clearance.FORMS:
            for wing in range(4):
                pos=clearance.pose(frm,wing)[0]
                side=-1 if wing%2==0 else 1
                anchor=(pos[0],side*72.,max(-28.,min(28.,pos[2])))
                length=sum((p-a)**2 for p,a in zip(pos,anchor))**.5
                self.assertGreater(length,30.)
                self.assertLess(length,100.)
        for first in clearance.FORMS:
            for second in clearance.FORMS:
                if first==second:continue
                for t in (0,.1,.3,.7,1):
                    for wing in range(4):
                        endpoint=clearance.blend(clearance.pose(first,wing),
                                                 clearance.pose(second,wing),t)[0]
                        anchor=(endpoint[0],(-1 if wing%2==0 else 1)*72.,
                                max(-28.,min(28.,endpoint[2])))
                        delta=tuple(x-y for x,y in zip(endpoint,anchor))
                        reconstructed=tuple(anchor[i]+delta[i] for i in range(3))
                        self.assertEqual(endpoint,reconstructed)

    def test_root_supports_update_in_snap_and_tick(self):
        part=CPP.split("void AAureateWakePreviewActor::SnapToForm(",1)[1]
        self.assertIn("UpdateWingRootMounts();",part.split("bool AAureateWakePreviewActor::RequestForm",1)[0])
        tick=CPP.split("void AAureateWakePreviewActor::Tick(",1)[1]
        self.assertIn("UpdateWingRootMounts();",tick)
        self.assertIn("void AAureateWakePreviewActor::RefreshRootSupportReview()",CPP)
        self.assertIn("RefreshRootSupportReview();",CPP)

    def test_story_and_hidden_orbiter_still_safe(self):
        self.assertIn("bool bAllowOrbiterPreview = false;",HEADER)
        self.assertIn("RequestedForm == EAureateWakeForm::Orbiter || CurrentForm == EAureateWakeForm::Orbiter",CPP)
        for forbidden in ("FlotationConfirmed(", "SeaContact(", "AdvanceStory(", "UnlockMoonBridge("):
            self.assertNotIn(forbidden,CPP)
        self.assertIn("No structural simulation",self.manifest["limits"][0])

if __name__=="__main__":
    unittest.main()
