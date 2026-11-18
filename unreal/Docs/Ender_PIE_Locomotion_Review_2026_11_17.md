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
The Shift mapping is globally declared but bound only in editor PIE or
editor-built `-game` worlds; it never binds in shipping builds. PIE still
requires the explicit private Blueprint opt-in. For the specific First Wake
title review launcher, an additional `-EnderReviewSprint` switch enables
walking at 260 cm/s and holding Shift to run at 600 cm/s. The preview is
restricted to the possessed standalone V5/VS02 review pawn and the explicit
review namespace; production maps remain denied. No static mesh animation
is implied by the increased speed.

**User feedback:** Shift did not change speed in the previous title launch
because it was `-game`, while the feature was PIE-only and disabled by
default. The running old binary is unchanged. This new source revision
requires an exact-head native rebuild and full test receipt before relaunch.

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

## Nov 18 — opt-in extracted root motion for private Ender retarget candidates

The earlier in-place-only source gate above remains the default behavior. A separate **OFF-by-default** editor-only `bAllowEnderPIERootMotionExtractionReview` switch now permits a different, tightly constrained case: the exact private Ender idle/walk/jog triplet in `/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/Animations/`, with idle root-motion flag **OFF**, walk/jog **ON**, the same verified USkeleton as the possessed private Ender mesh, no existing animation owner, and the unchanged PIE/world/grounding constraints. An arbitrary opt-in root-motion animation must still be denied.

Actual UE5.8.4 read-only inspection on Neontic under clean source head `2e3a9173cd5b50deb098f913d109281db3ceb901` measured the `genesis9` bone root track in **152-track** private sequences: idle 0 cm/7.567 s, walk **+454.163 cm local Y/1.5 s (~302.8 cm/s)**, jog **+1072.1934 cm local Y/1.767 s (~606.9 cm/s)**. The five-frame samples and private SHA-locked receipt are held locally at `Saved/MigrationEvidence/EnderRetargetPrivate/root_track_probe_20261118.json`; exact native guard host receipt `HostReceipts/fe56cd23-e496-4207-8afd-a9fa5148e93b/host_receipt.json` returned `NATIVE_AUDIT_PASS`. This is root-track metadata, **not playable animation**. Direct raw-track key extraction returned no keys despite validated frame-pose sampling and 152 enumerated tracks, so editing raw keys is NOT an authorized fix.

For this explicit private case, the original pawn's transient `UAnimSingleNodeInstance` is requested to use `ERootMotionMode::IgnoreRootMotion` immediately after `PlayAnimation`, so the existing `UCharacterMovementComponent` capsule remains the sole intended translation owner. The source denies a missing/replaced single-node instance and keeps the prior owner-lease guarantees. This is an **API request only**, not proof that Unreal actually extracted and discarded root travel under player motion. Epic's UE5.8 Animation Blueprint Editor documents Ignore Root Motion as extraction without application: https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-blueprint-editor-in-unreal-engine.

**Local implementation validation:** 862 engine-free source tests completed with 2 skipped; focused Ender preview 3/3. Neontic UE5.8.4 Win64 Editor C++ native build succeeded (`Result: Succeeded`, exit 0) against the temporary three-file working change on parent head `2e3a9173...`; `Saved/MigrationEvidence/EnderRetargetPrivate/RootMotionReviewCompile_20261118/native_build_receipt.json` holds the guarded receipt. Original protected project/INI hashes unchanged; no production asset/map written. This is native **COMPILATION only**, not exact post-commit hosted CI, real PIE, animation playback or creator-approved appearance. A clean commit/native automation/actual PIE still require distinct checks.

**Next acceptance:** 38/38 native automation on a clean exact source commit, review-only private Blueprint assignment (all existing opt-ins remain off until explicitly enabled in an isolated copy), actual posed Ender observed in standalone PIE, verify the IgnoreRootMotion policy prevents capsule double translation, compare clip speed with 260/600 cm/s movement, correct cadence/foot planting and inspect staff/goggles/hair. Leave PR #853 draft/unmerged and all private licensed/Epic template assets untracked.
