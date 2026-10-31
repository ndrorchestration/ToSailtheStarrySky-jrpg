#!/usr/bin/env python3
"""Deterministic UV-mapped manifold dragonfly wing, centimeters; +X root to tip."""
from pathlib import Path
from collections import Counter
import argparse, math

def build_wing(segments=40, span=280., width=105.):
    if segments < 8 or span <= 0 or width <= 0:
        raise ValueError("invalid wing dimensions")
    vertices, uv, faces = [], [], []
    for sign in (1, -1):
        for i in range(segments + 1):
            t = i / segments
            half = width * .5 * max(.025, math.sin(math.pi*t)**.8) * (.78 + .22*t)
            for edge in (-1, 1):
                vertices.append((span*t, 12*math.sin(math.pi*t)+edge*half,
                                 sign*(.8+2.8*math.sin(math.pi*t))))
                uv.append((t,(edge+1)*.5))
    n = (segments+1)*2
    for i in range(segments):
        a=2*i; b=a+1; c=a+2; d=a+3
        faces.extend(((a,c,d),(a,d,b),(a+n,b+n,d+n),(a+n,d+n,c+n)))
        for edge in (0,1):
            x=2*i+edge; y=2*(i+1)+edge
            if edge == 0: faces.extend(((x,x+n,y+n),(x,y+n,y)))
            else: faces.extend(((x,y+n,x+n),(x,y,y+n)))
    for a,b in ((0,1),(2*segments,2*segments+1)):
        faces.extend(((a,b,b+n),(a,b+n,a+n)))
    return vertices,uv,faces

def validate(vertices,uv,faces):
    assert len(vertices)==len(uv)
    assert all(0<=u<=1 and 0<=v<=1 for u,v in uv)
    assert all(len(set(f))==3 for f in faces)
    edge_counts=Counter(tuple(sorted((a,b))) for f in faces
                        for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])))
    assert all(count==2 for count in edge_counts.values())
    return len(edge_counts)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=Path("AureateWake_DragonflyWing_Prototype.obj"))
    parser.add_argument("--segments",type=int,default=40)
    args=parser.parse_args()
    verts,uv,faces=build_wing(args.segments)
    edges=validate(verts,uv,faces)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",encoding="utf-8") as f:
        f.write("# Unreal reference geometry in centimeters; UV0, no vein geometry\n")
        f.write("mtllib AureateWake_Wing.mtl\no DragonflyWingPrototype\n")
        for x,y,z in verts: f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
        for u,v in uv: f.write(f"vt {u:.6f} {v:.6f}\n")
        f.write("usemtl MembranePrototype\n")
        for a,b,c in faces:
            f.write(f"f {a+1}/{a+1} {b+1}/{b+1} {c+1}/{c+1}\n")
    (args.output.parent/"AureateWake_Wing.mtl").write_text(
        "newmtl MembranePrototype\nKd 0.22 0.65 0.73\nKs 0.65 0.72 0.78\nNs 90\nd 0.85\n",
        encoding="utf-8")
    print(f"PASS {len(verts)} vertices, {len(faces)} triangles, {edges} manifold edges, UV0")

if __name__=="__main__": main()
