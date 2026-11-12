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


## 2026-11-11 — first actual native C++ compile and repair boundary

- An exact-head, detached checkout was created on Neontic in a new **disposable audio worktree** at `9768f976a4b2fd80498f0759ba2c6335574d96d8` (same PR #804; no other branches reset). Visual Studio/MSVC 14.44 and Unreal BuildTool from **UE 5.8.4** were established. One-worker `ToSailTheStarrySkyEditor Win64 Development` compiled through shared PCH/UHT and reached actual module C++.
- **Native FAIL, not PASS:** `TSTSSAudioSubsystem.cpp(99): error C2440`; `TMap<FName,TObjectPtr<UAudioComponent>>::Find` was incorrectly assigned to `UAudioComponent* const*`. Build exit 6. Exact diagnostic, resource snapshot and non-authorization in `Docs/Evidence/Audio/first_native_compile_and_resource_gate_2026_11_11.review.json`.
- The smallest repair at `a918f4b7a951844cee923c46e9c6e61b8aad01c6` uses `const TObjectPtr<UAudioComponent>*` and explicit `Existing->Get()`. Source regression check committed in `0cf1fddbf24ae0b3c07e30f1c833c3f79454e0a2`. No second native build has compiled this repair; hosted source tests do **not** establish C++ success.
- The failed build created a single 2.40 GiB generated shared PCH. NTFS compression applied **only to that disposable cache** reduced physical size to approximately 0.86 GiB, no unrelated worktrees touched. Free space briefly reached 14.36 GiB, then fluctuated below 14 GiB while other work proceeded. A subsequent attempted rebuild was refused **before launching UBT** by the 6.5/14 GiB safety gate. Never write `NATIVE_BUILD_PASS` for the repaired commit until an exact-head UBT run succeeds.
- Ten original QA WAVs with original-source SHA-256 receipt were generated in a separate scratch directory on Neontic. They are **not** Editor SoundWaves, shipping assets, licensed third-party Foley or audible PIE evidence.

## Disposable Denith audio-scene stager (code prepared, NOT executed)

- `unreal/Tools/stage_first_wake_audio_qa.py` implements an opt-in Editor-only path using Epic 5.8 editor subsystems: `EditorAssetSubsystem`, `EditorActorSubsystem` and `LevelEditorSubsystem.NewLevelFromTemplate`. This is designed to create a **new** `/Game/TSTSS/Audio/QAReview/VS01_DenithHarbor_OriginalQATest` map from the existing `VS01_DenithHarbor` template, never to overwrite its source map.
- The stager verifies the ten WAV/receipt hashes, requires the detached AudioReview worktree and **full user-selected expected Git SHA**, explicitly checks no tracked edits, enough free RAM and C: space, no current PIE, no preexisting QA map or sound assets, and strictly refuses destination overwrite. It creates ten QA-only SoundWaves and adds a cue bank, harbor environment actor, local-player audio zone and grounded-footstep observer; actual QA map/editor behavior is **not yet run or attested**.
- Required deliberate opt-ins: `TSTSS_AUDIO_STAGE_OPT_IN=I_APPROVE_DISPOSABLE_QA_MAP_ONLY`, `TSTSS_AUDIO_REVIEW_OPT_IN=I_APPROVE_QA_AUDIO_IMPORT_ONLY`, `TSTSS_AUDIO_REVIEW_SOURCE=<directory containing audio_preview_receipt.json>`, and `TSTSS_AUDIO_EXPECTED_SOURCE_SHA=<exact currently staged 40-character Git commit>`. Run in isolated UE5.8.4 Editor Python, **not a global/default startup workflow**.
- The stage names all resulting assets under `/Game/TSTSS/Audio/QAReview`, excluded from Git by `unreal/.gitignore`. Generated QA assets are not release-authorized; even a successful stage receipt has `STAGED_QA_UNAUDITIONED_NOT_RELEASE_AUTHORIZED` status. A real PIE run and actual listening/headphone quality test would still be needed.
- Ambient surf, gulls, marketplace, rain and storm loops remain source-missing; the stager intentionally leaves those SoundBase fields empty instead of mislabeling synthesized footsteps/tones. Actual material/physical surface mappings also require review in the copied map.
- Source and negative test: `python unreal/Tools/test_audio_stage_source.py`; CI validates stage admission, SHA custody, permissions, resource failures and non-overwrite intentions. That does **not** execute Unreal scripting.

**Next native admissibility:** restore above 6.5 GiB idle RAM and 14 GiB free C: without disturbing other process/worktrees, run a single worker exact-head UE5.8.4 UBT build, inspect every native error, then separately stage and test disposable QA audio if the resource gates remain satisfied. Treat all unverified/audio release criteria as OPEN.

## 2026-11-12 — original QA harbor loops and resource admission

- New zero-dependency `unreal/Tools/build_audio_harbor_loops.py` generates six wholly original, deterministic synthetic 6-second WAVs: surf, gull-like whistles, marketplace murmur, wind, rain and storm. All are 48 kHz mono 16-bit PCM, each with SHA-256, original-QA-only provenance and an exact first/last PCM seam in `harbor_loop_receipt.json`. They are rough **testing** sounds, not licensed Foley, composer work or final cinematic sound.
- `unreal/Tools/test_audio_harbor_loops.py` validates all six audio files, tamper and release denial, source directory exclusion, reproducibility and seamless-boundary assertions. The optional disposable Denith stager now requires a separate `TSTSS_AUDIO_AMBIENCE_SOURCE` folder alongside the earlier 10 one-shot/footstep QA files; it verifies all 16 sources, makes six SoundWave assets loop in the Editor, and assigns the six ambient beds to the existing weather-driven `ATSTSSAudioEnvironmentDirector`. This new source stager has **not been run inside Unreal**.
- All five CI source/legacy checks passed at exact pre-documentation commit `fde6546d544f0ddb0b9cc1d26fdcd5774542de3a`; [audio contract run](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/43159633415). Earlier prototype CI failures revealed scalar-versus-array errors in the original generator and were corrected; none is evidence of native compilation.
- The six WAVs were also generated on Neontic under `C:\TSTSS_AudioReview_HarborLoops_20261112` and checked against their original SHA manifest. The earlier 10-file source remains in `C:\TSTSS_AudioReview_QASamples_20261111`. No other worktree, historical music or shipping assets were written.
- Latest initial Neontic snapshot this turn: approximately 7.06 GiB free RAM and **11.51 GiB free C:**, below the existing 14 GiB native-build safety threshold. Read-only cache audit: npm approximately 1.07 GiB, codex-runtimes approximately 1.30 GiB, Puppeteer approximately 0.69 GiB, hyperframes approximately 0.26 GiB; Node processes active. None of these caches was removed or compressed. **No native Editor, UHT/UBT, SoundWave import, placed QA map, audio capture or PIE playback occurred.**
- Epic Unreal 5.8 API documentation supports `LevelEditorSubsystem.new_level_from_template`, `EditorActorSubsystem.spawn_actor_from_class`, and `SoundWave.looping`. API existence is not proof those bindings executed successfully in the project.

**Next strict gate:** Reclaim at least 14 GiB stable C: free without interfering with concurrent agent processes, then exact-head Win64 Unreal 5.8.4 UBT; only after success run the disposable QA Editor stage and actual game audio tests. Starbourne, Lyra recruitment, physics, historical MP3 rights and production status are unchanged.
