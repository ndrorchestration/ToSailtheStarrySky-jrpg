"""Engine-free contract checks for the pending registered V4 GPU review trial."""
import ast
import hashlib
import importlib.util
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'Tools'
RUNNER = TOOLS / 'run_aureate_v4_registered_gpu_capture.py'
sys.path.insert(0, str(TOOLS))
from test_aureate_v4_png_pixel_integrity import synthetic_png


def load_runner():
    spec = importlib.util.spec_from_file_location('aureate_v4_registered_capture', RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class RegisteredGPUCaptureTests(unittest.TestCase):
    def setUp(self):
        self.runner = load_runner()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.png = Path(self.temp.name) / 'capture.png'
        raw = synthetic_png()
        self.png.write_bytes(raw)
        self.test_name = 'Editor.Python.AureateV4Gpu_a01.test_aureate_v4_skybourne_a01'
        self.report = {'succeeded': 1, 'failed': 0, 'notRun': 0,
                       'tests': [{'fullTestPath': self.test_name, 'state': 'Success'}]}
        self.native = {'state': 'NATIVE_D3D11_CAPTURE_ONE_FRAME_TASK_PASS_PIXEL_QA_PENDING',
                       'native_task_complete': True,
                       'source_map_sha_before': self.runner.MAP_SHA,
                       'source_map_sha_after': self.runner.MAP_SHA,
                       'png_sha256': hashlib.sha256(raw).hexdigest(),
                       'png_bytes': len(raw)}

    def verify(self):
        return self.runner.validate_native(self.report, self.native, self.png,
                                           self.test_name, self.runner.MAP_SHA)

    def test_pass_stays_pixel_qa_pending_and_not_art_acceptance(self):
        self.assertEqual(self.verify()['dimensions'], [1280, 720])
        self.assertIn('pixel_integrity', self.verify())
        self.assertFalse(self.verify()['pixel_integrity']['art_approved'])

    def test_missing_exact_registered_test_fails(self):
        self.report['tests'][0]['fullTestPath'] = 'Editor.Python.Different.Test'
        with self.assertRaises(ValueError):
            self.verify()

    def test_duplicated_reported_test_fails(self):
        self.report['tests'].append(dict(self.report['tests'][0]))
        with self.assertRaises(ValueError):
            self.verify()

    def test_missing_or_failed_test_fails(self):
        self.report['tests'][0]['state'] = 'Fail'
        with self.assertRaises(ValueError):
            self.verify()

    def test_native_receipt_pending_fails(self):
        self.native['state'] = 'NATIVE_CAPTURE_REQUESTED_NOT_YET_DONE'
        with self.assertRaises(ValueError):
            self.verify()

    def test_png_tampering_fails(self):
        self.png.write_bytes(self.png.read_bytes() + b'corrupted')
        with self.assertRaises(ValueError):
            self.verify()

    def test_map_hash_mismatch_fails(self):
        with self.assertRaises(ValueError):
            self.runner.validate_native(self.report, self.native, self.png,
                                        self.test_name, 'wrong-map-sha')

    def test_engine_free_source_contract(self):
        s = RUNNER.read_text(encoding='utf-8')
        ast.parse(s)
        capture = (TOOLS / 'capture_aureate_v4_skybourne_native_gpu.py').read_text(encoding='utf-8')
        ast.parse(capture)
        for term in ('PythonAutomationTest', 'Content/Python',
                     'Automation RunTests ', 'ReportExportPath=',
                     'free_ram() < 6.5', 'free_ram() < 1.5',
                     'ORIGINAL.read_text', "temporary_project.open('xb')",
                     "temporary_test.open('xb')", 'MAP_SHA',
                     'source_map_sha_postflight', 'validate_native('):
            self.assertIn(term, s)
        self.assertIn('TSTSS_V4_CAPTURE_ATTEMPT', capture)
        self.assertIn('NATIVE_D3D11_CAPTURE_ONE_FRAME_TASK_PASS_PIXEL_QA_PENDING', capture)
        self.assertNotIn('git push origin main', s)
        self.assertNotIn('SetPlayerStarbourneUnlocked', s)


if __name__ == '__main__':
    unittest.main()
