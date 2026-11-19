"""Decode actual exported binary geometry and hierarchy, independent of UE."""
import copy
import importlib.util
import math
from pathlib import Path
import struct
import sys
import unittest

SOURCE=Path(__file__).resolve().parents[1]/'ArtSource/ShipReview'
sys.path.insert(0,str(SOURCE))
import build_aureate_shared_hull_rig as rig


def positions(doc,binary,primitive):
    a=doc['accessors'][primitive['attributes']['POSITION']]
    v=doc['bufferViews'][a['bufferView']]
    start=v.get('byteOffset',0)+a.get('byteOffset',0)
    return [struct.unpack_from('<3f',binary,start+i*12) for i in range(a['count'])]


class SharedHullRigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.parts,cls.manifest=rig.build()

    def test_all_binary_vertices_indices_and_normals(self):
        for filename,data in self.parts.items():
            if not filename.endswith('.glb'): continue
            doc,binary=rig.unpack(data)
            for mesh in doc['meshes']:
                for p in mesh['primitives']:
                    vertices=positions(doc,binary,p)
                    self.assertTrue(vertices)
                    self.assertTrue(all(math.isfinite(x) for v in vertices for x in v))
                    a=doc['accessors'][p['indices']];v=doc['bufferViews'][a['bufferView']]
                    ids=struct.unpack_from('<'+'I'*a['count'],binary,v.get('byteOffset',0)+a.get('byteOffset',0))
                    self.assertEqual(len(ids)%3,0)
                    self.assertLess(max(ids),len(vertices))
                    for i in range(0,len(ids),3):
                        a,b,c=(vertices[j] for j in ids[i:i+3])
                        ab=[b[k]-a[k] for k in range(3)];ac=[c[k]-a[k] for k in range(3)]
                        area=(ab[1]*ac[2]-ab[2]*ac[1])**2+(ab[2]*ac[0]-ab[0]*ac[2])**2+(ab[0]*ac[1]-ab[1]*ac[0])**2
                        self.assertGreater(area,1e-20)

    def test_exact_four_wings_share_one_mesh_and_have_four_parents(self):
        doc,_=rig.unpack(self.parts['AureateWake_SharedHull_Seabourne_REVIEW.glb'])
        wings=[(i,n) for i,n in enumerate(doc['nodes']) if n['name'].startswith('DragonflyWing_')]
        self.assertEqual(len(wings),4)
        self.assertEqual(len({n['mesh'] for _,n in wings}),1)
        parents=[]
        for index,_ in wings:
            owner=[n['name'] for n in doc['nodes'] if index in n.get('children',[])]
            self.assertEqual(len(owner),1);parents+=owner
        self.assertEqual(set(parents),{'SailAzimuth_'+str(i) for i in range(1,5)})

    def test_trim_changes_only_one_azimuth_and_no_mesh_or_hull(self):
        original,_=rig.unpack(self.parts['AureateWake_SharedHull_Seabourne_REVIEW.glb'])
        for i in range(4):
            trim=[0.]*4;trim[i]=35.
            changed,_=rig.unpack(rig.assembly(self.parts,trim))
            self.assertEqual(original['meshes'],changed['meshes'])
            delta=[a['name'] for a,b in zip(original['nodes'],changed['nodes']) if a!=b]
            self.assertEqual(delta,['SailAzimuth_'+str(i+1)])

    def test_reject_invalid_trim(self):
        for trim in ((0,0,0),(0,0,0,36),(float('nan'),0,0,0),(0,0,float('inf'),0)):
            with self.assertRaises(ValueError): rig.assembly(self.parts,trim)

    def test_glb_units_and_hull_wing_span(self):
        for key,axis,low,high in [('hull',0,7.9,8.1),('wing',0,2.95,3.0),('mast',1,.81,.83)]:
            doc,binary=rig.unpack(self.parts[rig.FILES[key]])
            pts=[v for p in doc['meshes'][0]['primitives'] for v in positions(doc,binary,p)]
            span=max(v[axis] for v in pts)-min(v[axis] for v in pts)
            self.assertTrue(low<span<high,(key,span))

    def test_two_foils_and_bridge_are_attached_to_same_root(self):
        doc,_=rig.unpack(self.parts['AureateWake_SharedHull_Seabourne_REVIEW.glb'])
        root=doc['nodes'][0]
        direct=[doc['nodes'][i]['name'] for i in root['children']]
        self.assertIn('ForwardBridge_FIXED',direct)
        self.assertEqual(len([n for n in direct if n.startswith('Hydrofoil_')]),2)
        self.assertEqual(len(doc['meshes']),5)
        self.assertFalse(self.manifest['starbourne_unlocked'])


if __name__=='__main__': unittest.main()
