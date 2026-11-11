"""Fail-closed independent Ender focus review asset provenance checks."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase,main,mock
import verify_ender_resonator_focus_native as native

class FocusReadbackTests(TestCase):
    def test_canonical_committed_binary_and_audio_source_hashes(self):
        payload=native.verify_sources()
        self.assertEqual(len(payload["assets"]),4)
        self.assertEqual(len(payload["source_wav"]),2)
        self.assertFalse(payload["statuses"]["independent_editor_readback"])
        self.assertEqual(payload["other_magic_status"],"DesignOnly / Correspondence ON HOLD")

    def test_bad_project_path_denied(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError,"isolated review worktree"):
                native.verify_sources(project=Path(tmp)/"unreal")

    def test_mutated_manifest_blocks_readback(self):
        with TemporaryDirectory() as tmp:
            m=json.loads(native.MANIFEST.read_text(encoding="utf8"))
            m["assets"]["Audio/SFX_ResonantPulse.uasset"]="f"*64
            path=Path(tmp)/"manifest.json"
            path.write_text(json.dumps(m),encoding="utf8")
            with self.assertRaisesRegex(RuntimeError,"committed asset bytes mismatch"):
                native.verify_sources(manifest=path)

    def test_extra_executable_spell_fails_closed(self):
        with TemporaryDirectory() as tmp:
            m=json.loads(native.MANIFEST.read_text(encoding="utf8"))
            m["executable_spells"].append("Ender_CorrespondenceThread")
            path=Path(tmp)/"manifest.json"
            path.write_text(json.dumps(m),encoding="utf8")
            with self.assertRaisesRegex(RuntimeError,"authority manifest drift"):
                native.verify_sources(manifest=path)

    def test_invalid_head_and_changed_source_denied_before_engine(self):
        with mock.patch.dict(native.os.environ,{native.ENV:"0"*40},clear=False):
            with self.assertRaisesRegex(RuntimeError,"unchanged explicit HEAD"):
                native.verify_sources(require_exact_head=True)

    def test_exact_sha_validation(self):
        self.assertTrue(native.exact_sha("a"*40))
        self.assertFalse(native.exact_sha("x"*40))
        self.assertFalse(native.exact_sha("a"*39))

if __name__=="__main__":main()
