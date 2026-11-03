"""Hosted source-only audit of the disposable UE V4 native import scripts.

This does not run the engine, render images, or validate material appearance.
"""
from pathlib import Path
import ast
import unittest

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"Tools"


class V4NativeScriptContract(unittest.TestCase):
    def read(self,name):
        path=TOOLS/name
        self.assertTrue(path.is_file(),name)
        source=path.read_text(encoding="utf8")
        ast.parse(source,filename=str(path))
        return source

    def test_bootstrap_refuses_existing_projects_and_checks_resources(self):
        source=self.read("bootstrap_aureate_cinematic_v4_sandbox.py")
        self.assertIn("if root.exists()",source)
        self.assertIn("raise FileExistsError",source)
        self.assertIn("15 * 1024**3",source)
        self.assertIn("AureateCinematicV4Sandbox",source)
        self.assertIn("AUREATE_CINEMATIC_V4_REVIEW_ONLY",source)
        self.assertNotIn("git reset",source)

    def test_native_entry_restricts_sandbox_and_checks_actual_material_slots(self):
        source=self.read("native_aureate_cinematic_v4_import_entry.py")
        self.assertIn("Paths.project_dir()",source)
        self.assertIn("preflight(SOURCE)",source)
        self.assertIn("native_import(SOURCE,source_receipt)",source)
        self.assertIn('if len(slots)!=4',source)
        self.assertIn("native_import_receipt.json",source)
        self.assertIn("NATIVE_IMPORT_AND_FIVE_STATICMESH_FOUR_MATERIAL_SLOT_READBACK_PASS",source)
        self.assertNotIn("request_form(",source)
        self.assertNotIn("save_current_level(",source)

    def test_runner_limits_resources_time_and_its_process_only(self):
        source=self.read("run_aureate_cinematic_v4_native_import.py")
        for pattern in ("MemoryStatus","GlobalMemoryStatusEx","free_memory_gib()<4.0",
                        "shutil.disk_usage(ROOT).free<14*1024**3",
                        "MAX_SECONDS=150","UnrealEditor-Cmd.exe",
                        "Popen(command","launched.terminate()","launched.kill()"):
            self.assertIn(pattern,source)
        self.assertNotIn("taskkill /im UnrealEditor.exe",source)
        self.assertNotIn("Stop-Process",source)
        self.assertIn("native_import_active.lock",source)

    def test_no_automatic_game_asset_admission(self):
        for name in ("bootstrap_aureate_cinematic_v4_sandbox.py",
                     "native_aureate_cinematic_v4_import_entry.py",
                     "run_aureate_cinematic_v4_native_import.py"):
            with self.subTest(name=name):
                source=self.read(name)
                for banned in ("RequestForm(", "merge_pull_request", "git push origin main",
                               "unreal.AureateWakeForm", "PublishArtifact"):
                    self.assertNotIn(banned,source)

    def test_receipt_maintains_distinct_import_and_stage_gates(self):
        doc=(ROOT/"Docs"/"AUREATE_CINEMATIC_V4_NATIVE_IMPORT_EVIDENCE_2026_11_03.md").read_text()
        self.assertIn("NATIVE ASSET IMPORT PASS",doc)
        self.assertIn("ASSEMBLED SCENE / CINEMATIC RENDER HOLD",doc)
        self.assertIn("zero completed maps",doc)
        self.assertIn("Starbourne stays",doc)
        self.assertIn("5.8.4-58902052",doc)


if __name__=="__main__":
    unittest.main()
