# Unreal 5.8.4 dependency baseline and update policy

**Observed 2026-11-01, review only.** This is a dependency inventory, **not** an engine/package upgrade or a claim of full native project acceptance.

## Native runtime and build requirements

| Component | Observed/pinned in source | Role | Update rule |
| --- | --- | --- | --- |
| Unreal Engine | `unreal/ToSailTheStarrySky.uproject` `EngineAssociation: 5.8`; authorized Windows `neontic` installation reports **5.8.4** | Native Unreal Editor, UBT, automation, D3D rendering | **Hold at 5.8.x** until exact-head native build, tests, import, visual and save checks demonstrate another version works |
| Unreal C++ | Game/Editor Target.cs use `BuildSettingsVersion.V7`, `EngineIncludeOrderVersion.Unreal5_8` | UE 5.8 C++ compilation | Do not change build defaults independently of engine upgrade |
| UE module dependencies | `Core`, `CoreUObject`, `Engine`, `InputCore` in `ToSailTheStarrySky.Build.cs` | Minimal native C++ graph | Add only when a concrete feature requires it, with UHT/link/automation proof |
| Toolchain | Earlier verified native foundation used VS 2022 Build Tools **14.44** and Windows SDK **10.0.26100.0**; same SDK directory observed on `neontic` on 2026-11-01 | Windows compile/link | Record version in each native receipt; verify exact compiler build before claiming current toolchain proof |
| Native automation | `unreal/Tools/Verify-Unreal.ps1`; **15 required names in source registry** on review PR #702 | Build + per-test JSON result check | Native suite at new source HEAD must actually run before claiming 15/15; source registration alone is insufficient |

The earlier **foundation-specific** Unreal Win64 native build and **12/12** automation PASS documented in `UE58_NATIVE_BUILD_VERIFICATION_2026-11-01.md` is valid **only for its recorded source revision**. Likewise, older 13/13 or 14/14 source/native evidence cannot automatically validate later C++ changes. The coupled bridge/quarters PR #702 remains **not natively verified** at its reviewed head. Unreal source/CI PASS and a sampled collision proxy are separate evidence classes.

## Engine-free Python tooling

- On `neontic`, **CPython 3.14.5**, **NumPy 2.5.1**, and **SciPy 1.18.0** were observed on 2026-11-01.
- `unreal/Tools/requirements-geometry.txt` pins **NumPy 2.5.1** as the only third-party package required by the checked-in optional 126-pose geometry scripts. NumPy is **NOT required** for native Unreal/UBT, ordinary Python stdlib contract tests, or GitHub's engine-free source preflight. Tests that conditionally skip NumPy-specific cases in hosted CI do not count as a real generated-mesh geometry run.
- SciPy was observed locally and used in a prior **local-only vertex proximity diagnostic**; no checked-in production Unreal or current source geometry script requires SciPy. Do not add it to the shared Python requirements without a reviewed source dependency and test need.
- Installing `requirements-geometry.txt` is **optional and a developer action**, not a requirement to run the game. This documentation change **does not execute pip, install or upgrade anything**. When a new compatible NumPy is proposed, update the pinned requirement and record Windows Python version, negative fixtures, exact asset hashes, 126-pose receipts, and comparison results on an isolated review branch.

## Legacy browser/desktop lane (DO NOT conflate with Unreal)

The repository root `package.json`/`package-lock.json` belong to the **historical browser, p5.js, NW.js and Playwright development lane**, including the older `nw`, `nwjs`, `nw-builder` and `playwright` packages. This is **not the Unreal C++ runtime dependency graph**. Do not perform an opportunistic `npm update`, remove packages, regenerate the lockfile or run a legacy Windows packaging/release as part of the Unreal review. The legacy NW.js release-security HOLD is documented in `docs/security/LEGACY_NWJS_RELEASE_HOLD_2026-10-26.md`; preserve it.

## Update and QA procedure

1. Identify the **exact branch/head** and which lane the dependency belongs to. Read the `.uproject`, `.Build.cs`, both `Target.cs` files, package manifests and `Verify-Unreal.ps1` before edits.
2. For a **no-install** documentation/metadata update, run `python3 unreal/Tools/check_unreal_dependency_contract.py` and `python3 unreal/Tools/test_unreal_dependency_contract.py`; record all passes against an immutable clean checkout, plus hosted CI.
3. For **NumPy** changes, validate clean install resolution in an isolated environment, run the geometry unit suites *and actual deterministic pinned GLB clearance audit* with independently verified source/asset hashes. If dependencies are unavailable, do not claim geometry PASS.
4. For **Unreal / C++ module** changes, run UnrealHeaderTool and Win64 Editor compilation, all named native tests with report evidence, and actual renderer-enabled import/animation/swept-geometry reviews at the **same exact SHA**. Re-validate save/load and packaged Windows behavior before any promotion.
5. Preserve **PR review-only**, creator-approved four-form art, rotating dome + quarters as a coupled unit, the Starbourne/Orbiter progression hold, and separate structural/crewed-space acceptance. Do **not merge or release** through a dependency update.

## Current open gates

- Ship source branch #702: opt-in coupled habitation pivot, 15 registered tests, 126-sample noncanonical proxy/wing screen, **no native exact-head build or renderer/crew/access certification** yet.
- Wing-root V2 geometry variant #701: better venation clearance on finite samples, **unapproved mechanical hinge connection** and continuous-time HOLD.
- No UE-wide dependency version change, native package install or root npm lock change is authorized or carried out here.
