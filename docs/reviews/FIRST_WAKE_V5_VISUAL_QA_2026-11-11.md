# First Wake V5 — corrected visual review baseline

**Status:** REVIEW-ONLY. Source branch only; NOT art approved, NOT merged, NOT production.
**Native authoring source commit:** `f53f20efeb8e98b3e8d2fa05dce906f93ad6fc0a`
**Review map:** `/Game/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview`
**Native map SHA-256:** `ff2b5c1423a370c4ac318b9b241088d8f20fec5eee993c998c2a5ed335cbb299`
**Original V2 SHA-256:** `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80` (unchanged)

## Verified

- Native UE 5.8.4 map authoring exited `0`; original V2 stayed bit-identical.
- V5 switches from the clipped 75,000 lux V4 sun key to 1,500 lux, sky fill 0.4, fog density 0.001, and -1 exposure bias. The review sign rotation explicitly uses named `pitch=0,yaw=180,roll=0`.
- Actual standalone D3D11 game loaded the map and rendered an intelligible initial traversal path, full readable sign captions, visible harbor blockout props, depth and a nonblack sky/horizon. Earlier V3 reversed text and V4 blank-white render are corrected **at the review level**.
- No native gameplay intervention, physical water contact, story authorization, character equipment change, asset promotion, title routing or main merge was performed by V5 native authoring.

[Native V5 standalone visual frame](assets/firstwake_v5_corrected.png)

## Not yet verified or approved

V5 is a low-fidelity **playability/legibility proxy**, not the final cinematic environment. The image remains bright, flat and under-detailed for AAA art, with provisional geometry, a HUD debug overlay, no polished character representations or final environmental materials. Exact full-opening traversal, E interactions, dock-fall auto-recovery and multi-map handoff must be tested after separately admitting this V5 route in review source. Preserve Starbourne closed and the primary party as Ender, Ionia and Lyra only.
