"""Offline integrity and fail-closed generation for sky/sea review-only assets."""
import hashlib,io,json,struct,sys,tempfile,unittest
from pathlib import Path
from contextlib import redirect_stderr

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"Tools"))
import author_aureate_sky_sea_review as mod

def dimensions(blob):
    if blob[:8]!=b"\x89PNG\r\n\x1a\n":raise ValueError("not a PNG")
    return struct.unpack_from(">II",blob,16)

class SkySeaReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.assets,cls.manifest=mod.build()

    def test_exact_two_review_images_and_documented_sha256(self):
        self.assertEqual(set(self.assets),{mod.SKY,mod.SEA})
        self.assertEqual(self.manifest["status"],mod.STATUS)
        self.assertEqual(self.manifest["orbiter"],"LOCKED")
        self.assertTrue(self.manifest["no_existing_map_or_asset_overwrite"])
        for name,blob in self.assets.items():
            self.assertEqual(hashlib.sha256(blob).hexdigest(),self.manifest["sha256"][name])

    def test_png_signature_dimensions_and_nonempty_compressed_data(self):
        self.assertEqual(dimensions(self.assets[mod.SKY]),mod.SIZE)
        self.assertEqual(dimensions(self.assets[mod.SEA]),mod.SEA_SIZE)
        self.assertGreater(len(self.assets[mod.SKY]),2000)
        self.assertGreater(len(self.assets[mod.SEA]),2000)

    def test_sky_tone_and_ocean_oscillation_are_bounded(self):
        for x,y in ((0,0),(100,110),(300,135),(400,210)):
            self.assertEqual(mod.sky_pixel(x,y)[3],255)
            self.assertTrue(all(0<=c<=255 for c in mod.sky_pixel(x,y)))
        self.assertGreater(sum(mod.sky_pixel(350,120)[:3]),sum(mod.sky_pixel(350,0)[:3]))
        values={mod.ocean_pixel(i,30) for i in range(0,512,17)}
        self.assertGreater(len(values),8)

    def test_deterministic_regeneration(self):
        repeat,receipt=mod.build()
        self.assertEqual(self.assets,repeat)
        self.assertEqual(self.manifest,receipt)

    def test_reject_occupied_directory_without_clobbering(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"target";root.mkdir()
            (root/"existing.bin").write_bytes(b"preserve")
            with self.assertRaises(SystemExit):
                with redirect_stderr(io.StringIO()):
                    mod.main(["--output-dir",str(root)])
            self.assertEqual((root/"existing.bin").read_bytes(),b"preserve")
            self.assertEqual(len(list(root.iterdir())),1)

if __name__=="__main__":unittest.main()
