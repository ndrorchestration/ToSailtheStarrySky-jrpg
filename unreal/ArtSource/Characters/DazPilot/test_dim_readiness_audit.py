"""Engine-free Daz Install Manager fixture tests. No applications are launched."""
from pathlib import Path
import contextlib
import io
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dim_readiness_audit import inspect, main, sku_from_manifest, MAX_MANIFEST_BYTES

def manifest(product):
    return ('<DAZInstallManifest VERSION="0.1">'
            '<ProductStoreIDX VALUE="'+product+'-1"/>'
            '<UserInstallAccount VALUE="EXCLUDE_FROM_REPORT"/>'
            '</DAZInstallManifest>').encode("utf-8")

class DazReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir=Path(self.temp.name)/"ManifestFiles"
        self.dir.mkdir()
        (self.dir/"content.dsx").write_bytes(manifest("86958"))
        self.exe=Path(self.temp.name)/"DAZStudio.exe"

    def test_manifest_is_not_a_license(self):
        result=inspect(self.dir)
        self.assertTrue(result["products"]["86958"]["dim_installed_manifest_observed"])
        self.assertFalse(result["unreal_3d_asset_export_authorized"])
        self.assertFalse(result["interactive_license_verified"])
        self.assertNotIn("EXCLUDE_FROM_REPORT",json.dumps(result))

    def test_studio_executable_only_makes_daz_candidate(self):
        self.exe.write_bytes(b"fixture")
        r=inspect(self.dir,self.exe)
        self.assertEqual(r["daz_only_reference_preflight"],"CANDIDATE")
        self.assertFalse(r["daz_native_figure_load_verified"])
        self.assertFalse(r["ue58_bridge_compatibility_verified"])

    def test_bridge_presence_never_approves_unreal(self):
        (self.dir/"bridge.dsx").write_bytes(manifest("72003"))
        r=inspect(self.dir)
        self.assertTrue(r["products"]["72003"]["dim_installed_manifest_observed"])
        self.assertFalse(r["unreal_3d_asset_export_authorized"])

    def test_missing_directory_is_not_confirmed_installed(self):
        r=inspect(self.dir/"absent")
        self.assertEqual(r["manifest_directory"],"NOT_FOUND")
        self.assertFalse(r["products"]["86958"]["dim_installed_manifest_observed"])

    def test_corrupt_and_large_manifest_are_not_accepted(self):
        (self.dir/"bad.dsx").write_bytes(b"<incomplete>")
        (self.dir/"too_big.dsx").write_bytes(b"x"*(MAX_MANIFEST_BYTES+1))
        r=inspect(self.dir)
        self.assertEqual(r["malformed_manifest_count"],1)
        self.assertEqual(r["oversize_manifest_count"],1)

    def test_nonnative_manifest_does_not_count(self):
        self.assertIsNone(sku_from_manifest(b'<Other><ProductStoreIDX VALUE="86958"/></Other>'))
        self.assertEqual(sku_from_manifest(manifest("00086958")),"86958")

    def test_receipt_is_unique_and_non_overwriting(self):
        out=Path(self.temp.name)/"result.json"
        with contextlib.redirect_stdout(io.StringIO()):
            main(["--manifest-dir",str(self.dir),"--receipt",str(out)])
        before=out.read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(FileExistsError):
                main(["--manifest-dir",str(self.dir),"--receipt",str(out)])
        self.assertEqual(out.read_bytes(),before)

    def test_only_known_products_reported(self):
        (self.dir/"other.dsx").write_bytes(manifest("123456"))
        r=inspect(self.dir)
        self.assertEqual(set(r["products"]),{"86958","72003"})

if __name__=="__main__":
    unittest.main()
