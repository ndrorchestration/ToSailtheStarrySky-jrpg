# First Wake V3 visual QA — review-only experiment

**Branch:** `review/ue58-opening-and-dock-rescue-20261111`
**Authoring source commit:** `e8a32f7ddb7f1fe552fec0a713992c839164387c`
**Review map:** `/Game/TSTSS/Review/FirstWake_PreludeInteraction_V3_VisualReview`
**SHA-256:** `12620a480110f4b402c4542054c86b7caefae3d8083401f0e01a59b9433bb1ce`
**V2 original SHA-256 unchanged:** `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80`
**Status:** Native authored and standalone rendered, not approved, not routed from New Game, not merged.

## Native evidence and QA

- The native UE 5.8.4 authoring process exited `0`. Its receipt is stored locally under `unreal/Saved/OpeningDockReview/v3_native_visual_authoring.json`.
- Standalone D3D11 Game mode successfully loaded V3 under `TSTSSGameMode` and produced an actual screenshot.
- Brightly lit harbor floor and physical shadows are now visible; the prior explicit six-light-rebuild warning was not visible in the captured V3 frame.
- **Visual review FAIL**: black/incomplete sky and reversed or rolled in-world review sign text.
- Native map actor inspection proved all seven signs are saved with `yaw=180, roll=180`, rather than the intended `yaw=180, roll=0`. The sun was saved with an unintended `pitch=42, yaw=180, roll=137`, rather than `pitch=-43, yaw=138, roll=0`.
- Root cause: Unreal's Python `unreal.Rotator` positional argument behavior was assumed incorrectly. Named `pitch`, `yaw` and `roll` are required for the next isolated revision.

## Attached visual comparison

- [Original V2 standalone frame](assets/firstwake_v2_initial.png)
- [V3 standalone light/sign frame](assets/firstwake_v3_lit_but_rolled.png)

Both screenshots are review evidence, not marketing or approval assets. V3 contains no new playable interaction or party promotion. Do not modify or replace it in place; stage a distinct V4 and validate natively.
