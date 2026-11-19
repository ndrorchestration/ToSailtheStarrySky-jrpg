# Native C# World Map — Independent Contract Proposal

**Status: PROPOSAL ONLY, NOT A MERGED/ACCEPTED GAME FEATURE.**

This directory is an **original, engine-neutral C#/.NET architecture experiment** created after the creator’s 2026-10-25 direction: **Godot game engine with C# product scripting**, not GDScript or JS/p5.js. It is isolated from all existing GDScript studies and the browser game's `main`. It does **not** port PR #364 or #367, instantiate a Godot scene, choose the production project structure, change saves or ship art, or implement/disclose private story routes.

## What exists

- `WorldMap.Contracts` — pure C# 12 / .NET 8 data-value contracts and conventional great-circle/spherical-horizon formulas; **radius is always an explicit caller parameter**, not a canonical in-game value.
- `WorldMap.ContractChecks` — dependency-free deterministic console checks of antimeridian/polar navigation, ambiguous bearings, horizon bounds, invalid/nonfinite inputs, tile identity, deduplication and independent capacity limits.
- `TileAdmission` is only a **bounded admission interface for an externally prioritized list**. It does NOT choose visible tiles, calculate chunk LOD, produce meshes, copy GDScript logic, stream data, or guarantee frame-time budgets.
- `TileTransitionPlanner` is a **pure per-frame change planner**: given already-selected desired IDs, current IDs and explicit work-item quotas, it computes non-destructive retire/admit/retained sets. Quotas are **counts**, not measured CPU/GPU time, VRAM, FPS or safety of engine-side disposal. It builds no tiles and does not schedule Godot calls.
- `QuadtreeCoverage` is a **pure six-face coverage invariant**: a complete initial root set must have exactly six nonoverlapping face covers; refinement replaces one leaf with all four children atomically, and coarsening does the reverse only if all siblings are resident. Tile ID geometry and level-12 unit-area sums detect missing quarters and parent/child overlaps; budgets and work quotas can deny the proposal without creating holes. **No GPU geometry, seam stitching, actual navigation view, loaded tile content, art acceptance or true render continuity is established.**
- `.github/workflows/godot-csharp-worldmap-contract.yml` builds with .NET SDK on Linux; this establishes **C# compilation and pure-function contracts only**.

## Run isolated checks

Install an official .NET SDK capable of targeting `net8.0`. From repository root:

```bash
dotnet run -c Release --project native-csharp/WorldMap.ContractChecks/WorldMap.ContractChecks.csproj
```

There are no third-party NuGet package references or direct engine dependencies. No separate test framework download is necessary.

## Product adoption is NOT automatic

The project has **no `Godot.NET.Sdk` package reference, no Godot .NET 4.7.2 editor import and no 3D renderer**. For production C# in Godot, use the official **Godot .NET** editor plus .NET SDK. A separate, creator-approved decision must settle the exact target engine, .NET TFM, solution/asset layout, GitHub branch integration plan, and which (if any) study concepts should be ported. The earlier native GDScript work stays historical evidence.

The proposed `net8.0` TFM is a bounded **standalone CI fixture**, not acceptance of the game's eventual target framework. Version selections, physics and route access remain unresolved.

## QA gates before admission

1. Creator approval of C# solution layout and repository destination, with clear HyperAgent branch/PR collision review.
2. Explicit review of any feature proposed for independent C# implementation — do **not** silently translate a GDScript study.
3. Pin supported official Godot **.NET** 4.7.2 editor and corresponding NuGet SDK/binding version (or creator-approved alternative), import and build under its actual engine and C# compiler.
4. Native real Forward+/Compatibility GPU captures, device profiling, collisions/LOD/planet coverage and creator visual acceptance.
5. Windows release security Defender hold separately. No production merge, `main` switch, existing save migration or private-story reveal.

Read [the decision proposal](../docs/C_SHARP_WORLD_MAP_PRODUCT_DIRECTION.md) and [agent handoff #366](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/366).
