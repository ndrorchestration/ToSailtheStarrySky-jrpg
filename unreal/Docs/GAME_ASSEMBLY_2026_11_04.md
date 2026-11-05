# TSTSS unified game assembly — 2026-11-04

## P0: cinematic gameplay
Believable scale, curvature and lighting; intentional framing, atmospheric depth and readable contrast remain the highest visual priority. Native beauty shots and actual player input must be reviewed together before declaring the slice complete.

## One integration branch
`review/ue58-game-assembly-20261104` combines:
- First Wake #735 at `3cc3c979aba0dfe21f2929ce625459c16d19230e`: opening interactions, objective HUD, save/restore contracts, water rewind, physical-water greybox authoring.
- Hybrid class UMG #745 at `fb5fc351b7f562f37e9e689b9b637b3caccd9de9`: class definitions/catalog validation, selection projection, passive UMG board and config guard.
- Ender gear/combat #746 at `3057e46769303c5e258db91aa815e6f0d11f1ca9`: owned equipment ledger and staff/armor/learned-spell native integration fixture.

This assembles source systems; it does not make the class board interactive, attach equipment to a playable battle, or place the approved character/ship assets into First Wake. No protected-main merge or release.

## Integration corrections
Preserved all 29 distinct automation identities when resolving the verifier conflict. Updated strict report acceptance and shortened-registry rejection to 29. Added the existing UE UMG module to both source dependency inventories; no third-party install or engine upgrade. Scoped the old Canvas HUD no-UMG check to HUD independence, since the separate class board legitimately uses UMG. All dependency-denial tests remain active.

## Assembly sequence and ownership
| Layer | Source | Next observable completion |
|---|---|---|
| Opening/story/save/water | Combined branch above | Real default-start movement, E/J/F5/F9, ordered Ionia-first progression and disk save/reload |
| Class/equipment/combat | Combined branch above | One interactive encounter driven by real controller/UI, preserving learned-skill and owned-gear validation |
| Aureate Wake | #732 visual candidate; #747 envelope audit | Crew-scale floor/eye-height, wing clearance and unobscured native camera before staging shared scene |
| Ender | #721 model/goggles; #749 lighting candidate | Approved face/hair/outfit, rig/grip and animation before player replacement |
| Environment | #705 and #738 studies | Native physically lit sky/ocean and horizon framing alongside ship |
| Shared visual slice | Future isolated scene on this assembly | Side-by-side approved-art/native gameplay captures; separate performance and accessibility review |

Do not import all divergent ship actor branches wholesale. The V4 bridge/quarters study has envelope and crew-scale holds; an artistic screenshot is not physical clearance. Ender's diagnostic lighting improvement is not final likeness approval.

## Playable acceptance
1. Fresh start as Ender, Ionia hiring/boarding, engineering inspections, launch.
2. Real hull-water interaction, stable flotation, Splashdown begins Chapter 1 Act 1; Lyra enters afterward.
3. One usable battle: staff strike, armor response, authorized technique/spell, visible costs and feedback.
4. Disk save/reload preserves story/party; class/equipment persistence remains a separate schema decision.
5. Native gameplay capture with ship/characters/environment, readable UI and measured frame time.

Five Lights and character ranks stay canon; test fixture numbers/jobs are not new canon. Starbourne remains gated. Existing source reports and historic native receipts are not transferable to this combined revision.

## Verification and next handoff
Source suite: 218/218 Python tests, 29 registered native identities, and 16/16 synthetic report fixtures passed during assembly. Native result must be read from the exact-head receipt; source tests alone prove neither PIE nor cinematic approval.

Initial combined native verification at ca653c16b980583b689042665798b1433a55299d: UE 5.8.4 Editor build and strict native verifier PASS, exit 0. Final source housekeeping/doc head is verified separately; see its Saved/MigrationEvidence exact-head report.

## First Wake review entrypoint
`unreal/Tools/Start-FirstWakeReview.ps1 -EngineRoot "C:\Program Files\Epic Games\UE_5.8" -ExpectedHead <full-SHA>` performs preflight only. Add `-OpenEditor` to open the explicit V2 Prelude map with D3D11; click Play in Editor to use WASD/mouse, E interaction, J objective, **F6/F9** isolated story-only review save/load; normal non-PIE Game saving remains F5. F5 is never bound to the PIE pawn quicksave action. This is an Editor review path, not a packaged game launcher.

Requires current clean source, unchanged V2 map, exact-head 29-test native report, strict native map admission, no existing saves, no other Editor/Live Coding and sufficient RAM. It protects both tracked configs for the Editor lifetime and restores their writable attributes when the Editor closes; keep the launcher terminal running until then. Never save over the tracked map. Existing review saves cause refusal on subsequent launches rather than deletion or silent overwrite.

The native map checker and its launcher now explicitly admit this named game-assembly checkout in addition to the two historical QA roots. Exact SHA, map digest, source cleanliness, save exclusion and every native receipt check remain required.

The V2 map has seven interactive milestones ending at engineering signoff. Opening it is not evidence of launch, real water/Splashdown, combat UI or cinematic completion. Real human input and visual acceptance remain separate from commandlet map-actor verification.
