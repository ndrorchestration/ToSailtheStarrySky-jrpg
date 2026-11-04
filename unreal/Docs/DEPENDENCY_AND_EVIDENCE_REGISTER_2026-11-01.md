# Unreal dependencies and verification evidence register

**SUPERSEDING NATIVE VERIFICATION RECEIPT — 2026-11-02 (exact SHA `e3e3ff5f349c98b2051a18a5f0c3db6097af8040`):** On an authorized Windows `neontic` workstation, an **isolated detached PR #713 checkout** with its two tracked default INI files protected by read-only attributes passed the **Unreal Engine 5.8.4 Win64 Editor UBT build AND all 25 named native automations**, with zero failed, zero not-run and **a clean tracked source tree after testing**. Full `Verify-Unreal.ps1` exited 0. An independent readback found **25 distinct Success records / 25 unique paths / 0 non-success**. Original engine-generated config-write failure from the first unprotected checkout remains a separate preserved diagnostic, not overwritten or ignored. Report SHA-256: `243ad1eedaa344cd52dd4a3380e59cbef34fcfcd3e39c61cc1307195921733a5` (raw report local to the disposable review machine; never upload generated Android File Server tokens). **Evidence status at that exact SHA: `EDITOR_BUILD=PASS`; `NATIVE_25=PASS`; `SOURCE_CUSTODY=CLEAN`; `PIE_P01_P13=NOT_TESTED`; `PRODUCTION_ART=NOT_AUTHORIZED`; `RELEASE=NOT_AUTHORIZED`.** This is *not* an acceptance of actual 13-scenario keyboard gameplay, sea contact/flotation, Splashdown, D3D12 art, packaged install or release. **A subsequent documentation-only SHA cannot inherit the exact-head receipt without its own verification.** See [integrated review gate](INTEGRATION_GATE_2026-11-02.md), [native command and evidence rules](UNREAL_TEST_COMMANDS.md), and [PR #713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713).


**Current November 2 cross-discipline handoff (integrated [draft #713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713)):** This document's older #712 and #685 SHAs are historical, not the active test result. The authorized Windows `neontic` workstation is **online** and its installed `UE_5.8/Engine/Build/Build.version` reports **5.8.4**, with MSVC 14.44 and Windows SDK 10.0.26100. An isolated detached checkout at `fd0b68c28e6289d45f8b8c70228631c24577a352` **passed native Win64 Editor compilation**. A subsequent native Editor automation report contained **25 distinct Success entries / 0 failed / 0 not run**, but the strict post-run clean-tree gate **FAILED**, because Unreal rewrote tracked `DefaultEngine.ini` and `DefaultInput.ini` in that isolated worktree. The first file gained generated Android File Server settings including a local token. **Do not stage, publish or copy any generated token or config diff into documentation or a PR. Do not reset the worktree without reviewing its forensic state.** Native 25/25 acceptance is **HOLD — CONFIG_MUTATION**, despite successful test entries; P01–P13 interactive PIE remains **NOT TESTED**. The log/report evidence is local to the isolated worktree's non-overwriting `unreal/Saved/MigrationEvidence/` path; source SHA and outcome are separated from the now-moving review PR HEAD. **Never infer a newer documentation head has the same native receipt.** See [integrated review gate](INTEGRATION_GATE_2026-11-02.md), [save-safety notes](FIRST_WAKE_REVIEW_OBJECTIVES_2026-11-02.md) and [native test commands](UNREAL_TEST_COMMANDS.md).

**Integration-review overlay (2026-11-02):** This historical cross-branch register is included for evidence and ownership traceability in an isolated composition from #712, #657 and #711. Its November 1 references to editing or not editing AGENTS.md describe the original #711 ownership only. This integrated branch **does include** the scoped #657 AGENTS.md and README.md updates; they are not merged to protected main. The current strict declaration gate is `unreal/Tools/check_first_wake_dependency_contract.py`; `check_dependency_contract.py` is retained as an independent legacy baseline comparator. Neither baseline authorizes an engine/plugin/package upgrade or a release.

**Scope:** Unreal-first development under a draft branch; **as-of November 1, 2026**. This is a *source declaration inventory and change-control contract*, not an installed-dependency audit, third-party license approval, release authorization or verified game build. The user selected **Unreal Engine 5.8.4** for forward development; historical Godot and NW.js builds are preserved for reference and recovery, not forward game changes. The separate creator-engine-authority [PR #657](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/657) proposes the canonical root `AGENTS.md` reconciliation; **this PR deliberately does not edit `AGENTS.md`**, to avoid racing that review.

## Consolidation decision and merge boundaries — November 1, 2026

**Review-candidate register: this file, in a draft branch only.** This section
reconciles the overlapping documentation approaches below; it is **not**
a declaration that any draft branch, dependency setting, or model asset has
been adopted into protected `main`. Choose one integration target and recheck
its exact head before promoting this candidate. Preserve the original dated
Godot/browser evidence and the creator's Unreal-first direction simultaneously.

| Draft | Exact head inspected, 2026-11-01 | Review base / distinct contribution | Consolidation disposition |
| --- | --- | --- | --- |
| [#707](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/707) | `b5ce6647adc1321546356bde7ff720c7336ff98d` | Stacks on #699; Unreal-first root routing, four form display labels, handoff guidance and no-explicit-plugin baseline | Retain the root/agent entrypoint proposal for a **separate** authority review against #657; link useful scope here, do not wholesale copy its ancestor |
| [#708](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/708) | `245c31fe1f02949476338590a0ab0203b4d7bed5` | Stacks on #704; this evidence register, `dependency_baseline.json`, fail-closed checker, native-test commands, First Wake evidence | **Selected review-candidate document and source checker**, NOT merged or canonized; its baseline is specific to its own branch |
| [#709](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/709) | `95139eb3790bc5564abc204f7a1776b645bdfada` | Stacks on #705; Godot/legacy reconciliation, ship D3D12 evidence, auroral/ocean study and **black sky HOLD** | Incorporate its distinct asset/provenance and visual-status *references*, not a duplicate authority register or untested VFX code |
| [#657](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/657) | root-authority draft, head must be rechecked on merge | Root `AGENTS.md`, creator/character authority proposal | **Existing separate owner** for root agent authority; do not race with #707/#709 root-file edits |

### One important branch-specific plugin decision — do not paper over it

The actual `unreal/ToSailTheStarrySky.uproject` manifests fetched at the
three exact documentation heads differ:

- **#708:** `EngineAssociation="5.8"`, runtime module
  `ToSailTheStarrySky`, with explicitly enabled `PythonScriptPlugin`.
  The current `unreal/Tools/dependency_baseline.json` therefore requires
  `enabled_project_plugins=["PythonScriptPlugin"]` in this review stack.
- **#707 and #709:** `EngineAssociation="5.8"`, the same runtime module,
  and **no explicit `Plugins` array**. This means *no project-enabled
  plugins are declared in those particular manifests*, **not** that
  Unreal's engine distribution has no plugins.
- The variants must **not** be normalized by silently changing the baseline
  or suppressing the check. Before taking the checker to a chosen integration
  commit, decide explicitly whether Editor Python needs project-level
  activation, verify editor-only versus packaged-game scope, inspect the
  real manifest and plugin license/packaging behavior, then **write a new
  versioned baseline** with a matching negative-control regression and
  exact-head CI/native proof. Do not infer a runtime Python requirement
  from Editor-only authoring scripts.

**Do not auto-merge the three PRs.** Their parents #699, #704 and #705
contain unrelated naming, First Wake and atmospheric/visual review work.
A green check in one lineage does not establish its content on another.

### Documentation ownership and acceptance ledger

| Area | Preferred owner / next safe action | Admission evidence |
| --- | --- | --- |
| Root `AGENTS.md`, root `README.md`, agent handoff | Reconcile #657 against #707/#709 under one authority edit; date the Unreal-first supersession without deleting original Godot QA | Source diff and explicit creator engine direction; no claim of merged Unreal game |
| Native dependency declarations | This register plus `unreal/Tools/dependency_baseline.json` and `check_dependency_contract.py` | Project/Build.cs/Target.cs/legacy npm lock comparison and negative controls at **integration SHA** |
| Native compilation and automation | `unreal/Docs/UNREAL_TEST_COMMANDS.md`, `unreal/Docs/PRODUCTION_VERIFICATION_MATRIX.md` | Per-PR/commit **SOURCE / GAME BUILD / EDITOR BUILD / NAMED TEST JSON / CLEAN TREE** entries; Live Coding/INI drift must not be bypassed |
| First Wake → Splashdown | `unreal/Docs/FIRST_WAKE_PLAYABLE_LEVEL_SETUP.md` and story handoff | Seven-actor scene and map hashes separately from real **PIE E interaction, F5/F9 save/load, ordered Ionia recruitment, sea landing** |
| Aureate Wake and environment studies | Source/provenance docs for #692, #697, #700, #702, #705, #706 | **IMPORT / D3D12 RENDER / continuous swept COLLISION / CREATOR ART ACCEPTANCE** independently; sampled endpoint checks are not continuous collision proof, and #705's black-sky visual status remains **HOLD** |
| New GLB/texture/character/rig/shader | Asset manifest, rights/source, deterministic input and SHA-256, import path/units, skeleton/LOD and materials | Exact native import/render, clearance or gameplay proof, and separate visual approval; approved 2D references do not approve generated 3D |
| Node/NW.js legacy security | Root `package.json` + `package-lock.json`, security triage **read only** | Confirm affected dependency paths/advisories/fix versions, runtime reachability and Windows legacy tests before any scoped change |

A **GitHub push banner reporting advisory counts is not a package-level
security audit**. No specific affected dependency or safe fixed version has
been independently verified from that notice; do not claim an npm fix or
change an Unreal runtime dependency based on it.

**Explicit holds:** do not install/upgrade Unreal, MSVC, SDK, plugin, Python,
npm, lockfile or GitHub Action major; do not toggle release jobs, merge
protected branches, expose host tokens, promote review art, claim chapter
playability, or unlock Starbourne/Orbiter. Only scoped review documentation,
CI source checks and exact-head evidence can advance here.

## Dependency baseline: what the repository really declares

| Domain | Current declaration | Role and disposition |
| --- | --- | --- |
| Unreal family | `EngineAssociation: "5.8"` in `unreal/ToSailTheStarrySky.uproject`; review workstation UE **5.8.4** observed | Active forward engine; patch installed is host evidence, not enforced by `.uproject` |
| Native Game + Editor targets | `BuildSettingsVersion.V7`, `EngineIncludeOrderVersion.Unreal5_8` | Known reviewed UE5.8 compilation settings; preserve on both targets |
| UE C++ public modules | `Core`, `CoreUObject`, `Engine`, `InputCore` | These are engine-provided modules, not four external package downloads |
| Project-enabled plugin | `PythonScriptPlugin` | Needed for Editor scene staging and native Python verification; **packaged game role not yet evidenced** |
| Project's additional runtime packages | None declared in `unreal/Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs` | Do not infer every transitive engine binary is inventoried or licensed by this table |
| Legacy JS/NW.js | npm root `package.json` and committed `package-lock.json` v3 | Browser/old desktop project; security/release HOLD, NOT an Unreal runtime dependency |
| Legacy root dev dependencies | `nw ^0.116.0`, `nwjs ^1.4.4`, `nw-builder ^4.5.0`, `playwright ^1.63.0` | Existing declaration only; no new install or version update in this change |

The machine-readable snapshot lives in `unreal/Tools/dependency_baseline.json`. `unreal/Tools/check_dependency_contract.py` compares the project, both target build declarations, C++ module dependencies, enabled plugin set, legacy npm manifest, and package-lock root record against that snapshot. CI runs positive and tamper negative-controls. **Passing this proves only that source declarations agree**, not that Epic binaries exist on a host, that dependencies are vulnerability-free, that `PythonScriptPlugin` packages correctly, or that any game starts.

## Current native-engine and gameplay evidence (keep SHA boundaries)

- [Combat integration #685](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/685) at `813abdce`: real UE5.8.4 **Game and Editor Win64 builds PASS**, **23/23 native Editor NullRHI automation tests PASS**, clean-tree verifier exit 0. These are historic facts about **that exact draft head**, not transferable to new ones.
- [Prelude V2 map #694](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/694): source-tracked `.umap` (56,053 bytes, SHA-256 `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80`); real seven-actor verification in a parallel V2 review; no completed keyboard/PIE.
- [Independent Prelude QA #703](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/703): source-level map hash/inputs PASS; new native isolated SaveGame roundtrip pending due to separate Editor's Live Coding.
- [Camera interaction correction #704](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/704) at C++ ancestor `0a6160b4`: actual UE5.8.4 **Game-target UBT build PASS (11/11 actions)**, 24th automation test registered but **24/24 native Editor tests NOT YET RUN**. A **direct, unpackaged Game executable launched unsuccessfully**, logging missing premade asset registry and `BufferReader` assertion/crash. Do **not** call this branch playable; a GitHub repository smoke PASS is not a Windows executable start PASS. The fail-closed crash-log checker now rejects that evidence.
- None of these receipts proves D3D12 art, player walkability, E interaction in PIE, real F5/F9 keypresses, water-physics Splashdown, packaged installer, creator art review or release.

## Dependency update and admission procedure

1. **Observe** current file declarations, installed host versions, plugin sources and licenses; capture exact branch SHA. Check native plugin scope (Editor-only vs packaged) rather than assuming.
2. **Propose** dependency updates separately by domain. Upgrading Unreal family, build tools, or C++ plugins requires an engine-upgrade plan and Game + Editor compile, per-test automation JSON, PIE, save migration/compatibility and packaged-Windows proof. Do not silently change `EngineAssociation` or engine `IncludeOrderVersion`.
3. **New Unreal plugin/module:** document exact product/source/license/version, editor/runtime role, transitive dependency and asset provenance; run import, compile and packaged-game verification. In particular, a plugin or imported asset used only in test tooling must not be presented as production art.
4. **Legacy npm upgrade:** leave root `package.json`/`package-lock.json` frozen until a separate security-impact review, regenerated lock, existing NW/Playwright tests and relevant Windows Defender-on build verification. Avoid legacy feature investment merely to update tools used by the Unreal project.
5. **Host-only tooling:** PowerShell 7, Visual Studio Build Tools MSVC 14.44, Windows SDK 10.0.26100, Python, Node and Desktop Commander are **environment/tool dependencies**, not Unreal in-game modules. Record availability separately from repo declarations; no installs or updates should be inferred by this register.
6. **Only promote with evidence:** source CI is a preflight, not native proof. Preserve exact tested commit, native Game & Editor receipts, full per-test export, clean-tree checks, Visual/PIE screenshots, crash/cook/installer logs and art signoff. Release/merge/canon promotion require creator authorization.

## Documentation reconciliation backlog

| Priority | Document / dependency area | Action and ownership |
| --- | --- | --- |
| P0 | Root `AGENTS.md` | Historical Godot-forward claim conflicts with creator's Unreal-first choice; resolve through **existing draft #657**, not competing edits here |
| P0 | `unreal/README.md`, `unreal/Docs/UNREAL_TEST_COMMANDS.md` | Replace unqualified "no builds or maps" language with exact-head verified-versus-held status; retain historical notes |
| P0 | `unreal/Docs/FIRST_WAKE_PLAYABLE_LEVEL_SETUP.md` | Mark V2 map existence, seven actor proof, unproven PIE and 360/300 camera interaction fix (draft #704) |
| P0 | Runtime startup gate | Distinguish raw un-packaged `.exe` asset registry failure from a cooked/package launch; run a separate engine-supported launch mode before diagnosing C++ as root cause |
| P1 | `unreal/Docs/PRODUCTION_VERIFICATION_MATRIX.md` | Include head-scoped 23 native tests, 24th test pending, crash/Pie status |
| P1 | CI dependency drift | Keep this inventory/source gate on draft; do not auto-install or auto-upgrade anything |
| P2 | Python/visual tools | If the project adopts `requirements.txt`, Python pinning or external DCC asset tools, add only proven package names and hashes; currently standard-library test scripts suffice |
| P2 | Cinematic asset provenance | Require rights, canonical-reference tie-in, checksums, import settings, skeleton/rig/LOD and native D3D12 screenshot before promoting GLB/texture/ship/character sources |

**No engine/plugins/npm package upgrades or production dependency changes are made in this register.** It is a reviewable, low-risk foundation for future verified upgrades.
