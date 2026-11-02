# Unreal-first development and dependency authority register

**Checkpoint: November 1, 2026 · Draft source documentation · No dependency upgrades or merges.**

This register reconciles creator direction, active Unreal 5.8.4 draft branches and historically preserved Godot/browser material. It describes **what can be worked on**, not an assertion that draft features are merged into the default branch or accepted cinematic game content. The canonical story, Five Lights and creator-approved character/ship references remain author-controlled.

## Current development authority

| Lane | Function | Authority and restrictions |
| --- | --- | --- |
| **Unreal Engine 5.8.4 / C++ / Editor** | **Active engine implementation and visual verification** for To Sail the Starry Sky | Work only in isolated reversible review branches; capture exact Git SHA, native compile, Automation RunTests, Unreal import and D3D12 screenshot evidence separately. Unmerged drafts do not establish production adoption. |
| Godot 4.7.2 / GDScript | Preserved historical implementation, migration/behavior reference and existing story contracts | Creator-approved narrative details survive engine change, but Godot runtime and released build are **not** the current active implementation target. Do not delete source, rewrite old evidence, silently change saves, or imply new Godot runtime development is requested. |
| Browser p5.js / NW.js / Node | Preserved compatibility, regression and historical desktop/reference tooling | `package.json`, `package-lock.json`, `npm ci` and JS smoke tests govern this **legacy lane only**. Do not infer that native Unreal requires the npm dependency tree. Historical Windows NW.js/NSIS publishing remains **security-held**; CI release blocks must stay intact. |
| Notion canon/design and creator-approved artwork | Creative authority and design decisions | Creator acceptance of a reference image **does not grant approval** to a procedurally generated GLB, imported StaticMesh, shader screenshot, or shipping render. Do not publish restricted postgame material in public repository docs. |

### Player-facing vessel names

**Skybourne → Seabourne → Submersible → Starbourne.** The corresponding serialized C++ enum names/ordinals may still use `Skyborne`, `Seaborne` and `Orbiter` for compatibility; a presentation-label change does **not** override Starbourne's story and geometric locks. [Draft form-label review #699](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/699) is separate from this documentation update.

## Native Unreal review evidence; not shipping acceptance

- [PR #692](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/692) — real UE 5.8.4 Windows compile, **13/13** native automation tests, hull/bridge/wing import, and three ordinary-form D3D12 screenshots at its documented tested heads.
- [PR #697](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/697) — review-only wing UV correction: **1,798** UV-degenerate faces repaired, near-zero bi-normal native import warning reduced **1 → 0**, deterministic generator receipts, and **13/13** native TSTSS tests at its specified source head.
- [PR #700](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/700) — genuine D3D12 Skybourne screenshot using the repaired V3 candidate wing, in a separate native map.
- [PR #705](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/705) — native imported sky and ocean preview: blue ocean rendered on second genuine D3D12 frame but **sky still black**, so **atmosphere visual QA = HOLD**. The parent snapshot is `13c60cbf8f05b16fd50b8fdcaf08eb74919749d7`.
- Other simultaneous ship, Prelude, bridge and fairing PRs must be inspected at their **actual live heads** before stacking, rebasing or making claims. None of the above proves a released UE game, accepted character meshes, finished Chapter 1, continuous swept collision or final art quality.

## Dependencies actually observed in this branch

| Dependency / mechanism | Declared source | Verified current context | Update policy |
| --- | --- | --- | --- |
| Unreal Engine | `unreal/ToSailTheStarrySky.uproject` | `EngineAssociation: 5.8`; author-side Windows reviews used installed **UE 5.8.4**. The .uproject does not pin the patch version. | **Hold engine upgrade** until exact-head native C++ compilation, import, 13+ automation cases, D3D12 captures, compatibility and plugin validation. |
| C++ engine modules | `unreal/Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs` | `Core`, `CoreUObject`, `Engine`, `InputCore`. Existing project compiles with UE engine-provided modules in verified source branches. | Review any additional module dependency for actual symbol use and Windows build success. Avoid speculative additions. |
| Unreal Editor Python / Interchange | Existing engine/editor APIs, local opt-in scripts under `unreal/Tools` | Native review texture and GLB imports verified in isolated editor sessions. The engine-bundled Python integration is an **editor-only workflow**; not a shipped runtime dependency. | Record the plugin/Interchange availability and explicit opt-in; pin and verify before any CI/workstation upgrades. Do not add it to the shipped game without demonstrated need. |
| Source-only Python 3 | `unreal/Tools/*.py`, `unreal/Tests/*.py` | Relevant source generators and source QA use the **Python standard library**; no new `pip` requirements were added for the ship/sky/sea slices. | Prefer standard library, deterministic generators, exact byte/SHA receipts, no-overwrite policies. Introduce a third-party dependency only alongside license, pinned version, lock and CI proof. |
| Historical Node/NW.js tools | root `package.json` + npm lock v3 | Declared: `nw ^0.116.0`, `nw-builder ^4.5.0`, `nwjs ^1.4.4`, `playwright ^1.63.0`. Resolved at this source head: **nw 0.116.0, nw-builder 4.20.0, nwjs 1.4.4, playwright 1.63.0**. Lock has **322** package records. | **No blind upgrade**; preserve the retired Windows release hold, run separate lock-only vulnerability triage and JS smoke tests, and prove desktop compatibility without auto-publishing. This manifest does not pin native UE. |
| GitHub Actions CI | `.github/workflows/*.yml` | Source-only Unreal preflight/inventory vs legacy Node game smoke are distinct; workflow action majors include `actions/checkout@v4` and `actions/setup-node@v4`. | Version upgrades or action SHA pinning need independent workflow evidence and review of permissions/branch protections. Green source CI is not a native Windows test. |

**Security note:** a GitHub push message on this repository reported **18 default-branch vulnerability findings (2 critical, 8 high, 8 moderate)** during November 1 development. This is a *notification*, not an independently inspected list of vulnerable dependency paths, affected versions, remediation or exploitability. Do not attribute those counts to Unreal or npm without reviewing actual GitHub Security/Dependabot records or a dated lockfile-based audit. **No dependency version or lockfile was changed in this register.**

## Safe update sequence

1. **Now — docs and provenance, review-only:** keep this register, Unreal-first/legacy-lane banners, safe PR stacking links, required exact-head evidence and outstanding visual defects up to date; reflect in Notion with public-safe links. Record active head and test status rather than promising completion.
2. **Next — low-risk tooling QA:** add/test an engine-free dependency-manifest inventory and drift checker; audit the historical npm lock, classify advisories and distinguish build-only vs shipped runtime exposure. Audit is *read-only* until decisions are made.
3. **Then — isolated dependency PRs:** for any necessary npm/action/UE plugin update, one bounded package family per PR, preserve old lock and reference evidence, run `npm ci --ignore-scripts` and legacy smoke where relevant, plus native UE 5.8.4 build/import/render for any Unreal-impacting change. Evaluate licenses and no-cost tooling. Never flip a retired release workflow or install/pay for tools implicitly.
4. **Before integration or promotion:** require actual head-pinned test receipts and creator approval of art/canon, formal release authorization, security validation and protected-branch review. Starbourne remains fail-closed.

## Required status vocabulary

Each work report should separately state **IMPLEMENTED SOURCE**, **HOSTED SOURCE TESTS**, **NATIVE COMPILE**, **NATIVE AUTOMATION**, **ASSET IMPORT**, **RENDER EVIDENCE**, **CREATOR ART ACCEPTANCE**, **GAMEPLAY/RELEASE AUTHORIZATION** and **OPEN BLOCKERS**. These labels are not interchangeable; a CI green badge is not cinematic fidelity or a playable release.

**Entry points:** [Unreal README](../README.md), [native verification instructions](../Tools/README.md), [project agent handoff](../../AGENTS.md), [documentation bridge](../../docs/NOTION_SOURCE_INDEX.md). Avoid copying private Notion text into a public repository.
