using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace StarrySky.WorldMap.Contracts;

/// <summary>
/// A proposal for pure, deterministic per-frame admission. Counts represent
/// work-item limits, NOT measured milliseconds, VRAM, draw calls or hardware FPS.
/// Does not generate world geometry or port the GDScript tile streamer.
/// </summary>
public sealed record TileTransition(
    IReadOnlyList<TileId> Retire,
    IReadOnlyList<TileId> Admit,
    IReadOnlyList<TileId> ActiveAfter,
    int DeferredTargetCount);

public static class TileTransitionPlanner
{
    public static TileTransition Next(
        IEnumerable<TileId> activeTiles,
        IEnumerable<TileId> prioritizedTargetTiles,
        TileBudget budget,
        int maxAdmissionsPerFrame,
        int maxRetirementsPerFrame)
    {
        ArgumentNullException.ThrowIfNull(activeTiles);
        ArgumentNullException.ThrowIfNull(prioritizedTargetTiles);
        if (budget.MaxActive < 1 || budget.MaxCached < budget.MaxActive)
            throw new ArgumentOutOfRangeException(nameof(budget));
        if (maxAdmissionsPerFrame < 0 || maxAdmissionsPerFrame > budget.MaxActive)
            throw new ArgumentOutOfRangeException(nameof(maxAdmissionsPerFrame));
        if (maxRetirementsPerFrame < 0 || maxRetirementsPerFrame > budget.MaxActive)
            throw new ArgumentOutOfRangeException(nameof(maxRetirementsPerFrame));

        var current = activeTiles.ToList();
        if (current.Count > budget.MaxActive || current.Count != current.Distinct().Count())
            throw new ArgumentException("Active tile set exceeds capacity or contains duplicates.",
                nameof(activeTiles));

        // The existing constructor validates user-created addresses, but
        // records are structs and a caller could supply untrusted default data.
        // A uniform central validator keeps the transition boundary explicit.
        foreach (var id in current)
            Validate(id);

        IReadOnlyList<TileId> wanted = TileAdmission.PrioritizedDistinct(
            prioritizedTargetTiles, budget);
        var desired = new HashSet<TileId>(wanted);

        // Retire *only* tiles no longer in the desired target. Deterministic
        // order is independent of hash/dictionary enumeration.
        var retire = current.Where(t => !desired.Contains(t))
            .OrderBy(t => t.ToString(), StringComparer.Ordinal)
            .Take(maxRetirementsPerFrame).ToList();
        var retireSet = new HashSet<TileId>(retire);
        var remaining = current.Where(t => !retireSet.Contains(t)).ToList();
        int available = budget.MaxActive - remaining.Count;
        int allocation = Math.Min(available, maxAdmissionsPerFrame);

        var retainedSet = new HashSet<TileId>(remaining);
        var admit = new List<TileId>();
        foreach (var item in wanted)
        {
            if (retainedSet.Contains(item))
                continue;
            if (admit.Count == allocation)
                break;
            retainedSet.Add(item);
            admit.Add(item);
        }

        var after = remaining.Concat(admit).ToList();
        int deferred = wanted.Count(x => !retainedSet.Contains(x));
        if (after.Count > budget.MaxActive || after.Distinct().Count() != after.Count)
            throw new InvalidOperationException("Transition violated tile capacity.");

        return new TileTransition(
            new ReadOnlyCollection<TileId>(retire),
            new ReadOnlyCollection<TileId>(admit),
            new ReadOnlyCollection<TileId>(after),
            deferred);
    }

    private static void Validate(TileId id)
    {
        if (!Enum.IsDefined(id.Face) || id.Level < 0 || id.Level > 12 ||
            id.Column < 0 || id.Row < 0 ||
            id.Column >= (1 << id.Level) || id.Row >= (1 << id.Level))
            throw new ArgumentOutOfRangeException(nameof(id));
    }
}
