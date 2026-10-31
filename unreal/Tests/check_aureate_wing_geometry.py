#!/usr/bin/env python3
"""Read-only structural checks for generated wing files. Not an Unreal render test."""
import argparse
from pathlib import Path


def validate(folder: Path):
    obj = folder / "aureate_wing.obj"
    mtl = folder / "aureate_wing.mtl"
    assert obj.is_file() and mtl.is_file(), "OBJ/MTL missing"
    vertices, uvs, faces, materials = [], [], [], set()
    for line in obj.read_text(encoding="utf-8").splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == "v":
            vertices.append(tuple(map(float, p[1:4])))
        elif p[0] == "vt":
            uvs.append(tuple(map(float, p[1:3])))
        elif p[0] == "usemtl":
            materials.add(p[1])
        elif p[0] == "f":
            assert len(p) == 4, "Non-triangle face"
            faces.append(p[1:])
            for v in p[1:]:
                vertex, texcoord = (int(i) for i in v.split("/")[:2])
                assert 1 <= vertex <= len(vertices), "Invalid vertex reference"
                assert 1 <= texcoord <= len(uvs), "Invalid UV reference"
    assert len(vertices) > 5000 and len(faces) > 10000, "Insufficient detail"
    assert len(vertices) == len(uvs), "Missing UV coordinates"
    assert materials == {"membrane", "gold_spars", "gold_veins"}
    assert all(0 <= u <= 1 and 0 <= v <= 1 for u, v in uvs), "UV outside [0,1]"
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    assert -1 < min(xs) < 1 and 99 < max(xs) < 101, "Root to tip invalid"
    assert -24 < min(ys) < -18 and 18 < max(ys) < 24, "Wing width invalid"
    for name in ("aureate_wing_atmospheric_albedo.png", "aureate_wing_atmospheric_orm.png"):
        assert (folder / name).is_file(), f"Missing {name}"
    assert "map_Kd aureate_wing_atmospheric_albedo.png" in mtl.read_text()
    return len(vertices), len(faces)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("asset_folder", type=Path)
    args = parser.parse_args()
    vertex_count, triangle_count = validate(args.asset_folder)
    print(f"PASS: {vertex_count} vertices, {triangle_count} triangles, UV/material refs")
    print("Unreal import, compiled runtime and artistic acceptance remain NOT VERIFIED.")
