# Celestial Arc — Godot-native integration boundary

**Project owner:** [To Sail the Starry Sky](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg)  
**Engine:** Godot 4.7.2.  
**Workstream:** planetary, auroral and lunar exploration, tracked in [#372](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/372).  
**Status:** in development; no merged native celestial runtime; cinematic visual and Windows/GPU acceptance pending.

This directory is intentionally **nested within the owning game project**, not treated as an unrelated product or engine. It is a **public-safe coordination surface**. The creator's v0.8.1 Godot project remains in private source storage, pending a separately provisioned *private* Git repository.

## Directory contract

- `README.md`: public scope, integration limits, and acceptance authority.
- `PRIVATE_SOURCE_HANDOFF.md`: operational intake instructions and blocked/unblocked states without protected gameplay details.
- `private_native/`: **reserved private checkout path**, ignored from the PUBLIC repository. Do not commit private source here, even on a draft branch.
- Existing `godot/flight_slice/`: experimental noncanonical art study on [PR #370](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/370), not the production lunar runtime.
- Existing [PR #369](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/369): public evidence only; its source archive was deliberately not included.

## Privacy and project ownership

**GitHub does not provide per-directory or per-branch privacy.** A `private/` path or a branch named `private/*` in this PUBLIC repository would still be public. Keep the unreleased v0.8.1 sources, assets, review fixtures, gates and spoiler conditions outside this repository until a distinct **PRIVATE** Git remote exists. A private repository can later be mounted at `godot/celestial_arc/private_native/` locally, and may be registered as a private git submodule following security and access review. Its content must never be staged into this public Git tree.

## Definition of done

A single independently reviewable Godot candidate demonstrates shipboard departure → spherical planetary navigation → late-game auroral transit → authorized guarded lunar transfer → explorable moon geography → safe return and persistence; it also provides creator-reviewed high-fidelity cinematics, accessibility, installer QA, and target-Windows-GPU evidence. The tests or software captures of one isolated prototype cannot satisfy the whole gate.

No merge, game release, canon promotion, installer publication, or permission to expose private story content is implied by this public-safe directory.
