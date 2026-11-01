"""Reproducible, immutable Ender sculpt pilot tests. No Unreal required."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from build_ender_fidelity_v1 import build
from verify_ender_fidelity_v1 import check

ROOT=Path(__file__).resolve().parent
BASELINE_SHA="d516f68b49301cd04ae17c58eeeb2ca318b5f9b6a42f300be773fb62a7a3d6f2"
PILOT_SHA="3fc37924bb457dfe3b62877ca8709efb693a1c1c73251cf6f5dcfbe012babd38"

class EnderFidelityV1Tests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.output=Path(self.t.name)/"candidate"

    def test_current_platform_reproducibility_and_source_lock(self):
        receipt=build(self.output)
        self.assertEqual(len(receipt["source"]["sha256"]),64)
        self.assertTrue(receipt["source_baseline_untouched"])
        pinned=ROOT/"FidelityCandidates"/"EnderV1"
        original_receipt=__import__("json").loads((pinned/"receipt.json").read_text())
        self.assertEqual(original_receipt["source"]["sha256"],PILOT_SHA)
        self.assertEqual(hashlib.sha256((pinned/original_receipt["source"]["file"]).read_bytes()).hexdigest(),PILOT_SHA)
        self.assertEqual(receipt["source"]["mesh_parts"],original_receipt["source"]["mesh_parts"])
        self.assertIn("unresolved",receipt["hair_palette"])
        self.assertFalse(receipt["approved_original_art_replaced"])
        self.assertEqual(hashlib.sha256((ROOT/"Candidates"/"Ender.glb").read_bytes()).hexdigest(),BASELINE_SHA)
        self.assertEqual(receipt["height_order_canon"],"Reson > Aepex > Ender > Ionia > Lyra")

    def test_curved_geometry_and_detail_parts(self):
        receipt=build(self.output)
        proof=check(self.output/receipt["source"]["file"],receipt)
        self.assertEqual(proof["status"],"CURVED_NONCANONICAL_GLTF_GEOMETRY_PASS")
        self.assertGreater(proof["triangles"],17000)
        self.assertGreater(proof["named_parts"],120)

    def test_reject_overwrite(self):
        build(self.output)
        with self.assertRaises(FileExistsError):build(self.output)

    def test_source_tamper_fails(self):
        receipt=build(self.output)
        file=self.output/receipt["source"]["file"]
        raw=bytearray(file.read_bytes())
        raw[-8]^=0x01
        file.write_bytes(raw)
        with self.assertRaises(AssertionError):check(file,receipt)

    def test_deterministic_second_build(self):
        first=build(self.output)
        second=build(Path(self.t.name)/"other")
        self.assertEqual(first["source"]["sha256"],second["source"]["sha256"])

if __name__=="__main__":unittest.main()
