# Aureate Wake — six-directed-route native support contract

**2026-11-01 · Unreal Engine 5.8.4 · DRAFT / REVIEW ONLY / NONCANONICAL**

## Starting point

- Forked without editing protected `main` from draft PR #656 at exact head `61e02fd2fbdcd5ae59078867b5f37f54d6e52a17`.
- PR #656 reports a native Editor build, 13 Unreal automation tests and pre-strut D3D12 captures. **Those historical results do not verify this new branch.**
- The #656 screenshots predate the hydrofoil-strut change: they do not certify the new supports, attachment geometry, or cinematic fidelity.
- Creator direction: **Unreal Engine is the forward development target**; legacy Godot assets and story canon remain preserved, not newly developed.

## What this slice adds

The preview actor now refreshes its provisional wing-root and hydrofoil support transforms **in the same `RequestForm` call** that reveals hydrofoils, avoiding a one-frame discrepancy before the first `Tick`. The six-route test checks immediate start visibility and midpoint support-to-pivot tracking. This remains review-only proxy presentation, not physical validation.

An additional Unreal Editor native automation test, `TSTSS.Ship.ReviewSupportSixDirectedRoutes`, in the existing `AureateWakePreviewNativeTests.cpp`. It uses a transient world, native actor components, and an explicitly noncanonical Engine Cube in place of the review wing GLB.

1. Inspects all four provisional root brackets and two hydrofoil struts. Checks hidden default and disabled collision.
2. Opts into root-pivoted review wing poses and separately enables the preview toggle, then confirms Orbiter **continues to be rejected**.
3. Executes all **six directed ordinary routes** between Skyborne, Seaborne and Submersible, including midpoint and completion.
4. During each midpoint, checks support visibility and that the positive-X tip of each temporary scaled Cube reaches the live wing/foil pivot within 0.5 cm; also checks interruption/Orbiter refusals.
5. At each destination, checks state, completion, retained 4+2 component identity and Seaborne-only visibility of hydrofoil struts.
6. Registers both the existing `TSTSS.Ship.PreviewFormsAndOrbiterHold` and new test as named **required** native cases in `unreal/Tools/Verify-Unreal.ps1`.

## Exact-head acceptance procedure (not yet executed for this slice)

In a **fresh isolated, clean** checkout of this branch, with Unreal 5.8.4 installed:

```powershell
pwsh -File .\unreal\Tools\Verify-Unreal.ps1 -EngineRoot 'C:\Program Files\Epic Games\UE_5.8'
```

Use the actual installed engine path. The script refuses dirty checkouts; records exact Git HEAD; builds the Editor target; runs all `TSTSS` native automation tests via `UnrealEditor-Cmd`; requires both named ship cases in the exported automation JSON; and rechecks HEAD and cleanliness before claiming PASS. If the toolchain or device is unavailable, mark **NATIVE NOT VERIFIED**, not successful.

## Remaining boundaries

- This is a **regression contract**, not a continuous swept-volume clearance proof or proof of no physical hull collision; geometry is temporary and sampled at one midpoint per route.
- Zero collision on supports is intentional in noncanonical review geometry; it is not proof of correct load paths, hydrofoil physics, pressure sealing, or final mounting.
- It does not import GLBs, capture post-strut renders, generate final bridge/hull materials, or establish the cinematic target.
- Orbiter authored-wing motion remains **hard blocked**; no story progression, automatic spell access, UI authority, release, merge, save/load schema, or canonical art approval changes.
- Do not merge until native exact-head evidence, visual review and reconciliation with competing Unreal ship branches have been recorded.

## Next bounded tasks

1. Native Win64 Editor compile + new/old ship automation results at exact head.
2. Capture a true post-strut Seaborne UE renderer screenshot and inspect whether both supports visually attach.
3. Add a separate authored-geometry swept-clearance study for all six ordinary routes; retain Orbiter hold.
4. Replace review-only bridge/hull proxies only in an independently approved visual branch, keeping the forward geodesic glass dome and dragonfly-derived wing silhouette.
