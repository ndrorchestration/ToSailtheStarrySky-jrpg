# Proposed C# World Map Path — Decision Record (review only)

**Date:** October 25, 2026  
**Authority source:** [GitHub agent handoff issue #366](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/366), HyperAgent coordination brief settled by creator 2026-10-25.  
**Status:** C# product direction established; the **implementation layout and port/admission decisions are NOT made**.

## Reconciled authority

| Subject | Direction / evidence |
|---|---|
| Product engine | Godot |
| Product scripting language | **C#**, not GDScript; earlier JS/p5.js is historical |
| GDScript PRs #364 and #367 | **Study/prototype**. Preserve original evidence; do not extend as product without explicit creator authorization |
| Art target | Beautiful and emotionally compelling. Golden-hour crew warmth/wind/sea reference establishes **mood**, not settled photorealistic rendering or 2.5D styling |
| Secret lore, world geography | Private, not to be published; placeholder seed coasts remain **NON-CANON** |
| Merge/release/save migration | Creator's explicit per-decision approval required. Security hold remains in force |

## Actual independent C# deliverable

A separate pure-C# `native-csharp` contract/check project, initially **based on main**, without invoking or copying the GDScript renderer code. It offers physically interpretable spherical coordinate and geometric-horizon value contracts, optional undefined-bearing handling, conservative tile identity/capacity gates, per-frame work-count transition proposals and a **six-face hole-free quadtree cover invariant** (atomic 1↔4 refinement/coarsening proposals). Every planet radius is caller-supplied. Hosted compiler and seeded deterministic checks test contracts only. This is **not yet a Godot game scene** and not a claim of production readiness.

The **proposed** .NET 8 contract target is chosen only to make independent tests executable on hosted CI; it does not decide the engine's full native C# toolchain or target version.

## Explicitly unresolved and reserved for creator/HyperAgent reconciliation

- Confirm engine runtime version and Godot .NET release for the **product**. Godot 4.7.2 **.NET** and a separately installed .NET SDK are a tested-software candidate, not automatic selection because the GDScript study uses Godot 4.7.2 Standard.
- Agree C# solution layout, project namespaces, asset-import pipeline and ownership with HyperAgent before connecting `native-csharp` to scenes. No parallel overwrite of a local HyperAgent patch.
- Confirm which old study ideas, if any, deserve **deliberate C# reimplementation**; do not lift GDScript code or treat a design comparison as port authorization.
- Approve visual aesthetic and example images' intended use (mood vs photorealism). Avoid using a photoreal crew asset as approved sprite authority.
- Determine first true C# world-map feature (scene boot, map camera, streaming scheduler, biome asset registry, etc.) and its native shader/render benchmarks.
- Defer exact world's planet radius, coastlines, cities, auroral routes and story access.

## Proposed order

1. Review independent C# contract CI and the proposed layout with HyperAgent/Herald; inventory HyperAgent's actual local work via branch/PR receipt.
2. If approved, create the actual **Godot .NET** isolated project with signed engine version and standalone native scene, then run its real C# build and render.
3. Perform art direction and benchmark acceptance, followed by incremental map-scale and near-field gameplay integration in creator-reviewed slices.

**Current disposition:** hold product admission. Preserve all existing GDScript and legacy branch evidence. The newly added C# source is an independently testable *proposal*, not a migration PR and not a merge authorization.
