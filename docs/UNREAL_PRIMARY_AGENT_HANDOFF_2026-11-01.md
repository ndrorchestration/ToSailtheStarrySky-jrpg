# Unreal 5.8.4 primary-engine directive and collaborator handoff (2026-11-01)

**Status: creator direction for review; proposed publication through a draft PR.** This file records the creator's newer Unreal-first decision and gives external agents a public-safe navigation route to existing source. It does **not** merge Unreal code, make a draft implementation canonical, approve artwork, or change game/story authority.

## Engine decision

- **Primary target for new game development: Unreal Engine 5.8.4**, using C++ with Blueprints and data assets where appropriate. This supersedes the 2026-10-24 Godot-as-active-engine entry in `AGENTS.md` once the coordinating documentation update is accepted.
- Preserve historical Godot and browser code as bounded reference/oracle material, not as the implementation destination. Do not delete it or rewrite save formats without parity and recovery evidence.
- Creator-approved characters, story, aesthetic, party order, and visual anchors are independent of engine selection. A new engine choice is **not** approval to rewrite canon or promote prototype art.
- Existing November 2026 integration, March 2027 alpha and May 2027 beta roadmap dates were drafted under earlier assumptions. Treat them as historical planning targets pending an Unreal-specific, evidence-based rebaseline, **not** promised delivery gates.
- Historical Godot F5/Chapter 1 QA remains a valid *Godot historical acceptance issue*, but a successful Godot run is not a prerequisite for *review-only Unreal work*, and passing it cannot certify Unreal behavior.

## Where the Unreal source actually lives

**Do not infer “no Unreal project” from `main`.** The current public `main` may still be mostly JS and legacy docs. Unreal code and its `unreal/ToSailTheStarrySky.uproject` are on unmerged, often stacked draft PR branches. Read exact current PR heads, bases, changed files and CI receipts; never assume the heads or results below remain fixed after this document was written.

| PR | Review lane | Relationship / limits |
| --- | --- | --- |
| [#608](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/608) | UE 5.8 foundation | Engine scaffold; foundation for later draft slices |
| [#610](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/610) | Aureate Wake actor | Four-form mechanics prototype, default Orbiter hold |
| [#626](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/626) | Corrected wing GLB | Authored-wing pose and sampled clearance review; Orbiter collision hold |
| [#631](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/631) | Root-support geometry | Noncanonical four-support lookdev, guarded import and native review receipts in discussion |
| [#643](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/643) | Cast lookdev | Five draft static meshes and provenance/orientation gates, not approved rigs |
| [#656](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/656) | Ship forms | Native Seaborne/Submersible review work and follow-up hydrofoil-strut verification gates |
| [#662](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/662) | Spell/weapon technique executor | Source candidate: gated DataTable skills, review execution and nonrendering cues; 260 design-only seeds are **not** approved spells |
| [#665](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/665) | Combat data contract | Claude-authored candidate: validation, baseline/ability catalog bridge; parallel to #662; do not duplicate runtime admission paths |
| [#666](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/666) | Turn manager | Stacked on #662; 1–3 active party, initiative and terminal outcomes, not yet proven in native engine |

**No draft PR above is an automatic merge, release, final artistic acceptance or production gameplay authority.** A successful source-only test is not a UE native build, rendered screenshot, gameplay proof, or creator approval.

## Collaborator lanes (avoid overlapping edits)

**Claude / combat-data lane:** Start by reviewing #665 against #662 and #666 at their **live exact heads**. Identify duplicated types/catalog sources and incompatible validation rules before writing anything. Favor the smallest reversible *integration test/adapter* over a second combat framework. Own data contracts, validation, party abilities and source-vs-engine verification; coordinate changes to existing combat runtime files.

**Ship + native art lane:** Aureate Wake geometry, transform/hydrofoil/root-support scene and captures belong with #610/#626/#631/#656. Do not edit these files from the combat lane except through a separately agreed integration slice. Four wings, hydrofoil form, visibly tucked Submersible wings, and explicit authored-wing Orbiter rejection remain review invariants. Orbiter is locked.

**Character / cinematic lane:** #643 and the creator-approved visual references govern lookdev, not approved game-ready topology, skinning or cinematic materials.

Use `ToSailtheStarrySky-jrpg` and appropriate draft branches as the starting code source. Do not scaffold a duplicate UE foundation in `ToSailtheStarrySky-Dev` merely because `main` lacks `unreal/`. A second repository requires an explicit architecture and synchronization rationale.

## Public-safe gameplay constraints

- Five playable leads: Ender, Ionia, Lyra, Reson, Aepex. Three active party members; bench identities persist.
- Ender has the highest starting magic stats and MP, Lyra second. Lyra has the lowest starting HP, Ender second lowest. **Do not port legacy JS numeric values that violate this order** or fabricate new starting numbers.
- Story affinities: Ender—Spirit, Ionia—Earth, Lyra—Water, Reson—Fire, Aepex—Air. Affinity alone does not grant a learned spell, skill school, ability rank or combat entitlement.
- Party resonance is a story energy concept, **not** automatically a combat-magic resource.
- Ionia joins first in the approved introduction. Preserve the approved First Wake → Splashdown story sequence without exposing restricted unpublished plot content.
- Do not add canonical spell names, item catalogs, numeric stats, effect unlocks, story beats or character details without a cited creator-approved specification.

## Native verification, provenance and boundaries

- For every implementation, report source repo/branch, exact head and stacked bases, dependencies, changed paths, automated checks and **separate** native UHT/C++ compile, Editor automation, imported-asset verification, genuine renderer capture and creator approval.
- The creator's Windows machine has been used to compile an **isolated** Unreal 5.8.4 integration build and render ship support comparison scenes. Review details are in [PR #631 discussion](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/631), but this **does not** imply that pristine #631 compiles without its documented pinned-foundation reconciliation, or that external collaborators can access the workstation.
- No connector to a user's computer, repository push access, or background task is implied: ask for the relevant tool permission when needed. If read-only, deliver a small patch/review artifact rather than requesting personal access tokens in chat.
- Preserve noncanonical art boundaries, collision and Orbiter holds, authoritative story/save behavior, and public spoiler restrictions. No silent merges, source-of-truth replacements, public builds, or approval by passing CI.
- On handoff use **CREATOR CANON / ESTABLISHED SPEC / IMPLEMENTED / PROPOSAL / OPEN / RESTRICTED**, with links to primary evidence and known failures.

## Current combat integration watchpoints (2026-11-01 source inspection)

The following are **confirmed differences in draft source interfaces**, not native compile results or claims that the branches were already integrated:

1. **Data ownership:** #665 declares `FTSTSSActionDefRow` (`Attack/Spell/WeaponTechnique/Support`, `ETSTSSApproval`, `UnlockLevel`, `Learners`) and derives `FTSTSSAbilitySpec` plus learned sets for the **lower-level** `FTSTSSCombatAbilities::TryUse`. #662 declares a separate `FTSTSSBattleSkillRow` (`Spell/WeaponTechnique/JobArt`, `DesignOnly/ReviewExecutable`, mastery, weapon-class, cooldown) and implements gated `FTSTSSBattleSkillSystem::TryUseDataTable`; #666 calls the latter. **Do not wire #665's low-level catalog straight into turn-manager execution** or infer that level eligibility satisfies #662's authorization rules.
2. **Admission/provenance:** #665 checks `CreatorApproved` for `bShipping=true`, whereas #662 requires explicit `ReviewExecutable` for its review execution path. An adapter needs a clear, fail-closed mapping and should not convert any `Placeholder`, `Proposed`, or `DesignOnly` entry into executable content.
3. **Active-party policy:** #665's `ValidateActiveParty` requires exactly **3** distinct protagonists; #666's `InitializeEncounter` accepts **1–3** active entries. Specify separate preview/test vs production encounter semantics before harmonizing; do not silently change behavior.
4. **Shared test verifier:** #662, #665 and #666 all edit `unreal/Tools/Verify-Unreal.ps1`. Reconcile its required-suite registry and ensure bidirectional inventory checks pass at an actual combined commit, not just on individual PR heads.

**Smallest fail-closed next test:** build a disposable combined-head branch with isolated suites, prove that review-only skill execution still requires independent learning, mastery, equipment and cooldown checks, and add negative cases where level eligibility / proposed provenance alone cannot execute. Compile and run native Unreal automation only after source-level reconciliation; record exact combined SHA and do not merge.

## Concrete first task for a combat collaborator

1. Inspect the current heads and changed files of #608, #662, #665 and #666; write a short interface/diff reconciliation matrix.
2. Locate the single authoritative action data contract, validator, learned-skill checks, execution entry point, actor-local costs/cooldowns and turn-manager call path. Flag duplicate definitions or any silent fail-open behavior.
3. Produce the smallest isolated, source-first compatibility test or adapter proposal that proves #665 can coexist with #662/#666 *without* reimplementing their runtime logic or granting design-only spells.
4. Run available tests; clearly mark Windows native UHT/C++ Editor automation and gameplay capture **unverified** until actually executed at an exact integration head.
5. Submit a small **draft** PR or patch for review; do not merge. If conflicts exist, stop with a concrete dependency reconciliation plan and source references, rather than papering over them.

This handoff is intentionally scoped to coordination and review, not a license to change lore, release gates, production art or engine installations.
