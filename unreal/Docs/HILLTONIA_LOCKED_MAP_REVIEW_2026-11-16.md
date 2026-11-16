# Hilltonia locked map — local Unreal review pass

Status: DRAFT, LOCAL ONLY, source-authored; native build, traversal,
visual approval and production integration are not established by this note.

Creator-selected geography: First Wake Harbor and ocean east; road west
to Hilltonia; Greenwood forest north/northwest; The Green is the village
market green by the square. Latitude analogy remains provisional.

This pass extends the existing V5 standalone review scene: two additional
non-interactive names, a small placeholder market-green surface and a
denser non-colliding backdrop of thirty primitive trees and shrubs.
Existing road, collision route, opening interactions, progression, save
schema and ship/party gates are unchanged. These shapes are review proxies,
not final foliage, market activity, wildlife, or a native Landscape.
The locked map is a design reference, not an imported game texture.

Coordinate warning: the existing implementation calls -X west and +Y
seaward, while the locked geographic reference places east toward the
ocean. These local axis names are not yet a proven compass transform. Do
not claim world-axis alignment or rotate production levels without a
spatial reconciliation and playtest.

The private free-plan export must remain outside the public repository and
must not be published. A licensing-compliant export is a separate future
task; none is included in this worktree.

Next gates: exact-head UE 5.8.4 compile and registered automation; player
walk from harbor to town, Greenwood and back; inspect collision, sign
orientation, grounded scenery, scale, performance and screenshots; then
creator visual feedback. Native tests do not substitute for player or
visual acceptance. Do not merge or publish this branch automatically.

## First live route and material repair — 2026-11-16

At prior exact source `d7a3820763aae813001b749cd99a821279b8fe13`,
the reviewed standalone title opened the V5 map and an automated keyboard
operator walked harbor -> west end -> woodland edge -> harbor. The
read-only route parser reported all eleven checkpoints, 95 heartbeat
samples and 165.4 m measured, with all sampled footing grounded and
supported. This is an automated-input walkthrough, not a human playtest
or creator approval; parser status remains
`REVIEW_ROUTE_LOG_CONSISTENT_NOT_NATIVE_ATTESTATION`.

Real GPU windows showed placeholder house blocks, primitive trees, white
ground, and a sign reversed from the west end. V5 reported that
`M_VS_Green` lacked instanced-static-mesh usage. The material was changed
only in this isolated worktree, and a fresh UE 5.8.4 native readback
confirmed the flag persisted. The map was not resaved. The earlier walk
and captures predate this material change; a new head requires fresh
native validation and a new rendered inspection. No final art acceptance
is implied.

## Two-sided wayfinding candidate — 2026-11-16

The initial player-camera review showed a mirrored forest-turn sign from
the town-west return. This isolated review candidate uses a noncolliding
timber backing and centered labels facing opposite directions at each
of the six existing locations. It adds no quest interaction, travel state
or saved map changes. Native camera captures from both approaches are
required to assess orientation, contrast, size and overlapping scenery.

## Creator geography revision — 2026-11-16

**Creator direction:** Hilltonia should extend inland from Greenwood's
edge toward the harbor, with a meaningful land buffer from the beach. The
main road runs east-west from the forest through town to the dock; the
dock projects east into the water. This supersedes the earlier review
layout's suggestion that the primary forest route branches north from
the square. The locked Inkarnate image remains unchanged and private.

**Review implementation:** add connected inland and coastal ground
shelves, move the six home proxies and hall 7 m farther west, and extend
the existing road another 66 m west toward a corridor of 32 primitive
trees. The previous northern woodland spur remains an optional side path.
Local review directions use +X east and -X west; final landscape, world
compass registration, shore grade, art, paths and distances remain open.
Existing original dock/quest marker assets are unchanged. The ocean in
this review scene is visual-only; this pass does not establish buoyancy.

The prior eleven-waypoint logger covers the earlier town and northern spur
route only; it does not attest to the new western road. Separate
source-bound native walking evidence is required for the extension. All
new geography remains review-only until checked in Unreal and by the
creator.
