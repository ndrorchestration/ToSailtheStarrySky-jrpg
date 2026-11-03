# Legacy `nwjs` npm wrapper removal: scratch-only candidate — 2026-11-02

**STATUS: SOURCE/LOCKFILE-ONLY EXPERIMENT — NOT APPLIED OR APPROVED.** This is a reversible documentation/test child of [draft #727](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/727), not a request to merge, install software, build a legacy game, release an installer, dismiss advisories or alter the authoritative dependencies. [Security issue #293](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/293) remains **OPEN** after a real Windows Defender detection of a historical QA NSIS uninstaller. Its classification is unresolved; **do not run, recover, whitelist, build or distribute** that held installer/uninstaller.

## Hypothesis

The **npm package named `nwjs`** (`^1.4.4`, locked 1.4.4) may be a redundant legacy **development wrapper**, **not the actual NW.js runtime used by the game**. The root manifest independently declares `nw@^0.116.0`, `nw-builder@^4.5.0`, and `playwright@^1.63.0`. The historical `package:windows` command invokes **`nwbuild`** from `nw-builder` with an explicit **NW.js runtime `--version=0.116.0`**. The browser game itself uses the global `nw.Window` API when available; that does not imply it imports the npm package named `nwjs`.

At source SHA `011a05616a60ce3a7103dcbbafd54ea4dc5ed216`, a read-only scan across **tracked repository files** found `nwjs` npm package references in the root manifest/lockfile and the newer **audit documentation/test inventory**, but no direct executable code import, shell invocation or active package script that explicitly needs the npm wrapper. **Absence of a textual import is not proof that the historical build works after removal.** Preserve the original historical Aetherwake/JS/NW.js material and all feature/release holds.

## Non-installing, isolated Windows experiment

An isolated scratch directory, `C:\TSTSS_Review\PR728_UnusedNWJS_LockOnly_20261102`, was created by copying **only `package.json` and `package-lock.json`** from the clean detached exact source head above. No original project file was edited. Scratch `package.json` and the lock root declaration had only `nwjs` removed from `devDependencies`. With Node **v24.16.0** / npm **11.17.0**, the following commands were run **only in that scratch directory** with cache also isolated outside the repository:

```powershell
npm install --package-lock-only --ignore-scripts --no-audit --no-fund --no-save
npm prune --package-lock-only --ignore-scripts --no-audit --no-fund
npm audit --json --package-lock-only --ignore-scripts --no-fund --loglevel=silent
npm ls --package-lock-only --all --json --offline
```

The first `npm install --package-lock-only` canonicalized the lock but initially retained now-orphaned `nwjs` paths; the **`npm prune --package-lock-only`** step removed them. Both exited 0, no `node_modules` directory was created, no install scripts ran, and the original checkout stayed clean. No `npm ci`, `nwbuild`, NSIS, installer, uninstaller, Unreal Editor, native build or packaged game was run. npm registry access for lockfile metadata/advisory lookup is **not** a security clearance or offline runtime proof.

### Exact source and comparison receipts

| Measure | Original dated lock | Scratch proposal |
| --- | ---: | ---: |
| Lockfile package records | **322** | **94** |
| Records removed by pruning | — | **228** |
| Added package records | — | **0** |
| Non-root survivors with changed version | — | **0** |
| Non-root survivors with changed package metadata | — | **0** |
| Root direct development dependencies | `nw`, `nwjs`, `nw-builder`, `playwright` | `nw`, `nw-builder`, `playwright` |
| `nw` locked version | **0.116.0** | **0.116.0** |
| `nw-builder` locked version | **4.20.0** | **4.20.0** |
| `playwright` locked version | **1.63.0** | **1.63.0** |
| Existing `scripts` content | unchanged | **identical** |
| npm audit: critical affected packages | **3** | **0** |
| npm audit: high affected packages | **15** | **0** |
| npm audit: moderate affected packages | **14** | **6** |
| npm audit: all affected package entries | **32** | **6** |

The **six remaining moderate** affected packages, reported by the live npm audit on this scratch lock, are `@nwutils/builder`, `archiver`, `glob`, `minimatch`, `nw-builder`, and `readdir-glob`. These remain on the **`nw-builder` development-tool chain**. npm audit exit 1 indicates remaining vulnerabilities; a complete valid JSON was parsed. No automatic `npm audit fix` or suggested major **downgrade** was applied.

`npm ls --package-lock-only --all --json --offline` exited **0** on the candidate lockfile, listing `nw`, `nw-builder` and `playwright` as its top-level dependencies, with no reported `problems`. **This is lockfile consistency only**; it neither runs any of those packages nor verifies NW.js 0.116.0 executable/packager behavior.

The in-memory Node-style `dependencies` plus `optionalDependencies` root traversal from just those three remaining devDependency roots independently reproduced the exact **94** candidate package paths (including the `@node-rs/crc32` platform optional packages) with **zero missing and zero extra entries** compared with npm's scratch-pruned lock. This is a structural check, not a replacement for a real package/install test.

**Evidence fingerprints and custody** (all detailed reports remain local on the authorized workstation, **not published**):

- Original `package-lock.json` Windows SHA-256: `cbd32a793748f2aa7f6e538057ca4e38113ec229ce98a0854b312e386dd005f6`; canonical LF version: `f9aecbddb8453d868627023bac06700df6082c0000fbf98876ec94dd482ffdce`.
- Scratch-pruned `package-lock.json` SHA-256: `5d3132ecb33c1f3afd2363284f032c058caaa61ba51aa61ed0e1b26dc88d157f`.
- Scratch npm audit complete JSON SHA-256: `184f179517bb2900ab70330d33ab4f5e4cb7e9fa435a1b91c1347f69ba3e954b`. Audit JSON observed **2026-11-03T04:50:12.898959Z** (November 2 in US Eastern).
- Sorted remaining package-path list SHA-256 (UTF-8, LF joined, no final newline): `5f9cd3285febfa5852bdde3793dee7bab8b74ec4d87961197a1150beb195d350`.
- Sorted removed package-path list SHA-256 (same encoding): `85acffa1fb88e8eb7f79ebae3d4242685eea0e23a8b813920998ae0ead2edb31`.
- Full source checkout remained clean; no package/lockfile modifications to the Git repository.

## Required acceptance before any manifest/lockfile change

1. **Review source ownership and compatibility** with the historical JS and Windows packaging workflows and document which, if any, hidden script or CI integration depends on the legacy `nwjs` npm wrapper. Preserve archived evidence and do **not** reactivate the held publisher to test this.
2. **Separate source PR:** if the owner approves a scoped removal, update root `package.json` and `package-lock.json` together in a new isolated branch, plus the **versioned** `unreal/Tools/dependency_baseline.json` and dependent negative-control tests. Do not mutate historical dated audit receipts or force the original 32-package evidence to describe a later different lock.
3. **Independently validate candidate:** run source contract checks and a fresh live npm audit on the exact proposed lock, inventory its residual **six** findings and review licenses/provenance. Some old tests intentionally require the original `nwjs` root and will need carefully reviewed candidate-version test variants, not silent bypasses.
4. **Keep release denial and trusted binary custody separate:** the prior Defender detection in #293 must receive independent security adjudication and authorized Windows Defender-on package/install/uninstall QA **before** any legacy distribution. Do not build, execute or restore the flagged NSIS file in the meantime. A vulnerability-count reduction is not antivirus acceptance.
5. **Unreal is the forward engine target.** This experiment is exclusively about historical Node/NW.js tooling, not a justification to change `PythonScriptPlugin`, Unreal 5.8.4, the Aureate Wake, playable First Wake, character models, or Starbourne gating.

**Decision:** `CANDIDATE_REDUCES_AUDITED_LOCK_RISK=YES`, `PACKAGED_BINARY_COMPATIBILITY=UNVERIFIED`, `LEGACY_RELEASE_SECURITY_HOLD=ACTIVE`, `MANIFEST_OR_LOCKFILE_UPDATE=NOT_APPLIED`, `MERGE_OR_RELEASE_AUTHORITY=NONE`.
