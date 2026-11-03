# Legacy npm security triage and Unreal Python plugin scope — 2026-11-02

**Decision status: READ-ONLY EVIDENCE / REMEDIATION HOLD.** This report is a
review artifact stacked on [draft #711](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/711).
It is **not** an authorization to modify a dependency, enable/disable a plugin,
merge, package, release, or claim the Unreal game is vulnerable to these npm
advisories. Preserve all historical Godot/NW.js source and current Starbourne
story/review gates.

## Exact-source legacy npm audit — completed, not repaired

- Audit date: **November 2, 2026, 22:29 America/New_York**
  (**2026-11-03T03:29:40.028121+00:00** receipt time).
- Isolated, clean Windows repository clone:
  `C:\TSTSS_Review\PR711_ConsolidatedDocs_SourceQA_20261101`;
  **exact source commit** `4e4a40aed34c0ff6789ce4a69ca757f75139fee2`
  from draft #711. npm 11.17.0 on Node v24.16.0.
- The query used `npm audit --json --package-lock-only --ignore-scripts
  --no-fund --loglevel=silent`, with npm cache and output **outside** the Git
  tree. The direct npm audit process returned **exit 1 because it reported
  vulnerabilities**. The evidence wrapper then parsed and validated a
  complete version-2 JSON report and exited **0**. An earlier stderr/PowerShell
  wrapper attempt was incomplete and is **not** the evidence cited here.
- Read-only response: **32 affected package entries** —
  **3 critical, 15 high, 14 moderate; 0 low**, according to the live npm
  audit service at this observed time. Counts are package-level findings, **not**
  unique GHSA IDs, proof of exploitable production exposure, or an
  independently verified GitHub Dependabot-alert count.
- Critical transitive packages: **`form-data`, `lodash`, `request`**.
  Directly declared affected development packages:
  **`nwjs` (high)** and **`nw-builder` (moderate)**.
  The other findings are transitive dependencies in the historical
  Node/NW.js toolchain, **not Unreal `Build.cs` or `.uproject` packages**.
- **Do not run `npm audit fix` automatically.** The audit suggests
  `nwjs@0.0.15` and `nw-builder@4.2.1` as major-version-change
  remediations for affected direct dependency chains. These are
  **downgrades relative to the existing lock** (`nwjs@1.4.4`,
  `nw-builder@4.20.0`) and **not validated as compatible** with the
  historical desktop renderer/build. `fixAvailable: true` on an
  individual transitive node likewise does not establish application-level
  safety, reachability or compatibility.
- **Exact lockfile SHA-256 before AND after:**
  `cbd32a793748f2aa7f6e538057ca4e38113ec229ce98a0854b312e386dd005f6`.
  For cross-platform checks, Git's LF-normalized checkout bytes hash to
  `f9aecbddb8453d868627023bac06700df6082c0000fbf98876ec94dd482ffdce`.
  Windows Git's CRLF working-tree conversion **changes raw-byte hashes but
  not the audited dependency declarations**; the raw Windows receipt and
  LF-normalized canonical hash must be treated separately. This was
  confirmed after a GitHub Linux runner first rejected an incorrectly
  cross-platform raw-byte assertion. Repository `git status --porcelain`
  remained **empty**.
  No package/lockfile was installed, upgraded, downgraded or modified;
  no package scripts executed; no publisher/release work was resumed.
- Private, local-only evidence: raw complete npm JSON at
  `C:\TSTSS_Review\PR711_NpmReadOnlyAudit_20261102\npm-audit-complete.json`
  SHA-256 `ecc4ed936f9a8b1a79cfbcbbbdb5dea8a7f7ac5498627985ea6266cd4656590b`;
  derived sanitized package summary `npm-audit-summary.json` SHA-256
  `f286c4fc733a530c9a2c7506a00737133606afa3d69c66e56f4387dd78ec1da1`.
  These files have not been uploaded to the public repository.

**Why the earlier GitHub alert banner differs:** a prior push notification
reported **18 default-branch alerts** (2 critical, 8 high, 8 moderate).
That was a snapshot of a *different* alert source and reference, not a parsed
npm audit. The now-confirmed **32** npm package-level findings on draft
#711's lockfile must **not** be silently equated to GitHub Dependabot's
individual advisories, versions, alert lifecycle, or security scope. Actual
GitHub security-alert records remain **NOT INSPECTED** in this slice.

## Native UE5.8.4 Python plugin — descriptor-level finding

Inspected the installed engine descriptor **without editing it**:

`C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\PythonScriptPlugin\PythonScriptPlugin.uplugin`

- Descriptor SHA-256:
  `bd796b32b69f8c4113e0b2547ee12e3620507c063f23090d5cc6042ad387b5cb`.
- **`EnabledByDefault: false`** in the installed engine.
- Declared modules: **`PythonScriptPluginPreload`: `Runtime`,
  `EarliestPossible`**; and **`PythonScriptPlugin`: `UncookedOnly`,
  `PreDefault`**.
- The project `.uproject` on #708/#711 explicitly enables
  `PythonScriptPlugin`, while the manifests examined at #707/#709
  contain **no explicit Plugins array**. They are not equivalent review
  configurations. The module categories are **not proof** that enabling
  the plugin is packaged-game safe or that the runtime preload cannot
  enter a Windows build. A general assertion that the entire plugin is
  *Editor-only* is incorrect at this observed engine descriptor.
- **Open decision:** if future Unreal authoring relies on project-enabled
  Python, identify required Editor scripts and precise loading stage, then
  choose explicit project-level activation versus a separate authoring
  workspace. On the **selected eventual integration source SHA**, test
  Game+Editor UHT/MSVC, named automation, actual Editor Python imports,
  cooked/packaged Win64 behavior and plugin-specific runtime/cook logs
  before ratifying the dependency baseline. Reconcile its
  `dependency_baseline.json` with the **actual** chosen `.uproject`;
  never alter or weaken the checker just to make a merged branch green.

## Ordered remediation / dependency update gates

1. **Legacy security triage, no writes:** Obtain the actual GitHub
   Dependabot advisories and match GHSA, vulnerable package/version,
   lockfile path, severity, direct/transitive role, fix candidates and
   **whether dependencies reach installed legacy desktop artifacts**.
   Preserve the historical NW.js release hold until the risk is understood.
2. **Separate compatibility proposals:** For each independently justified
   npm dependency remediation, select a supported replacement or scoped
   transitive version with licenses and an expected behavior delta. Do
   not automatically accept the `nwjs@0.0.15` or
   `nw-builder@4.2.1` downgrade suggestions.
3. **Reproducible verification:** In a new isolated PR, regenerate and
   review `package-lock.json` only if changes are proposed. Require
   package and installer smoke, Windows runtime/Defender-on acceptance,
   unchanged release gates and a fresh audit. No auto-deploy.
4. **Unreal plugin decision:** Record a separate explicit decision
   on whether the installed `PythonScriptPlugin` should be enabled in
   the chosen project lineage, and prove its Game/Editor/packaged role.
   Never conflate npm remediation with Unreal plugin upgrades.
5. **Maintain evidence labels:** `SOURCE DECLARATIONS`, `AUDIT
   OBSERVATION`, `REMEDIATION VERIFIED`, `NATIVE BUILD`,
   `PACKAGE TEST`, `CREATOR APPROVAL`, and `RELEASE AUTHORITY`
   are independent. At this audit, only the first two have evidence.

**Current conclusion:** audit observed real legacy tooling risk requiring
security review, but **no remediation tested, no exploitable shipping path
established, no Unreal runtime vulnerability inferred, and no dependency
version or plugin status changed**.
