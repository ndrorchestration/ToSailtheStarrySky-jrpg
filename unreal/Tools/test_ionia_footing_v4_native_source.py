"""Engine-free fail-closed contracts for noncanonical First Wake Ionia V4 footing."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent
STAGE=ROOT/"stage_firstwake_ionia_footing_v4.py"
VERIFY=ROOT/"verify_firstwake_ionia_footing_v4.py"
V3="54b4e266683347fc950a56c8ac8691d99aaddb41d61e304ddf0f5b4d0730e2b5"
V2="4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80"
V4="09ee6d30805bcb54a2b29f0dbfe7ec8975ea9e8abd15c1f8dda1fdf975c2ce3a"
def contract(text):
    return all(s in text for s in (
        'center,ext=ionia.get_actor_bounds(False)',
        'old_foot=float(center.z-ext.z)',
        'offset=-old_foot',
        'new_foot=float(after_center.z-after_ext.z)',
        'abs(new_foot)<0.02',
        'len(matches)==1'))
class TestIoniaFooting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage=STAGE.read_text(encoding="utf8")
        cls.verify=VERIFY.read_text(encoding="utf8")
    def test_source_syntax(self):
        ast.parse(self.stage);ast.parse(self.verify)
    def test_source_identity_pinned(self):
        for x in (V2,V3):
            self.assertIn(x,self.stage);self.assertIn(x,self.verify)
        self.assertIn(V4,self.verify)
    def test_new_map_is_nonoverwriting(self):
        for s in ('REVIEW_V4_IONIA_FOOTING','not NEW_FILE.exists() and not RECEIPT.exists()',
                  'not lib.does_asset_exist(NEW)','new_level_from_template(NEW,OLD)'):
            self.assertIn(s,self.stage)
    def test_original_map_sha_guarded(self):
        self.assertIn('sha(OLD_FILE)==OLD_SHA and sha(BASE)==BASE_SHA',self.stage)
    def test_bounded_native_offset_from_geometry(self):
        self.assertTrue(contract(self.stage))
        self.assertNotIn('offset=165.5862',self.stage)
    def test_mutation_hardcoded_offset_fails(self):
        self.assertFalse(contract(self.stage.replace('offset=-old_foot','offset=165.5862')))
    def test_mutation_groundline_check_deleted_fails(self):
        self.assertFalse(contract(self.stage.replace('abs(new_foot)<0.02','True')))
    def test_one_ionia_only_move(self):
        self.assertIn('get_actor_label()==LABEL',self.stage)
        self.assertIn('ionia.set_actor_location(adjusted,False,False)',self.stage)
        self.assertIn('len(matches)==1',self.stage)
    def test_actor_story_gates_unchanged(self):
        for source in (self.stage,self.verify):
            self.assertIn('len(actors)==34',source)
            self.assertIn('unreal.PlayerStart',source)
            self.assertIn('FlyerDiscovery',source)
            self.assertIn('EngineeringApproval',source)
            self.assertIn('STARBOURNE',source.upper())
    def test_no_destructive_ops_or_production_changes(self):
        for source in (self.stage,self.verify):
            for s in ('delete_asset(', 'delete_directory(', 'force_delete', 'SaveGameToSlot'):
                self.assertNotIn(s,source)
        self.assertNotIn('save_current_level(',self.verify)
    def test_readback_independence_and_negative_checks(self):
        for s in ('OLD_BOUNDS','not RECEIPT.exists()',
                  'sha(NEW_FILE)==SHA and sha(V3)==V3_SHA and sha(BASE)==BASE_SHA',
                  'set(bylabel)==set(current)','unrelated staged actor moved','abs(foot)<0.02'):
            self.assertIn(s,self.verify)
    def test_no_false_visual_or_playable_admission(self):
        self.assertIn('"art_approved":False',self.stage)
        self.assertIn('"independent_readback_verified":False',self.stage)
        self.assertIn('"visual_art_approved":False',self.verify)
        self.assertIn('"gameplay_verified":False',self.verify)
if __name__=="__main__":unittest.main()
