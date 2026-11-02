# Aureate Wake hydrofoil-strut native regression — review-only evidence

Date: 2026-11-01. Proposed as [draft PR #695](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/695), stacked on [draft PR #656](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/656). The ship implementation, authoring/canon boundary, and Orbiter gate are unchanged.

## Scope and asserted mechanics

`TSTSS.Ship.HydrofoilStrutNativeReview` is a proposed **native C++ automation** test using a transient UE world and the noncanonical `AAureateWakePreviewActor` with **BasicShapes** review geometry. It checks:

- Runtime discovery of both struts and hydrofoils by their named UStaticMeshComponents; supports configured with no collision.
- Both hydrofoils/struts hidden in Skyborne; visible during a permitted ordinary transition.
- Expected **halfway** Skyborne → Seaborne foil and strut positions, including a centerpoint computed from the actual moving foil transform.
- Seaborne endpoints on both sides, support scale/orientation, and the BasicShapes cube's local-X endpoints ±50 cm transformed to the proxy hull anchor and hydrofoil center.
- During Seaborne → Submersible folding, both supports remain available until the transition completes; fully tucked state hides both foil and support.
- Submersible → Seaborne → Skyborne round trip re-displays then hides the correct components.
- Orbiter request continues to be rejected, and no unfinished transition is permitted to be forcibly completed.

**Important:** These checks are **assertions in uncompiled source** until an actual native Unreal automation report is obtained. Passing a separate Python source-contract checker is not evidence the C++ code runs or meshes are rendered.

## Evidence and reproducer

On `neontic`, the first independent build attempt at PR #695 initial head `09f9c4c7aef2c9880e68266a161b69cf6240e25a` reached UHT (22 generated files) and C++ compile but was deliberately interrupted when free physical RAM dropped to roughly **0.16 GiB**. No C++ compilation or automation result is available for that revision. The new test extensions have **not** been natively built.

A new clean detached source-only checkout of head `aaed56ebe1eda9bbf942bfdfd03fcabb2bf1db20` was used for lightweight Python checks:

```powershell
py -3 unreal/Tools/test_hydrofoil_review_contract.py
py -3 unreal/Tools/check_automation_registry.py
py -3 unreal/Tools/check_unreal_test_inventory.py
```

Observed locally: **5/5 contract unit tests PASS**, **14/14 registered** source tests, and **14/14 source inventory** PASS (0 tracked modifications). The source contract includes mutated-actor-gate and mutated-test-assertion negatives and checks simple symmetric proxy endpoints at three interpolation values. This is **engine-free**. Hosted [source inventory #41365802986](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41365802986), [source preflight #41365803003](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41365803003), and [game smoke #41365802976](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41365802976) all succeeded on the same commit.

Native compilation remains blocked on insufficient headroom. [Draft PR #677](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/677) includes an optional **read-only** experimental guard requiring 6 GiB free physical RAM and 4 GiB available commit for new build attempts, with unvalidated conservative thresholds. Last observed live sample: **2.43 GiB physical free, 2.945 GiB available commit**; an existing Unreal Editor session was running. Do **not** close it or unrelated apps as part of an automatic retry.

## Exit criteria, separated

| Evidence dimension | State |
| --- | --- |
| Native C++ assertions authored | DONE (draft review source) |
| Source-only registry, contract and inventory | PASS |
| Exact-head UE 5.8.4 Win64 Editor build of **latest** test | NOT_VERIFIED |
| Actual Unreal automation report: `TSTSS.Ship.HydrofoilStrutNativeReview` | NOT_EXECUTED |
| Genuine post-strut D3D12 Seaborne screenshot (PR #656) | NOT_CAPTURED |
| Visual inspection of BOTH hydrofoil supports | NOT_VERIFIED |
| Real continuous hull/foil geometry clearance and hydrodynamics | NOT_VERIFIED |
| Authoritative art promotion, merge or Orbiter unlock | NOT_AUTHORIZED |

When available memory/commit headroom improves **and there is no conflicting Editor**, create a fresh detached **exact-head** worktree; run the resource gate; run one native Unreal Win64 Editor build and `TSTSS.Ship.HydrofoilStrutNativeReview` with a report exported to a new `Saved/` evidence path. If insufficient headroom, leave the machine untouched and preserve the pending state. Native test success is separate from visual or art approval.
