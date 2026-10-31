#!/usr/bin/env python3
"""Generate ORIGINAL Aureate Wake dragonfly-wing asset (OBJ, MTL, PBR maps).

Noncanonical art prototype; no engine install, payment or source art required.
Coordinate contract: X-forward root (0,0,0) to +X tip (~100,0), Y is width;
Z curves upward. Dimensions in centimeters, for Unreal.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

SPAN_CM = 100.0
NX, NY = 64, 20
THICKNESS_CM = 0.32


def half_width(t: float) -> float:
    if t <= 0.0:
        return 4.25
    return 0.55 + 25.0 * math.pow(math.sin(math.pi * t), 1.08) * (0.72 + 0.28 * t)


def camber(t: float, v: float) -> float:
    return (1.45 * math.sin(math.pi * t) * (1.0 - v * v)
            + 0.65 * math.sin(3.0 * math.pi * t) * (1.0 - abs(v)))


def surface(t: float, v: float, underside: bool = False):
    width = half_width(t)
    return (SPAN_CM * t, width * v + 0.075 * width * (1.0 - v * v),
            camber(t, v) - (THICKNESS_CM if underside else 0.0))


class OBJ:
    def __init__(self):
        self.v, self.vt, self.lines = [], [], []
        self.faces = 0

    def vertex(self, point, uv):
        self.v.append(tuple(point))
        self.vt.append(tuple(uv))
        return len(self.v)

    def triangle(self, a: int, b: int, c: int):
        self.lines.append(f'f {a}/{a} {b}/{b} {c}/{c}')
        self.faces += 1

    def quad(self, a, b, c, d):
        self.triangle(a, b, c)
        self.triangle(a, c, d)

    def tube(self, name, points, radius, material, sides=8):
        """Add closed real 3D tubes; modeled veins, not texture decals."""
        self.lines += [f'o {name}', f'usemtl {material}']
        rings = []
        for i, point in enumerate(points):
            prev, nxt = points[max(0, i - 1)], points[min(len(points) - 1, i + 1)]
            tangent = tuple(nxt[j] - prev[j] for j in range(3))
            norm = math.hypot(*tangent)
            if norm < 1e-5:
                raise ValueError('Degenerate rib path')
            tangent = tuple(x / norm for x in tangent)
            u = (-tangent[1], tangent[0], 0)
            ul = math.hypot(*u)
            u = tuple(x / max(ul, 1e-5) for x in u)
            w = (tangent[1] * u[2] - tangent[2] * u[1],
                 tangent[2] * u[0] - tangent[0] * u[2],
                 tangent[0] * u[1] - tangent[1] * u[0])
            ring = []
            for side in range(sides):
                theta = side * 2.0 * math.pi / sides
                p = tuple(point[j] + radius * (
                    math.cos(theta) * u[j] + math.sin(theta) * w[j]
                ) for j in range(3))
                ring.append(self.vertex(p, (i / max(1, len(points) - 1), side / sides)))
            rings.append(ring)
        for a, b in zip(rings, rings[1:]):
            for k in range(sides):
                self.quad(a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k])
        for ring, reverse in ((rings[0], True), (rings[-1], False)):
            midpoint = tuple(sum(self.v[p - 1][j] for p in ring) / sides for j in range(3))
            center = self.vertex(midpoint, (0.5, 0.5))
            for k in range(sides):
                p, q = ring[k], ring[(k + 1) % sides]
                if reverse:
                    self.triangle(center, q, p)
                else:
                    self.triangle(center, p, q)

    def export(self, path: Path):
        with path.open('w', encoding='utf-8', newline='\n') as stream:
            stream.write('# Original dragonfly wing visual study; not canonical\n')
            stream.write('# UE cm: rooted at local (0,0,0), tip +X, membrane +/-Y\n')
            stream.write('mtllib aureate_wing.mtl\ns 1\n')
            for v in self.v:
                stream.write('v {:.6f} {:.6f} {:.6f}\n'.format(*v))
            for uv in self.vt:
                stream.write('vt {:.6f} {:.6f}\n'.format(*uv))
            for line in self.lines:
                stream.write(line + '\n')


def build_mesh(path: Path):
    obj = OBJ()
    obj.lines += ['o WingMembrane', 'usemtl membrane']
    grids = []
    for underside in (False, True):
        grid = []
        for i in range(NX + 1):
            t = i / NX
            row = []
            for j in range(NY + 1):
                v = -1.0 + 2 * j / NY
                row.append(obj.vertex(surface(t, v, underside), (t, j / NY)))
            grid.append(row)
        grids.append(grid)
        for i in range(NX):
            for j in range(NY):
                a, b, c, d = grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]
                if underside:
                    obj.quad(a, d, c, b)
                else:
                    obj.quad(a, b, c, d)

    top, bottom = grids
    obj.lines += ['o MembraneRim', 'usemtl membrane']
    for i in range(NX):
        for j in (0, NY):
            if j == 0:
                obj.quad(top[i][j], bottom[i][j], bottom[i + 1][j], top[i + 1][j])
            else:
                obj.quad(top[i][j], top[i + 1][j], bottom[i + 1][j], bottom[i][j])
    for j in range(NY):
        for i in (0, NX):
            if i == 0:
                obj.quad(top[i][j], top[i][j + 1], bottom[i][j + 1], bottom[i][j])
            else:
                obj.quad(top[i][j], bottom[i][j], bottom[i][j + 1], top[i][j + 1])

    obj.tube('CentralGoldSpar',
             [tuple(v + (0.56 if k == 2 else 0.0)
                    for k, v in enumerate(surface(i / 90, 0.0))) for i in range(91)],
             0.83, 'gold_spars')
    for j, t in enumerate((0.11, 0.2, 0.29, 0.38, 0.47, 0.56, 0.65, 0.74, 0.83)):
        for side in (-1, 1):
            points = []
            for k in range(18):
                a = k / 17
                v = side * (0.08 + 0.86 * a)
                tt = min(0.987, t + 0.025 * a * a + (0.009 if side > 0 else 0))
                x, y, z = surface(tt, v)
                points.append((x, y, z + 0.45))
            obj.tube(f'Vein_{j + 1}_{"R" if side > 0 else "L"}',
                     points, 0.28 + (1 - t) * 0.11, 'gold_veins', 6)
    for side in (-1, 1):
        points = []
        for i in range(1, 96):
            t = i / 96
            x, y, z = surface(t, side * 0.98)
            points.append((x, y, z + 0.30))
        obj.tube(f'EdgeRim_{"R" if side > 0 else "L"}',
                 points, 0.24, 'gold_veins', 6)
    obj.export(path)
    return len(obj.v), obj.faces


def generate_maps(out: Path, resolution: int):
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError('Pillow required: pip install Pillow') from exc
    albedo, orm = Image.new('RGB', (resolution, resolution)), Image.new('RGB', (resolution, resolution))
    a, o = albedo.load(), orm.load()
    # RGB ORM: ambient occlusion (R), roughness (G), metallic (B).
    # Original blue/teal pearlescent pattern; NOT a UE iridescence shader.
    for iy in range(resolution):
        v = iy / (resolution - 1)
        for ix in range(resolution):
            u = ix / (resolution - 1)
            stripes = 0.5 + 0.5 * math.sin(2 * math.pi * (7 * u + 0.9 * math.sin(10 * v)))
            hexveil = (0.5 + 0.5 * math.cos(2 * math.pi * (16 * u + 5 * v))) ** 12
            gloss = 0.25 + 0.25 * math.sin(4 * math.pi * v + 12 * u)
            a[ix, iy] = (
                int(max(0, min(255, 24 + 52 * stripes + 26 * gloss))),
                int(max(0, min(255, 94 + 65 * stripes + 22 * hexveil))),
                int(max(0, min(255, 125 + 65 * (1 - stripes) + 16 * hexveil))))
            o[ix, iy] = (255, int(70 + 62 * gloss), int(26 + 34 * stripes))
    albedo.save(out / 'aureate_wing_atmospheric_albedo.png', optimize=True)
    orm.save(out / 'aureate_wing_atmospheric_orm.png', optimize=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, default=Path('aureate_wing_generated'))
    ap.add_argument('--resolution', type=int, default=1024, choices=[256, 512, 1024, 2048])
    args = ap.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    vertices, faces = build_mesh(out / 'aureate_wing.obj')
    (out / 'aureate_wing.mtl').write_text('''# MTL for OBJ preview; author actual UE master material separately.
newmtl membrane
Kd 0.30 0.70 0.81
Ks 0.25 0.40 0.49
Ns 250
illum 2
map_Kd aureate_wing_atmospheric_albedo.png

newmtl gold_spars
Kd 0.76 0.54 0.18
Ks 0.9 0.8 0.45
Ns 500
illum 2

newmtl gold_veins
Kd 0.62 0.47 0.25
Ks 0.65 0.6 0.48
Ns 300
illum 2
''', encoding='utf-8')
    generate_maps(out, args.resolution)
    (out / 'README.txt').write_text('''Aureate Wake procedural wing prototype (noncanonical).
Import aureate_wing.obj in Unreal as static mesh. Keep centimeters and root pivot.
Use atmospheric_albedo for membrane BaseColor; ORM G roughness, B metallic.
Author Unreal iridescent shader and OrbiterSailBlend separately.
All four wing components share this physical mesh; no extra spacecraft.
No UE native compilation/render or creator art approval is implied.
''', encoding='utf-8')
    print(f'Wrote {out} with {vertices} vertices, {faces} triangles and {args.resolution}px maps')


if __name__ == '__main__':
    main()
