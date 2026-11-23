"""Source gates for single-variable IK Root Motion child-propagation study."""
import ast
import unittest
from pathlib import Path

TOOLS=Path(__file__).parent
AUTHOR=(TOOLS/"author_private_ender_nochildprop_study.py").read_text("utf8")
HOST=(TOOLS/"Invoke-EnderNoChildPropagationStudy.ps1").read_text("utf8")

class EnderNoChildPropStudyGuards(unittest.TestCase):
 def test_three_sha_locked_sources_and_private_namespace(self):
  ast.parse(AUTHOR)
  self.assertEqual(AUTHOR.count('"MF_Unarmed_Walk_Bwd":')+
                   AUTHOR.count('"MF_Unarmed_Walk_Left":')+
                   AUTHOR.count('"MF_Unarmed_Walk_Right":'),3)
  for x in ("MannequinWalkSources_PRIVATE","DirectionalNoChildPropV1_PRIVATE",
            "RTG_MannyToEnder_NoChildPropV1_PRIVATE","SOURCE_HASH_",
            "OUTPUT_NOT_IGNORED","overwrite_existing_files=False"):
   self.assertIn(x,AUTHOR)

 def test_only_duplicate_root_motion_child_propagation_changes(self):
  for x in ("EditorAssetLibrary.duplicate_asset(ORIGINAL_RETARGET,DUPLICATE_RETARGET)",
            'str(ctrl.get_op_name(3))=="Root Motion"',
            'settings.get_editor_property("propagate_to_non_retargeted_children")',
            'settings.set_editor_property("propagate_to_non_retargeted_children",False)',
            'op.set_settings(settings)',"DUPLICATED_RETARGETER",
            "normal_retargeter_modified"):
   self.assertIn(x,AUTHOR)
  for forbidden in ("set_anim_instance_class(","PlayAnimation(","SaveLevel(",
                    "delete_asset(","overwrite_existing_files=True"):
   self.assertNotIn(forbidden,AUTHOR)

 def test_numeric_spine_screen_and_no_premature_signoff(self):
  for x in ("get_anim_pose_at_time","AnimPoseSpaces.LOCAL","get_ref_bone_pose",
            "max_spine1_local_offset_cm","<=10.0",
            "SPINE_GEOMETRY_SCREEN_PASS_NOT_VISUAL",
            "HOLD_SPINE_GEOMETRY_CHILDPROP_STUDY",
            '"art_or_playback_accepted":False'):
   self.assertIn(x,AUTHOR)

 def test_host_exact_head_asset_hashes_config_and_fail_closed(self):
  for x in ("PROTECTED_FILE_MISSING","ORIGINAL_BINARY_MUTATED",
            "SOURCE_DIRTY_AFTER","CONFIG_RESTORE","EXPECTED",
            "GEOMETRY_REJECTED","CANDIDATE_HASH",
            "ENGINE_BUSY","RAM","DISK","PRIVATE_OUTPUT_ALREADY_EXISTS"):
   if x=="EXPECTED":
    self.assertIn("ExpectedHead",HOST)
   elif x=="RAM" or x=="DISK":
    self.assertIn("RESOURCES",HOST)
   else:
    self.assertIn(x,HOST)
  for forbidden in ("reset --hard","git clean","Remove-Item -Recurse",
                    "git push","-Force"):
   self.assertNotIn(forbidden,HOST)

if __name__=="__main__":
 unittest.main()
