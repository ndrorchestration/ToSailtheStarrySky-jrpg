# Ender — Private PIE idle/walk/run preview (Nov 17, 2026)

**Status: source-staged only / draft / native NOT VERIFIED / art NOT APPROVED.**

## Why

PR #853 already contains the real `ATSTSSExplorerCharacter` playable pawn, an
editor-only privately assigned skeletal mesh, opt-in hair/goggles/staff and
read-only possessed-pawn speed telemetry. This increment allows an **optional
single-node animation preview** of three legitimately licensed **in-place**
`UAnimSequence` clips, without building a second pawn or treating capsule
speed as proof of a deforming animated body.

Epic UE 5.8 API references: `USkeletalMeshComponent::PlayAnimation`
(<https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/USkeletalMeshComponent/PlayAnimation>),
`USkeletalMeshComponent::GetSingleNodeInstance`
(<https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/USkeletalMeshComponent>),
and `UAnimSingleNodeInstance::GetCurrentAsset`
(<https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UAnimSingleNodeInstance>).
The API only requests transient playback; source tests and log entries do **not**
establish native pose evaluation, foot placement or rendered evidence.

## Optional controlled walk/sprint review (separate from animation clips)

The existing pawn now supports the review-only `EnderPIEReviewSprint` key
(`LeftShift`, held to run), **disabled by default** via the private Blueprint
property `bEnableEnderPIEWalkRunControls=false`. When explicitly enabled,
only the genuinely player-possessed standalone PIE V5/VS02 review pawn receives
a 260 cm/s walk cap; holding Shift requests 480 cm/s until released. This is
a physical movement-speed review control: it does **not** prove, request or
author any skeletal animation, and it can be tested before the three private
animation clips are available.

The controller leases the preexisting `MaxWalkSpeed` from the spawned pawn,
refuses speeds outside 180–900 cm/s or non-finite speeds, and writes only when
the last observed speed is still the one it owns. If another owner changes the
speed, the control stops and never forces a takeover. On release at PIE EndPlay
or when the review scope is lost, it restores the original speed **only if**
the last assigned value remains unchanged. Flyer and engine-focus UI suppress
running; existing WASD/E/quest/save bindings and production movement untouched.
The Shift mapping is globally declared but **bound only in editor PIE**;
without the explicit Blueprint opt-in it is inert.

Native acceptance requires comparing observed walk/sprint speeds and animation
bands on an actual player-controlled Ender, ensuring walking does not accidentally
fire run pose and transitions do not override camera/E/story/modal controls.

## Non-negotiable gates

1. **Editor only, explicit opt-in:** a private review Blueprint derived from
   the existing player pawn must set `bEnableEnderPIELocomotionPreview=true`
   and explicitly supply private `EnderSliceReviewBody` plus all three
   `EnderPIEIdleAnimation`, `EnderPIEWalkAnimation`, `EnderPIERunAnimation`.
   All are blank/off by default. Do not commit or redistribute private assets.
2. **Real player, isolated world:** only a possessed pawn in standalone PIE,
   under `/Game/TSTSS/Review/`, in the V5 First Wake visual review or
   `VS02_AureateInteriors`. Production maps, game runtime and other pawns
   remain untouched.
3. **Fail closed before mutation:** actual bound skeletal body matches the
   explicitly assigned candidate, registered and visible, grounded; three clips
   load together, use **exact same USkeleton**, and have root motion disabled.
   Existing animation Blueprints, custom and pre-assigned single-node
   animation owners are not replaced. After starting the review, each next
   transition requires its prior single-node asset to still match the asset
   requested by this preview. An external owner replacing a clip without
   changing animation mode triggers a fail-closed HOLD, rather than a takeover.
   A failing gate causes a one-shot HOLD log and leaves the previous animation
   owner intact.
4. **Review behavior:** transition among looping idle (speed <10 cm/s),
   walk (10–299.9 cm/s) and run (>=300 cm/s) from the possessed capsule's
   `GetVelocity().Size2D()` while grounded; request playback only on band
   transitions. This is **not** blending, jumping/falling/turning, locomotion
   retargeting, physical foot-contact proof, or production animation design.
5. **No authority:** no story, save, recruitment, magic, actor location,
   input, collision, level, canonical art or game permissions change.

## Native next action — only when Neontic resources are safe

- Check Desktop Commander online and current independent UE editor/process
  ownership; preserve the disk safety reserve (C: >=14 GiB free at all times,
  preferably >17 GiB starting margin) and RAM admission threshold (>=6.5 GiB
  physically available) before attempting Unreal Engine 5.8.4 native build.
- At **exact PR #853 head**, complete safe Win64 UHT and full Editor C++ build.
  A Python source CI green is not a native pass.
- Stage only assets with verified game-use rights into a **private** throwaway
  review Blueprint; record skeleton identity, 3 animation asset identities,
  root-motion flags and import hashes; do not add these assets to GitHub.
- Play V5 and VS02. Capture controller possession, third-person camera,
  responsive WASD, footprint/grounding, actual visible deforming cloth,
  3 requested animation state logs and **frame-by-frame rendered** idle,
  walk and run. Check accessories follow animated head/hand without floating.
- Compare three-angle face/hair/goggles/outfit/staff screenshots against the
  approved November 11 Main Party Bible Ender panel (second from left, private
  ChatGPT Library file `file_00000000e1d081f5ab980b4f2ba93a49`).
- Keep **draft/unmerged** if skeletal/animation asset incompatible, clipping,
  root-motion drift, temporary disk collapse, non-native evidence, rights
  ambiguity, or unapproved likeness remains.

**Acceptance:** a truly player-controlled, visibly deformed and animated Ender
in real UE 5.8.4 editor PIE with exact-head native logs/video plus creator art
approval. None of that is claimed by this source-only increment.
