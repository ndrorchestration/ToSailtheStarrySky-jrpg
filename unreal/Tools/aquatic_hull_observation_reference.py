"""AQ-02 synthetic hull point aggregation; never flotation or story authority.

This is a conservative reference, not a hydrodynamic solver. Each probe has
one explicit snapshot location and zero or one candidate water column. Multiple
candidates (even identical ones) are ambiguous until a native resolver exists.
"""
from dataclasses import dataclass, replace
import unittest
from aquatic_query_reference import (
    Column, Context, Sample, cm_to_m, finite_number, sample, valid_context, valid_id,
)


@dataclass(frozen=True)
class Probe:
    expected: Context
    z_cm: float
    candidates: tuple[Column, ...]


@dataclass(frozen=True)
class Observation:
    state: str
    body: str | None = None
    samples: tuple[Sample, ...] = ()
    wet_points: int | None = None
    point_count: int | None = None


def observe_hull(body: str, probes: tuple[Probe, ...]) -> Observation:
    """Aggregate a bounded set of points; do not infer volume or contact force.

    Two to 64 probes are an experimental reference bound, not a ship design.
    A missing provider is unknown; malformed or mixed snapshots are invalid;
    multiple providers are ambiguous. Any such result carries no geometry.
    """
    if not valid_id(body) or type(probes) is not tuple or not 2 <= len(probes) <= 64:
        return Observation('invalid')
    contexts = []
    for probe in probes:
        if (type(probe) is not Probe or not valid_context(probe.expected)
                or probe.expected.body != body or not finite_number(probe.z_cm)
                or type(probe.candidates) is not tuple):
            return Observation('invalid')
        contexts.append(probe.expected)
    first = contexts[0]
    if (len({c.location for c in contexts}) != len(contexts)
            or any((c.datum, c.frame, c.epoch, c.revision, c.time_s) !=
                   (first.datum, first.frame, first.epoch, first.revision, first.time_s)
                   for c in contexts)):
        return Observation('invalid')
    if any(len(p.candidates) > 1 for p in probes):
        return Observation('ambiguous')
    # Evaluate every supplied candidate before classifying missing providers.
    rows = tuple(sample(p.candidates[0] if p.candidates else None,
                        cm_to_m(p.z_cm), p.expected) for p in probes)
    if any(s.state in ('invalid', 'below_bed') for s in rows):
        return Observation('invalid')
    if any(s.state == 'unknown' for s in rows):
        return Observation('unknown')
    wet = sum(s.state == 'submerged' for s in rows)
    state = 'wet_points' if wet else 'surface_points' if any(
        s.state == 'surface' for s in rows) else 'no_wet_points'
    return Observation(state, body, rows, wet, len(rows))


class HullTests(unittest.TestCase):
    def setUp(self):
        self.a = Context('ocean', 'datum', 'world', 'bow', 'epoch', 'v2', 1)
        self.b = replace(self.a, location='stern')

    def p(self, ctx, z=-100, surface=0, bed=-10, dry=False):
        return Probe(ctx, z, (Column(ctx, surface, bed, (0, 0, 0), dry),))

    def q(self, a=None, b=None):
        return observe_hull('ocean', (a if a is not None else self.p(self.a),
                                      b if b is not None else self.p(self.b)))

    def test_wet(self):
        r = self.q()
        self.assertEqual((r.state, r.wet_points, r.point_count), ('wet_points', 2, 2))
        self.assertEqual(r.samples[0].immersion_m, 1)

    def test_mixed(self):
        r = self.q(b=self.p(self.b, 100))
        self.assertEqual((r.state, r.wet_points), ('wet_points', 1))

    def test_surface(self):
        self.assertEqual(self.q(self.p(self.a, 0), self.p(self.b, 100)).state, 'surface_points')

    def test_above(self):
        self.assertEqual(self.q(self.p(self.a, 100), self.p(self.b, 100)).state, 'no_wet_points')

    def test_dry(self):
        self.assertEqual(self.q(self.p(self.a, 0, -1, 0, True), self.p(self.b, 100)).state, 'no_wet_points')

    def test_bed_penetration(self):
        self.assertEqual(self.q(b=self.p(self.b, -1100)), Observation('invalid'))

    def test_missing(self):
        self.assertEqual(self.q(b=Probe(self.b, -100, ())), Observation('unknown'))

    def test_wrong_body(self):
        lake = replace(self.b, body='lake')
        self.assertEqual(self.q(b=self.p(lake)), Observation('invalid'))
        self.assertEqual(self.q(b=Probe(self.b, -100, self.p(lake).candidates)), Observation('invalid'))

    def test_overlapping_bodies(self):
        lake = replace(self.b, body='lake')
        b = Probe(self.b, -100, self.p(self.b).candidates + self.p(lake, surface=2).candidates)
        self.assertEqual(self.q(b=b), Observation('ambiguous'))
        self.assertEqual(self.q(b=replace(b, candidates=b.candidates[::-1])), Observation('ambiguous'))

    def test_duplicate_candidate(self):
        b = self.p(self.b)
        self.assertEqual(self.q(b=replace(b, candidates=b.candidates*2)), Observation('ambiguous'))

    def test_duplicate_location(self):
        self.assertEqual(self.q(b=self.p(self.a)), Observation('invalid'))

    def test_snapshot_mismatch(self):
        for field, value in [('datum','other'), ('frame','other'), ('epoch','other'),
                             ('revision','v3'), ('time_s',2)]:
            with self.subTest(field=field):
                self.assertEqual(self.q(b=self.p(replace(self.b, **{field:value}))), Observation('invalid'))

    def test_invalid_geometry(self):
        self.assertEqual(self.q(b=self.p(self.b, surface=-11)), Observation('invalid'))

    def test_invalid_over_missing(self):
        self.assertEqual(self.q(Probe(self.a, -100, ()), self.p(self.b, surface=-11)), Observation('invalid'))

    def test_malformed(self):
        for value in (True, float('nan'), float('inf'), '10', 10**1000):
            with self.subTest(kind=type(value).__name__):
                self.assertEqual(self.q(b=self.p(self.b, value)), Observation('invalid'))
        self.assertEqual(observe_hull('ocean', (self.p(self.a),)), Observation('invalid'))
        self.assertEqual(observe_hull('ocean', (self.p(self.a),)*65), Observation('invalid'))

    def test_no_authority_fields(self):
        r = self.q()
        for key in ('flotation_confirmed', 'story_advance', 'buoyant_force', 'volume_fraction'):
            self.assertFalse(hasattr(r, key))


if __name__ == '__main__':
    unittest.main()
