# TSTSS — Ender Resonator: Centering + Resonant Pulse focus

## November 13, 2026 — #826 spherical Pulse source supersession (draft, review only)

**Source of authority:** [draft PR #826](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/826), stacked on [review ownership PR #825](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/825). The November 11 text below describes the **historical #810 one-enemy prototype**. Its phrases "Target: one living enemy" and "cyan expanding ring" are **SUPERSEDED ONLY IN THIS #826 SOURCE CANDIDATE**, not in protected main, shipped content or native-verified gameplay.

- **Creator mechanic:** Centered on Ender, a **point-blank, expanding 3D spherical area effect** that damages **living enemy-faction actors only**, including enemies above/below the caster; allies are never hurt even when inside. Radius is **provisional 600 cm** (design/balance not approved). Ender must explicitly know ResonanceHarmonic rank 1 and the spell; 3 MP, Power 6, exactly one accepted turn/cooldown/cue per cast.
- **Combat source:** `FTSTSSBattleSkillSystem::TryUseResonantPulseArea` filters an authoritative review roster against the complete position map. It validates factions, alive actors, bounded finite coordinates and 3D radius, selects deterministic enemy IDs, commits once to the existing combat/MP authority and adds extra enemy HP hits in the same local transaction with zero extra MP/turn. The old `TryUseRow` and generic `SubmitCommand` single-target Pulse pathways now reject that spell; the explicit `SubmitResonantPulseArea` is the review-only adapter.
- **One shared spatial calculation:** `unreal/Source/ToSailTheStarrySky/Public/Combat/TSTSSPulseAreaMath.h` owns a standard C++17 sphere predicate used by the UE executor. An independent portable `g++`/ `clang++` build/run of this **same C++ predicate**, exercised by `test_ender_pulse_cpp_geometry.py`, tests 28 cases (600 cm inclusive/601 cm excluded, Z-plane, XYZ translation, invalid/overflow coordinates). It does NOT prove the other UE combat semantics compile or work in PIE.
- **Visual source:** the Pulse style uses 72 points on a deterministic expanding Fibonacci sphere + 32 motes and a caster-centered core/light; gameplay radius and visual maximum reuse the same 600 cm constant. This is **source-authored 3D geometry, not an Unreal GPU screenshot**.
- **Focused review only:** key 2 reads actor positions from review cube components in the isolated focus encounter. Production gameplay position provenance, campaign spell menu/cast UI, First Wake map, save, physical splashdown and full route still require integration and native proof. Neither party unlocks nor Starbourne access change.
- **Centering unchanged:** 5 MP, +15% physical DEF for living active allies, 3 rounds, refresh without stacking. Correspondence and all other unselected spells stay DesignOnly.
- **Source verification:** `unreal/Tools/test_ender_pulse_aoe_source.py` contains 12 bounded mutation controls; existing `TSTSS.Magic.ResonatorCueContract` native test has stronger enemy/ally/radius/MP/turn negatives and the explicit 600/601 cm vertical edge, **but new-head Unreal native tests are NOT EXECUTED**. The precise source CI result must be bound to the exact final PR head. Do **not** borrow #810's historical 35-test native receipt or any 36-test V5 parent proof.
- **Neontic native gate:** available disk was approximately 14.11–14.18 GiB, too close to the existing 14 GiB minimum for a new isolated UE worktree/build. No new build was started, no preexisting worktree/evidence modified or deleted. Await safe capacity, clean exact-head checkout and independent UE5.8.4 UHT/Win64 Editor/native/PIE + audible/GPU proof.

**Disposition:** `SOURCE_IMPL_CANDIDATE; EXACT_HEAD_PORTABLE_CXX_VERIFIABLE; NATIVE_NOT_TESTED; PIE_NOT_TESTED; VISUAL_NOT_APPROVED; MAIN_UNMERGED; VS-C03/VS-D05_OPEN`. The older sections below remain intact for historical evidence, not present-tense targeting.

---

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
