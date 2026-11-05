# Unreal upstream integration audit — 2026-10-30

**Disposition:** SOURCE-BOUND ADAPTATION, not cherry-pick/merge, not runtime verified.
**Baseline:** GitHub main at `725ecc5f56516466d46987fb04421f4decb5d5ef`. Unreal branch compared against main: 64 ahead, 0 behind at inspection. Existing Unreal branch includes combat abilities/turn files and tests; inspect their actual contents before changing combat interfaces.
**Engine decision:** Creator approved Unreal migration on 2026-10-30. Historical Godot 4.7.2 remains the reference and preservation line; the older `AGENTS.md` default-engine statement is superseded for this *new isolated migration* only. No existing historical native evidence is re-labeled Unreal evidence.

## Source candidates and bounded pull-in plan

| Authority source | Reusable contract | Unreal adaptation | Gates |
|---|---|---|---|
| Godot #547 at eae84a63d370d64bc5a11b049df4abb958301394 | Default entry, flyer/hire, three checks, actual water contact/flotation, separate F5/F9 save checkpoints | Character interaction events + 3 station state + physics-derived water contact; keep chapter-order assertions | Native Unreal editor test, game capture and cold-launch replay |
| Godot #548 at 8bd149b153e0ab417c4c5314ee08336df3cdf267 | Later family, material acquisition, failed material-only retest, player-driven melody interpretation | Separate optional/unintegrated chapter extension behind phase-completion gates | Never infer this is part of #547 default route or release |
| Godot #551 at 9cfca20b07a3823fb345b22e186ed9bdfcd40931 | Installer lifecycle and Windows smoke expectations | Adapt manifest, exact binary identity, install/launch/uninstall evidence | Native Unreal packaging, Defender-on custody and independent Windows QA |
| docs/CHAPTER_ONE_HIGH_QUALITY_POLISH_CHECKLIST_2026-10-28.md | 32 open Chapter I gates CH1-01..CH1-32, evidence schema and 15 P0 items | Mirror gate IDs in Unreal review; do not close merely because source/test scaffolds exist | Exact-head tests plus real art/story/player/security evidence |
| docs/CHARACTER_AND_ART_AUTHORITY.md | Characters and production reference constraints; Ender staff geometry; Ionia green eyes and blonde curls; Lyra/Talen, Reson and Aepex characterization | Import manifest with provenance, copyright eligibility, 3D rigging, silhouette and in-engine side-by-side review | Creator approval of each native rendered asset; October 30 approved cast art supersedes conflicting older candidate visuals |
| docs/WORLD_SHIP_VISUAL_DIRECTION.md | Compact dragonfly ship, four articulated veined wings, geodesic dome/home, landing geometry, luminous solarpunk world, real world physics | UE asset/vehicle specifications and filmic renderer acceptance; no generic aircraft stand-in | Native geometry, collision, animation, climate/horizon and performance evidence |
| Godot combat PR #601 and main combat policy / tests | Atomic roster behavior, rejected invalid actions, party identity and costs | Compare UE transactional abilities/turn code with exact Godot fixtures; port *test vectors* not GDScript | Parity fixtures at exact source refs and in-engine automation |
| docs/MAGIC_SYSTEM.md | Affinity distinct from learned mastery and authorized combat actions | Keep magic catalog locked until implemented and approved; Five Lights as story affinities | Negative grant tests, no implied battle spells |

## Required conflict resolutions before parity claims

1. Historical JS documents describe Lyra-first onboarding and 1–5 active combat members; these are **not** authoritative for the revised opening or the currently requested 3-active battle design. Use Ender → Ionia → Lyra recruitment, and limit active combat participants to three pending explicit design change.
2. Existing Unreal `UTSTSSFirstWakeState` represents a short ordered preflight/water landing only; it must not auto-advance later reunion, materials, retest or melody.
3. Old agent entrypoint and native QA refer to Godot as forward engine; update an engine-decision addendum at review rather than silently rewriting history.
4. Keep unpublished/private lore and unlicensed artwork out of the public repository. Include source IDs/hashes and descriptions, not private assets.
5. Character cast composition itself was approved October 30; no in-engine character mesh or animation is approved by that decision alone.
6. A compiler PASS cannot establish artistic acceptance, packaged-playability, native physics, security clearance or release approval.

## Smallest reversible integration steps

- **A:** Implement three separately acknowledged preflight inspections with guard preventing launch before all three, and tests for repeated/out-of-order checks.
- **B:** Bind water contact and sustained flotation to measured collision/physics values, never scripted milestone shortcuts.
- **C:** Build stable 3-member active formation, keep five recruitable roster identities without inventing early recruits, and mirror Godot combat parity fixtures.
- **D:** Connect first chapter save checkpoints and versioned snapshot restore to a true native scene.
- **E:** Import approved art with source manifest and capture reference-matched stills in Unreal.
- **F:** Execute Win64 editor and automation verification, review visuals, then separately package.

**All adaptations pending implementation or verification unless explicitly recorded in this branch. No merge, release or acceptance is authorized by this audit.**
