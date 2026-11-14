"""Pure source-only fail-closed assertions for native optical-review copy."""
from pathlib import Path
import hashlib,json,os,unittest
from unittest.mock import patch
import stage_vs02_optical_playtest as stage

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
READBACK=ROOT/"unreal/Saved/OpticalVS02Stage/readback.json"

class VS02OpticalStageContracts(unittest.TestCase):
    def test_owned_source_and_destination_unique(self):
        self.assertEqual(stage.ROOT,ROOT)
        self.assertTrue(stage.SOURCE_FILE.exists())
        self.assertNotEqual(stage.SOURCE_FILE,stage.DEST_FILE)
        self.assertEqual(stage.DEST,"/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview")
        self.assertEqual(stage.HEAD,"e7686bcb2f262ca9de0e6f9ceba96c812b93731f")
        self.assertEqual(len(stage.LIGHTS),len(set(stage.LIGHTS)))
        self.assertNotIn(stage.GAUGE,stage.LIGHTS)
    def test_replay_requires_explicit_opt_in(self):
        with patch.dict(os.environ,{"TSTSS_VS02_OPTICAL_PHASE":"prepare",
                 "TSTSS_VS02_OPTICAL_STAGE_EXPLICIT":""}):
            with self.assertRaisesRegex(RuntimeError,"explicit opt in"):
                stage.custody()
    def test_safety_checks_contain_native_guardrails(self):
        source=(HERE/"stage_vs02_optical_playtest.py").read_text(encoding="utf-8")
        for evidence in ('source_sha256','config_sha256','Save Map As',
                'get_dirty_map_packages','explicit_review_opt_in',
                'CineCameraActor','CameraFocusMethod.DISABLE','get_class().get_name()'):
            self.assertIn(evidence,source,evidence)
        self.assertIn('not list((PROJECT/"Saved/SaveGames").glob("*.sav"))',source)
        self.assertIn('source_lights_replaced_in_copy',source)
    def test_native_receipt_does_not_claim_pie_or_art(self):
        if not READBACK.exists():
            self.skipTest("native readback receipt local to Neontic")
        r=json.loads(READBACK.read_text(encoding="utf-8"))
        self.assertEqual(r["status"],"VS02_OPTICAL_SAVED_COPY_NATIVE_READBACK_PASS_NOT_PIE_OR_RENDER")
        self.assertEqual((r["gauge_count"],r["director_count"],r["disabled_receiver_count"],r["camera_count"]),(1,1,1,2))
        self.assertFalse(r["pie_input_tested"])
        self.assertFalse(r["gpu_captured"])
        self.assertFalse(r["creator_approved"])
        self.assertEqual(hashlib.sha256(stage.SOURCE_FILE.read_bytes()).hexdigest(),r["source_sha256"])
        self.assertEqual(hashlib.sha256(stage.DEST_FILE.read_bytes()).hexdigest(),r["review_map_sha256"])

if __name__=="__main__":unittest.main()
