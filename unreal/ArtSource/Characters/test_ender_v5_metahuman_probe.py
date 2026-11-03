"""Engine-free negative controls for the native MetaHuman authoring proof.

These synthetic tests DO NOT replace the independently recorded real Unreal run.
"""
import json
import tempfile
import unittest
from pathlib import Path
from verify_ender_v5_metahuman_probe import verify_native,ASSET,MAP_SHA

ROOT=Path(__file__).resolve().parent

class V5NativeProbeTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.d=Path(t.name)
        self.r=self.d/"receipt.json"
        self.a=self.d/"asset.uasset"
        self.l=self.d/"native.log"
        self.p=self.d/"CastAllSandbox.uproject"
        self.m=self.d/"refmap.umap"
        self.m.write_bytes(b"not the real Unreal map")
        # We deliberately do not weaken the production map SHA check:
        # patch only this test's module constant.
        import verify_ender_v5_metahuman_probe as v
        self.native_sha=v.MAP_SHA
        v.MAP_SHA=__import__("hashlib").sha256(self.m.read_bytes()).hexdigest()
        self.addCleanup(lambda:setattr(v,"MAP_SHA",self.native_sha))
        data={
          "status":"NATIVE_METAHUMAN_AUTHORING_BASE_PASS_ART_HOLD",
          "asset_path":ASSET,"project_guard":"DISPOSABLE_V5_ONLY",
          "project_name":"CastAllSandbox","plugin":"MetaHumanCharacter",
          "engine":"5.8.4-test",
          "native_asset_created":True,"native_asset_saved":True,
          "native_face_landmark_edit_surface_verified":True,
          "editor_subsystem_present":True,"registered_for_face_edit":True,
          "meta_human_authoring_bases_only":True,"face_landmarks_count":79,
          "first_landmark_xyz_native_unreal":[-4.7,9.5,165.2],
          "saved_reference_map_sha256":v.MAP_SHA,
        }
        for key in v.NOT_APPROVED:data[key]=False
        self.r.write_text(json.dumps(data),encoding="utf-8")
        self.a.write_bytes(bytes.fromhex("c1832a9e")+b"x"*101000)
        self.p.write_text(json.dumps({
          "Description":"Disposable TSTSS Ender V5 testing only",
          "EngineAssociation":"5.8",
          "Plugins":[{"Name":"MetaHumanCharacter","Enabled":True}]}),encoding="utf-8")
        self.l.write_text(
          "Mounting Engine plugin MetaHumanCharacter\n"
          "TSTSS_ENDER_V5_METAHUMAN_NATIVE_PROBE\n"
          "Test Completed. Result={Success} Name={test_ender_v5_metahuman_native}\n"
          "TEST COMPLETE. EXIT CODE: 0\n"
          "MetaHuman Optional Content folder not found\n"
          "skin editing will be disabled\n"
          "AssetCompile memory estimate is greater than available\n",
          encoding="utf-8")

    def call(self):
        return verify_native(self.r,self.a,self.l,self.p,self.m)

    def test_valid_shape_remains_art_hold(self):
        result=self.call()
        self.assertTrue(result["metahuman_optional_content_missing"])
        self.assertTrue(result["skin_editing_disabled"])
        self.assertEqual(result["face_landmarks_count"],79)
        self.assertFalse(result["creator_likeness_approved"])

    def test_false_approvals_and_missing_face_data_fail_closed(self):
        for k,v in [("likeness_approved",True),
                    ("imported_from_v4_mesh",True),
                    ("assembly_completed",True),
                    ("native_asset_saved",False),
                    ("face_landmarks_count",0),
                    ("asset_path","/Game/Characters/Ender.Ender"),
                    ("project_guard","PRODUCTION")]:
            with self.subTest(k=k):
                current=json.loads(self.r.read_text())
                altered={**current,k:v}
                self.r.write_text(json.dumps(altered))
                with self.assertRaises(AssertionError):
                    self.call()
                self.r.write_text(json.dumps(current))

    def test_corrupt_package_and_forged_exit_fail(self):
        original=self.a.read_bytes()
        self.a.write_bytes(b"BAD!"+original[4:])
        with self.assertRaises(AssertionError):
            self.call()
        self.a.write_bytes(original)
        log=self.l.read_text()
        self.l.write_text(log.replace("TEST COMPLETE. EXIT CODE: 0","TEST COMPLETE. EXIT CODE: 1"))
        with self.assertRaises(AssertionError):
            self.call()

    def test_engine_script_cannot_rig_download_or_promote(self):
        script=(ROOT/"probe_ender_v5_metahuman_native.py").read_text(encoding="utf-8")
        self.assertIn("DISPOSABLE_V5_ONLY",script)
        self.assertIn("Refuse overwrite",script)
        self.assertIn('"rigged":False',script)
        self.assertNotIn("request_auto_rigging(",script)
        self.assertNotIn("request_textures(",script)
        self.assertNotIn("run_assembly(",script)
        self.assertNotIn('"/Game/Characters/"',script)

if __name__=="__main__":
    unittest.main()
