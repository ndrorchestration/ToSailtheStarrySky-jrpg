"""Review-only native Editor module provenance and fail-closed fixtures."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0,str(Path(__file__).parent))
import prepare_first_wake_editor_module as module

class TestNativeModuleCustody(unittest.TestCase):
    def test_bounded_module_manifest(self):
        self.assertEqual(3,len(module.BINARY_FILES))
        self.assertEqual(3,len(set(module.BINARY_FILES)))
        self.assertFalse(any(".pdb" in p.lower() for p in module.BINARY_FILES))
        self.assertTrue(all("unreal/Binaries/Win64/" in p for p in module.BINARY_FILES))

    def test_only_compile_source_paths_are_compared(self):
        self.assertIn("unreal/Source",module.SOURCE_PATHS)
        self.assertIn("unreal/Config",module.SOURCE_PATHS)
        self.assertIn("unreal/ToSailTheStarrySky.uproject",module.SOURCE_PATHS)
        self.assertFalse(any("ArtSource" in p or "Docs" in p for p in module.SOURCE_PATHS))

    def test_preflight_rejects_wrong_named_worktrees(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(module,"SOURCE",Path(d)/"source"),mock.patch.object(module,"DEST",Path(d)/"dest"):
                with self.assertRaisesRegex(RuntimeError,"wrong native module"):
                    module.preflight()

    def test_hash_inventory_rejects_tamper_and_false_native_loaded_flag(self):
        with tempfile.TemporaryDirectory() as srcdir,tempfile.TemporaryDirectory() as dstdir:
            src,dst=Path(srcdir),Path(dstdir)
            files=[]
            for rel in module.BINARY_FILES:
                source=src/rel
                target=dst/rel
                source.parent.mkdir(parents=True,exist_ok=True)
                target.parent.mkdir(parents=True,exist_ok=True)
                source.write_bytes(("native-test-fixture:"+rel).encode())
                target.write_bytes(source.read_bytes())
                files.append({"relative_path":rel,"sha256":module.digest(source),"bytes":source.stat().st_size})
            receipt={"status":"EVIDENCE_BOUND_EDITOR_MODULE_COPIED_NATIVE_LOAD_NOT_YET_RUN",
                     "source_native_head":module.SOURCE_HEAD,"git_cpp_config_diff_count":0,
                     "engine_version":"5.8.4",
                     "native_readback_verified_historical":True,
                     "new_worktree_native_module_load_verified":False,
                     "files":files}
            output=dst/module.MANIFEST
            output.parent.mkdir(parents=True,exist_ok=True)
            with mock.patch.object(module,"SOURCE",src),mock.patch.object(module,"DEST",dst),mock.patch.object(module,"diff_paths",return_value=[]),mock.patch.object(module.intake,"git",return_value="head"):
                output.write_text(json.dumps(receipt),encoding="utf-8")
                self.assertEqual(3,module.verify_module()["module_count"])
                target=dst/module.BINARY_FILES[0]
                target.write_bytes(target.read_bytes()+b"malicious-mutation")
                with self.assertRaisesRegex(RuntimeError,"drift"):
                    module.verify_module()
                target.write_bytes((src/module.BINARY_FILES[0]).read_bytes())
                receipt["new_worktree_native_module_load_verified"]=True
                output.write_text(json.dumps(receipt),encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError,"custody claims"):
                    module.verify_module()
                receipt["new_worktree_native_module_load_verified"]=False
                receipt["files"]=files[:-1]
                output.write_text(json.dumps(receipt),encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError,"file receipts"):
                    module.verify_module()
                receipt["files"]=files
                output.write_text(json.dumps(receipt),encoding="utf-8")
                with mock.patch.object(module,"diff_paths",return_value=["unreal/Source/changed.cpp"]):
                    with self.assertRaisesRegex(RuntimeError,"source parity"):
                        module.verify_module()

    def test_copy_uses_exclusive_outputs_and_checks_hashes(self):
        with tempfile.TemporaryDirectory() as srcdir,tempfile.TemporaryDirectory() as dstdir:
            src,dst=Path(srcdir),Path(dstdir)
            files=[]
            for rel in module.BINARY_FILES:
                path=src/rel
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(b"test-binary:"+rel.encode())
                files.append({"relative_path":rel,"sha256":module.digest(path),"bytes":path.stat().st_size})
            fake={"status":"VERIFIED_NATIVE_SOURCE_EQUIVALENCE_NO_MODULE_COPIED",
                  "files":files,"source_native_head":module.SOURCE_HEAD}
            with mock.patch.object(module,"SOURCE",src),mock.patch.object(module,"DEST",dst),mock.patch.object(module,"preflight",return_value=fake):
                self.assertEqual("EVIDENCE_BOUND_EDITOR_MODULE_COPIED_NATIVE_LOAD_NOT_YET_RUN",
                                 module.copy_module()["status"])
                with self.assertRaises(FileExistsError):
                    module.copy_module()
                self.assertTrue((dst/module.MANIFEST).is_file())

if __name__=="__main__":
    unittest.main()
