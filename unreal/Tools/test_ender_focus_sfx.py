"""Review-only original audio synthesis tests, no UE or network dependency."""
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase,main
import wave
import build_ender_focus_sfx as audio

class FocusSfxTests(TestCase):
    def test_exact_two_distinct_deterministic_voices(self):
        self.assertEqual(set(audio.DURATIONS),{"SFX_Centering","SFX_ResonantPulse"})
        a,b=(audio.samples(n) for n in audio.DURATIONS)
        self.assertEqual(a,audio.samples("SFX_Centering"))
        self.assertNotEqual(hashlib.sha256(a).digest(),hashlib.sha256(b).digest())

    def test_refuse_external_namespace(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError,"out-of-scope"):
                audio.generate(Path(tmp)/"AudioSource")

    def test_wav_header_and_one_use(self):
        with TemporaryDirectory() as tmp:
            dest=Path(tmp)/"Review"/"ResonatorFocus"/"AudioSource"
            result=audio.generate(dest)
            self.assertEqual(len(result["files"]),2)
            for name in audio.DURATIONS:
                with wave.open(str(dest/(name+".wav")),"rb") as w:
                    self.assertEqual(w.getnchannels(),1)
                    self.assertEqual(w.getsampwidth(),2)
                    self.assertEqual(w.getframerate(),24000)
            with self.assertRaisesRegex(RuntimeError,"overwrite"):
                audio.generate(dest)
if __name__=="__main__":main()
