"""No network audio generation and fail-closed overwrite tests."""
import hashlib
from pathlib import Path
import tempfile
from unittest import TestCase,main
import wave
import build_tstss_jrpg_review_audio as audio

class SynthReviewAudioTests(TestCase):
    def test_four_distinct_deterministic_original_sounds(self):
        self.assertEqual(len(audio.NAMES),4)
        contents=[audio.build_pcm(n) for n in audio.NAMES]
        self.assertEqual(len({hashlib.sha256(x).hexdigest() for x in contents}),4)
        for name,data in zip(audio.NAMES,contents):
            self.assertEqual(len(data),round(audio.RATE*audio.SECONDS[name])*2)
            self.assertEqual(audio.build_pcm(name),data)

    def test_no_outside_review_dir(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(RuntimeError,"review namespace"):
                audio.generate(Path(d)/"AudioSource")

    def test_real_wav_writes_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            review=Path(d)/"Review"/"AudioSource"
            out=audio.generate(review)
            self.assertEqual(len(out["assets"]),4)
            for name in audio.NAMES:
                with wave.open(str(review/(name+".wav")),"rb") as wav:
                    self.assertEqual(wav.getframerate(),audio.RATE)
                    self.assertEqual(wav.getnchannels(),1)
                    self.assertEqual(wav.getsampwidth(),2)
            protected=(review/(audio.NAMES[0]+".wav")).read_bytes()
            with self.assertRaisesRegex(RuntimeError,"refuse audio source overwrite"):
                audio.generate(review)
            self.assertEqual((review/(audio.NAMES[0]+".wav")).read_bytes(),protected)

if __name__=="__main__":
    main()
