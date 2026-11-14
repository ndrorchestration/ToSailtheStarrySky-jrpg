"""Hilltonia harbor/town/forest source geometry, NOT a native Unreal walking test.

Samples a real round-trip plan every 20 cm with five capsule-footprint
probes; detects unsupported floor, solid props blocking the path, changed
source authority and disconnected land. Never mutates a map or save.
"""
from dataclasses import dataclass
import math
from pathlib import Path
import re
import unittest

CPP = (Path(__file__).resolve().parents[1] /
       'Source/ToSailTheStarrySky/Private/TSTSSHilltoniaReviewExtension.cpp').read_text(encoding='utf-8')
RADIUS = 35.0


@dataclass(frozen=True)
class Rect:
    lo_x: float
    hi_x: float
    lo_y: float
    hi_y: float
    label: str

    def contains(self, x, y):
        return self.lo_x <= x <= self.hi_x and self.lo_y <= y <= self.hi_y

    def distance(self, x, y):
        return math.hypot(max(self.lo_x - x, 0, x - self.hi_x),
                          max(self.lo_y - y, 0, y - self.hi_y))


def box(x, y, sx, sy, label):
    return Rect(x - 50 * sx, x + 50 * sx, y - 50 * sy, y + 50 * sy, label)


def require(source, tokens):
    for token in tokens:
        if token not in source:
            raise ValueError('Source authority/geometry drift: ' + token)


def plan(source):
    require(source, [
        'TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',
        'StartsWith(TEXT("/Game/TSTSS/Review/"))',
        'World->GetNetMode() != NM_Standalone',
        'bSolid ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision',
        'bSolid ? ECC_WorldStatic : ECC_WorldDynamic',
        'for (float X = RoadFirstX; X >= RoadLastX; X -= RoadStep)',
        'Place(Road, X, RoadCenterY, -30.f, 6.2f, 7.8f, .6f)',
        'for (int32 Step = 0; Step < 6; ++Step)',
        'Place(Road, -7350.f, -620.f - 500.f * Step, -30.f,',
        '3.6f, 5.2f, .6f)',
        'for (const float X : {-5050.f, -6250.f, -8500.f})',
        'for (const float Y : {-1090.f, 900.f})',
        'Place(Buildings, X, Y, 158.f, 7.0f, 5.4f, 3.16f)',
        'Place(Buildings, -7450.f, 1110.f, 190.f, 9.2f, 6.3f, 3.8f)',
        'Place(TreeTrunks, -4280.f, -600.f, 155.f, .55f, .55f, 3.1f)',
        'FMath::Abs(X + 7350.f) < 420.f',
        'Y < -1500.f && Y > -3400.f',
    ])
    def constant(name):
        match = re.search(r'constexpr float ' + name + r' = (-?\d+(?:\.\d*)?)f;', source)
        if not match:
            raise ValueError('Missing route constant: ' + name)
        return float(match.group(1))
    first, last, step, y = (constant(n) for n in (
        'RoadFirstX', 'RoadLastX', 'RoadStep', 'RoadCenterY'))
    if (first, last, step, y) != (-3650., -9050., 600., -150.):
        raise ValueError('Unreviewed route geometry')
    roads = [box(first - i * step, y, 6.2, 7.8, f'town-{i}') for i in range(10)]
    roads += [box(-7350., -620. - i * 500., 3.6, 5.2, f'wood-{i}') for i in range(6)]
    number = r'(-?\d+(?:\.\d*)?)f'
    pattern = r'Place\(Ground,\s*' + r',\s*'.join([number] * 6) + r'\)'
    raw = [tuple(map(float, values)) for values in re.findall(pattern, source)]
    if len(raw) != 2:
        raise ValueError('Expected precisely two ground placements')
    soil = []
    for i, (x, gy, gz, sx, sy, sz) in enumerate(raw):
        if not math.isclose(gz + 50 * sz, -10., abs_tol=0.001):
            raise ValueError('Ground top drift')
        soil.append(box(x, gy, sx, sy, f'soil-{i}'))
    solids = [box(x, by, 7., 5.4, 'house')
              for x in (-5050., -6250., -8500.) for by in (-1090., 900.)]
    solids += [box(-7450., 1110., 9.2, 6.3, 'hall'),
               box(-4280., -600., .55, .55, 'signpost')]
    for row in range(4):
        for col in range(8):
            x = -4950. - col * 640. + (-135. if row & 1 else 0.)
            ty = -1900. - row * 670. + (-95. if col & 1 else 0.)
            if abs(x + 7350.) < 420. and -3400. < ty < -1500.:
                continue
            solids.append(box(x, ty, .55, .55, 'tree'))
    return roads, soil, solids


def samples():
    # Pier -> town end -> forest -> pier, at <=20cm intervals.
    waypoints = [(-2780., 0.), (-3650., -150.), (-7350., -150.),
                 (-9050., -150.), (-7350., -150.), (-7350., -620.),
                 (-7350., -3120.), (-7350., -620.), (-7350., -150.),
                 (-3650., -150.), (-2780., 0.)]
    path = []
    for a, b in zip(waypoints, waypoints[1:]):
        length = math.dist(a, b)
        count = max(1, math.ceil(length / 20.))
        path += [(a[0] + (b[0] - a[0]) * i / count,
                  a[1] + (b[1] - a[1]) * i / count)
                 for i in range(count)]
    return path + [waypoints[-1]]


def check(roads, soil, solids):
    dock = Rect(-3750., 2550., -700., 700., 'existing-harbor')
    support = [dock, *roads]
    points = samples()
    for i, (x, y) in enumerate(points):
        for dx, dy in ((0, 0), (RADIUS, 0), (-RADIUS, 0),
                       (0, RADIUS), (0, -RADIUS)):
            if not any(r.contains(x + dx, y + dy) for r in support):
                raise ValueError(f'Unsupported capsule footprint at {i}: {x:.1f}, {y:.1f}')
        if any(r.distance(x, y) <= RADIUS for r in solids):
            raise ValueError(f'Collidable obstacle intersects path at {i}')
        if x <= -3750. and not any(r.contains(x, y) for r in soil):
            raise ValueError(f'No dry land beneath town/forest at {i}')
    if len(roads) != 16 or len(soil) != 2:
        raise ValueError('Unexpected scene inventory')
    a, b = soil
    if min(a.hi_y, b.hi_y) - max(a.lo_y, b.lo_y) < 200.:
        raise ValueError('Disconnected town and woodland ground')
    return len(points)


class HilltoniaSourceRouteTests(unittest.TestCase):
    def test_harbor_town_forest_and_return(self):
        count = check(*plan(CPP))
        self.assertGreater(count, 900)

    def test_missing_town_road_section_rejected(self):
        roads, soil, solids = plan(CPP)
        with self.assertRaisesRegex(ValueError, 'Unsupported capsule'):
            check([r for r in roads if r.label != 'town-4'], soil, solids)

    def test_missing_forest_lane_section_rejected(self):
        roads, soil, solids = plan(CPP)
        with self.assertRaisesRegex(ValueError, 'Unsupported capsule'):
            check([r for r in roads if r.label != 'wood-3'], soil, solids)

    def test_obstructing_prop_rejected(self):
        roads, soil, solids = plan(CPP)
        with self.assertRaisesRegex(ValueError, 'Collidable obstacle'):
            check(roads, soil, solids + [box(-7350., -2400., 1., 1., 'test-obstruction')])

    def test_missing_town_ground_rejected(self):
        roads, soil, solids = plan(CPP)
        with self.assertRaisesRegex(ValueError, 'No dry land'):
            check(roads, [soil[-1], soil[-1]], solids)

    def test_wrong_ground_height_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Ground top drift'):
            plan(CPP.replace('70.f, 58.f, 1.6f)', '70.f, 58.f, 2.6f)'))

    def test_removed_review_authority_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Source authority'):
            plan(CPP.replace('World->GetNetMode() != NM_Standalone',
                             'World->GetNetMode() != NM_Client'))


if __name__ == '__main__':
    unittest.main()
