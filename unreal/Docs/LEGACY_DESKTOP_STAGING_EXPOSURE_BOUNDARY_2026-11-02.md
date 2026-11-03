# Legacy desktop staging exposure boundary — 2026-11-02

**Scope: read-only source staging audit; no desktop package built, installed, executed or published.** This report continues the real [legacy npm audit](LEGACY_NPM_SECURITY_AND_UE_PYTHON_PLUGIN_SCOPE_2026-11-02.md) and is a separate reversible child of [draft #723](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/723). The release-security hold remains in force under [issue #293](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/293).

## Exact checked source

- Detached, clean Windows checkout: `C:\TSTSS_Review\PR712_LegacySecurity_SourceQA_20261102`; **source head** `d0c9d945af8056e3dd4006f6e03cb015157ca40b`.
- Examined source: `scripts/stage-memories-desktop.js`, root `package.json`, `tests/desktop-package-contract.test.js`, `.github/workflows/desktop-package.yml`, `scripts/build-windows-release.ps1`, tracked `modules/` files and the staged HTML/JavaScript/CSS sources. No downloaded archived release binary or actual built package inspected.
- Script-defined staging payload: the six files `index-embedded.html`, `tosailthestarrysky.js`, `p5.min.js`, `embedded-fonts.css`, `icon.svg`, `icon.ico`, and the recursive `modules/` tree (**29 tracked module files** in this exact source revision).
- The script constructs a dedicated `.desktop-runtime/package.json` manifest with main `www/index-embedded.html`; its manifest literal does **not** declare npm `devDependencies`. It explicitly rejects top-level `tests`, `docs`, `.github`, `node_modules`, and `package-lock.json` in the staging root or `www`.
- Exact-source inventory: **zero tracked `node_modules/` entries**, **zero nested tracked `node_modules/` folders under the 29 `modules/` paths**, **zero `package.json` or `package-lock.json` files under tracked `modules/`**, and **zero direct literal imports of `nwjs`, `nw-builder`, `lodash`, `request`, or `form-data`** in the six named runtime files plus the 29 tracked modules (bounded import-pattern scan, not a complete static/dynamic vulnerability analysis).
- Root `package.json` marks the legacy npm packages as **devDependencies**: `nw`, `nwjs`, `nw-builder`, `playwright`. The historical `package:windows` command targets the staging directory `.desktop-runtime` for `nwbuild` and separately specifies the `NW.js 0.116.0` Windows runtime. This last point is **not proof** of the contents or security of an already-built executable.

## What this proves, and what it does not

| Surface | Source evidence | Confidence / boundary |
| --- | --- | --- |
| Tracked application staging copy | Six listed files and recursive tracked `modules/`; no tracked nested node_modules or matching direct imports in bounded scan | **SOURCE-ONLY STAGING PLAN INSPECTED**. No staged output was generated, no runtime binary checked |
| npm package dependency vulnerabilities | Prior complete `npm audit` on the same lockfile: 32 affected legacy npm package entries (3 critical, 15 high, 14 moderate), including direct `nwjs` and `nw-builder`; critical transitive `form-data`, `lodash`, `request` | **AUDIT OBSERVATION**, not unique advisories or demonstrated shipped runtime exploitability |
| NW.js runtime / native executable contents | Historical packager requests NW.js 0.116.0, but creates its executable from external tooling/runtime | **BINARY CONTENT AND TRANSITIVE RUNTIME EXPOSURE NOT VERIFIED**. npm advisory coverage does not establish its Chromium/Node binary security |
| Historical NSIS install/uninstall | [Security issue #293](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/293) records a real Windows Defender `Trojan:Win32/Bearfoos.A!ml` detection of a QA generated uninstaller; security classification unresolved | **SECURITY HOLD**. Do not execute, restore, whitelist, rebuild, publish or redistribute flagged artifacts |
| Current release controls | `.github/workflows/desktop-package.yml` is an inert legacy workflow with no push/tag publisher and read-only token; manual dispatch rejects execution. `scripts/build-windows-release.ps1` throws `SECURITY_HOLD_293` before npm/NSIS/Start-Process | **SOURCE CONTAINMENT VERIFIED**, not an exhaustive audit of every workflow, older tag or previously distributed binary |
| Native Unreal C++ game | `unreal/ToSailTheStarrySky.uproject` and `Build.cs` declare UE5.8 and engine-provided modules, independent of root NW.js npm devDependencies | **DISTINCT DEPENDENCY LANE**. Does not attest native Unreal plugin packaging or installed UE security |

**Key interpretation:** The scanned **source staging plan does not directly include the audited npm development dependency tree**. This **does not clear the NW.js runtime, the historical Windows installer/uninstaller, dynamic imports, untracked local files, outside-stage packaging inputs or the current production game**. A library absent from the staged JavaScript tree can still affect the packaging host, build chain, external binaries or historical artifacts. No claim is made that all 32 advisory findings are irrelevant.

## Safe next verification, in priority order

1. Record actual GitHub Dependabot advisory IDs/path/severity and correlate them to the npm-lock snapshot. The earlier push-banner **18 alerts** and direct npm audit **32 affected package entries** are different observations.
2. Conduct a **nonexecuting, isolated artifact manifest inspection** only after security authorization for an existing trusted candidate, with SHA-256 and Defender-on custody. No downloading, restoring, running or rebuilding the historically flagged installer or uninstaller under the present hold.
3. For proposed legacy tooling remediation, review supported upstream versions/licenses, direct and transitive affected paths and whether install-time/build-only packages are used to generate the binary; avoid automatic `nwjs@0.0.15` and `nw-builder@4.2.1` downgrade suggestions. Any dependency changes require a separate reversible PR, fresh lock review and independent Windows/Defender validation.
4. Keep Unreal Engine native Game+Editor, `PythonScriptPlugin` preload/cook/package, screenshots, tests, creator art acceptance and release permissions as **separate gates**. Nothing here unlocks Starbourne.

**No package, lockfile, application asset, publisher workflow, Unreal runtime dependency, engine or machine package was changed in this source audit. No live legacy game or uninstaller was run.**
