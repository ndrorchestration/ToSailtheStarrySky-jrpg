# First Wake input convergence proposal: F6 save / F7 Continue (review-only)

## Why this is needed
Draft [#781](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/781) preserves the mainline PIE **F6 save**, normal game **F5 save**, session-scoped **F9 load** and Shift+F5 editor-stop protection. Draft [#782](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/782) instead reassigned F6 to two-press Continue and bound quicksave to F5 in PIE, creating an unresolved conflict at vertical-slice [issue #778](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/778).

This **isolated stacked proposal** changes only #782's experimental source to keep the established save controls and assign **F7 preview/confirm Continue**. It is not merged into #781, does not grant cross-session compatibility, and does not establish native gameplay.

## Proposed review controls
| Context | Save | Load | Continue |
| --- | --- | --- | --- |
| PIE disposable First Wake review | F6 (Shift keys rejected) | F9 (only this session's owned slot) | F7 twice within 30s (only bound, prelaunch, explicit player confirmation) |
| Normal game | F5 | F9 | Not bound |
| Unreal Editor | Shift+F5 stops PIE | — | No silent restoration |

Continue is restricted to prelaunch saves with matching review project/map, bounded digest and valid player/story snapshot, with user confirmation, no auto-load, no ship physics/contact resume, and no Lyra/Starbourne shortcuts. First Wake runtime save/Continue test still requires an actual Windows Editor restart; no cross-branch integration was attempted.

## Acceptance
- Source-level positive/negative checks for distinct bindings, PIE vs normal game branching, Shift protection, two-step preview and HUD labels.
- Existing #782 manifest, save and objective tests, and all other source preflight checks on exact head.
- After resource admission and an authorized integration successor: genuine UE 5.8.4 C++ build, 29 native automations, physical W/E route, F6 save plus sidecar hash, F9 same-session replay, clean Editor restart, F7 preview without mutation and F7 confirmed continue restoring Ender position/story, negative malformed/foreign saves.
- Compare #781 physics/marker/collision behavior and #783/#788 directly observed splashdown constraints. **Do not merge by overwriting #781's F6 or rely on ancestor test receipts.**

No protected maps, files under Saved/SaveGames, production assets, licensing, canon, Starbourne gate, or release permissions changed. A source pass is not a native or playable result.
