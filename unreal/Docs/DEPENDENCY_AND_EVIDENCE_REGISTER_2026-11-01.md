# Unreal dependencies and verification evidence register

**Scope:** Unreal-first development under a draft branch; **as-of November 1, 2026**. This is a *source declaration inventory and change-control contract*, not an installed-dependency audit, third-party license approval, release authorization or verified game build. The user selected **Unreal Engine 5.8.4** for forward development; historical Godot and NW.js builds are preserved for reference and recovery, not forward game changes. The separate creator-engine-authority [PR #657](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/657) proposes the canonical root `AGENTS.md` reconciliation; **this PR deliberately does not edit `AGENTS.md`**, to avoid racing that review.

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
