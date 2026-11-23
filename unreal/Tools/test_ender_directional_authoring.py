"""Static fail-closed controls for private UE5.8 directional IK study."""
import ast
import unittest
from pathlib import Path

TOOLS=Path(__file__).resolve().parent
AUTHOR=(TOOLS/"author_private_ender_directional_walk.py").read_text("utf8")
HOST=(TOOLS/"Invoke-EnderDirectionalRetarget.ps1").read_text("utf8")


class EnderDirectionalAuthorTests(unittest.TestCase):
    def test_python_syntax_and_exact_three_directional_clips(self):
        ast.parse(AUTHOR)
        for name in ("MF_Unarmed_Walk_Bwd", "MF_Unarmed_Walk_Left",
                     "MF_Unarmed_Walk_Right"):
            self.assertIn(name, AUTHOR)
        for forbidden in ("MF_Unarmed_Jog_Bwd", "MM_Idle_EnderDirectional",
                          "save_game", "spawn_actor", "delete_asset("):
            self.assertNotIn(forbidden, AUTHOR)

    def test_native_asset_guards_and_root_provenance(self):
        for value in ("TSTSS_DIRECTIONAL_EXPECTED_HEAD", "TSTSS_PRIVATE_DIRECTIONAL_CREATE",
                      "DIRTY_TRACKED_SOURCE", "SOURCE_HASH_", "OUTPUT_ALREADY_EXISTS_",
                      "OUTPUT_NOT_IGNORED", "TARGET_IDLE", "SOURCE_MESH", "TARGET_MESH",
                      "IKRetargetBatchOperationInputs", "overwrite_existing_files=False",
                      "include_referenced_assets=False", "source_skeleton", "target_skeleton",
                      "PRIVATE_DIRECTIONAL_RETARGET_CREATED_NOT_PLAYBACK_ACCEPTED"):
            self.assertIn(value, AUTHOR)

    def test_only_ignored_review_output_and_no_direct_playback(self):
        self.assertIn("DirectionalWalkV1_PRIVATE", AUTHOR)
        self.assertIn("MannequinWalkSources_PRIVATE", AUTHOR)
        self.assertIn("skeleton", AUTHOR)
        for forbidden in ("set_anim_instance_class(", "set_actor_location(",
                          "unreal.GameplayStatics.open_level(", "save_level(",
                          "delete_asset(", "overwrite_existing_files=True"):
            self.assertNotIn(forbidden, AUTHOR)

    def test_host_protects_preexisting_assets_and_no_destructive_cleanup(self):
        for value in ("WRONG_COMMIT", "BRANCH", "ENGINE_BUSY", "RAM", "DISK",
                      "PROTECTED_ASSET_BASELINE_TOO_SMALL", "PROTECTED_ASSET_CHANGED_",
                      "SOURCE_NOT_IGNORED", "OUTPUT_NOT_IGNORED", "COPY_HASH_",
                      "NATIVE_PRIVATE_DIRECTIONAL_RETARGET_PASS", "RECEIPT=",
                      "TSTSS_PRIVATE_DIRECTIONAL_CREATE", "overwrite"):
            # Host uses no overwrite by File.Copy(...,false), not destructive cleanup.
            if value=="overwrite":
                self.assertIn("false", HOST)
            else:
                self.assertIn(value, HOST)
        for forbidden in ("reset --hard", "clean -fd", "git push",
                          "Remove-Item -Recurse", "delete_asset(", "-Force"):
            self.assertNotIn(forbidden, HOST)


if __name__=="__main__":
    unittest.main()
