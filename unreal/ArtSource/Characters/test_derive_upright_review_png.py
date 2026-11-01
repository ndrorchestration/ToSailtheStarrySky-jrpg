"""Proof that review-image correction is exact and non-destructive."""
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from derive_upright_review_png import derive

class UprightReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.raw=self.root/"raw.png"
        self.out=self.root/"upright.png"
        im=Image.new("RGB",(500,400),(0,0,0))
        im.putpixel((8,10),(240,1,2))
        im.putpixel((490,388),(1,220,3))
        im.save(self.raw)

    def test_exact_rotated_pixels_and_raw_unchanged(self):
        original=self.raw.read_bytes()
        report=derive(self.raw,self.out)
        with Image.open(self.out) as im:
            self.assertEqual(im.getpixel((491,389))[:3],(240,1,2))
            self.assertEqual(im.getpixel((9,11))[:3],(1,220,3))
        self.assertEqual(original,self.raw.read_bytes())
        self.assertEqual(report["status"],"DERIVED_DISPLAY_ROTATED_180_NOT_ENGINE_CAPTURE")
        self.assertTrue(report["original_unmodified"])
        self.assertFalse(report["visual_quality_approved"])

    def test_no_overwrite(self):
        derive(self.raw,self.out)
        with self.assertRaises(FileExistsError):
            derive(self.raw,self.out)

    def test_same_path_rejected(self):
        with self.assertRaises(ValueError):
            derive(self.raw,self.raw)

    def test_non_png_rejected(self):
        self.raw.write_text("not an actual native PNG")
        with self.assertRaises(Exception):
            derive(self.raw,self.out)

if __name__=="__main__":unittest.main()
