using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;

namespace StarrySky.WorldMap.Contracts;

/// <summary>Tile naming only. No GDScript tile maths are ported or imported.</summary>
public enum CubeFace { PositiveX, NegativeX, PositiveY, NegativeY, PositiveZ, NegativeZ }

public readonly record struct TileId
{
    public CubeFace Face { get; }
    public int Level { get; }
    public int Column { get; }
    public int Row { get; }

    public TileId(CubeFace face, int level, int column, int row)
    {
        if (!Enum.IsDefined(face))
            throw new ArgumentOutOfRangeException(nameof(face));
        if (level < 0 || level > 12)
            throw new ArgumentOutOfRangeException(nameof(level));
        int n = 1 << level;
        if (column < 0 || column >= n)
            throw new ArgumentOutOfRangeException(nameof(column));
        if (row < 0 || row >= n)
            throw new ArgumentOutOfRangeException(nameof(row));
        Face = face;
        Level = level;
        Column = column;
        Row = row;
    }

    public override string ToString() => $"{Face}/{Level}/{Column}/{Row}";
}

/// <summary>
/// A caller-supplied resource budget; no frame-rate, memory-per-tile or
/// performance guarantee is inferred from an active tile count.
/// </summary>
public readonly record struct TileBudget
{
    public int MaxActive { get; }
    public int MaxCached { get; }

    public TileBudget(int maxActive, int maxCached)
    {
        if (maxActive is < 1 or > 256)
            throw new ArgumentOutOfRangeException(nameof(maxActive));
        if (maxCached < maxActive || maxCached > 4096)
            throw new ArgumentOutOfRangeException(nameof(maxCached));
        MaxActive = maxActive;
        MaxCached = maxCached;
    }
}

/// <summary>
/// Deterministic, deduplicating admission gate for a PRIORITIZED set of
/// already-authorized tile IDs. Not a camera/horizon/LOD planner. No tile is
/// generated, fetched, rendered, cached or declared visible by this contract.
/// </summary>
public static class TileAdmission
{
    public static IReadOnlyList<TileId> PrioritizedDistinct(
        IEnumerable<TileId> candidates, TileBudget budget)
    {
        ArgumentNullException.ThrowIfNull(candidates);
        if (budget.MaxActive < 1 || budget.MaxCached < budget.MaxActive)
            throw new ArgumentOutOfRangeException(nameof(budget));

        var output = new List<TileId>(budget.MaxActive);
        var seen = new HashSet<TileId>();
        foreach (var tile in candidates)
        {
            // A default zero-value TileId is a valid initial root tile.
            if (tile.Level is < 0 or > 12 ||
                !Enum.IsDefined(tile.Face) ||
                tile.Column < 0 || tile.Row < 0 ||
                tile.Column >= (1 << tile.Level) || tile.Row >= (1 << tile.Level))
                throw new ArgumentOutOfRangeException(nameof(candidates), "Invalid tile ID.");

            if (!seen.Add(tile))
                continue;
            output.Add(tile);
            if (output.Count == budget.MaxActive)
                break;
        }
        return new ReadOnlyCollection<TileId>(output);
    }
}
