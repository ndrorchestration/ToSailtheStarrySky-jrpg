"""Engine-free negative controls for original noncanonical Ender goggles GLB.

A structural test is portable across Python/platform math implementations.
Native Unreal import and material/shader fidelity are separate evidence gates.
"""
import json
import math
import struct
import tempfile
from pathlib import Path
import unittest

from tstss_ender_goggles_generator import encode

class TestDetachableEnderGoggles(unittest.TestCase):
    def test_goggles_are_real_3d_geometry_and_unapproved(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"goggles.glb"
            result=encode(path)
            raw=path.read_bytes()
            self.assertEqual(raw[:4],b"glTF")
            self.assertEqual(struct.unpack_from("<II",raw,4),(2,len(raw)))
            n,kind=struct.unpack_from("<I4s",raw,12)
            self.assertEqual(kind,b"JSON")
            self.assertEqual(n%4,0)
            doc=json.loads(raw[20:20+n])
            self.assertEqual(len(doc.get("meshes",[])),1)
            self.assertEqual(len(doc["meshes"][0]["primitives"]),9)
            self.assertEqual(len(doc["materials"]),9)
            self.assertEqual(len(doc["nodes"]),1)
            self.assertFalse(doc.get("skins"))
            self.assertFalse(doc.get("animations"))
            self.assertFalse(doc.get("images"))
            self.assertEqual(result["triangle_count"],15920)
            self.assertEqual(result["vertex_count"],8562)
            self.assertEqual(result["material_count"],9)
            self.assertGreater(result["byte_length"],400_000)
            self.assertLess(result["byte_length"],410_000)
            self.assertEqual(result["source_units"],"meters")
            self.assertFalse(result["canonical"])
            self.assertFalse(result["fitted_to_enders_face"])
            self.assertFalse(result["rigged"])
            self.assertFalse(result["native_unreal_import_verified"])
            self.assertFalse(result["shader_appearance_verified"])
            mins,maxs=result["bounds_min_m"],result["bounds_max_m"]
            extents=[hi-lo for lo,hi in zip(mins,maxs)]
            self.assertAlmostEqual(extents[0],0.182176814,places=5)
            self.assertAlmostEqual(extents[1],0.1535,places=5)
            self.assertAlmostEqual(extents[2],0.061,places=5)
            self.assertTrue(all(math.isfinite(x) for x in mins+maxs))
            self.assertTrue(any("glass" in material["name"].lower() and
                                material.get("alphaMode")=="BLEND"
                                for material in doc["materials"]))
            self.assertTrue((path.with_suffix(".json")).exists())
            # Only a single source run per process; never overwrite the candidate.
            with self.assertRaises((RuntimeError,FileExistsError)):
                encode(path)

if __name__=="__main__":unittest.main()
