"""Safety and receipt fixtures for PRIVATE native Harbor intake (engine-free)."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0,str(Path(__file__).parent))
import transfer_first_wake_harbor_review as intake

class TestHarborIntake(unittest.TestCase):
    def test_allowlisted_folders_have_only_first_wake_dependencies(self):
        self.assertEqual(7,len(intake.FOLDERS))
        self.assertEqual(6,len(intake.FILES))
        all_paths=" ".join((*intake.FOLDERS,*intake.FILES)).lower()
        self.assertNotIn("starbourne",all_paths)
        self.assertNotIn("submersible",all_paths)
        self.assertIn("FirstWake_HarborEnvironment_20261104_REVIEW_V1.umap",
                      intake.FILES[1])

    def test_reject_escape_absolute_windows_and_restricted(self):
        for path in ("../private","unreal/../Saved/private","C:/Users/Admin/secrets",
                     "unreal\\..\\Users\\private","/unreal/Content/Evil",
                     "unreal/Content/TSTSS/StarbourneSailMotif.uasset",
                     "unreal/Content/TSTSS/SubmersibleRail.uasset"):
            with self.subTest(path=path):
                with self.assertRaises(RuntimeError): intake.safe_rel(path)

    def test_accept_backslashes_and_slashes_equivalently(self):
        a=intake.safe_rel("unreal/Content/TSTSS/Review/Scenes")
        b=intake.safe_rel("unreal\\Content\\TSTSS\\Review\\Scenes")
        self.assertEqual(a,b)

    def test_wrong_named_root_preflight_refuses_before_git(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/"source"
            dst=Path(d)/"target"
            with self.assertRaisesRegex(RuntimeError,"wrong named"):
                intake.preflight(src,dst)

    def test_selected_source_folders_are_required(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(RuntimeError,"missing source package folder"):
                intake.selected_files(Path(d))

    def test_selects_exact_allowlist_with_receipts(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)
            for folder in intake.FOLDERS:
                p=src/folder/"mesh.uasset"
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(b"material-and-mesh")
            for name in intake.FILES:
                p=src/name
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(b"fixture")
            selected=intake.selected_files(src)
            self.assertEqual(len(intake.FOLDERS)+len(intake.FILES),len(selected))
            self.assertEqual(len(selected),len(set(selected)))
            self.assertTrue(all(str(p).startswith("unreal") for p in selected))

    def test_copy_rehash_and_never_overwrite_fixture(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as dest:
            s,d=Path(source),Path(dest)
            paths=["unreal/Content/TSTSS/Review/Scenes/a.umap",
                   "unreal/Content/ArtLookdev/Characters/Ionia/Ionia/StaticMeshes/Ionia.uasset"]
            for i,path in enumerate(paths):
                p=s/path
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(("native-private-fixture-"+str(i)).encode())
            report={"status":"PRIVATE_SOURCE_DEPENDENCIES_ADMITTED_NOT_COPIED",
                    "selected":paths,"source_files":2}
            result=intake.copy_private_files(dict(report),s,d)
            self.assertEqual("VERIFIED_PRIVATE_HARBOR_ASSETS_COPIED_NOT_UNREAL_LOADED",result["status"])
            receipt=json.loads((d/intake.MANIFEST).read_text(encoding="utf-8"))
            self.assertEqual(2,len(receipt["file_hashes"]))
            for path in paths:
                self.assertEqual((s/path).read_bytes(),(d/path).read_bytes())
                self.assertEqual(hashlib.sha256((d/path).read_bytes()).hexdigest(),
                                 receipt["file_hashes"][path])
            with self.assertRaises(FileExistsError):
                intake.copy_private_files(dict(report),s,d)
            self.assertTrue((d/intake.MANIFEST).exists())

    def test_bad_source_receipts_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            project=Path(d)/"unreal"
            saved=project/"Saved/FirstWakeEnvironmentV1"
            saved.mkdir(parents=True,exist_ok=True)
            base=project/"Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3.umap"
            harbor=project/"Content/TSTSS/Review/Scenes/FirstWake_HarborEnvironment_20261104_REVIEW_V1.umap"
            base.parent.mkdir(parents=True,exist_ok=True)
            base.write_bytes(b"source world fixture")
            harbor.write_bytes(b"review Harbor fixture")
            bh=intake.digest(base); hh=intake.digest(harbor)
            native={"status":"NATIVE_HARBOR_MAP_SAVED_PENDING_INDEPENDENT_READBACK",
                    "map_sha256":hh,"parent_map_sha256":bh,
                    "previous_actor_count":34,"new_actor_count":50}
            host={"status":"NATIVE_MAP_SAVED_PENDING_INDEPENDENT_READBACK",
                  "new_map_sha256":hh,"source_head":intake.SOURCE_HEAD,
                  "editor_exit_code":0,"config_hashes_preserved":True}
            readback={"status":"INDEPENDENT_NATIVE_HARBOR_SAVED_WORLD_READBACK_PASS_NOT_PIE",
                      "new_map_sha256":hh,"inherited_actor_count":34,
                      "milestones_verified":7}
            host_rb={"status":"INDEPENDENT_NATIVE_HARBOR_READBACK_VERIFIED_NOT_PIE",
                     "new_map_sha256":hh,"verified_actor_count":84,
                     "verified_material_count":8,"editor_exit_code":0}
            sources={"native_harbor_stage.json":native,"host_harbor_stage.json":host,
                     "independent_harbor_readback.json":readback,
                     "host_harbor_readback.json":host_rb}
            for name,record in sources.items():
                (saved/name).write_text(json.dumps(record),encoding="utf-8")
            with mock.patch.object(intake,"HARBOR_SHA",hh),mock.patch.object(intake,"ASSET_WORLD_SHA",bh):
                self.assertTrue(intake.receipt_check(Path(d))["native_readback_verified"])
                # False claim must fail, even though two map checksums still match.
                host_rb["verified_actor_count"]=83
                (saved/"host_harbor_readback.json").write_text(json.dumps(host_rb),encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError,"proof incomplete"):
                    intake.receipt_check(Path(d))
                host_rb["verified_actor_count"]=84
                host_rb["editor_exit_code"]=1
                (saved/"host_harbor_readback.json").write_text(json.dumps(host_rb),encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError,"proof incomplete"):
                    intake.receipt_check(Path(d))

    def test_private_custody_not_uploaded_by_source_workflow(self):
        workflow=Path(__file__).resolve().parents[2]/".github/workflows/unreal-first-wake-slice-objects.yml"
        content=workflow.read_text(encoding="utf-8")
        self.assertIn("test_first_wake_harbor_intake.py",content)
        self.assertNotIn("Saved/FirstWakeSliceObjectsV1/harbor_private_intake_manifest.json",content)
        self.assertNotIn("transfer_first_wake_harbor_review.py --copy",content)

    def test_native_readback_host_requires_exact_staged_evidence(self):
        import run_first_wake_slice_objects_readback as reader
        host={"status":"NATIVE_STAGE_SAVED_PENDING_INDEPENDENT_READBACK",
              "new_map_sha256":"map","source_commit":"commit",
              "config_hashes_preserved":True,"source_map_preserved":True,
              "commit_preserved":True}
        native={"status":"NATIVE_OBJECT_MAP_SAVED_PENDING_INDEPENDENT_READBACK",
                "new_map_sha256":"map","source_map_sha256":"parent",
                "new_native_actor_count":31,"native_static_mesh_assets":22}
        self.assertTrue(reader.verify_stage_proof(host,native,"map","parent","commit"))
        for key,bad in (("native_static_mesh_assets",21),("new_native_actor_count",30),
                        ("source_map_sha256","other"),("new_map_sha256","other")):
            with self.subTest(key=key):
                mutated=dict(native,**{key:bad})
                with self.assertRaisesRegex(RuntimeError,"incomplete"):
                    reader.verify_stage_proof(host,mutated,"map","parent","commit")
        with self.assertRaisesRegex(RuntimeError,"incomplete"):
            reader.verify_stage_proof(dict(host,config_hashes_preserved=False),
                                      native,"map","parent","commit")

    def test_native_readback_claim_cannot_exceed_saved_inventory(self):
        import run_first_wake_slice_objects_readback as reader
        obj={"status":"INDEPENDENT_NATIVE_OBJECT_READBACK_PASS_NOT_PIE",
             "saved_world_sha256":"verified","actors":115,
             "new_visual_actors":31,"distinct_imported_static_meshes":22,
             "milestones_preserved":list(reader.stage.MILESTONES),"player_starts":1,
             "physics_verified":False,"pie_verified":False,
             "render_verified":False,"art_approved":False}
        self.assertTrue(reader.verify_native_receipt(obj,"verified"))
        for key,bad in (("actors",114),("new_visual_actors",30),
                        ("distinct_imported_static_meshes",21),("player_starts",2),
                        ("saved_world_sha256","changed"),("pie_verified",True),
                        ("art_approved",True),("physics_verified",True)):
            with self.subTest(key=key):
                with self.assertRaisesRegex(RuntimeError,"bounded"):
                    reader.verify_native_receipt(dict(obj,**{key:bad}),"verified")
        with self.assertRaisesRegex(RuntimeError,"bounded"):
            reader.verify_native_receipt(
                dict(obj,milestones_preserved=list(reader.stage.MILESTONES)[:-1]),"verified")

if __name__=="__main__":
    unittest.main()
