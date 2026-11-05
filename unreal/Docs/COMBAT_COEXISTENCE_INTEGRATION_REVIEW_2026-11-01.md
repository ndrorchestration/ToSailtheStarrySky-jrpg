# Combat data / guarded skills / turn-manager coexistence — review-only

**State:** Source-composed, unmerged, NOT native-verified, NOT a playable gameplay integration.

## Pinned provenance

- Base: PR #666 head `5d46713032aff8077fcf4fb85d1fde45d8dd1d1e`, which already incorporates PR #662 head `75a89e8c26edaeed063a818133c94142139ee14c`; both descend from PR #608's foundation `4b85f0d1d7b8870f09d72420871abf4553e3dfbf`.
- Added the **seven previously absent** #665 data-contract, tests, CSV-template, and documentation files byte-for-byte from PR #665 head `a0be01ed280279e3a650d4c8f5d9f051ef6f4a00`. Their source Git blob IDs should be compared during review.
- Reconciled `unreal/Tools/Verify-Unreal.ps1` to require the existing turn manager, magic/weapon, and four data-contract suites, plus one new coexistence suite.
- Added `TSTSSCombatDataCoexistenceTests.cpp` as a new noncanonical fixture. **No existing execution implementation modified.**

## Gate ownership; no implicit adapter

| Concern | Existing source owner | This branch does NOT do |
| --- | --- | --- |
| Data definition, affinity, level eligibility, baseline validation | #665 `FTSTSSCombatData` | Grant execution rights from an affinity, level or proposed catalog |
| Explicit spell/weapon admission, mastery, equipment, cooldown | #662 `FTSTSSBattleSkillSystem` | Derive `ReviewExecutable` from `CreatorApproved`, `Proposed` or DataTable presence |
| Three-active production party target | Creator specification / #665 validation | Change #666's existing **1–3** active preview allowance to exactly 3 |
| Turn selection and accepted commands | #666 `UTSS_CombatTurnManager` | Change the `TryUseDataTable` call path or add a parallel damage resolver |
| Original transactional damage/heal executor | #608 `FTSTSSCombatAbilities` | Offer a new direct gameplay entry point that bypasses #662 |
| Story Lights and resonance | Creator story direction | Convert the Five Lights into combat-element entitlement or resonance into an MP pool |

**Outstanding design hazard:** In #665, non-shipping `TryBuildAbilityData` may intentionally derive a level-eligible catalog from `Proposed` rows. The low-level `FTSTSSCombatAbilities::TryUse` is not a substitute for #662's higher-level admission/memory/equipment/cooldown checks. This branch **does not connect the output** to the #666 turn manager. Any future runtime adapter must require explicit provenance and independently authored skill/weapon admission, and must deny unknown, unapproved or DesignOnly entries by default. This isn't established merely by coexisting in one build.

## New acceptance regression

`TSTSS.CombatIntegration.DataContractCannotAutoAuthorize` is a native Editor automation declaration. It exercises:

1. Valid **noncanonical** five-character baseline ordering and a `Proposed` level-1 design spell, confirming the review data builder may expose it without execution authorization.
2. Shipping-mode rejection of proposed/unapproved data **without mutating existing catalog or learned outputs**.
3. Higher-level `DesignOnly` denial even when the source-derived learned set contains that spell and mastery exists, preserving candidate state and cue outputs.
4. An **independent** `ReviewExecutable` fixture denied while unlearned, then denied without mastery, and permitted only after explicit knowledge and mastery are set. Successful execution changes only the returned candidate state, not the original.

Fixture spells and numbers are **not approved gameplay content**. These checks do not prove no future developer could manually mislabel a proposed source as `ReviewExecutable`. Require separate provenance-aware admission design before integrating data into gameplay.

## Source checks performed

- Read source at the exact heads above.
- Compared declared test registrations against `Verify-Unreal.ps1`: **20 declared, 20 required, no duplicates or missing** across nine C++ test files (source-text enumeration).
- No Windows native UE 5.8.4 UHT/C++ compile or Editor automation has been performed for this *combined branch*. The authorized RDC device was offline at review time; a previously successful ship-only Unreal build is not evidence for this combat branch.

## Required native verification before merge or gameplay wiring

1. Fetch this integration PR at its **exact current HEAD**, check a clean checkout, and run `unreal/Tools/Verify-Unreal.ps1 -EngineRoot 'C:\Program Files\Epic Games\UE_5.8'` in UE 5.8.4 Windows (building and running all 20 named suites).
2. If UHT/compile fails, record exact error and fix only in the disposable review branch; avoid stubs, false-green tests, or changes to shipping progression.
3. Inspect Editor automation report per test; run explicit negatives for invalid target, no mastery, no weapon, DesignOnly, proposed data, failed cooldown, and rollback. Positive review fixtures are not permission to publish gameplay.
4. Decide creator-approved data categories, exact three-active production behavior and strict runtime provenance mapping **before** any real catalog-to-turn-manager adapter or save migration.
5. Keep #662, #665, #666 and this new integration PR draft; no merges to main, no art promotion, no Orbiter changes.

This branch is only a reversible compatibility review, preserving independent agent ownership.
