# Gemini turn manager review — native Unreal adapter

**Status:** PROPOSED / source-only review integration, stacked on draft PR #662, never merged to main. Origin: Gemini-supplied \`UTSS_CombatTurnManager\` idea shared by creator on 2026-11-01. The original code was not copied verbatim: this revision keeps the successful UX goals but removes authorization and continuity defects.

## Source changes

- \`Public/Combat/TSS_CombatTurnManager.h\` and \`Private/Combat/TSS_CombatTurnManager.cpp\` are an engine-native ActorComponent facade over the existing \`FTSTSSCombatTurns\`, \`FTSTSSEncounterGate\`, and \`FTSTSSBattleSkillSystem\` authorities.
- Explicit \`ActivePlayerIds\` selects 1–3 currently available protagonists from the full (up to five) canonical roster. There is no accidental silently truncated first-three party. Reserve IDs are retained as review metadata; their progression/save state is not implemented by this component.
- Deterministic agility DESC initiative, then case-sensitive ID sorting on ties. Validates duplicate IDs, factions, HP/resources/stats, enemy presence, roster size and allowed five protagonists before applying state.
- \`SubmitCommand\` identifies a **skill ID** in the supplied \`UDataTable\` of \`FTSTSSBattleSkillRow\`; never directly trusts a dangling or undefined \`UTSS_AbilityDataAsset\` pointer. Zero admitted rows by default; \`DesignOnly\` abilities fail closed.
- Invalid/unlearned/underfunded/wrong-target/out-of-turn commands do not advance the turn or emit cues. Valid results issue \`ResolvingAction → TurnComplete → TurnSelection\` or terminal \`Victory/Defeat/Draw\` events; audiovisual cue IDs are dispatched but VFX/animations not spawned.
- No per-frame Tick and no second combat turn cursor; everything derives from the existing transactional combat state. This is a synchronous action dispatcher, **not** an animation-awaiting command queue.
- Automation suites \`TSTSS.Combat.InitiativeAndActiveParty\` and \`TSTSS.Combat.TurnManagerTerminalOutcomes\` cover 5-to-3 selection, reserves, initiative, illegal commands, authorization, HP mutation, victory and defeat. Both added to the required native verifier.

## Why not import the Gemini source as-is?

The original references nonexistent \`TSS_CombatTypes.h\`, \`TSS_CombatResolver.h\` and \`UTSS_AbilityDataAsset\` within this checkout, silently truncates five characters to the first three, accepts commands without ability or target validation, lacks terminal states and dead-turn skipping, and defines a second independent turn cursor. Its single test cannot establish working combat. This proposal preserves the intent without introducing two competing authorities.

## Remaining blockers

- **Native 5.8.4 C++ compile + Unreal automation execution** at exact SHA remains required. Engine-free GitHub checks are not C++ proof.
- Reviewer must inspect any UHT/UDataTable/bindings failures on Windows. No VFX, montages, actual UI, or playable build demonstrated.
- Actors/animation completion requires a separate **asynchronous** action queue with explicit completion/error/timeout rules. Never advance action state solely on untrusted animation callbacks.
- Save schema, reserve-party progression, dynamic speed/status changes, reactive actions, multi-action initiatives and stable saveable turn authority are future work.
- Approved party recruit order Ender → Ionia → Lyra → Reson → Aepex is unchanged. The Five Lights are not combat school unlocks.
- Production ownership for all 260 design-only magic seeds remains unapproved; a DataTable's explicit \`ReviewExecutable\` flag only authorizes isolated testing.

## Required run

From an isolated, clean checkout with matching compiler and Unreal Engine 5.8.4:

\`\`\`powershell
pwsh -File unreal/Tools/Verify-Unreal.ps1 -EngineRoot "C:\Program Files\Epic Games\UE_5.8"
\`\`\`

The script requires the complete exact-head registry plus native Editor automation evidence. Collect compiler log, per-test JSON and at least one renderer-enabled preview frame independently. Keep the stacked PR draft, no merge/release.
