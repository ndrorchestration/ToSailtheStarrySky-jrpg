# Legacy desktop retirement, npm candidate, and safe-check matrix — 2026-11-03

**STATUS: REVIEW-ONLY SECURITY/DEPENDENCY QA — NO INSTALLER, PACKAGE, RELEASE OR MERGE AUTHORIZED.** This document is stacked on [draft #728](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/728), the scratch-only `nwjs` wrapper removal model. It addresses a false failure in the retired historical desktop packaging contract and inventories outstanding security and license gates. Source changes in this child are **documentation, test expectations and CI-only**; the historical `package.json` and `package-lock.json` are not changed.

## Exact-current source and Windows environment

- Parent draft #728 was checked **open, unmerged, review-only**, head `e9f336149d5e7172e40a79badf63bd0548ced731`.
- At that exact head, a clean authorized Windows review checkout `C:\TSTSS_Review\PR728_ScratchCandidate_SourceQA_20261102` was inspected; a separate child checkout `C:\TSTSS_Review\PR729_RetirementContract_SourceQA_20261103` at initial review commit `e77dd58cfc60f407009b950d23f33d35b5bb8f8f` returned `Aetherwake archived desktop source layout and security hold: PASS (no build)` for the corrected desktop source test.
- User machine observed approximately **6,156 MiB free RAM** and **13.86 GiB free disk**, with an active `UnrealEditor.exe` process. Do **not** start a competing UE 5.8.4 native Game+Editor/packaging build under that resource contention or terminate someone else's Editor. No native Unreal verification occurred in this slice.

## Checks run without installing or executing held binaries

A recorded read-only Windows test sweep at source SHA `e9f336149d5e7172e40a79badf63bd0548ced731` wrote logs **outside Git** under `C:\TSTSS_Review\PR728_AllSafeChecks_20261102`. It produced SHA-256 `c0c3a0cb8bd4003b973c08f9ef111b2c35761463d6cc8b6a977fe61e9a5d6475` for `safe_checks_summary.json`. The original source checkout and lockfile hashes remained unchanged, no scratch `node_modules` folder was created.

| Test/check at parent exact SHA | Result | Meaning |
| --- | --- | --- |
| Scratch-only `nwjs` removal in-memory candidate model | **10/10 PASS** | Same 94 kept / 228 removed package paths; not installation |
| Dated affected npm advisory root mapping | **8/8 PASS** | Tracked lockfile path model, not executed reachability |
| Bounded legacy app staging exposure | **9/9 PASS** | Source copy boundary only |
| Actual npm audit/plugin descriptor claim controls | **8/8 PASS** | Receipt and versioned source scope, not native |
| Dated dependency register reconciliation | **8/8 PASS** | Source authority/manifest consistency only |
| Baseline dependency declaration tests | **14/14 PASS** | Source contract matches held legacy lock; no upgrade |
| Standalone `check_dependency_contract.py` | **PASS** | `DECLARATIONS_MATCH_REVIEW_BASELINE_NOT_NATIVE_OR_SECURITY_PROOF` |
| `node scripts/verify-legacy-release-hold.mjs` | **9/9 PASS** | Historical GitHub workflow and PowerShell local path fail closed |
| `node --test tests/legacy-release-hold-safety.test.js` | **4/4 PASS** | Synthetic control mutations and isolated refusal, no installer |
| Scratch `npm ls --package-lock-only --all --json --offline` | **PASS** | Scratch lockfile dependency tree coherent, no executable |
| Original `node tests/desktop-package-contract.test.js` | **FAIL — STALE TEST** | Old test demands `npm ci`, `nwbuild`, NSIS and a live publisher in an intentionally retired workflow. First error: `desktop workflow must use the lockfile`. Its expectation is superseded by security hold #293, not proof the publisher should be restored |
| Revised source-only desktop contract at child initial SHA | **PASS** | Explicit retirement-aware static gate: no push/tag, write token, build/install/release steps; manual refusal; local PowerShell early hold; original staging/layout/UI source structure retained |

The corrected contract **does not** execute `npm`, `nwbuild`, NSIS or any game. It no longer requires README or the archival desktop guide to advertise an active installer. The old guide `docs/DESKTOP_BUILD.md` now begins with a prominent **RETIRED / SECURITY HOLD** warning, superseding its obsolete October 6 release-success claims and installation procedures while preserving their historical provenance.

## Candidate license and installer-script metadata (not legal clearance)

A purely read-only JSON inventory of the 94-record scratch candidate lock found **93 non-root packages** with populated license metadata fields: **MIT 69**, **Apache-2.0 12**, **BlueOak-1.0.0 8**, **ISC 3**, and **BSD-3-Clause 1**; **zero missing license metadata fields**. This is only declared lockfile metadata, **not a third-party rights or actual packaged license audit**. The candidate still contains `node_modules/nw` with `hasInstallScript=true`; removing the deprecated `nwjs` wrapper does **not** make future package installation or build-script execution risk-free. The original lock had install-script metadata for both `nw` and `nwjs`. The local-only inventory `candidate_license_installscript_inventory.json` SHA-256 is `b732046f7adaaa52fcc7ab99d8d23536c6d001ed6e83a55034f374f491a081b6`.

The separate scratch npm audit observation still stands: baseline **32** affected entries (3 critical / 15 high / 14 moderate) versus `nwjs`-removed scratch lock **6** entries (all moderate, `nw-builder` branch). It remains a **hypothesis for a later reviewed manifest/lock/baseline PR**, not a GitHub default-branch fix, binary compatibility claim, or security authorization.

## Critical residual containment gap: direct npm command

**WARNING: the existing security-hold guards are not repo-wide.** The obsolete `.github/workflows/desktop-package.yml` is blocked on manual trigger with read-only token and no publisher, and `scripts/build-windows-release.ps1` throws before packaging. However, root `package.json` still declares a directly invocable:

`npm run package:windows` → `npm run stage:desktop && nwbuild --mode=build --platform=win --version=0.116.0 ...`.

Its `package:windows:clean` script aliases `npm run package:windows`. **Neither direct npm CLI is guarded by the disabled GitHub publisher or the PowerShell throw.** This is an **UNREMEDIATED bypass of the two *specific* launch guards**, not evidence that somebody ran it. Do **not** run either command or any old NSIS package/installer/uninstaller, even for testing. Further containment should be proposed and reviewed separately, preserving the historical build recipe in Git history while placing an early unconditional fail-closed guard on the direct npm entrypoint. That would require an explicit changeset to root `package.json`, review of associated lock/source tests, and separate authorization—not an unnoticed side effect of this child PR.

## Outstanding gates and authority

1. **Root direct CLI containment not achieved:** `npm run package:windows` and `package:windows:clean` remain callable. Replacing them requires a separate reviewed security containment diff; until then, warning/documentation is the only added protection.
2. **Actual scratch candidate package compatibility not proven:** `npm ci`, `nwbuild`, real NW.js runtime and NSIS must **not** be run under the current #293 security hold merely to seek a green check. The `nw` install-script metadata further prevents an unwarranted "no installation risk" claim.
3. **Historical binary security remains unresolved:** [Defender issue #293](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/293) is OPEN; real `Trojan:Win32/Bearfoos.A!ml` was detected in a historical QA uninstaller. Neither a false-positive nor malicious-root-cause conclusion is established. No flagged binaries were restored, whitelisted, executed, rebuilt or distributed in this audit.
4. **Legal and advisory review incomplete:** lockfile license fields were present, but license text and distribution rights are **not** independently approved; six moderate npm package entries remain in the scratch candidate; 18 previously verified open GitHub development-scoped Dependabot alerts will not close from this scratch-only review.
5. **UE native Game/Editor/packaged plugin checks HOLD:** installed `PythonScriptPlugin` contains a Runtime preload and UncookedOnly module; source preflight does not validate cooked/packaged Win64 or the renderer. Active UE Editor and limited memory/disk prevented a safe new native build in this slice. Ship/Starbourne/collision/art gates remain separate.
6. **Canonical source and protected main untouched:** no dependency/version/lockfile/engine/Unreal source/runtime or release authorization changes, no merges or creator approval inferred.

**Result:** `SAFELY_EXECUTABLE_SOURCE_CHECKS=COMPLETED`, `RETIRED_DESKTOP_TEST_MISMATCH=CORRECTED_IN_DRAFT`, `DIRECT_NPM_PACKAGER_BYPASS=OPEN`, `REAL_PACKAGE_COMPATIBILITY=UNVERIFIED`, `DEFENDER_INSTALLER_HOLD=ACTIVE`, `UNREAL_NATIVE_PROOF=NOT_ATTEMPTED`, `MERGE_OR_RELEASE=NOT_AUTHORIZED`.
