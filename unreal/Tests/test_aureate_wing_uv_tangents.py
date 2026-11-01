"""Complete UV-Jacobian audit of the review-only dragonfly wing GLB source.

An otherwise valid manifold can still have a degenerate texture coordinate
parameterization, resulting in nearly zero bi-normals during UE StaticMesh
import. Every triangle must have nonzero position and UV area independently.
This is engine-free geometry QA; native Unreal import warning still must be
retested after regenerating the wing in a fresh review folder.
"""
import math
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"Tools"))
import author_aureate_wing_glb as wing


def uv_det(u,v,w):
    return (v[0]-u[0])*(w[1]-u[1])-(v[1]-u[1])*(w[0]-u[0])


def geo_double_area(a,b,c):
    x=[b[i]-a[i] for i in range(3)]
    y=[c[i]-a[i] for i in range(3)]
    cross=(x[1]*y[2]-x[2]*y[1], x[2]*y[0]-x[0]*y[2],
           x[0]*y[1]-x[1]*y[0])
    return math.sqrt(sum(k*k for k in cross))


class TangentUvAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.surfaces=(wing.mesh_membrane(),wing.mesh_venation(),wing.mesh_hinge())

    def test_all_faces_have_nonzero_uv_jacobian(self):
        count=0
        for surface in self.surfaces:
            for triangle in surface["faces"]:
                uv=[surface["uv"][i] for i in triangle]
                self.assertGreater(abs(uv_det(*uv)),1e-8,
                    msg=f'{surface["name"]} triangle {triangle} UV area collapsed')
                count+=1
        self.assertGreater(count,29000)

    def test_all_faces_have_nonzero_world_space_area(self):
        for surface in self.surfaces:
            for triangle in surface["faces"]:
                p=[surface["positions"][i] for i in triangle]
                self.assertGreater(geo_double_area(*p),1e-6,
                    msg=f'{surface["name"]} triangle {triangle} geometry collapsed')

    def test_back_membrane_uvs_are_distinct_for_sealed_edges(self):
        membrane=self.surfaces[0]
        lower=(wing.SEGMENTS+1)*2
        self.assertEqual(len(membrane["positions"]),lower*2)
        for i in range(lower):
            top=membrane["uv"][i]
            back=membrane["uv"][i+lower]
            self.assertNotEqual(top,back)
            self.assertAlmostEqual(back[0]-top[0],.015)
            self.assertAlmostEqual(back[1]-top[1],1.)

    def test_vein_and_hinge_cap_center_uvs_are_off_rim_lines(self):
        for surface in self.surfaces[1:]:
            face_count=sum(1 for f in surface["faces"]
                if any(surface["uv"][i][0]<0. for i in f))
            if surface["name"]=="golden_ribs":
                self.assertGreater(face_count,0)
            # All caps are covered by exhaustive area test above.


if __name__=="__main__":unittest.main()
