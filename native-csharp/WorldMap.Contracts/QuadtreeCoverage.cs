using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace StarrySky.WorldMap.Contracts;

/// <summary>
/// Pure, conservative six-face quadtree COVERAGE contract. A candidate can
/// refine one parent into all four children or coarsen four siblings into one
/// parent only as an atomic *proposed tile-set change*. It does not load or
/// display terrain, select geographic detail, reconcile adjacent LOD edges,
/// promise hardware frame time, or authorize any world/canon content.
/// </summary>
public static class QuadtreeCoverage
{
    private const int MaxAddressLevel = 12;
    private const long FaceUnits = 1L << (2 * MaxAddressLevel);

    public static IReadOnlyList<TileId> SixFaceRoots()
    {
        var roots = Enum.GetValues<CubeFace>()
            .Select(face => new TileId(face, 0, 0, 0)).ToArray();
        return Array.AsReadOnly(roots);
    }

    /// <summary>
    /// Proves every face has exactly one disjoint normalized area cover.
    /// Geometric area is calculated in level-12 quadtree address units; this
    /// does NOT prove terrain stitching, tangent continuity or rendered pixels.
    /// </summary>
    public static bool IsCompleteSixFaceCover(IEnumerable<TileId> candidates)
    {
        ArgumentNullException.ThrowIfNull(candidates);
        var list = candidates.ToList();
        if (list.Count is < 6 or > 4096)
            return false;
        if (list.Count != list.Distinct().Count())
            return false;
        foreach (var t in list)
            if (!IsValid(t))
                return false;

        var areas = new long[6];
        for (int i = 0; i < list.Count; i++)
        {
            var a = list[i];
            areas[(int)a.Face] += 1L << (2 * (MaxAddressLevel - a.Level));
            for (int j = i + 1; j < list.Count; j++)
            {
                var b = list[j];
                if (a.Face != b.Face)
                    continue;
                if (Contains(a, b) || Contains(b, a))
                    return false;
            }
        }
        return areas.All(x => x == FaceUnits);
    }

    /// <summary>
    /// Return a validated snapshot with a single leaf replaced by its four
    /// children; reject incomplete or oversubscribed requests without changing
    /// the prior cover. Quotas are count-based, NOT time-based.
    /// </summary>
    public static bool TryRefine(IReadOnlyList<TileId> cover, TileId target,
        TileBudget budget, int admissionsRemaining, int retirementsRemaining,
        out IReadOnlyList<TileId> resultingCover)
    {
        ValidateInput(cover, budget, admissionsRemaining, retirementsRemaining);
        resultingCover = Snapshot(cover);
        if (!IsCompleteSixFaceCover(cover))
            throw new ArgumentException("Source must fully cover all six faces.", nameof(cover));
        if (!IsValid(target))
            throw new ArgumentOutOfRangeException(nameof(target));
        if (target.Level >= MaxAddressLevel || !cover.Contains(target)
            || cover.Count + 3 > budget.MaxActive
            || admissionsRemaining < 4 || retirementsRemaining < 1)
            return false;

        var next = cover.Where(x => x != target).ToList();
        foreach (int offsetY in new[] { 0, 1 })
            foreach (int offsetX in new[] { 0, 1 })
                next.Add(new TileId(target.Face, target.Level + 1,
                    target.Column * 2 + offsetX, target.Row * 2 + offsetY));

        if (!IsCompleteSixFaceCover(next))
            throw new InvalidOperationException("Proposed refinement created a hole or overlap.");
        resultingCover = Snapshot(next);
        return true;
    }

    /// <summary>
    /// Replace exactly four complete sibling leaves with their parent. Does
    /// not coarsen partial siblings, convert protected atlas regions into
    /// canon, or implicitly make an engine render transition safe.
    /// </summary>
    public static bool TryCoarsen(IReadOnlyList<TileId> cover, TileId parent,
        TileBudget budget, int admissionsRemaining, int retirementsRemaining,
        out IReadOnlyList<TileId> resultingCover)
    {
        ValidateInput(cover, budget, admissionsRemaining, retirementsRemaining);
        resultingCover = Snapshot(cover);
        if (!IsCompleteSixFaceCover(cover))
            throw new ArgumentException("Source must fully cover all six faces.", nameof(cover));
        if (!IsValid(parent))
            throw new ArgumentOutOfRangeException(nameof(parent));
        if (parent.Level >= MaxAddressLevel || admissionsRemaining < 1
            || retirementsRemaining < 4 || cover.Contains(parent))
            return false;

        var children = new HashSet<TileId>();
        foreach (int offsetY in new[] { 0, 1 })
            foreach (int offsetX in new[] { 0, 1 })
                children.Add(new TileId(parent.Face, parent.Level + 1,
                    parent.Column * 2 + offsetX, parent.Row * 2 + offsetY));
        if (!children.All(cover.Contains))
            return false;

        var next = cover.Where(x => !children.Contains(x)).ToList();
        next.Add(parent);
        if (!IsCompleteSixFaceCover(next))
            throw new InvalidOperationException("Proposed coarsening created a hole or overlap.");
        resultingCover = Snapshot(next);
        return true;
    }

    public static bool IsAncestorOrSelf(TileId ancestor, TileId child)
        => IsValid(ancestor) && IsValid(child) && Contains(ancestor, child);

    private static bool Contains(TileId a, TileId b)
    {
        if (a.Face != b.Face || a.Level > b.Level)
            return false;
        var diff = b.Level - a.Level;
        return (b.Column >> diff) == a.Column && (b.Row >> diff) == a.Row;
    }

    private static bool IsValid(TileId t)
        => Enum.IsDefined(t.Face) && t.Level >= 0 && t.Level <= MaxAddressLevel
            && t.Column >= 0 && t.Row >= 0
            && t.Column < (1 << t.Level) && t.Row < (1 << t.Level);

    private static IReadOnlyList<TileId> Snapshot(IEnumerable<TileId> tiles)
        => new ReadOnlyCollection<TileId>(tiles.ToList());

    private static void ValidateInput(IReadOnlyList<TileId> cover, TileBudget budget,
        int admissions, int retirements)
    {
        ArgumentNullException.ThrowIfNull(cover);
        if (budget.MaxActive <= 0 || budget.MaxCached < budget.MaxActive)
            throw new ArgumentOutOfRangeException(nameof(budget));
        if (cover.Count > budget.MaxActive)
            throw new ArgumentException("Source already exceeds tile budget.", nameof(cover));
        if (admissions < 0 || retirements < 0 ||
            admissions > budget.MaxActive || retirements > budget.MaxActive)
            throw new ArgumentOutOfRangeException(nameof(admissions),
                "Invalid per-transition work quotas.");
    }
}
