# Chapter 1 Beta Roadmap — solo development planning baseline

> **ACTIVE ENGINE & STAGE OVERRIDE — 2026-11-02:** This document began as an October Godot-first roadmap. **Unreal Engine 5.8.4** is now the creator-selected forward engine. Preserve the October native Godot evidence only as historical comparison. The opening progression is **Ender → Ionia → Lyra → Reson → Aepex**, and **Splashdown begins Chapter 1, Act 1** after the First Wake prelude. The current [integrated Unreal draft #713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713) is review-only; [production QA matrix](../unreal/Docs/PRODUCTION_VERIFICATION_MATRIX.md) and [integration gate](../unreal/Docs/INTEGRATION_GATE_2026-11-02.md) take precedence over older engine implementation steps below. Dates remain *provisional planning targets*, not game release authorization.

> **2026-10-28 evidence update:** Pinned Windows Godot 4.7.2 import, five headless tests and nine native render frames passed at `4d2ec5fb`. **New P0 acceptance blocker:** the captured Chapter 1 review scene uses legacy Lyra-first startup and labels Ionia-first opt-in, while the desired production startup is Ionia-first. P1: text occlusion, mixed character presentation and historical branding. These are distinct from the separate main-entry-to-water regression PASS. Do not advance the November integration milestone until normal F5 default-route gameplay and visuals are independently verified. [Native audit](CHAPTER_1_NATIVE_INTEGRATION_AUDIT_2026-10-28.md).

**Planning date:** 2026-10-28  
**Alpha target:** 2027-03-31  
**Beta target:** 2027-05-31  
**Contingency window:** June–August 2027  
**Status:** planning proposal, not release commitment or proof of completion.

## Evidence boundary
The repository contains historical browser/p5.js and Godot/GDScript preservation work, while **Unreal Engine 5.8.4 C++/Blueprints** is the current forward-development target. Recent Unreal First Wake, combat, ship, artwork and Windows packaging efforts include multiple **draft, unmerged pull requests**. Passing tests on a draft branch do not establish main-branch behavior, artistic acceptance, shipped Windows artifacts, or a complete Chapter 1. Preserve established Five Lights/celestial canon and the current Ionia-first native opening; treat older Lyra-first browser documents as historical until reconciled.

## Monthly gates
| Deadline | Phase | Evidence required |
|---|---|---|
| 2026-11-30 | Integration foundation | One canonical **Unreal** First Wake prelude → genuine sea landing → Splashdown review path, correct Ionia-before-Lyra sequence, exact-head UE Editor build and automations, isolated save contract and reproducible PIE evidence; Windows installed candidate remains a separate future gate |
| 2026-12-31 | Narrative and JRPG | Core quest progression and playable representative battle, deterministic rules for stats/skills/magic/leveling, save/resume |
| 2027-01-31 | Cinematic environments | Chapter 1-critical locations, ocean, berth, Aureate Wake, coherent materials, lighting, sky/weather and camera; side-by-side native render review |
| 2027-02-28 | Characters and battle | Creator-correct Five Lights visuals, real gameplay animations, enemy/effects/UI integration, encounter balance review |
| 2027-03-31 | Feature-complete alpha | Fresh-save start-to-end unassisted Chapter 1 completion with no debug shortcuts or hard blockers; freeze major feature scope |
| 2027-04-30 | Beta candidate | Independent playtest, visual review, profiling, accessibility, major defect triage |
| 2027-05-31 | Beta decision | No known critical blockers, tested Windows installer/launch/uninstall, compatible saves, verified artifact/commit hashes and creator approval |
| 2027-06-01 through 2027-08-31 | Contingency | Extend only on evidence of unmet gates; do not silently lower beta quality bar |

## Scope and effort assumptions
Baseline 15–25 focused solo hours weekly, with a 20-hour planning scenario, approximately 70% effective productive capacity after coordination, investigation and rework. These are assumptions, not observed velocity. Scope prioritizes the complete Chapter 1 hero route, not production completion of the entire planetary globe, Moon Bridge or submersible traversal. Preserve underlying data/contracts for later expansion. AI-generated code and art studies do not count as accepted playable production until integrated and tested.

## Beta acceptance checklist
- [ ] Complete Chapter 1 narrative start-to-finish without developer commands
- [ ] Character, ship, environments, lighting and effects pass creator-directed cinematic review
- [ ] Combat, stats, leveling, equipment, magic, skill availability and costs agree with documented mechanics
- [ ] Save/resume, scene transitions and story/party state preserve progress
- [ ] No known critical blockers; performance targets defined and measured on Windows test hardware
- [ ] Dialogue presentation, sound, music, UI and accessibility reviewed
- [ ] Fresh-machine download, installer, launch, save, uninstall/reinstall and hashes verified
- [ ] At least five external tester sessions attempted, blockers captured and triaged

## Governance
Every Friday review: exact commit + PR state, playable path, latest native screenshots, passing/failed tests, defects, scope, owner visual approval and date forecast. Keep **verified merged behavior**, **draft candidates**, **historical compatibility runtime**, **planned work**, and **human artistic acceptance** separate. If integration slips, move dependent milestones instead of declaring incomplete work complete. No automatic merge, canon change or public release is authorized by this plan.

## October 28 native PR integration evidence
See [exact-head Chapter 1 integration audit](CHAPTER_1_NATIVE_INTEGRATION_AUDIT_2026-10-28.md) for observed stacked PR relationships, divergence against `main`, integration sequence and unresolved gates. It is an audit snapshot, not permission to merge.

## Immediate work (November P0)
1. Audit and deduplicate recent Chapter 1 draft PR stacks; identify exact-head dependencies, conflicts and actual main state.
2. Reconcile **Unreal** Ionia-first recruitment and Prelude/Splashdown stage boundary against the historical Lyra-first JS/Godot descriptions; validate in actual Editor PIE rather than assuming the seven-marker scene proves Chapter 1.
3. Validate a native **Unreal** continuous First Wake → real sea landing → Splashdown path behind source-locked Win64 and PIE gates. Do not promote review-only markers as genuine sea-water physics.
4. Establish one authoritative save version and clean Windows install candidate.
5. Measure a full native capture and first 30-minute unassisted player path before increasing scope.

Related anchors: [GitHub repository](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg), [3D/JRPG cohesion draft PR #582](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/582), [art draft PR #583](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/583), [Windows packaging draft PR #565](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/565).
