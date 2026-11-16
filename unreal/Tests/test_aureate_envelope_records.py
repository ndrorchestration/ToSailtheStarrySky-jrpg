"""Behavioral contract for native snapshot -> verifier conversion."""
import copy, math, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"Tools"))
import aureate_envelope_records as conv

ROLES=("hull","bridge","quarters","deck")
WINGS=("FORE_PORT","FORE_STARBOARD","AFT_PORT","AFT_STARBOARD")
LABELS={x:"actor_"+x for x in ROLES+WINGS}
def snapshot():
    return {"schema":"aureate_envelope_snapshot_v1","units":"cm","frame":"review_ship_frame_1",
      "map_package":"/Game/Test/Map","map_sha256":"a"*64,"actors":[
       {"label":LABELS[x],"mesh":"/Game/mesh_"+x,"bounds_min":[-1,-2,-3],"bounds_max":[3,4,5],
        "position":[n*100,0,0],"rotation_xyzw":[0,0,0,1],"scale":[1,1,1]}
       for n,x in enumerate(ROLES+WINGS)]}
class ConverterTests(unittest.TestCase):
    def setUp(self): self.a=snapshot(); self.b=copy.deepcopy(self.a)
    def test_translates_native_records_into_verifier_schema(self):
        r=conv.build_config(self.a,self.b,LABELS,LABELS,clearance=5)
        self.assertEqual(r["units"],"cm")
        self.assertEqual({v["role"] for v in r["obstacles"]},set(ROLES))
        self.assertEqual({v["identity"] for v in r["wings"]},set(WINGS))
        self.assertEqual(r["wings"][0]["parts"][0]["center"],[1,1,1])
        self.assertEqual(r["wings"][0]["parts"][0]["half_extents"],[2,3,4])
    def test_scaled_rotated_obstacle_applies_local_center(self):
        a=self.a["actors"][0]; a["position"]=[10,20,30]; a["scale"]=[2,3,4]
        a["rotation_xyzw"]=[0,0,math.sqrt(.5),math.sqrt(.5)]
        self.b=copy.deepcopy(self.a)
        r=conv.build_config(self.a,self.b,LABELS,LABELS,clearance=0)
        p=r["obstacles"][0]["parts"][0]
        for actual,expected in zip(p["center"],[7,22,34]): self.assertAlmostEqual(actual,expected)
        self.assertEqual(p["half_extents"],[4,9,16])
        for actual,expected in zip(p["rotation_quat"],[math.sqrt(.5),0,0,math.sqrt(.5)]): self.assertAlmostEqual(actual,expected)
    def test_wing_endpoints_keep_native_pose_and_scale(self):
        i=4; self.b["actors"][i]["position"]=[1000,20,30]; self.b["actors"][i]["scale"]=[2,3,4]
        r=conv.build_config(self.a,self.b,LABELS,LABELS,clearance=1)
        w=r["wings"][0]
        self.assertEqual(w["pose_to"]["position"],[1000,20,30])
        self.assertEqual(w["pose_to"]["scale"],[2,3,4])
        self.assertEqual(w["pose_to"]["rotation_quat"],[1,0,0,0])
    def test_refuses_moving_obstacles(self):
        self.b["actors"][0]["position"][0]=1
        with self.assertRaisesRegex(ValueError,"obstacle"): conv.build_config(self.a,self.b,LABELS,LABELS,clearance=0)
    def test_refuses_duplicate_labels(self):
        self.a["actors"].append(copy.deepcopy(self.a["actors"][0]))
        with self.assertRaisesRegex(ValueError,"duplicate"): conv.build_config(self.a,self.b,LABELS,LABELS,clearance=0)
    def test_refuses_mismatched_geometry(self):
        self.b["actors"][4]["bounds_max"][0]=4
        with self.assertRaisesRegex(ValueError,"geometry"): conv.build_config(self.a,self.b,LABELS,LABELS,clearance=0)
    def test_rejects_unknown_frame(self):
        self.b["frame"]="another"
        with self.assertRaisesRegex(ValueError,"frame"): conv.build_config(self.a,self.b,LABELS,LABELS,clearance=0)
    def test_rejects_nonfinite_and_invalid_scale(self):
        for bad in (0,-1,float("nan"),float("inf")):
            with self.subTest(bad=bad):
                a=copy.deepcopy(self.a); a["actors"][4]["scale"][0]=bad
                with self.assertRaises(ValueError): conv.build_config(a,self.b,LABELS,LABELS,clearance=0)
    def test_missing_or_duplicated_mapping_fails_closed(self):
        m=dict(LABELS); m["deck"]=m["hull"]
        with self.assertRaises(ValueError): conv.build_config(self.a,self.b,m,LABELS,clearance=0)
    def test_verifier_accepts_config_and_checks_all_pairs(self):
        import importlib.util
        p=Path(__file__).resolve().parents[1]/"ArtSource"/"ShipReview"/"aureate_swept_clearance.py"
        sp=importlib.util.spec_from_file_location("verifier",p); mod=importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
        result=mod.verify(conv.build_config(self.a,self.b,LABELS,LABELS,clearance=0))
        self.assertNotEqual(result["verdict"],mod.V_INVALID)
        self.assertEqual(len(result["pairs"]),22)
if __name__=="__main__": unittest.main()
