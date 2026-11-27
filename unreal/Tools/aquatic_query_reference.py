"""Noncanonical, engine-free water-column reference; not a runtime or story gate."""
from dataclasses import dataclass
from math import isfinite
import unittest

@dataclass(frozen=True)
class Column:
    body: str
    datum: str
    time_s: float
    surface_m: float
    bed_m: float
    current_mps: tuple[float, float, float]

@dataclass(frozen=True)
class Sample:
    state: str
    column_depth_m: float | None = None
    immersion_m: float | None = None
    bottom_clearance_m: float | None = None


def sample(column: Column | None, z_m: float, time_s: float, datum: str) -> Sample:
    """Exact-time local vertical sample; unknown is never equivalent to dry."""
    if column is None:
        return Sample('unknown')
    try:
        values = (column.time_s, column.surface_m, column.bed_m, z_m, time_s, *column.current_mps)
        valid = (len(column.current_mps) == 3 and all(isfinite(v) for v in values)
                 and bool(column.body.strip()) and bool(datum.strip())
                 and column.datum == datum and column.time_s == time_s and time_s >= 0)
        if not valid:
            return Sample('invalid')
        depth = column.surface_m - column.bed_m
        clearance = z_m - column.bed_m
        immersion = column.surface_m - z_m
        if not all(isfinite(v) for v in (depth, clearance, immersion)):
            return Sample('invalid')
    except (TypeError, AttributeError, ValueError, OverflowError):
        return Sample('invalid')
    if depth <= 0:
        return Sample('dry', 0.0)
    state = 'below_bed' if clearance < 0 else 'above_surface' if immersion < 0 else 'surface' if immersion == 0 else 'submerged'
    return Sample(state, depth, max(0.0, min(depth, immersion)) if clearance >= 0 else None, clearance)


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.c = Column('synthetic', 'local', 1, 2, -8, (1, 0, 0))
    def q(self, z, c=None, time=1, datum='local'):
        return sample(self.c if c is None else c, z, time, datum)
    def test_surface(self): self.assertEqual(self.q(2), Sample('surface', 10, 0, 10))
    def test_above(self): self.assertEqual(self.q(3), Sample('above_surface', 10, 0, 11))
    def test_submerged(self): self.assertEqual(self.q(-3), Sample('submerged', 10, 5, 5))
    def test_bed(self): self.assertEqual(self.q(-8), Sample('submerged', 10, 10, 0))
    def test_below(self): self.assertEqual(self.q(-9), Sample('below_bed', 10, None, -1))
    def test_dry(self): self.assertEqual(self.q(0, Column('a', 'local', 1, 0, 1, (0,0,0))), Sample('dry', 0))
    def test_unknown(self): self.assertEqual(sample(None, 0, 1, 'local'), Sample('unknown'))
    def test_stale(self): self.assertEqual(self.q(0, time=2), Sample('invalid'))
    def test_datum(self): self.assertEqual(self.q(0, datum='other'), Sample('invalid'))
    def test_nan(self): self.assertEqual(self.q(float('nan')), Sample('invalid'))
    def test_current(self): self.assertEqual(self.q(0, Column('a', 'local', 1, 2, -8, (0,0,float('inf')))), Sample('invalid'))
    def test_overflow(self): self.assertEqual(self.q(0, Column('a', 'local', 1, 1e308, -1e308, (0,0,0))), Sample('invalid'))
    def test_tide(self): self.assertEqual(self.q(-3, Column('synthetic', 'local', 1, 3, -8, (1,0,0))), Sample('submerged', 11, 6, 5))
    def test_repeat(self): self.assertEqual(self.q(-3), self.q(-3))

if __name__ == '__main__':
    unittest.main()
