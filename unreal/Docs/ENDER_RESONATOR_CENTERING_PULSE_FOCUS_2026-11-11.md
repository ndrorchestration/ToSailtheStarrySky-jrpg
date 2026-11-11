# TSTSS — Ender Resonator: Centering + Resonant Pulse focus

**November 11, 2026. Draft research/review only. No main merge, canon spell grant or release.**

## Creator direction and holding rule

Ender's vertical-slice main combat job is Resonator, not a replacement for his permanent Harmonic Resonance Engineer profession or Spirit-aligned Shine. Its broad learning curricula remain Resonance/Harmonic, Correspondence, Psychic/Psion and Synergy/Combination.

**Correspondence spells and its cross-school combinations are ON HOLD.** The catalog keeps all existing examples for future work. This isolated review branch makes only Centering and Resonant Pulse executable. The eight other spell rows (including the two Correspondence rows and Correspondence-dependent synergy) have DesignOnly admission. No skill is automatically learned in the real campaign.

## Centering spell — review tuning

- SkillId: Ender_Centering
- School: ResonanceHarmonic; explicitly learned, mastery rank >= 1; caster Ender
- Resource: 5 MP; consumes the real action/turn
- Target: self-cast, grants the status to each living active party member
- Effect: +15% physical Defense, rounded upward, minimum +1 bonus
- Duration: 3 combat round boundaries following the successful cast. No elapsed-seconds timer.
- Recast: same bonus, three-round refresh, no stacking
- Exclusions: does not reduce magical damage; does not buff foes, reserves, or unrecruited characters; no automatic Shine/SP gain; no infinite refresh without paying MP
- Engine: status is stored separately from base Defense and resolved during authorized physical WeaponTechnique/JobArt damage, with the existing CombatRules as the final damage calculator.
- Cue: original mint/teal 3D harmonic ring expansion (2.7 seconds) and original synthetic tonal settling SFX.

## Resonant Pulse spell — review tuning

- SkillId: Ender_ResonantPulse
- School: ResonanceHarmonic; explicitly learned, mastery rank >= 1; caster Ender in the focused battle adapter
- Resource: 3 MP; consumes an authorized turn
- Target: one living enemy
- Effect: provisional Power 6 (actual final HP outcome uses power, combat Attack and target Defense, not a parallel hit calculator)
- Cue: cyan expanding ring impulse plus dedicated original synthetic resonant wave/strike sound.
- Centering cannot reduce Resonant Pulse damage since it is not a physical action.

## Actual native tests

At source commit fd960d94e4816edd78cda88bea726048f9b6e606:
- UE 5.8.4 Win64 Editor C++ build succeeded. Strict verification then stopped because disposable local Intermediate took available disk below 14 GiB.
- Safe deletion of only this new worktree's disposable Intermediate/Build restored disk margin, preserving the real built DLL.
- A separate guarded commandlet ran all 35 TSTSS native tests against the same source commit. Existing strict native report validator accepted all 35, 0 failures/unrun. Evidence: C:\TSTSS_CenteringPulse_20261111\unreal\Saved\FocusNativeTests\fd960d94e481-20261111\verified-native.json.
- Direct negative tests cover no free mastery, design-only denial, insufficient MP, no cross-faction or self-target bypass, physical-only defense, no stacking and round expiry, actual Pulse damage, and real manager HUD defense readback.
- This is not evidence of a witnessed player keyboard session or final VFX/SFX art.

## Continued playable-focused implementation

- In the isolated review-only scene, ATSTSSResonatorFocusReviewActor will read a source-locked native DataTable containing all ten catalog rows but admit only these two.
- Dedicated keyboard input: 1 = Centering; 2 = Resonant Pulse, only during Ender's actual turn.
- Ionia and a synthetic foe take turns through the same native combat manager (never off-ledger damage).
- UTSTSSResonatorFocusHUD shows HP/MP, effective physical Defense, remaining rounds, available keys and current turn.
- ATSTSSResonatorVfxActor spawns effects only from accepted Ender skill/VFX cue pairs, not unearned preview actions.
- Two original WAVs are source-generated and imported as Unreal SoundWave assets under the ResonatorFocus review folder.
- No First Wake map, campaign save, real party recruitment or starting loadout is changed. No AAA art or native full PIE acceptance until witnessed.

## Review acceptance still required

Finish exact-head UE build and native automations after new actor, import two native SoundWaves plus DataTable and isolated .umap with hash receipts, verify independent Editor readback, then perform live PIE keyboard/audio/GPU visual approval. Any unobserved acceptance tier stays UNVERIFIED.

**Status: source implementation in progress, review-only.**
