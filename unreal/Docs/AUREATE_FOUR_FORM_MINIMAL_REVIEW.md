# Aureate Wake: minimal four-form review slice

## Bound source and authority
Review baseline: PR #610, `aba8d207614dbe9157a43d3427d05fc75e17755e`, open/draft/unmerged at inspection on 2026-10-31.
This isolated review/fix branch is based on that exact commit. It does not integrate #625/#626/#629/#631, replace Godot authority, alter story/save state, admit artwork, or authorize merge/release.
The Oct 30 approved ship direction guides review: one recognizable hull and forward bridge, four persistent dragonfly-derived wings, Seaborne hydrofoils, visible tucked Submersible wings, four equal radial Orbiter sails. BasicShapes are NONCANONICAL. No hidden progression conditions are specified here.

## Smallest reversible slice
One bounded hydrofoil visibility fix, transient actor automation, an isolated C++ request probe and one unsaved empty Editor review level. No production map, mesh, material, collision or story edits.
Revert this branch's commits to roll back; original #610 and main remain unchanged.

Run `python unreal/Tests/check_aureate_preview_source.py` and `python unreal/Tests/check_aureate_request_logic.py` (requires g++). The latter compiles the actual RequestForm method with minimal array/component/pose substitutes: it checks request visibility decisions only, not Unreal types, transforms, renderer or physics.
Build the project's Development Editor Win64 target with the intended UE 5.8 toolchain, recording exact engine build and candidate git SHA.
In Editor Session Frontend > Automation run `TSTSS.AureateWake.Review.FourFormMechanics`. Preserve report/log and failures.
The test exercises actual actor requests and Tick in a transient world; it does not mock/reimplement pose mathematics.

Coverage: 12 directed transitions; invalid/same/busy/default-locked Orbiter rejection; negative delta; midpoint retains source form; overshoot completes; four component identities remain; visible tucked wings; foil visibility at request, midpoint and endpoints; cardinal equal radial sails; fixed bridge; sail blend endpoints; preview wing collision disabled.
Orbiter permission is enabled only on transient test actors. It is not a player unlock.

## Native visual review
Use a single actor with default BasicShapes, no AuthoredWingMesh and no WingMaterial. Keep a neutral background and matched camera/scale.
Keep Orbiter disabled for ordinary review. Exercise Skyborne -> Seaborne -> Submersible -> Skyborne and reverse routes; capture start, midpoint and end, preferably continuous clips.
On a separate disposable review instance, explicitly enable preview Orbiter, capture its four cardinal sails, and inspect every incoming/outgoing transformation. Discard the level without saving.
Compare front, side and three-quarter views to creator-approved reference, recording the exact reference identity privately.
Check persistent hull/forward bridge, four wing identities, Sea foil deployment, visible tucked underwater wings, equal sail dimensions, clipping/occlusion and discontinuities. Reject hidden wings, changing counts, bridge rotation or unsafe crossing.
Capture real renderer frames with normal rendering; NullRHI or source checks cannot supply visual evidence.

## Findings from exact baseline
- Existing source contract script executed locally: 10/10 PASS on fetched exact-head files. This is lexical checking only.
- RequestForm sets both hydrofoils visible for EVERY transition, including Skyborne <-> Submersible. Endpoints hide them again. Corrected in this review branch: moving foils are visible only when the source OR destination is Seaborne, preserving visible deployment/retraction. Native automation now checks request and midpoint as well as endpoints; engine execution remains pending.
- RefreshWingMeshes directly assigns imported meshes to centered-cube poses. Do not import root-pivot artwork into this baseline. Later adapter/art branches are separate candidates requiring explicit reconciliation.
- Wings interpolate translation, rotation AND scale. This is pose preview, not rigid articulated hinge mechanics or swept-volume clearance.
- The Orbiter switch is a preview permission, not narrative authorization. Disabling it during an accepted transition does not cancel that transition; scope this switch to isolated editor review.
- All preview mesh collision is disabled. No buoyancy, sealing, propulsion, contact, pressure or navigation proof follows from this test.

## Evidence and stop conditions
IMPLEMENTED: bounded preview visibility fix, native automation source, isolated method probe and review checklist.
VERIFIED locally: actual RequestForm compiled in an isolated g++ harness: 6/12 routes failed before the fix, 12/12 passed afterward; 10/10 lexical checks passed. This does not establish an Unreal build.
NOT RUN: Unreal C++ compile/native automation; Windows build; native render, materials, physics, performance and artistic acceptance.
Do not describe this as a playable migration or approved art. Stop admission on compilation/test failures, changed authority, unexpected unlock or visual defects.
Next: execute native test on a UE host; resolve observed failures in the same bounded slice; then port this additive test into the separately reviewed integration candidate after comparing current heads.
