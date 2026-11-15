# VS02 optical review: bridge spawn obstruction and scoped walkability repair

**Date:** 2026-11-15
**Status:** SOURCE-ONLY DIAGNOSIS + NONSHIPPING NATIVE STAGER PREPARED; **NOT** A SAVED MAP FIX, VERIFIED REAL PIE TRAVERSAL, OR CREATOR APPROVAL
**Worktree:** `C:\TSTSS_840_OpticalReach_20261115`
**Starting SHA:** `7321d555e8e8e4b94b8e807f86a18b90214f2dd5` from review PR #838; protected main, active PR #838 worktree, PR #839, original VS02 and all existing binaries must remain unchanged.

## Evidence and geometry

The original VS02 authoring source `unreal/Tools/build_vertical_slice_environment_maps.py` defines `TSTSS_VS_REVIEW_BridgeDeck` as an intentionally blocking 100cm BasicShapes Cube at **(−780,0,65) cm** and scale **(7,9,1.4)**. Thus the nominal occupied box spans X −1130..−430, Y −450..450 and Z −5..135 cm. The same source defines the original optical review PlayerStart at **(−1080,0,120) cm**, inside that blocking box. On Nov 14 PIE after authenticated V5 E/K/O progression, an on-screen C-key refusal required approaching LIFT. A later in-PIE console readback reported the player capsule's relative X **−1164.25 cm**, nearly exactly the western blocking face −1130 cm minus its reported radius ~34 cm. A second stored property readback reports the LIFT instrument at (−250,−250,270) cm. This aligns with a collision block as the leading **hypothesis**, but native actor bounds, capsule-world location, physical WASD navigation and true cause are still unverified.

At the original **authored** PlayerStart, Euclidean LIFT separation is approximately **879.7 cm** (the C-key source guard requires ≤450 cm). The later capsule-relative sample suggests ≈965 cm distance only if that component reading equals the actual pawn world location. Do not treat a relative-location console property as definitive world position.

**Source-only proposal:** In the existing nonshipping copied optical review map only, preserve the named BridgeDeck StaticMeshActor, its material and full QueryAndPhysics blocking response, but change its center/scale to **(−780,0,7.5) cm** / **(7,9,0.15)**. The resulting 15cm-thick, raised walkable review step sits on the main deck (Z 0..15 cm) instead of occupying the player start (Z 120 cm). Keep exactly one player start, one LIFT, one atmosphere director, two cameras and one *disabled* optical receiver; preserve the original 28-actor inventory and all First Wake story/party/SaveGame/F6–F9/C/O/K gates. This is provisional walkability lookdev; it flattens the bridge proxy and does **not** establish a finished Aureate Wake architecture.

## Executable fail-closed artifacts

- `unreal/Tools/verify_optical_bridge_reach_geometry.py` – engine-free exact-hash/source geometry model, optional local Saved receipt. **No** actor edits.
- `unreal/Tools/test_optical_bridge_reach_geometry.py` – six source/mutation/fail-closed tests; no Unreal runtime or GPU claims.
- `unreal/Tools/readback_vs02_optical_bridge_reach.py` - **NOT EXECUTED**. A fresh native Editor reread checks exact stage/backup/new-map hashes, 28 actors, unchanged PlayerStart/LIFT, dual optics, one atmosphere owner, disabled receiver and restored BridgeDeck collision; no map writes.
- `unreal/Tools/stage_vs02_optical_bridge_reach.py` – **NOT EXECUTED**. An explicitly gated native Editor staging script for only the existing `/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview` asset. Requires correct new isolated branch and exact SHA environment, clean worktree, UE5.8.4, no local PIE, pristine map/input files and expected 28-actor/mesh/receiver configuration. Creates an ignored Saved byte-for-byte backup before writing the one named BridgeDeck actor. The original `/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors` remains hash-guarded read-only.

**Baseline original VS02 SHA256:** `a97fbb057cb87c0e35fe95195ca06c30de1a5cc60158bf31a657f738b22a9d69`
**Baseline optical review copy SHA256:** `06f006b42d54a990ffefa5903bda0d24e34259a424c1f6bee4a51a29f0766223`

## Hard next acceptance gates

1. Coordinate with the existing PR #838 Editor/PIE owner; **do not terminate, trim, or manipulate their process**. Native staging requires ≥6.5 GiB free memory, ≥14 GiB free disk, no competing Editor/LiveCoding process, exact source branch+SHA and a fresh disposable UE5.8.4 Editor.
2. Run the guarded source-only tests, then native stage once with the explicit opt-in flags and preserve its receipt. Open a separate fresh-Editor process to independently read back the newly saved asset: BridgeDeck center/scale/collision, geometry bounds, all 28 original actors, the two camera optics, sky owner, player start, LIFT and intact original VS02/config hash. Refresh the lookdev manifest and source hash tests to the **new** map hash. No CI/native pass may be inherited from ancestor commits.
3. Native build and registered automation exact-head on the new branch. Physically play the genuine V5 seven E interactions → K → O. Walk WASD from the unmodified PlayerStart to LIFT at ≤450 cm. Press C, observe a real 65mm preview enter and auto-return after four seconds with move/look restored, plus negative direct-map and distance-out-of-range cases.
4. Compare D3D11/D3D12 Lit camera A/B with nonclipped exposure, visible depth planes and bokeh meaningful enough to review. Verify varied weather, accessibility, performance, sound, character/ship reference and creator visual signoff. All remain HOLD until witnessed. Keep Starbourne and unavailable party members fail-closed; preserve Seabourne plot lock.

No production assets, protected main, PR #838 session, external releases or SaveGames are to be changed by this source-only diagnosis.
