"""Source-only checks for three genuine but separately evidenced review scenes."""
from pathlib import Path
import ast
import unittest

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"Tools"

class RemainingThreeFormsSourceContracts(unittest.TestCase):
    def read(self,name):
        p=TOOLS/name
        self.assertTrue(p.is_file())
        s=p.read_text(encoding="utf8")
        ast.parse(s,filename=str(p))
        return s

    def test_all_three_form_names_have_fresh_private_review_paths(self):
        s=self.read("aureate_v4_full_editor_three_form_stage.py")
        self.assertIn('FORMS=("Seabourne","Submersible","Starbourne")',s)
        self.assertIn("AureateCinematicV4_",s)
        self.assertIn("FullEditor",s)
        self.assertIn("if lib.does_asset_exist(dest)",s)
        self.assertIn("save_current_level()",s)
        self.assertIn("THREE_NATIVE_FULL_EDITOR_REVIEW_MAPS_STAGED_PASS",s)

    def test_pins_verified_skybourne_before_followups(self):
        s=self.read("aureate_v4_full_editor_three_form_stage.py")
        self.assertIn("16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40",s)
        self.assertIn("SKYBOURNE_ONE_FORM_NATIVE_FULL_EDITOR_ACTOR_STAGE_PASS",s)
        self.assertIn("hashlib.sha256(skypath.read_bytes()).hexdigest()==SKY_SHA",s)
        self.assertIn("native_import_receipt.json",s)
        self.assertIn("AUREATE_CINEMATIC_V4_REVIEW_ONLY",s)

    def test_shared_vessel_four_wing_ids_and_two_seabourne_foils(self):
        s=self.read("aureate_v4_full_editor_three_form_stage.py")
        for identity in ("FORE_PORT","FORE_STARBOARD","AFT_PORT","AFT_STARBOARD"):
            self.assertIn(identity,s)
        self.assertIn("SHARED_PEARL_HULL_PROXY",s)
        self.assertIn("CENTRAL_LIVING_QUARTERS_PROXY",s)
        self.assertIn("FORWARD_GLASS_GEODESIC_BRIDGE_PROXY",s)
        self.assertIn('for side,label in ((-1,"PORT"),(1,"STARBOARD")):',s)
        self.assertIn("SeabourneHydrofoilDetail",s)
        self.assertIn("SubmersibleLightRail",s)

    def test_four_equal_developer_starbourne_sails_not_game_unlock(self):
        s=self.read("aureate_v4_full_editor_three_form_stage.py")
        for direction in ("UP","RIGHT","DOWN","LEFT"):
            self.assertIn('"'+direction+'"',s)
        self.assertIn("StarbourneSailMotif",s)
        self.assertIn('"radial_static_sails"',s)
        self.assertIn('"player_story_access"]="LOCKED"',s)
        self.assertIn('"starbourne_player_form_available":False',s)
        self.assertNotIn("RequestForm(",s)

    def test_full_editor_runner_has_resource_gate_and_no_gpu_claim(self):
        s=self.read("run_aureate_v4_three_form_full_editor_stage.py")
        self.assertIn("-ExecutePythonScript=",s)
        self.assertIn("-NullRHI",s)
        self.assertIn("free_ram()<4.2",s)
        self.assertIn("14*1024**3",s)
        self.assertIn("MAX_SECONDS=170",s)
        self.assertIn('"gpu_capture_claim":False',s)
        self.assertIn("user_editor_untouched",s)
        self.assertIn("len(native.get",s)
        self.assertIn("NATIVE_THREE_FORM_STAGE_PASS",s)

    def test_no_runtime_change_or_unintended_production_mutation(self):
        for name in ("aureate_v4_full_editor_three_form_stage.py",
                     "run_aureate_v4_three_form_full_editor_stage.py"):
            s=self.read(name)
            for bad in ("delete_asset(", "request_form(", "SaveGameToSlot(",
                        "git push origin main","Stop-Process","taskkill /im"):
                self.assertNotIn(bad,s)

if __name__=="__main__":
    unittest.main()
