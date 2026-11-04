"""Source-only checks for named isolated bridge framing tests 14 and 15."""
import ast,unittest
from pathlib import Path
TOOLS=Path(__file__).resolve().parents[1]/"Tools"
BASE_SHA="14e896f532e898836c98d51b3acf33936faf7c43f907b0d0fa20f9cac4ca4362"

class BridgeCameraReviewTests(unittest.TestCase):
    def sources(self):
        return tuple((TOOLS/name).read_text(encoding="utf8") for name in
          ("capture_aureate_v4_habitation_bridge_gpu_automation14.py",
           "capture_aureate_v4_habitation_framing_gpu_automation15.py"))

    def test_both_camera_scripts_are_review_map_sha_pinned(self):
        for text in self.sources():
            ast.parse(text)
            self.assertIn(BASE_SHA,text)
            self.assertIn('CAMERA="V4_NONCANONICAL_CAMERA_BRIDGE"',text)
            self.assertIn("AUREATE_CINEMATIC_V4_REVIEW_ONLY",text)
            self.assertIn("source_map_sha_after",text)
            self.assertIn("production_content_modified",text)
            self.assertIn("starbourne_player_unlock",text)
            self.assertNotIn("save_current_level",text)

    def test_camera_adjustment_is_transient(self):
        saved,temporary=self.sources()
        self.assertNotIn("camera_override_unsaved",saved)
        self.assertIn('info["camera_override_unsaved"]=True',temporary)
        self.assertIn("cam.set_actor_location(newpos,False,False)",temporary)
        self.assertIn('info["camera_authority"]="TEMPORARY_FRAMING_DIAGNOSTIC_NOT_APPROVED"',temporary)
        self.assertIn("cam.set_actor_rotation(",temporary)

    def test_registered_runners_have_separate_outputs_and_watchdogs(self):
        a=(TOOLS/"run_aureate_v4_habitation_bridge_gpu_automation14.py").read_text()
        b=(TOOLS/"run_aureate_v4_habitation_framing_gpu_automation15.py").read_text()
        for text in (a,b):
            ast.parse(text)
            self.assertIn("free_ram()<6.5",text)
            self.assertIn("14*1024**3",text)
            self.assertIn("UnrealEditor-Cmd.exe",text)
            self.assertIn("Previous automation capture attempt: refuse overwrite",text)
        self.assertIn("Automation14",a)
        self.assertIn("Automation15",b)
        self.assertNotIn("Automation15",a)
        self.assertNotIn("Automation14",b)

if __name__=="__main__":
    unittest.main()
