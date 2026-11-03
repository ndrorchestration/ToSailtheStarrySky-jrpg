# Legacy npm advisory and root-dependency mapping — 2026-11-02

**Status: READ-ONLY SECURITY TRIAGE, NOT REMEDIATION OR SHIPPING CLEARANCE.** Review-only child of [draft #725](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/725), which follows #723 and #711. This note does not modify any dependency or establish that a vulnerable package appears in any distributed application. The [historical NSIS security hold #293](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/293) remains active.

## Evidence provenance and source boundary

- **Git source head inspected:** `6dea499ef470303b2a885985847da9a121642a34`, clean detached Windows checkout `C:\TSTSS_Review\PR724_StagingExposure_SourceQA_20261102`. npm `package-lock.json` v3 contains **322** package records and four direct root devDependencies (`nw`, `nwjs`, `nw-builder`, `playwright`).
- **Audited lockfile:** raw Windows SHA-256 `cbd32a793748f2aa7f6e538057ca4e38113ec229ce98a0854b312e386dd005f6`; canonical LF-normalized SHA-256 `f9aecbddb8453d868627023bac06700df6082c0000fbf98876ec94dd482ffdce`. These reflect the same Git-tracked dependency data despite CRLF versus LF.
- **npm observation:** full `npm audit --json --package-lock-only --ignore-scripts --no-fund --loglevel=silent` on **2026-11-02 22:29 America/New_York / 2026-11-03T03:29:40Z**, npm 11.17.0 / Node v24.16.0. Result: **32 distinct affected package entries**, **3 critical / 15 high / 14 moderate** (package-level severity aggregation). The npm command reported vulnerabilities with exit 1; the JSON-reading wrapper completed successfully.
- **Actual repository GitHub Dependabot observation:** authorized, read-only GitHub REST GET `/repos/ndrorchestration/ToSailtheStarrySky-jrpg/dependabot/alerts?per_page=100&state=open` from the existing authenticated Windows GitHub CLI session, on November 2 US Eastern / November 3 UTC. The API returned **18 OPEN alerts: 2 critical, 8 high and 8 medium**, all declared **`scope=development`** and **`manifest_path=package-lock.json`**. This independently confirms the old **18-alert GitHub banner count**, rather than inferring it from the banner. Because 18 is below the API page size of 100, this request returned the complete currently open result set for that filter; it is a point-in-time snapshot, not future monitoring.
- The GitHub snapshot had **18 unique GHSA IDs; every one of those 18 IDs appears among the **25 distinct inline GHSA IDs** present in the npm audit JSON. The **7** additional npm-inline GHSA IDs are **not** among these currently open GitHub alerts. Distinct advisory IDs do not equal affected-package counts; an npm entry can aggregate multiple advisories or transitive package effects.
- Local-only raw audit evidence at `C:\TSTSS_Review\PR711_NpmReadOnlyAudit_20261102`: `npm-audit-complete.json`, SHA-256 `ecc4ed936f9a8b1a79cfbcbbbdb5dea8a7f7ac5498627985ea6266cd4656590b`; a sanitized full read-only GitHub open-alert snapshot `github-open-dependabot-alerts-20261102.json`, SHA-256 `d97688f7e30a0c5e7e33d051c0dfab2ec930d41207bcb4d857b219fd88470235`; a source-graph path reconstruction `npm-advisory-dependency-paths-20261102.json`, SHA-256 `fbcd69e8590bcb44c547c052d052ef56f4aa39c37457d62288a6ef51a0a087d2`. Full reports remain on the authorized workstation, not published in this PR.

## Root devDependency reachability in committed npm lockfile

A read-only Python walk reconstructed `packages` dependency/optionalDependency paths in the lockfile using Node-style ancestor `node_modules` lookup. The audit's 32 `vulnerabilities[*].nodes` matched 32 lockfile affected package entries with **zero unresolved audit nodes, zero unresolved dependency edges and zero unmapped affected packages** in the observed lockfile graph. These are **declared transitive package relationships**, not an executed module trace or a guarantee of build/install/download/runtime reachability.

| Direct root dependency | Number of the 32 affected package entries reachable |
| --- | ---: |
| `nwjs` | **28** |
| `nw-builder` | **6** |
| Shared by both | **2** (`glob`, `minimatch`) |
| `nw` | **0 in this npm report** |
| `playwright` | **0 in this npm report** |
| Unmapped in inspected lockfile | **0** |

**28 + 6 − 2 = 32 unique affected package entries.** Counts overlap. The **18 currently open GitHub Dependabot alerts** all map to packages reachable from the root **`nwjs`** devDependency under this lockfile reconstruction. This does **not** mean only `nwjs` has security risk, or that `nw-builder` does not; npm reported six package entries on the latter's path.

### Package-by-package source dependency roots (audit-observed severities)

| npm audit affected package | Audit severity | Direct legacy devDependency roots |
| --- | --- | --- |
| `@nwutils/builder` | Moderate | `nw-builder` |
| `aimer` | High | `nwjs` |
| `archiver` | Moderate | `nw-builder` |
| `cheerio` | High | `nwjs` |
| `configstore` | High | `nwjs` |
| `css-select` | High | `nwjs` |
| `css-what` | High | `nwjs` |
| `dot-prop` | High | `nwjs` |
| `extract-zip` | High | `nwjs` |
| `form-data` | Critical | `nwjs` |
| `glob` | Moderate | `nw-builder`, `nwjs` |
| `got` | Moderate | `nwjs` |
| `latest-version` | Moderate | `nwjs` |
| `lodash` | Critical | `nwjs` |
| `meow` | High | `nwjs` |
| `minimatch` | Moderate | `nw-builder`, `nwjs` |
| `node-fetch` | High | `nwjs` |
| `nth-check` | High | `nwjs` |
| `nugget` | Moderate | `nwjs` |
| `nw-builder` | Moderate | `nw-builder` (direct) |
| `nwjs` | High | `nwjs` (direct) |
| `nwjs-versions` | High | `nwjs` |
| `package-json` | Moderate | `nwjs` |
| `pget` | Moderate | `nwjs` |
| `qs` | Moderate | `nwjs` |
| `readdir-glob` | Moderate | `nw-builder` |
| `request` | Critical *aggregate npm entry* | `nwjs` |
| `shelljs` | High | `nwjs` |
| `tough-cookie` | Moderate | `nwjs` |
| `trim-newlines` | High | `nwjs` |
| `update-notifier` | High | `nwjs` |
| `uuid` | Moderate | `nwjs` |

**Critical-entry representative lockfile paths:**

- `nwjs@1.4.4 → pget → nugget → request@2.88.2 → form-data@2.3.3`. The npm report includes [GHSA-fjxv-7rqg-78g4](https://github.com/advisories/GHSA-fjxv-7rqg-78g4) and another `form-data` advisory. GitHub currently shows two open `form-data` advisories under this development lockfile.
- `nwjs@1.4.4 → nwjs-versions → aimer → cheerio → lodash@3.10.1`. The npm audit aggregates several `lodash` advisories, and GitHub has multiple open distinct `lodash` alerts.
- `nwjs@1.4.4 → pget → nugget → request@2.88.2`. Its **npm entry is critical in aggregate**, partly because it affects downstream packages; the separately published [GHSA-p8p7-x288-28g6](https://github.com/advisories/GHSA-p8p7-x288-28g6) itself is **moderate**, not critical. **Do not relabel the underlying advisory as critical** based on npm's aggregate entry severity.

## Shipping boundary, remediation and caveats

The existing [staging-source audit](LEGACY_DESKTOP_STAGING_EXPOSURE_BOUNDARY_2026-11-02.md) established only that six named runtime source files and 29 tracked `modules/` files were designated for staging, with no tracked `node_modules` or direct literal imports of selected audited names. The staging script and retired Windows publisher **do not prove anything about the external NW.js runtime, Node/Chromium binaries, previously packaged NSIS installer or uninstaller, dynamic imports, build-host scripts or untracked inputs**. Those remain unknown or **SECURITY HOLD**.

**No automatic `npm audit fix` or version changes.** npm suggested direct-root changes to `nwjs@0.0.15` and `nw-builder@4.2.1`, which would be untested major **downgrades** compared with this lockfile's `nwjs@1.4.4` and `nw-builder@4.20.0`. Each proposed remediation needs compatibility, license, provenance, lockfile, Windows Defender and release-gate review in its own isolated PR. Do not execute, restore or whitelist the historical Defender-flagged uninstaller.

**Status vocabulary:** `AUDIT OBSERVATION: VERIFIED AT DATE`; `DEPENDENCY LOCK GRAPH MAPPING: VERIFIED AS SOURCE DATA`; `GITHUB OPEN ALERT SNAPSHOT: READ-ONLY VERIFIED`; `BUILD TOOL HOST EXPOSURE: UNDETERMINED`; `HISTORICAL BINARY DISTRIBUTION EXPOSURE: UNVERIFIED`; `SECURITY REMEDIATION: NOT PERFORMED`; `NATIVE UNREAL SECURITY EFFECT: NOT ESTABLISHED`; `LEGACY INSTALLER RELEASE: HOLD`.

No release, dependency installation/upgrade, Unreal module/plugin change, canon/art promotion, Starbourne unlock or merge authorized by this source analysis.
