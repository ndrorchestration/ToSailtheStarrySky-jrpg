"""Offline regression checks for fail-closed V5 procedural PBR import."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).with_name("stage_first_wake_v5_pbr_materials.py")
S = SCRIPT.read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location("tstss_v5_pbr_import", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FirstWakeV5PBRImport(unittest.TestCase):
    def test_all_existing_texture_hashes_verified(self):
        inventory = module.source_inventory()
        self.assertEqual(inventory["source_texture_family_count"], 5)
        self.assertEqual(inventory["source_texture_count"], 15)
        self.assertEqual(len(inventory["files"]), 15)
        self.assertEqual(set(module.FAMILIES), {
            "timber", "stone", "brass", "aether", "ocean",
        })
        self.assertEqual(set(module.CHANNELS), {"BaseColor", "Normal", "ORM"})
        self.assertFalse(inventory["production_maps_changed"])
        self.assertFalse(inventory["scene_approved"])
        self.assertEqual(len(inventory["source_V5_map_sha256"]), 64)

    def test_non_native_plan_does_not_change_art_or_source(self):
        current = sorted(
            p.name for p in module.SOURCE.glob("T_FW_*")
        )
        plan = subprocess.run(
            [sys.executable, str(SCRIPT), "--plan"], check=True,
            capture_output=True, text=True, timeout=20,
        )
        self.assertIn('"source_texture_count": 15', plan.stdout)
        self.assertEqual(current, sorted(p.name for p in
                                         module.SOURCE.glob("T_FW_*")))

    def test_native_stage_is_strictly_opt_in(self):
        env = os.environ.copy()
        env.pop("TSTSS_V5_PBR_OPT_IN", None)
        p = subprocess.run(
            [sys.executable, str(SCRIPT), "--stage-native"],
            capture_output=True, text=True, env=env, timeout=20,
        )
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("explicit PBR opt-in missing", p.stderr)

    def test_requires_exact_git_head_native_suite_and_clean_files(self):
        for token in (
            "EXPECTED_WORKTREE",
            "TSTSS_V5_PBR_EXPECTED_HEAD",
            'git("status", "--porcelain", "-uall")',
            "exact_native_receipt(expected)",
            "len(names) != 36",
            "result.get(\"report_sha256\") != sha256(report)",
            "result.get(\"source_sha\") != expected",
            "actual[\"failed\"] != 0",
            "actual[\"notRun\"] != 0",
            "actual[\"succeeded\"] != 36",
            "Map", # source is retained at same sha
            "source_V5_map_sha256",
        ):
            if token == "Map":
                self.assertIn("SOURCE_MAP", S)
            else:
                self.assertIn(token, S)

    def test_imported_pbr_materials_include_real_base_normal_and_orm(self):
        for marker in (
            "AssetImportTask()", "replace_existing\", False",
            "MaterialExpressionTextureSample",
            "MaterialExpressionTextureCoordinate",
            "MP_BASE_COLOR", "MP_NORMAL", "MP_AMBIENT_OCCLUSION",
            "MP_ROUGHNESS", "MP_METALLIC",
            "TextureCompressionSettings.TC_NORMALMAP",
            "TextureCompressionSettings.TC_MASKS",
            "editor.recompile_material(material)",
            "save_loaded_asset(material)",
        ):
            self.assertIn(marker, S)

    def test_no_map_edits_or_story_modifications(self):
        for mutation in (
            "save_current_level(", "save_map(", "duplicate_asset(",
            "SetActorLocation(", "AdvanceTo(", "AdvanceWaterBeat(",
            "open_level(", "SaveGameToSlot(", "SpawnActor(",
        ):
            self.assertNotIn(mutation, S)
        self.assertIn("if sha256(SOURCE_MAP) != before:", S)
        self.assertIn('"production_maps_changed": False', S)
        self.assertIn('"creator_approved": False', S)


if __name__ == "__main__":
    unittest.main()
