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

## Further source-only transition audit — 2026-11-01

This review branch now runs a bounded analytical model of **all six ordered routes between Skyborne, Seaborne and Submersible** at 21 interpolation fractions per route, for **both** hydrofoil struts: 6 × 21 × 2 = **252 support poses**. The check uses the observed C++ review-proxy constants (hull anchor `Y=±60, Z=-30cm`; hydrofoil center `Y=±80, Z=-45/-140cm`), the source's cubic smoothstep easing, and an axis-aligned provisional hull half-width/half-height of **75/32.5 cm** derived from the BasicShapes cube proxy.

For each sampled pose it checks endpoint alignment, nonzero span, port/starboard symmetry, monotonic Z movement, and that each *centerline* exits the temporary hull proxy in the first 20% of its travel from the deliberately internal hull anchor. The inferred hull overlap at the anchor is **intentional**, not a clearance PASS. Only simple line arithmetic is verified; mesh radii, imported model surfaces, bridge intersection, hydrodynamic force, continuous sweeping, shaders and actual native rendering are outside the evidence.

The Python audit explicitly refuses Orbiter, malformed side/fraction inputs and unauthorized geometry changes: controls mutate the source hull anchor, deployed foil depth and easing expression and assert fail-closed detection. It also retains the prior per-form source and registered C++ test checks.

Observed at exact source `60e744b9bf90d87c551ad8ca398454e9bf5c180b` in a new clean detached Windows source worktree: **7/7 engine-free contract tests PASS; 14/14 registered native test names PASS; 14/14 source inventory PASS; no tracked changes**. Further source-only mutation controls were committed after that snapshot; see the latest hosted CI result for their status. **Native C++ test is still NOT COMPILED or EXECUTED** because local resource limits are not met.

This audit is source- and proxy-bound, with no art approval and no permission to enable Orbiter, merge drafts or describe the ship as flight-/water-/pressure-safe.

## 2026-11-01 — Native six-route 252-pose assertions added (execution still pending)

The prior 252-pose sweep existed **only** as engine-free Python arithmetic. A follow-on isolated source change adds the same six ordered ordinary-form routes to the real C++ test `TSTSS.Ship.HydrofoilStrutNativeReview` itself. It reuses one transient actor, prepares each starting ordinary form, begins each transition, and observes 20 intermediate sampling positions plus the completed endpoint. For **6 routes × 21 phases × 2 supports = 252 proposed runtime support observations**, the C++ assertions check:

- Actual `UStaticMeshComponent` foil and strut visibility during transitions and in the final ordinary forms.
- Moving foil center vs source-calibrated cubic-easing position (tolerance 0.2 cm).
- Strut midpoint, length scale, and transformed local-X 100cm cube endpoints vs the temporary hull anchor and foil center (0.3cm endpoint tolerance).
- Every transition completes to the requested ordinary form; Orbiter requests remain refused after every route.

New Python source-contract mutation tests guard against accidentally removing or shortening the six-route native test, endpoint assertions, or repeated Orbiter hold. Source inventory continues to require this one named native test. **Neither the Python sweep nor the C++ source asserts collision clearance, structural support, aerodynamic/hydrodynamic validity, or visual fidelity.**

**Resource state at the latest workstation check:** `neontic` online with *three existing* UnrealEditor processes (left untouched), available free physical memory **0.308 GiB**, available commit headroom **5.977 GiB**. The experimental read-only memory guard returned `BLOCK_INSUFFICIENT_BUILD_HEADROOM`, exit 1. No native build, Unreal automation or D3D12 render was launched. Prior native build was interrupted due to 0.16 GiB memory and does not validate this new test source. Do not weaken gates, close any active unrelated Editor, or claim `NATIVE_AUTOMATION=PASS` from source-only CI.

## 2026-11-01 — Source-level visibility defect and minimal reversible correction

While adding actual C++ 252-pose sampling, inspection identified a behavioral source risk in the **unmodified #656 review actor**: `RequestForm()` always called `Hydrofoils[Index]->SetVisibility(true)` for **every** transition. This meant a direct Skyborne ↔ Submersible transition could temporarily reveal both Seaborne-only hydrofoils and their struts even though neither ordinary endpoint deploys them. This is a deterministic source-control observation, not yet a native-rendered visual defect report.

The proposed fix, **isolated on this stacked draft #695 only**, changes that single visibility decision to `bShowFoilsDuringTransition = (CurrentForm == Seaborne || RequestedForm == Seaborne)`. Neither the hull or foil geometry nor the story/Orbiter authorization is changed. Ordinary transitions into or out of Seaborne continue to expose the review hardware during the change; a direct Skyborne ↔ Submersible transition keeps it concealed.

The new proposed C++ six-route test now distinguishes visible and concealed support observations. Of its **252 proposed native support observations**, **164** expect visible hardware (including completed Seaborne endpoints) and **88** expect hidden hardware (direct non-Seaborne routes and completed non-Seaborne endpoints). Only visible supports are subject to world-independent 100cm proxy cube endpoint alignment checks; concealed supports are checked for hiding, not for updated invisible transforms. Added engine-free policy modeling and negative controls rejecting regression to the prior unconditional reveal. These are source-only CI assertions until the C++ test actually compiles and runs in Unreal.

The behavior change is **review-only**; accept no art/canon approval or motion safety claim from it. The proposed native code must still be compiled on the exact revision, followed by real native automation, a post-strut D3D12 Seaborne PNG and independent visual assessment before any merge or promotion.
