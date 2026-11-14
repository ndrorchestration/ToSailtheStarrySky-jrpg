"""Pure source-only fail-closed assertions for native optical-review copy."""
from pathlib import Path
import hashlib,json,os,unittest
from unittest.mock import patch
import stage_vs02_optical_playtest as stage

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
READBACK=ROOT/"unreal/Saved/OpticalVS02Stage/readback.json"
LOOKDEV=ROOT/"unreal/DataSource/Cinematics/VS02OpticalLookdev.review.json"

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
    def test_current_review_map_matches_locked_manifest(self):
        data=json.loads(LOOKDEV.read_text(encoding="utf-8"))
        self.assertEqual(data["status"],"DRAFT_NONSHIPPING_NATIVE_MAP_SAVED_READBACK_PASS_PIE_GATED")
        self.assertEqual(data["camera_offset_cm"],[-380,650,260])
        self.assertEqual(data["camera_count"],2)
        self.assertEqual(data["camera_exposure_bias_ev"],-6.0)
        self.assertEqual(data["derives_from_review_head"],
                         "686935cb7c11960dab73ee5664d635eb6e19eb94")
        self.assertEqual(hashlib.sha256(stage.SOURCE_FILE.read_bytes()).hexdigest(),
                         data["original_source_sha256"])
        self.assertEqual(hashlib.sha256(stage.DEST_FILE.read_bytes()).hexdigest(),
                         data["current_review_map_sha256"])
        for claim in ("gpu_bokeh_quantitatively_established",
                      "verified_earned_story_pie_input","approved_assets",
                      "creator_visual_approved","merge_authorized"):
            self.assertFalse(data[claim],claim)

    def test_native_v2_readback_script_is_scoped_to_manifest(self):
        script=(HERE/"readback_vs02_optical_lookdev_v2.py").read_text(encoding="utf-8")
        for token in (
            "VS02OpticalLookdev.review.json",
            "current_review_map_sha256",
            "original_source_sha256",
            "TSTSSAtmosphereDirector",
            "camera_target_actor",
            "explicit_review_opt_in",
            "CameraFocusMethod.DISABLE",
            "camera_exposure_bias_ev",
            "map_write_performed",
            "physical_keyboard_tested",
        ):
            self.assertIn(token,script,token)
        self.assertNotIn("save_map(",script)
        self.assertNotIn("spawn_actor_from_class(",script)

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
        lookdev=json.loads(LOOKDEV.read_text(encoding="utf-8"))
        self.assertEqual(r["review_map_sha256"],lookdev["historical_review_map_sha256"])
        self.assertEqual(hashlib.sha256(stage.DEST_FILE.read_bytes()).hexdigest(),
                         lookdev["current_review_map_sha256"])

if __name__=="__main__":unittest.main()
