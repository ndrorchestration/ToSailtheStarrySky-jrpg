# TSTSS — JRPG battle presentation and reward loop, native review receipt

**November 11, 2026.** Isolated `review/unreal-slice-enemies-20261110` branch / draft PR #791. This is the optional Unreal V2 review sandbox, not approved First Wake campaign content.

## User-approved sequence

1. Physical walking reaches a weighted random encounter ticket, or an explicitly authorized scripted encounter ticket.
2. An **original encounter sting** plays while a cyan/amber full-screen flash overlays the exploration camera (0.42s).
3. A battle-reveal transition (0.36s) precedes initializing the existing authorized `UTSS_CombatTurnManager`; only then does the camera switch to the battle console and 3D enemies.
4. J/K commands are admitted only during actual combat. Flee initiates a separate transition with **no rewards**.
5. On authoritative `Victory`, the **victory fanfare** plays; 3D review proxies for only the available Ender/Ionia/Lyra party perform a short cheering/jump movement.
6. After 1.45s fanfare and 1.25s celebration, the **reward reveal** sound plays with a native UMG result window listing item names/counts, gold received, and XP earned per active party member.
7. Enter is required to dismiss the reward panel (or defeat panel); the **return whoosh** and 0.46s fade precede restoring the exploration camera and position (defeat returns to safe camp).

## Correctness / reward authority

- `UTSTSSJRPGReviewPresentation` enforces the transition order and rejects replay, skipped phases, cross-ticket commands, and premature return.
- `UTSTSSJRPGReviewRewards` applies a one-time **transient session** transaction for each unique victory ticket, credited to an exact canon-order, reviewer-selected active party. The amounts and item identifiers are provisional, not final game economy.
- A successful review fight updates in-memory total gold, per-character XP, and inventory item counters. It never claims to update the authoritative SaveGame, economy, permanently recruited party, or quest state.
- Defeat and voluntary escape never call reward issuance; Enter is blocked until the appropriate result screen is reached.
- The existing battle manager remains the single combat/damage/victory authority. No production battle engine or story map was replaced.

## Original native audio assets

Authored procedural source WAVs are owned by this project (24 kHz, 16-bit mono, original synthesized motifs, no commercially sampled music):

| Effect | Duration | WAV SHA-256 | SoundWave SHA-256 |
|---|---:|---|---|
| Encounter sting | 0.95s | `4809d0ce3ab350c4fb067e8017810b3269fb2ec109527b6a7f9a9bd31d4d0d43` | `0082877f36fa79b4b65470212b27d0ec8a5e40ca0e1dd4d5adffac3141c11836` |
| Victory fanfare | 2.20s | `7d6fb0822ff2ff97d6ca0edec4832692c880d65fcb6fb638563909f18b926929` | `2037105067e85779a6a4616e7045333892fdb71be23328ebe627602c4e2459b1` |
| Reward reveal | 1.15s | `7bb0108bd11531fdc4af5c8a011509d6f013fc0d5c39d293523798198f9f0ed0` | `d4f3c805eb3644e272611b2ee17065651bef8b96b7895eb9ae88e8ab0a6947de` |
| Return whoosh | 0.72s | `784435e9708c5a7777214136328f30a0d90566557f0a5a177c147d173a73d95a` | `9c2a77d96e742ae2db39abc7a783e9e0af07cf6885616c7e73f2e1c478caa297` |

- WAV originals: `unreal/Content/TSTSS/Review/AudioSource/SFX_*.wav`.
- Imported actual native Unreal `SoundWave` binaries: `unreal/Content/TSTSS/Review/Audio/SFX_*.uasset`.
- Four native asset import status: `FOUR_NATIVE_SOUNDWAVES_IMPORTED_NOT_PIE_AUDIO_PLAYBACK` from Unreal Editor Python commandlet; 0 editor errors / 0 warnings. Unreal compressed/imported all four SoundWaves and reported correct durations, mono channels, BINKA.
- The original local import receipt at `Saved/EnemyGalleryV3/audio-import-receipt.json` binds the import to exact source head `4e954a184bf9c87ab1ef8789348151d5462b6740` and records asset hashes. Its inherited `native_import_proven: false` plan flag was not overwritten in that first script version; treat the native import status, object readback, file existence, and hashes as the admission evidence. The script is corrected to set this flag for any future fresh import. Do not rewrite the immutable historical receipt.

## Verification boundaries

- Native Unreal C++ build, 32 registered native automations, and negative state/reward tests passed at source head `9a4e307218c8032cb0c1c96d1626e59717bcd6dd` **before** the new SoundWave commit.
- Native editor build-only verified at importer source head `4e954a184bf9c87ab1ef8789348151d5462b6740`, then the four SoundWave imports succeeded under that head.
- **At the time of this note, final exact-head native build+full suite with imported SoundWaves is pending.** No native D3D12 GPU screenshot or personally witnessed PIE input/audio playback is claimed yet.
- The party figures are low-cost procedural capsule proxies, not the approved Ender/Ionia/Lyra rigs, facial models, or authored animations.
- HUD, sound mix, crossfade, camera framing, balance, enemy skills, rewards and canonical First Wake integration all need direct authored/polished final visual/gameplay review.

**Disposition:** verified native import and source-bound functional logic; review sandbox only, PR remains draft/unmerged.
