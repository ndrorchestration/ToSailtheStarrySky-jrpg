"""Engine-free contracts for the reversible, noncanonical V4 habitation milestone."""
import hashlib, json, struct, sys, unittest
from pathlib import Path

TOOLS=Path(__file__).resolve().parents[1]/"Tools"
sys.path.insert(0,str(TOOLS))
import build_aureate_v4_habitation_lookdev as h

class CoupledHabitationTests(unittest.TestCase):
    def test_provenance_and_player_gate(self):
        self.assertIn("NONCANONICAL",h.PROVENANCE)
        self.assertEqual(h.STATUS,"NONCANONICAL_REVIEW_NOT_ART_ACCEPTED")
        self.assertEqual(h.DOME_ORIGIN_CM,(170.0,0.0,133.0))
        self.assertEqual(h.PIVOT_ORIGIN_CM,(40.0,0.0,72.0))
        self.assertEqual(len(h.FILES),2)

    def test_geodesic_panels_and_curved_quarters_both_populated(self):
        d=h.bridge_dome()
        q=h.quarters_surfaces()
        for section in (*d,*q):
            self.assertGreaterEqual(len(section.indices),36)
            self.assertEqual(len(section.indices)%3,0)
            self.assertEqual(len(section.pos),len(section.normal))
        self.assertGreater(len(d[1].indices),len(d[0].indices))
        self.assertGreater(len(q[0].pos),200)

    def test_quarters_bounded_and_not_a_cube(self):
        q=h.quarters_surfaces()
        vertices=q[0].pos
        xs=[p[0] for p in vertices]
        self.assertLess(min(xs),-1.7)
        self.assertGreater(max(xs),2.4)
        self.assertGreater(len({round(p[1],3) for p in vertices}),25)
        self.assertGreater(len({round(p[2],3) for p in vertices}),15)

    def test_deterministic_two_glb_payloads(self):
        a=h.payloads()
        b=h.payloads()
        self.assertEqual(a,b)
        self.assertEqual(set(a),set(h.FILES))
        self.assertNotEqual(hashlib.sha256(a[h.FILES[0]]).digest(),
                            hashlib.sha256(a[h.FILES[1]]).digest())
        for name,payload in a.items():
            self.assertEqual(payload[:4],b"glTF")
            self.assertEqual(struct.unpack_from("<I",payload,4)[0],2)
            self.assertEqual(struct.unpack_from("<I",payload,8)[0],len(payload))
            json_length=struct.unpack_from("<I",payload,12)[0]
            self.assertEqual(payload[16:20],b"JSON")
            model=json.loads(payload[20:20+json_length])
            self.assertEqual(len(model["materials"]),3)
            self.assertEqual(len(model["meshes"]),1)
            self.assertEqual(len(model["meshes"][0]["primitives"]),3)
            self.assertEqual(model["extras"]["authority"],h.STATUS)
            self.assertEqual(model["extras"]["sourceToGltfScale"],.01)
            self.assertFalse(any(m["name"].endswith("_PRODUCTION") for m in model["materials"]))

    def test_native_import_and_stage_are_fail_closed(self):
        native=(TOOLS/"intake_aureate_v4_coupled_habitation_native.py").read_text()
        stage=(TOOLS/"stage_aureate_v4_coupled_habitation_native.py").read_text()
        for token in ("AUREATE_CINEMATIC_V4_REVIEW_ONLY","replace_existing", "RECEIPT.exists()"):
            self.assertIn(token,native)
        self.assertIn("False",native)
        for token in ("AureateV4_Skybourne_CoupledHabitation_20261104",
                      "not lib.does_asset_exist(MAP)",
                      "COUPLED_HABITATION_PIVOT_REVIEW",
                      "17.5",
                      "verify_sources()",
                      "get_attach_parent_actor()==pivot",
                      "levels.save_current_level()"):
            self.assertIn(token,stage)
        self.assertNotIn("save_game",stage.lower())
        self.assertNotIn("save_game",native.lower())

if __name__=="__main__":
    unittest.main()
