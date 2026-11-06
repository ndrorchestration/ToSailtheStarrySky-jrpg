# P0-4 explicit first-session recovery — prelaunch review Continue

**Stacked on draft [PR #779](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/779), exact parent `e9989df6cfb180bc6a8d3332ea0365387b5d121a`.** Tracks [issue #778](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/778).

## User flow
- F5 in a **fresh** D3D11 PIE review project writes the existing v2 story SaveGame in `tstss_prelude_pie_quick` and a **separate** v1 `tstss_prelude_pie_manifest_v1` Unreal SaveGame companion, including review protocol, source-project root path, entire review map package, BLAKE3-160 hash of primary `.sav` bytes, version/beat/inspection state and Ender location/control orientation.
- F9 stays limited to the current PIE session's owned slot; it never silently adopts a previous Editor's save.
- After a clean Editor restart, press **F6 once to preview** the bound slot, beat/inspection summary and Ender's saved position. This does **not change** story/pawn collision. Press **F6 again within 30 seconds** to confirm only while the original current story generation/beat/mask and primary binary digest are unchanged. A second read validates the actual saved bytes and provenance again before applying.
- On successful preflight: validate the saved story against native rules in an isolated object; validate a collision-safe pawn teleport near the saved location (max 50 cm adjustment); apply the move, load the existing v2 story through the proven `LoadFirstWake` path (including review-marker rebind), restore view rotation, then mark the adopted slot as *owned in this new PIE session*. The player may then use regular F9; existing quicksave guard remains in effect until explicit adoption.
- Failure is **fail closed** with a visible reason and log; no silent Continue, no auto-load in BeginPlay, no unguarded overwrites or story success claims.
- A missing/corrupt/foreign/mismatched primary or manifest, unsupported/future version, unexpected party roster, unsupported map or out-of-bounds location are rejected. BLAKE3 digest is an **integrity binding**, NOT an authentication signature or proof of source commit identity.

## Deliberate limitations
- Review-only editor PIE; unchanged schema version 2. No final player menu, packaging, production SaveGames or release.
- **Flight-and-later saves deliberately cannot Continue yet**: no safe persisted ship transform, physics transient water contact, crew state or Chapter I streaming resume. Reject any saved beat `Launched` or later; no false landing status or early Lyra/Starbourne.
- The F5 story save and manifest use two UE SaveGame writes, not an atomic multi-file transaction. Partial write or digest mismatch prevents adoption; it does not silently fall back to a mismatched sidecar. Production persistence will require transactional write/backup and load rollback.
- The current review uses explicit project and map binding, not a secure signed manifest. Copying an old project elsewhere will fail closed; a future migration/relocation workflow needs deliberate authorization.

## Required verification
1. Local full engine-free regression suite and native exact-head Unreal 5.8.4 build. Native transient actor/manfiest tests cover good binding, swapped project/map/hash, future sidecar, unsafe position and unrecorded ship flight.
2. Separate **fresh F5 review** actual D3D11 PIE with a unique save slot, read-back of both binary files, screenshots and hashes. No use of existing SaveGames/production maps.
3. **Close the Editor fully**, restart same exact-head disposable project/map, press F9 (must refuse stale slot), press F6 preview (must not advance story), then F6 confirm. Verify native log `TSTSS_PIE_REVIEW_CONTINUE_ACCEPT`, Ender restored position, objective and pending inspection mask. Verify player can interact as expected after resume; verify save hashes not changed.
4. Negative controls: missing sidecar, changed primary, foreign path, unsupported version, after-launch and unsafe position; none may restore; originals preserved.
5. No protected-main merge, authoritative art promotion, Starbourne unlock or claim of full ship/save release without all gates.
