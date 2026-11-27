"""AQ-01 v2: noncanonical, engine-free point query, never hull or story authority."""
from dataclasses import dataclass
from math import isfinite
import unittest


def finite_number(value):
    # bool is an int subclass; reject it and non-built-in numeric types.
    try:
        return type(value) in (int, float) and isfinite(value)
    except OverflowError:
        return False


def valid_id(value):
    return type(value) is str and bool(value) and value == value.strip()


@dataclass(frozen=True)
class Context:
    body: str
    datum: str
    frame: str
    location: str
    epoch: str
    revision: str
    time_s: float


@dataclass(frozen=True)
class Column:
    context: Context
    surface_m: float
    bed_m: float
    current_mps: tuple[float, float, float]
    dry: bool = False  # explicit provider declaration, not inferred from inversion


@dataclass(frozen=True)
class Sample:
    state: str
    context: Context | None = None
    column_depth_m: float | None = None
    immersion_m: float | None = None
    bottom_clearance_m: float | None = None
    current_mps: tuple[float, float, float] | None = None


def valid_context(c):
    return (type(c) is Context and all(valid_id(x) for x in
            (c.body, c.datum, c.frame, c.location, c.epoch, c.revision))
            and finite_number(c.time_s) and c.time_s >= 0)


def cm_to_m(value):
    """Unit conversion only; callers must establish common frame and datum."""
    if not finite_number(value):
        raise ValueError('invalid centimeter value')
    result = value / 100.0
    if not finite_number(result):
        raise ValueError('invalid meter result')
    return result


def sample(column: Column | None, z_m: float, expected: Context) -> Sample:
    """Exact snapshot point query. Invalid/unknown carry no usable geometry."""
    if not valid_context(expected) or not finite_number(z_m):
        return Sample('invalid')
    if column is None:
        return Sample('unknown')
    if (type(column) is not Column or not valid_context(column.context)
            or column.context != expected or type(column.dry) is not bool
            or not all(finite_number(v) for v in (column.surface_m, column.bed_m))
            or type(column.current_mps) is not tuple or len(column.current_mps) != 3
            or not all(finite_number(v) for v in column.current_mps)):
        return Sample('invalid')
    try:
        depth = column.surface_m - column.bed_m
        clearance = z_m - column.bed_m
        immersion = column.surface_m - z_m
    except (OverflowError, TypeError):
        return Sample('invalid')
    if not all(finite_number(v) for v in (depth, clearance, immersion)):
        return Sample('invalid')
    if column.dry:
        # Explicit dry declaration must agree with non-positive depth.
        return Sample('dry', expected, 0.0) if depth <= 0 else Sample('invalid')
    if depth <= 0:
        return Sample('invalid')
    state = ('below_bed' if clearance < 0 else 'above_surface' if immersion < 0
             else 'surface' if immersion == 0 else 'submerged')
    return Sample(state, expected, depth,
                  max(0.0, min(depth, immersion)) if clearance >= 0 else None,
                  clearance, column.current_mps)


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.ctx = Context('ocean', 'datum', 'world', 'cell', 'epoch', 'v2', 1)
        self.c = Column(self.ctx, 2, -8, (1, 0, 0))

    def q(self, z, c=None, expected=None):
        return sample(self.c if c is None else c, z,
                      self.ctx if expected is None else expected)

    def test_surface(self): self.assertEqual(self.q(2).state, 'surface')
    def test_above(self): self.assertEqual(self.q(3).immersion_m, 0)
    def test_submerged(self): self.assertEqual(self.q(-3).immersion_m, 5)
    def test_bed(self): self.assertEqual(self.q(-8).bottom_clearance_m, 0)
    def test_below(self): self.assertIsNone(self.q(-9).immersion_m)
    def test_dry(self): self.assertEqual(self.q(0, Column(self.ctx, 0, 1, (0,0,0), True)).state, 'dry')
    def test_unknown(self): self.assertEqual(sample(None, 0, self.ctx), Sample('unknown'))
    def test_nan(self): self.assertEqual(self.q(float('nan')), Sample('invalid'))
    def test_current(self): self.assertEqual(self.q(0, Column(self.ctx, 2, -8, (0,0,float('inf')))), Sample('invalid'))
    def test_overflow(self): self.assertEqual(self.q(0, Column(self.ctx, 1e308, -1e308, (0,0,0))), Sample('invalid'))
    def test_tide(self): self.assertEqual(self.q(-3, Column(self.ctx, 3, -8, (1,0,0))).column_depth_m, 11)
    def test_repeat(self): self.assertEqual(self.q(-3), self.q(-3))
    def test_identity_mismatch(self):
        from dataclasses import replace
        for field, value in [('body','lake'), ('datum','other'), ('frame','other'),
                             ('location','other'), ('epoch','other'), ('revision','v3'), ('time_s',2)]:
            with self.subTest(field=field):
                self.assertEqual(self.q(0, expected=replace(self.ctx, **{field:value})), Sample('invalid'))
    def test_body_echo(self):
        from dataclasses import replace
        lake = replace(self.ctx, body='lake')
        self.assertNotEqual(self.q(0), sample(Column(lake,2,-8,(1,0,0)),0,lake))
    def test_boolean(self):
        from dataclasses import replace
        self.assertEqual(self.q(0, expected=replace(self.ctx,time_s=True)), Sample('invalid'))
        self.assertEqual(self.q(True), Sample('invalid'))
        self.assertEqual(self.q(0, Column(self.ctx, True,-8,(1,0,0))), Sample('invalid'))
        self.assertEqual(self.q(0, Column(self.ctx, 2,-8,(True,0,0))), Sample('invalid'))
    def test_inversion(self): self.assertEqual(self.q(0, Column(self.ctx,0,1,(0,0,0))), Sample('invalid'))
    def test_zero_depth(self): self.assertEqual(self.q(0, Column(self.ctx,0,0,(0,0,0))), Sample('invalid'))
    def test_dry_contradiction(self): self.assertEqual(self.q(0, Column(self.ctx,2,-8,(0,0,0),True)), Sample('invalid'))
    def test_invalid_query_even_without_provider(self): self.assertEqual(sample(None, True, self.ctx), Sample('invalid'))
    def test_units(self):
        self.assertEqual(cm_to_m(-800), -8)
        for v in (True, float('inf'), '800', 10**1000):
            with self.subTest(value=type(v).__name__), self.assertRaises(ValueError): cm_to_m(v)
    def test_grid(self):
        for surface in range(-3,4):
            for bed in range(-3,4):
                for z in range(-5,6):
                    with self.subTest(surface=surface,bed=bed,z=z):
                        c = Column(self.ctx,surface,bed,(0,0,0),surface<=bed)
                        s = self.q(z,c)
                        if surface <= bed:
                            self.assertEqual(s, Sample('dry',self.ctx,0.0))
                        else:
                            expected = 'below_bed' if z<bed else 'above_surface' if z>surface else 'surface' if z==surface else 'submerged'
                            self.assertEqual(s.state,expected)
                            self.assertEqual(s.column_depth_m,surface-bed)
                            self.assertEqual(s.bottom_clearance_m,z-bed)
                            self.assertEqual(s.immersion_m,None if z<bed else max(0,surface-z))
                            self.assertEqual(s.context,self.ctx)


if __name__ == '__main__':
    unittest.main()
