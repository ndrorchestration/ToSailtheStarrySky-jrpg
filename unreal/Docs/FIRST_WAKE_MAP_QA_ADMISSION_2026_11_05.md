# First Wake V2 — repaired native map-QA admission, November 5, 2026

**Status:** isolated review-only source candidate, not merged, not playable/PIE-verified, not creator-art approved. This work is a child of draft PR #769 source `c3da480583d35e80397998a14b19931fa47ae939`, not a modification to the PR head or protected main.

## What this fixes

The PR #769 outer map launcher `Invoke-NativePreludeMapQA.ps1` admits `TSTSS_P0CombinedF6Objectives_20261104`, but the inner `verify_pr713_native_prelude_map.py` still only admits older PR713 / PR735 / GameAssembly workspace names. Native map QA therefore cannot pass in the combined review workspace even when its C++ compilation and source tests are correct.

To preserve the already-verified PR #769 exact-head **29/29 native automation PASS** and original developer evidence, this change lives in a new explicitly named disposable checkout:

`C:\TSTSS_FirstWakeMapQARepair_20261105`

Branch: `review/ue58-firstwake-mapqa-admission-20261105`.

## Bounded patch

- Whitelist the **single new exact workspace name** in the inner map-QA Python verifier, the outer map-QA PowerShell launcher, the guarded GUI PIE launcher, and the read-only build/PIE readiness probe.
- Retain the strict 40-character expected-head, clean worktree, original Prelude V2 map SHA `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80`, native actor and geometry checks, compiled 29-test inventory, no existing SaveGames, no active Unreal/LiveCoding, 5-GiB native / 6.5-GiB PIE RAM and 14-GiB disk thresholds.
- Update source assertions to reject the new workspace name with an added suffix and refuse wrong source SHA/dirty worktree. Do **not** widen authorizations to arbitrary paths or relax missing proof.
- No changes to native gameplay code, Starbourne locking, maps, author-approved art, or player save logic.

## Native evidence and known gap

On the original PR #769 source commit, actual Unreal 5.8.4 Win64 Editor build passed and all 29 required native automation tests succeeded. The first run was rejected by the final clean-Git guard because Unreal generated two tracked INI changes. Those changes were **preserved in the ignored local evidence folder with SHA-256 before a scoped restore**. A second official native verification was run with both INIs temporarily read-only. All 29 tests passed and the native verifier accepted the exact original PR #769 source HEAD with clean Git/config hashes. This does **not** establish native results on this *new* child commit.

To progress the new child commit, run 273+ source tests, new exact-head UE build and 29 native automations, followed by **a separate build-only receipt** and actual `Invoke-NativePreludeMapQA.ps1` commandlet run. Each step requires a new nonoverwriting evidence folder, temporary config-read-only custody, and independent schema checks. Never reuse older-head native reports as acceptance proof. The new map QA is read-only Editor geometry/objective inspection, NOT PIE movement, F5/Shift+F5/F6/F9 behavior, SaveGame disk restart or physical water flotation.

## Next playable gates

After native stage/readback, require a fresh isolated PIE session with no existing saves, safe F5/Shift+F5 no-write tests, F6 exact review-save creation, F9 same-session load, J objective continuity, and eventually physical First Wake traversal to splashdown. Preserve all unexpected files; never delete a save to force gate passage. Later environmental/art review must include real D3D screenshots with creator approval and better water/character assets.

No release, art promotion, protected-main merge or Starbourne unlock is authorized.
