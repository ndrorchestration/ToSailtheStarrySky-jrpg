# First Wake audio foundation — isolated implementation review

**Date:** 2026-11-11. **State:** SOURCE CANDIDATE ONLY / DRAFT PR #804. Branch parent: PR #799 at `bb91ebbdae0cf39eaf8351923abbe103a5cdc6b8`. Unmerged; no native audition or cleared shipping soundtrack.

## Current source deliverables

- 56 prioritized and gated sound events for First Wake, ocean, harbor, weather, ship, UI, combat, magic and future biomes. Event names are a **design contract**, not recordings already in the game.
- Existing five-track MP3 register preserves historic SHA/byte provenance only. **Rights to ship and actual Unreal import are not established.** No historical music binaries were copied.
- Ten deterministic original QA WAV sketches (UI, repaired harmonics, engine instability, strange echo, gust, splashdown), plus a versioned SHA-256 manifest.
- `UTSTSSAudioSubsystem` and optional `ATSTSSAudioCueBankActor`: event registration, positional/2D sounds, loops, cooldowns, per-category master/music/voice/ambience/SFX/UI levels, mute and silent fallbacks. The bank has **no assigned sounds** until a designer configures actual rights-cleared SoundBase assets.
- `ATSTSSAudioEnvironmentDirector`: an optional weather-linked harbor mix with six configurable looping beds—surf, gulls, market, wind, rain and storm. Uses interpolated `ATSTSSAtmosphereDirector::GetAtmosphereProfile()` values and day/night factors. Defaults to inactive and has **no built-in sounds**.
- `ATSTSSHarborAudioZone`: optional non-blocking box trigger restricted to the local player. Activates/deactivates the harbor actor without changing story, physics, enemies or player state. A single zone per audio director is the currently supported review arrangement; overlapping multiple zones are not yet reconciled.
- Explicitly opt-in `unreal/Tools/import_first_wake_audio_review.py` validates ten original preview files and their checksums, refuses overwrites, guards free RAM (>=6.5 GiB) and disk (>=14 GiB), and imports only unsaved Editor QA assets. Never run it automatically in CI; never treat unsaved imports as production deliverables.
- Python negative fixtures test mismatched audio hashes, forged production approval, wrong file names, missing opt-in, insufficient available RAM, no authoritative story/physics mutations, and source integration contracts.

## Reproduce source-only checks

```bash
python3 unreal/Tools/test_audio_review_contract.py
python3 unreal/Tools/test_audio_integration_source.py
python3 unreal/Tools/build_audio_preview_samples.py --output /tmp/tstss-firstwake-audio-review
```

These tests and ZIP artifact are automated by `.github/workflows/firstwake-audio-contract.yml`. **Source tests passing does not establish Unreal native compilation, SoundWave imports, runtime playback, audiovisual quality or licensed third-party recordings.**

## Proposed native audit procedure (NOT EXECUTED)

1. Confirm an idle Editor lane and fresh minimum resources (6.5 GiB free RAM, 14 GiB free C:). Do not interfere with other TSTSS worktrees, SaveGames or Editor sessions.
2. In disposable pinned PR #804 Unreal checkout, generate private original audio into a scratch folder OUTSIDE Content. Set `TSTSS_AUDIO_REVIEW_SOURCE` to the scratch folder and `TSTSS_AUDIO_REVIEW_OPT_IN=I_APPROVE_QA_AUDIO_IMPORT_ONLY` only for an explicitly intended Editor audit; run the importer with the enabled Unreal Python plugin. Imported packages intentionally remain **unsaved**.
3. Assign imported SoundBase test assets to a review `ATSTSSAudioCueBankActor`. A looping WAV requires an authored loop-capable SoundCue/MetaSound or looping SoundWave; simply marking `FTSTSSAudioCue.bLooping` does not rewrite a one-shot file.
4. Place exactly one `ATSTSSAudioEnvironmentDirector` and one `ATSTSSHarborAudioZone` in a disposable harbor map, bind approved looping SoundBase sources, link `HarborAudio` property, and test entry/exit, night/day, clear/rain/storm, mute and missing-asset behavior. Existing scene maps are not rewritten by these source changes.
5. Verify successful inspections trigger cosmetic sound only after `TryActivate` succeeds; weather cues only after valid changed requests. Audio NEVER establishes sea-contact, permits an unlearned spell, recruits Lyra or unlocks Starbourne.
6. Run exact-head UE 5.8.4 native compile + full required existing native suite; perform PIE headphones/video capture, caption/visual parity and negative tests, mix review, and packaged Windows acceptance. Do not reuse historical or other-branch native receipts.

## Resource/licensing controls

Neontic read-only snapshot this turn: ~4.99 GiB free RAM and 10.99 GiB free C:—**below both thresholds**. Therefore no native Editor/import/build was attempted. <https://gdc.sonniss.com/> offers a 2026 bundle larger than 7 GiB; do NOT download the full bundle to the machine in its current storage condition. Effective Aug 27, 2026 Sonniss license: commercial game synchronization permitted; isolated redistribution and AI-training use restricted. See <https://sonniss.com/gdc-bundle-license/>. Kenney CC0 packages are a possible lightweight candidate; exact individual source files must be provenance-reviewed before import.

## Next accepted development gates (OPEN)

- Rights-cleared Foley library, exact-source hashes and source provenance.
- Real footsteps/material tags, enemy/combat outcomes, Resonator–Ionia–Lyra effects (Lyra only after recruitment), ship and ocean contact event wiring.
- Environmental audio obstruction/indoor transitions; event priority/voice concurrency and accessible captions.
- Native UHT/UBT, audio map, soundbank, rendered/listened mix, packaged build, and creator listening signoff.

**Authority:** This document is a reversible source review child of the master vertical-slice acceptance matrix, not an audio release approval.

## 2026-11-11 — footstep audio continuation, code only

- Added `ATSTSSFootstepAudioDirector`, a **map-opt-in actor** observing the local player and `UCharacterMovementComponent::IsMovingOnGround()`. It measures actual horizontal ground distance, never input key presses; rejects stop, air/swim, missing player, jump/teleport discontinuities, malformed DeltaSeconds and missing registered audio. Each accepted footstep does an `ECC_Visibility` trace requesting physical material and dispatches one of four footstep IDs via the cosmetic subsystem. No source change to the current moving Explorer Character or SaveGames.
- Review mapping is `SurfaceType1 = wood`, `SurfaceType2 = sand`, `SurfaceType3 = stone`, `SurfaceType4 = metal`. These are **local actor defaults**, not a global claim that the existing game's physics materials already use these names. The review map needs confirmed physical-surface settings/material assignments. Unknown or missing materials remain silent.
- Extended the deterministic original preview generator and strict importer from 6 to **10 WAVs** with the four short synthetic footsteps. Do not mistake these rough QA one-shots for production Foley, animation-synchronized footfall triggers, or sufficient variation for cinematic release. The current proposed solution uses ground distance to drive footsteps until character skeletal notify tracks are validated.
- Resource-aware guard: when the footstep bank is unregistered or muted, it skips the ground physics trace. Actual sample playback still requires an imported SoundWave, bank actor assigned in an isolated map and native UE5.8.4 verification.
- Since upstream PR #799 advanced nine commits from the base of PR #804, reconcile the latest trunked First Wake sources and verify no overlap before any integration. On the compared range only the Explorer Character files among audio-related touchpoints were updated; this audio change deliberately does not modify them.
