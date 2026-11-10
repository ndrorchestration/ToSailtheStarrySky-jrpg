using System;
using System.Collections.Generic;
using System.Linq;
using StarrySky.WorldMap.Contracts;

internal static class Program
{
    private const double R = 6371.0; // Only a numeric test fixture, NOT canon.
    private static int _assertions;

    private static void Check(bool valid, string name)
    {
        _assertions++;
        if (!valid)
            throw new Exception("CS_WORLDMAP_CONTRACT_FAIL: " + name);
    }

    private static void Near(double actual, double expected, double tolerance, string name)
        => Check(double.IsFinite(actual) && Math.Abs(actual - expected) <= tolerance, name);

    private static void Reject<T>(Action call, string name) where T : Exception
    {
        _assertions++;
        try
        {
            call();
        }
        catch (T)
        {
            return;
        }
        throw new Exception("CS_WORLDMAP_CONTRACT_FAIL: missing rejection " + name);
    }

    private static void GeodesicChecks()
    {
        var origin = new PlanetPosition(0, 0);
        Near(new PlanetPosition(12, 540).LongitudeDegrees, -180, 1e-9, "canonical antimeridian");
        Near(new PlanetPosition(90, -75).LongitudeDegrees, 0, 1e-9, "pole longitude irrelevant");
        Near(new PlanetPosition(0, -360).LongitudeDegrees, 0, 1e-9, "360-degree wrap");
        Near(PlanetGeometry.AngularSeparationRadians(origin, origin), 0, 1e-14, "same-point angle");
        Near(PlanetGeometry.AngularSeparationRadians(origin, new PlanetPosition(0, 180)),
            Math.PI, 1e-9, "antipodal angle");
        Near(PlanetGeometry.SurfaceDistanceKm(new PlanetPosition(0, 179.9),
            new PlanetPosition(0, -179.9), R), 22.23898533, 0.001, "seam surface distance");
        var destination = PlanetGeometry.Destination(origin, 90, 100, R);
        Near(destination.LatitudeDegrees, 0, 1e-9, "eastbound equator latitude");
        Near(PlanetGeometry.SurfaceDistanceKm(origin, destination, R), 100, 1e-7, "distance roundtrip");
        Check(PlanetGeometry.TryInitialBearingDegrees(origin, destination, out double bearing),
            "bearing defined for eastbound step");
        Near(bearing, 90, 1e-8, "eastbound initial bearing");
        Check(!PlanetGeometry.TryInitialBearingDegrees(origin, origin, out _),
            "coincident bearing fails closed");
        Check(!PlanetGeometry.TryInitialBearingDegrees(origin, new PlanetPosition(0, 180), out _),
            "antipodal bearing fails closed");
        var crossing = PlanetGeometry.Destination(new PlanetPosition(1, 179.95, 4),
            90, 30, R);
        Check(crossing.LongitudeDegrees < -179, "destination crosses antimeridian");
        Near(crossing.AltitudeKm, 4, 1e-9, "destination preserves altitude");
        Near(PlanetGeometry.HorizonSurfaceDistanceKm(0, R), 0, 1e-9, "zero-altitude horizon");
        Check(PlanetGeometry.HorizonSurfaceDistanceKm(2, R) > 150
            && PlanetGeometry.HorizonSurfaceDistanceKm(2, R) < 170,
            "2 km fixture physical horizon bounded");
        Check(!PlanetGeometry.HasGeometricLineOfSight(
            new PlanetPosition(0, 0), new PlanetPosition(0, 2), R),
            "distant surface-only site hidden");
        Check(PlanetGeometry.HasGeometricLineOfSight(
            new PlanetPosition(0, 0, 2), new PlanetPosition(0, 1), R),
            "raised observer sees nearby site");
        Check(!PlanetGeometry.HasGeometricLineOfSight(
            new PlanetPosition(0, 0, 2), new PlanetPosition(0, 30), R),
            "horizon does not reveal whole planet");
        var rng = new Random(2047);
        for (int i = 0; i < 256; i++)
        {
            var start = new PlanetPosition(rng.NextDouble() * 178 - 89,
                rng.NextDouble() * 720 - 360, rng.NextDouble() * 20);
            double course = rng.NextDouble() * 360;
            double distance = rng.NextDouble() * 1500;
            var arrived = PlanetGeometry.Destination(start, course, distance, R);
            Near(PlanetGeometry.SurfaceDistanceKm(start, arrived, R), distance,
                0.00001, "seeded great-circle roundtrip " + i);
            Check(arrived.LatitudeDegrees >= -90 && arrived.LatitudeDegrees <= 90
                && arrived.LongitudeDegrees >= -180 && arrived.LongitudeDegrees < 180,
                "seeded bounded coordinates " + i);
            Check(arrived.AltitudeKm == start.AltitudeKm, "seeded altitude invariant " + i);
        }
    }

    private static void TileChecks()
    {
        var budget = new TileBudget(3, 5);
        var a = new TileId(CubeFace.PositiveX, 4, 0, 0);
        var b = new TileId(CubeFace.PositiveZ, 4, 1, 1);
        var c = new TileId(CubeFace.NegativeX, 4, 15, 15);
        var d = new TileId(CubeFace.PositiveY, 4, 14, 14);
        var tiles = TileAdmission.PrioritizedDistinct(new[] { a, b, a, c, d }, budget);
        Check(tiles.Count == 3 && tiles[0] == a && tiles[1] == b && tiles[2] == c,
            "prioritized distinct bounded tile admission");
        Check(TileAdmission.PrioritizedDistinct(Array.Empty<TileId>(), budget).Count == 0,
            "empty candidates safe");
        Check(TileAdmission.PrioritizedDistinct(new[] { a, a, a }, budget).Count == 1,
            "dedup before cutoff");
        Check(new TileId(CubeFace.PositiveZ, 12, 4095, 4095).Level == 12,
            "max address level supported");
        Check(new TileId(CubeFace.NegativeZ, 0, 0, 0).ToString()
            == "NegativeZ/0/0/0", "traceable stable tile ID");
        Reject<ArgumentOutOfRangeException>(() => _ = new TileId(CubeFace.PositiveX, 12, 4096, 1),
            "invalid final tile column");
        Reject<ArgumentOutOfRangeException>(() => _ = new TileId((CubeFace)99, 2, 1, 1),
            "unknown tile face");
        Reject<ArgumentOutOfRangeException>(() => _ = new TileId(CubeFace.PositiveX, 13, 1, 1),
            "unknown LOD");
        Reject<ArgumentOutOfRangeException>(() => _ = new TileBudget(0, 12),
            "zero active budget");
        Reject<ArgumentOutOfRangeException>(() => _ = new TileBudget(64, 32),
            "cache smaller than active budget");
        Reject<ArgumentNullException>(() => _ = TileAdmission.PrioritizedDistinct(null!, budget),
            "null tile set");
    }

    private static void TransitionChecks()
    {
        var budget = new TileBudget(3, 5);
        var a = new TileId(CubeFace.PositiveX, 2, 0, 0);
        var b = new TileId(CubeFace.PositiveX, 2, 1, 0);
        var c = new TileId(CubeFace.PositiveX, 2, 2, 0);
        var d = new TileId(CubeFace.PositiveX, 2, 3, 0);
        var e = new TileId(CubeFace.NegativeZ, 2, 0, 0);
        var before = new List<TileId> { a, b, c };
        var target = new[] { c, d, e };
        var first = TileTransitionPlanner.Next(before, target, budget, 1, 1);
        Check(first.Retire.Count == 1 && first.Admit.Count == 1,
            "bounded first-frame add and retire");
        Check(first.ActiveAfter.Count == 3 && first.DeferredTargetCount == 1,
            "bounded in-flight active count/deferred tiles");
        var second = TileTransitionPlanner.Next(first.ActiveAfter, target, budget, 1, 1);
        Check(second.Retire.Count == 1 && second.Admit.Count == 1,
            "bounded second-frame add and retire");
        Check(second.ActiveAfter.Count == 3 && second.DeferredTargetCount == 0,
            "target fully resident without over-allocation");
        var settled = TileTransitionPlanner.Next(second.ActiveAfter, target, budget, 1, 1);
        Check(settled.Admit.Count == 0 && settled.Retire.Count == 0,
            "settled target has no spurious rebuild");
        var blocked = TileTransitionPlanner.Next(before, target, budget, 0, 0);
        Check(blocked.ActiveAfter.SequenceEqual(before)
            && blocked.Retire.Count == 0 && blocked.Admit.Count == 0,
            "zero work allowance leaves set unchanged");
        Reject<ArgumentOutOfRangeException>(() =>
            _ = TileTransitionPlanner.Next(before, target, budget, -1, 1),
            "negative admission quota");
        Reject<ArgumentException>(() =>
            _ = TileTransitionPlanner.Next(new[] { a, a }, target, budget, 1, 1),
            "duplicate input active set");
        Reject<ArgumentException>(() =>
            _ = TileTransitionPlanner.Next(new[] { a, b, c, d }, target, budget, 1, 1),
            "oversubscribed active set");

        // Sequences must converge without leaving active-capacity or per-frame
        // bounds even with changing target sets and polar/cross-face IDs.
        var pool = new List<TileId>();
        foreach (CubeFace face in Enum.GetValues<CubeFace>())
        {
            for (int i = 0; i < 8; i++)
                pool.Add(new TileId(face, 4, i, (i + (int)face) % 16));
        }
        var rng = new Random(87501);
        var live = new List<TileId>();
        var generous = new TileBudget(16, 32);
        for (int frame = 0; frame < 256; frame++)
        {
            var priorities = pool.OrderBy(_ => rng.Next()).Take(16).ToList();
            var next = TileTransitionPlanner.Next(live, priorities, generous, 3, 4);
            Check(next.Admit.Count <= 3 && next.Retire.Count <= 4,
                "frame work budgets " + frame);
            Check(next.ActiveAfter.Count <= 16
                && next.ActiveAfter.Distinct().Count() == next.ActiveAfter.Count,
                "active residency bound " + frame);
            Check(next.DeferredTargetCount >= 0 && next.DeferredTargetCount <= 16,
                "deferred backlog bounded " + frame);
            live = next.ActiveAfter.ToList();
        }
    }

    private static void CoverageChecks()
    {
        var original = QuadtreeCoverage.SixFaceRoots();
        var budget = new TileBudget(64, 128);
        Check(original.Count == 6
            && QuadtreeCoverage.IsCompleteSixFaceCover(original),
            "all six roots cover a complete world with no seams or omissions");
        foreach (var face in Enum.GetValues<CubeFace>())
        {
            Check(original.Any(x => x.Face == face && x.Level == 0),
                "six independently represented faces " + face);
        }

        var first = original[0];
        Check(!QuadtreeCoverage.TryRefine(original, first, budget, 3, 1, out var rejected)
            && rejected.SequenceEqual(original),
            "cannot partially admit four children when only three permits exist");
        Check(!QuadtreeCoverage.TryRefine(original, first, budget, 4, 0, out rejected)
            && rejected.SequenceEqual(original),
            "cannot split without retirement quota");
        Check(QuadtreeCoverage.TryRefine(original, first, budget, 4, 1, out var split),
            "complete atomic four-child refinement");
        Check(split.Count == 9 && QuadtreeCoverage.IsCompleteSixFaceCover(split),
            "refine has no missing ground tiles or overlapping parent surface");
        Check(!split.Contains(first)
            && split.Count(x => x.Face == first.Face && x.Level == 1) == 4,
            "retired root replaced by exactly four children");
        Check(!QuadtreeCoverage.TryRefine(split, first, budget, 4, 1, out rejected)
            && rejected.SequenceEqual(split),
            "cannot re-refine nonresident parent");
        Check(!QuadtreeCoverage.TryCoarsen(split, first, budget, 1, 3, out rejected)
            && rejected.SequenceEqual(split),
            "cannot partially retire a four-sibling cover");
        Check(QuadtreeCoverage.TryCoarsen(split, first, budget, 1, 4, out var restored)
            && QuadtreeCoverage.IsCompleteSixFaceCover(restored),
            "atomic sibling collapse returns complete coverage");
        Check(restored.ToHashSet().SetEquals(original),
            "full six-face coverage restored without inventing new tiles");

        Check(!QuadtreeCoverage.IsCompleteSixFaceCover(original.Skip(1)),
            "missing entire planet face not incorrectly accepted");
        Check(!QuadtreeCoverage.IsCompleteSixFaceCover(original.Concat(new[] { first })),
            "duplicate overdraw rejected");
        Check(!QuadtreeCoverage.IsCompleteSixFaceCover(
            original.Concat(new[] { new TileId(first.Face, 1, 0, 0) })),
            "ancestor plus descendent overlap rejected");
        Check(!QuadtreeCoverage.IsCompleteSixFaceCover(split.Where(x =>
            x != new TileId(first.Face, 1, 0, 0))),
            "missing geographic quadrant rejected");
        Check(QuadtreeCoverage.IsAncestorOrSelf(first, new TileId(first.Face, 10, 831, 301)),
            "ancestor containment across many LOD levels");
        Check(!QuadtreeCoverage.IsAncestorOrSelf(first,
            new TileId(CubeFace.NegativeX, 10, 831, 301)),
            "different cube faces never imply containment");
        Check(!QuadtreeCoverage.TryRefine(original, first,
                new TileBudget(8, 16), 4, 1, out rejected)
            && QuadtreeCoverage.IsCompleteSixFaceCover(rejected),
            "full residency budget denies splitting instead of making holes");

        Reject<ArgumentException>(() => QuadtreeCoverage.TryRefine(
            new[] { original[0], original[1] },
            first, budget, 4, 1, out _), "noncomplete source refused");
        Reject<ArgumentOutOfRangeException>(() => QuadtreeCoverage.TryRefine(
            original, first, budget, -1, 1, out _), "negative admission quota refused");

        // Seeded splits and reversible sibling collapses: every snapshot must
        // retain a complete six-face surface, even when tile budgets deny work.
        var random = new Random(44111);
        var current = original.ToList();
        for (int iteration = 0; iteration < 320; iteration++)
        {
            if (current.Count > 45 && random.Next(2) == 0)
            {
                var parentCandidates = current.Where(x => x.Level > 0)
                    .Select(x => new TileId(x.Face, x.Level - 1, x.Column >> 1, x.Row >> 1))
                    .Distinct().OrderBy(x => x.ToString(), StringComparer.Ordinal).ToList();
                if (parentCandidates.Count > 0)
                {
                    var candidate = parentCandidates[random.Next(parentCandidates.Count)];
                    if (QuadtreeCoverage.TryCoarsen(current, candidate,
                            budget, 1, 4, out var collapsed))
                        current = collapsed.ToList();
                }
            }
            else
            {
                var possible = current.Where(x => x.Level < 6).ToList();
                if (possible.Count > 0)
                {
                    var candidate = possible[random.Next(possible.Count)];
                    if (QuadtreeCoverage.TryRefine(current, candidate,
                            budget, 4, 1, out var refined))
                        current = refined.ToList();
                }
            }
            Check(current.Count is >= 6 and <= 64
                && QuadtreeCoverage.IsCompleteSixFaceCover(current),
                "seeded split/collapse keeps every face covered " + iteration);
        }
    }

    private static void RejectionChecks()
    {
        Reject<ArgumentOutOfRangeException>(() => _ = new PlanetPosition(91, 0),
            "latitude out of range");
        Reject<ArgumentOutOfRangeException>(() => _ = new PlanetPosition(0, double.NaN),
            "NaN longitude");
        Reject<ArgumentOutOfRangeException>(() => _ = new PlanetPosition(0, 0, double.PositiveInfinity),
            "infinite altitude");
        Reject<ArgumentOutOfRangeException>(() => PlanetGeometry.RequireRadius(-3),
            "negative planet radius");
        Reject<ArgumentOutOfRangeException>(() =>
            _ = PlanetGeometry.HorizonAngleRadians(-0.1, R),
            "negative observer altitude");
        Reject<ArgumentOutOfRangeException>(() =>
            _ = PlanetGeometry.Destination(new PlanetPosition(0, 0), 0, 10, 0),
            "zero radius");
        Reject<ArgumentOutOfRangeException>(() =>
            _ = PlanetGeometry.Destination(new PlanetPosition(0, 0), double.NaN, 10, R),
            "invalid heading");
        Reject<ArgumentOutOfRangeException>(() =>
            _ = PlanetGeometry.Destination(new PlanetPosition(0, 0), 20, Math.PI * R + 0.1, R),
            "ambiguous beyond-antipodal step");
    }

    private static int Main()
    {
        try
        {
            GeodesicChecks();
            TileChecks();
            TransitionChecks();
            CoverageChecks();
            RejectionChecks();
            Console.WriteLine($"CS_WORLDMAP_CONTRACT_PASS: {_assertions} deterministic assertions; no Godot runtime or canon admitted");
            Console.WriteLine("CS_WORLDMAP_GODOT_MONO_NATIVE=NOT_ESTABLISHED");
            Console.WriteLine("CS_WORLDMAP_VISUAL_ACCEPTANCE=NOT_ESTABLISHED");
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex.Message);
            return 1;
        }
    }
}
