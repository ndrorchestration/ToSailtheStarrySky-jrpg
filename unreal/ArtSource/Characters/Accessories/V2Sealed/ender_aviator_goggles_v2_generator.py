"""TSTSS Ender — V2 sealed aviator goggles. Original, source-editable 3D asset.

Design convention: meters; +X right, +Y forward (lens direction), +Z up.
One glTF mesh, multiple material primitives. Static only. Noncanonical.
Requires numpy and trimesh. No external assets or paid services.
"""
from pathlib import Path
import numpy as np
import trimesh
import math, json, hashlib, struct, itertools
OUT = Path('/mnt/data')
G = OUT / 'Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL.glb'
REPORT = OUT / 'Ender_Goggles_V2_3D_Validation.json'
TAU = 2 * np.pi
mat = {'AgedBrass': {'color': [0.49, 0.295, 0.095, 1], 'metallic': 0.82, 'roughness': 0.34}, 'BrushedGold': {'color': [0.8, 0.54, 0.19, 1], 'metallic': 0.91, 'roughness': 0.24}, 'PatinatedBronze': {'color': [0.25, 0.28, 0.2, 1], 'metallic': 0.77, 'roughness': 0.54}, 'DarkLeather': {'color': [0.105, 0.067, 0.042, 1], 'metallic': 0.02, 'roughness': 0.88}, 'LeatherEdge': {'color': [0.24, 0.124, 0.061, 1], 'metallic': 0.01, 'roughness': 0.82}, 'ElastomerSeal': {'color': [0.063, 0.065, 0.055, 1], 'metallic': 0.03, 'roughness': 0.93}, 'EmeraldGlass': {'color': [0.034, 0.32, 0.27, 0.79], 'metallic': 0.13, 'roughness': 0.12, 'alpha': 'BLEND'}, 'TurquoiseAccent': {'color': [0.065, 0.48, 0.4, 1], 'metallic': 0.54, 'roughness': 0.31}, 'DarkIron': {'color': [0.13, 0.15, 0.15, 1], 'metallic': 0.82, 'roughness': 0.47}, 'WaxedFabric': {'color': [0.2, 0.145, 0.086, 1], 'metallic': 0.0, 'roughness': 0.92}, 'Stitching': {'color': [0.64, 0.44, 0.215, 1], 'metallic': 0.0, 'roughness': 0.92}, 'GlassHighlights': {'color': [0.22, 0.71, 0.62, 0.65], 'metallic': 0.05, 'roughness': 0.09, 'alpha': 'BLEND'}}
parts = {k: [] for k in mat}

def push(mesh, material):
    assert material in parts
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(type(mesh))
    assert mesh.vertices.shape[0] and mesh.faces.shape[0]
    parts[material].append(mesh)

def surf_revolve_y(cx, cz, profile, n=80):
    """Revolve (y,r) sequence about line parallel Y, stitch adjacent rings."""
    angles = np.linspace(0, TAU, n, endpoint=False)
    vertices = np.array([[cx + r * np.cos(a), y, cz + r * np.sin(a)] for y, r in profile for a in angles], dtype=np.float64)
    faces = []
    for j in range(len(profile) - 1):
        for i in range(n):
            k = (i + 1) % n
            faces.extend([[j * n + i, j * n + k, (j + 1) * n + i], [(j + 1) * n + i, j * n + k, (j + 1) * n + k]])
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

def torus_y(cx, cy, cz, major, minor, n=80, m=12):
    th = np.linspace(0, TAU, n, endpoint=False)
    ph = np.linspace(0, TAU, m, endpoint=False)
    vertices = []
    faces = []
    for a in th:
        for b in ph:
            rr = major + minor * np.cos(b)
            vertices.append([cx + rr * np.cos(a), cy + minor * np.sin(b), cz + rr * np.sin(a)])
    for i in range(n):
        for j in range(m):
            a = i * m + j
            b = (i + 1) % n * m + j
            c = i * m + (j + 1) % m
            d = (i + 1) % n * m + (j + 1) % m
            faces.extend([[a, b, c], [c, b, d]])
    return trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=False)

def tube_points(P, radius=0.0015, segments=10):
    """Create cylinder along endpoint displacement."""
    P = np.asarray(P, dtype=np.float64)
    if np.linalg.norm(P[-1] - P[0]) < 1e-08:
        return None
    direct = P[-1] - P[0]
    tr = trimesh.geometry.align_vectors([0, 0, 1], direct)
    tr[:3, 3] = (P[0] + P[-1]) / 2
    return trimesh.creation.cylinder(radius=radius, height=np.linalg.norm(direct), sections=segments, transform=tr)

def curve_path(points, radius, material, segments=12):
    for p, q in zip(points[:-1], points[1:]):
        geom = tube_points([p, q], radius=radius, segments=segments)
        if geom is not None:
            push(geom, material)

def sphere(at, r, material, sub=1):
    s = trimesh.creation.icosphere(subdivisions=sub, radius=r)
    s.apply_translation(at)
    push(s, material)

def ribbon_curve(points, width=0.024, thickness=0.003):
    """Extruded band along XY path with vertical width, closed manifold."""
    points = np.asarray(points, dtype=np.float64)
    n = len(points)
    vs = []
    for p in points:
        for zoff, depth in ((-width / 2, -thickness / 2), (width / 2, -thickness / 2), (-width / 2, thickness / 2), (width / 2, thickness / 2)):
            vs.append([p[0], p[1] + depth, p[2] + zoff])
    faces = []
    for i in range(n - 1):
        a = i * 4
        b = (i + 1) * 4
        for p, q, r, s in ((a, a + 1, b, b + 1), (a + 2, a + 3, b + 2, b + 3), (a, a + 2, b, b + 2), (a + 1, a + 3, b + 1, b + 3)):
            faces.extend([[p, r, q], [q, r, s]])
    faces.extend([[0, 1, 2], [1, 3, 2]])
    a = (n - 1) * 4
    faces.extend([[a, a + 2, a + 1], [a + 1, a + 2, a + 3]])
    return trimesh.Trimesh(vertices=np.asarray(vs), faces=faces, process=False)

def lens(cx, cz, outer_r=0.0295, n=80, steps=14):
    """Convex real 3D green lens as pair of thin surfaces (not a painted circle)."""
    v = []
    f = []
    for front in (True, False):
        for t in range(steps + 1):
            r = outer_r * (t + 1e-06) / steps
            y = 0.0416 + (0.0019 * (1 - (r / outer_r) ** 2) if front else -0.0009)
            for a in np.linspace(0, TAU, n, endpoint=False):
                v.append([cx + r * np.cos(a), y, cz + r * np.sin(a)])
    num = (steps + 1) * n
    for side in range(2):
        start = side * num
        for j in range(steps):
            for i in range(n):
                k = (i + 1) % n
                a = start + j * n + i
                b = start + j * n + k
                c = start + (j + 1) * n + i
                d = start + (j + 1) * n + k
                f.extend([[a, b, c], [b, d, c]] if side == 0 else [[a, c, b], [b, c, d]])
    for i in range(n):
        a = steps * n + i
        b = steps * n + (i + 1) % n
        c = num + steps * n + i
        d = num + steps * n + (i + 1) % n
        f.extend([[a, c, b], [b, c, d]])
    return trimesh.Trimesh(vertices=v, faces=f, process=False)

def arc(cx, cy, cz, r, theta0, theta1, radius, material, count=24):
    points = [[cx + r * np.cos(t), cy, cz + r * np.sin(t)] for t in np.linspace(theta0, theta1, count)]
    curve_path(points, radius, material, segments=10)
for side in (-1, 1):
    cx = side * 0.0405
    cz = 0.006
    outer = [(-0.023, 0.0325), (-0.019, 0.0354), (-0.011, 0.0385), (-0.004, 0.037), (0.01, 0.036), (0.028, 0.0357), (0.038, 0.0357), (0.045, 0.0358)]
    inner = [(0.045, 0.0293), (0.037, 0.029), (0.019, 0.0283), (-0.005, 0.0262), (-0.02, 0.0265), (-0.023, 0.029)]
    push(surf_revolve_y(cx, cz, outer + inner), 'AgedBrass')
    push(surf_revolve_y(cx, cz, [(-0.025, 0.033), (-0.018, 0.0367), (-0.009, 0.0383), (0.003, 0.0368), (0.003, 0.0348), (-0.012, 0.0355), (-0.021, 0.03)]), 'DarkLeather')
    push(surf_revolve_y(cx, cz, [(-0.022, 0.0322), (-0.022, 0.0288), (-0.024, 0.0283), (-0.026, 0.029), (-0.026, 0.032)]), 'ElastomerSeal')
    push(torus_y(cx, -0.024, cz, 0.0301, 0.0035), 'ElastomerSeal')
    push(torus_y(cx, -0.018, cz, 0.034, 0.0025), 'LeatherEdge')
    for y, r in [(-0.008, 0.0384), (0.009, 0.0367), (0.027, 0.0363), (0.037, 0.0358)]:
        push(torus_y(cx, y, cz, r, 0.0017), 'PatinatedBronze')
    push(torus_y(cx, 0.042, cz, 0.0337, 0.0036), 'BrushedGold')
    push(torus_y(cx, 0.046, cz, 0.0299, 0.00115), 'TurquoiseAccent')
    push(lens(cx, cz), 'EmeraldGlass')
    for a in np.linspace(0, TAU, 8, endpoint=False):
        u = cx + 0.0346 * np.cos(a)
        w = cz + 0.0346 * np.sin(a)
        sphere((u, 0.0468, w), 0.00145, 'BrushedGold', sub=1)
    for a in [0.3 * np.pi, 0.42 * np.pi, 0.54 * np.pi, 0.66 * np.pi]:
        point = np.array([cx + 0.0365 * np.cos(a), 0.008, cz + 0.0365 * np.sin(a)])
        push(trimesh.creation.box(extents=[0.0055, 0.015, 0.0018], transform=trimesh.transformations.translation_matrix(point)), 'DarkIron')
    ex = cx + side * 0.037
    points = [(ex, -0.014, cz - 0.018), (ex + side * 0.009, -0.013, cz - 0.017), (ex + side * 0.011, 0.018, cz - 0.016), (ex + side * 0.006, 0.023, cz - 0.003), (ex + side * 0.011, 0.014, cz + 0.019), (ex + side * 0.007, -0.011, cz + 0.019)]
    plate = trimesh.convex.convex_hull(np.array(points))
    push(plate, 'PatinatedBronze')
    for sign in (-1, 1):
        sphere((ex + side * 0.009, 0, cz + sign * 0.012), 0.002, 'BrushedGold', sub=1)
    push(trimesh.creation.box(extents=[0.017, 0.029, 0.029], transform=trimesh.transformations.translation_matrix([cx + side * 0.047, -0.024, cz])), 'LeatherEdge')
    for zoffset in (-0.009, 0.009):
        sphere([cx + side * 0.05, -0.014, cz + zoffset], 0.002, 'BrushedGold', sub=1)
for zoff, yval, rad in [(0.026, 0.017, 0.0034), (0.009, 0.005, 0.003)]:
    pp = []
    for t in np.linspace(0, 1, 19):
        x = (t - 0.5) * 0.038
        y = yval + 0.006 * np.sin(np.pi * t)
        z = zoff + 0.004 * np.sin(np.pi * t)
        pp.append([x, y, z])
    curve_path(pp, rad, 'AgedBrass')
for x in (-0.019, 0.019):
    sphere([x, 0.016, 0.027], 0.004, 'BrushedGold', sub=2)
push(trimesh.creation.box(extents=[0.013, 0.022, 0.014], transform=trimesh.transformations.translation_matrix([0, -0.015, -0.012])), 'DarkLeather')
a = 0.088
b = 0.109
arcangles = np.linspace(0, np.pi, 76)
strap_path = np.array([[a * np.cos(t), -0.032 - b * np.sin(t), -0.006] for t in arcangles])
push(ribbon_curve(strap_path, width=0.027, thickness=0.004), 'WaxedFabric')
for sign in (-1, 1):
    upper = np.array([[p[0], p[1] - 0.0017, p[2] + sign * 0.0113] for p in strap_path])
    curve_path(upper, 0.0008, 'Stitching', segments=7)
for side in (-1, 1):
    x = side * 0.087
    push(trimesh.creation.box(extents=[0.006, 0.013, 0.035], transform=trimesh.transformations.translation_matrix([x, -0.034, -0.006])), 'DarkLeather')
    push(trimesh.creation.box(extents=[0.006, 0.014, 0.034], transform=trimesh.transformations.translation_matrix([x, -0.048, -0.006])), 'AgedBrass')
    for zoff in (-0.012, 0.012):
        push(trimesh.creation.box(extents=[0.007, 0.017, 0.0022], transform=trimesh.transformations.translation_matrix([x, -0.051, -0.006 + zoff])), 'BrushedGold')
    sphere([x, -0.041, -0.006], 0.0033, 'DarkIron', sub=1)
for t in np.linspace(0.33, np.pi - 0.33, 18):
    x = a * np.cos(t)
    y = -0.032 - b * np.sin(t)
    curve_path([[x, y - 0.0023, -0.006 - 0.0095], [x, y - 0.0023, -0.006 + 0.0095]], 0.00052, 'Stitching', segments=6)
assert G.exists() is False, 'Refusing to replace existing prototype'
combined = []
stats = {}
for material, group in parts.items():
    if not group:
        continue
    mesh = trimesh.util.concatenate(group)
    if len(mesh.faces) == 0:
        continue
    combined.append((material, mesh))
    stats[material] = {'parts': len(group), 'vertices': len(mesh.vertices), 'triangles': len(mesh.faces)}
blob = bytearray()
accessors = []
views = []
primitives = []

def pad4(buf, byte=b'\x00'):
    while len(buf) % 4:
        buf.extend(byte)

def add_data(arr, target=None):
    pad4(blob)
    offset = len(blob)
    data = np.ascontiguousarray(arr).tobytes()
    blob.extend(data)
    obj = {'buffer': 0, 'byteOffset': offset, 'byteLength': len(data)}
    if target:
        obj['target'] = target
    views.append(obj)
    return len(views) - 1

def accessor(arr, typ, component_type, target):
    idx = add_data(arr, target)
    shape = np.asarray(arr)
    n = len(shape)
    ent = {'bufferView': idx, 'byteOffset': 0, 'componentType': component_type, 'count': n, 'type': typ}
    if typ == 'VEC3' and component_type == 5126:
        ent['min'] = np.min(shape, axis=0).astype(float).tolist()
        ent['max'] = np.max(shape, axis=0).astype(float).tolist()
    accessors.append(ent)
    return len(accessors) - 1
materials = []
for material, mesh in combined:
    m = mat[material]
    data = np.asarray(mesh.vertices, dtype=np.float32)
    norm = np.asarray(mesh.vertex_normals, dtype=np.float32)
    triangles = np.asarray(mesh.faces, dtype=np.uint32).flatten()
    aa = accessor(data, 'VEC3', 5126, 34962)
    bb = accessor(norm, 'VEC3', 5126, 34962)
    cc = accessor(triangles, 'SCALAR', 5125, 34963)
    matinfo = {'name': material, 'pbrMetallicRoughness': {'baseColorFactor': m['color'], 'metallicFactor': m['metallic'], 'roughnessFactor': m['roughness']}, 'doubleSided': True}
    if 'alpha' in m:
        matinfo['alphaMode'] = m['alpha']
    materials.append(matinfo)
    primitives.append({'attributes': {'POSITION': aa, 'NORMAL': bb}, 'indices': cc, 'material': len(materials) - 1, 'mode': 4})
doc = {'asset': {'version': '2.0', 'generator': 'TSTSS Ender sealed goggles V2, original source, NONCANONICAL'}, 'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0, 'name': 'Ender_Sealed_Aviator_Goggles_V2_Static'}], 'meshes': [{'name': 'Ender_Sealed_Aviator_Goggles_V2_Static', 'primitives': primitives}], 'materials': materials, 'bufferViews': views, 'accessors': accessors, 'buffers': [{'byteLength': len(blob)}], 'extras': {'review_only': True, 'approved_by_creator': False, 'rigged': False, 'fitted_to_metahuman_head': False, 'no_spectacle_temple_arms': True, 'wearing_strap_is_continuous': True, 'authoritative_face_unchanged': True}}
pad4(blob)
doc['buffers'][0]['byteLength'] = len(blob)
js = json.dumps(doc, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
js += b' ' * ((4 - len(js) % 4) % 4)
whole = 12 + 8 + len(js) + 8 + len(blob)
with G.open('wb') as f:
    f.write(struct.pack('<4sII', b'glTF', 2, whole))
    f.write(struct.pack('<I4s', len(js), b'JSON'))
    f.write(js)
    f.write(struct.pack('<I4s', len(blob), b'BIN\x00'))
    f.write(blob)
scene = trimesh.load(G, force='scene')
assert len(scene.geometry) >= 1, 'GLB not loadable'
meshes = scene.dump()
joined = trimesh.util.concatenate(meshes)
mins = np.asarray(joined.bounds[0])
maxs = np.asarray(joined.bounds[1])
dims = maxs - mins
assert 0.15 < dims[0] < 0.23 and 0.14 < dims[1] < 0.25 and (0.06 < dims[2] < 0.12), (dims, mins, maxs)
assert len(doc['meshes']) == 1 and len(primitives) >= 10
assert not doc.get('skins') and (not doc.get('animations'))
report = {'status': 'STATIC_3D_SEALED_GOGGLES_V2_SOURCE_VALIDATED_NONCANONICAL', 'glb': str(G), 'glb_sha256': hashlib.sha256(G.read_bytes()).hexdigest(), 'glb_bytes': G.stat().st_size, 'source_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'material_count': len(materials), 'material_names': [m['name'] for m in materials], 'material_primitives': len(primitives), 'triangle_count': int(sum((x['triangles'] for x in stats.values()))), 'vertices': int(sum((x['vertices'] for x in stats.values()))), 'bounds_min_m': mins.tolist(), 'bounds_max_m': maxs.tolist(), 'extents_cm': np.round(dims * 100, 3).tolist(), 'mesh_count': 1, 'rigged': False, 'metahuman_fitted': False, 'native_unreal_import_verified': False, 'native_unreal_render_verified': False, 'approved_as_canonical': False, 'design_differences_from_v1': ['deep enclosed 5+cm eyecup barrels', 'continuous wide rear elastic headband', 'padded face seals', 'opaque side wind guards', 'convex genuine lens surfaces', 'no spectacle temple arms'], 'components_by_material': stats}
REPORT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'components_by_material'}, indent=2))
