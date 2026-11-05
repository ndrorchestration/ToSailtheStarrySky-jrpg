# Unreal quality acceleration — 2026-10-31

## Implemented in current isolated migration pass
- Reject water-tagged overlap without estimated hull immersion.
- Reject/reset water progress when chapter is neither Launched nor SeaContact.
- Require named water landing test evidence in Windows build verifier.
These are source edits, not claims of Unreal execution or speedup.

## Highest-return next steps, ordered by avoided rework
1. **Native compile first.** Stop piling on code paths until UnrealHeaderTool and Win64 editor builds succeed. Capture exact commit SHA, compiler output and named test reports. The project currently has no verified native build.
2. **One cinematic vertical slice.** Prioritize Ender finding flyer -> Ionia hiring -> three inspections -> short flight -> physical splashdown. Do not grow the world or Chapter 1 simultaneously.
3. **Physics source of truth.** Refactor ship buoyancy/contact into a dedicated hull + water simulation with sampled surface height, fixed-step force integration, damping and pitch/roll stability. Bounding-box water height is only an approximation. Prevent all generic story-progress APIs from granting SeaContact or FlotationConfirmed without trusted physics evidence.
4. **Art import pipeline.** Build an asset manifest: reference source, permission/license, import settings, skeleton/rig compatibility, texture maps, LOD, source hash and in-engine screenshot. Do not call 2D references production-ready meshes. Use material instances and shared master materials to reduce shader recompilation.
5. **Quality/performance budgets.** Profile GPU and game thread in one representative coastal scene. Record hardware, resolution, UE version, Nanite/Lumen settings, frame time and memory. Do not claim fixed FPS from design docs. Scale quality with tested presets.
6. **Port test vectors not engine code.** Reuse Godot #547 contact/safe return, #548 investigation and tuneable accessibility contracts; preserve exact branches/commits and check for canon drift before each port. Preserve the current normal New Game Ionia-first story.
7. **Ship and installer gates.** Keep Godot protected; draft Unreal PR only. Verify Windows install/launch/uninstall and Defender-on provenance separately after native packaging.

## Current blocking evidence
No confirmed Win64 UE compile, automation run, water physics runtime scene, cinematographic captures, approved Unreal 3D cast, release package or installer. Avoid equating tests present with tests passed.

## Workflow improvement
For each focused change: read latest branch -> isolate one behavior -> add negative test -> commit -> run native exact-head verifier -> assess performance -> review visual evidence -> only then proceed to next layer. Separate independently designed workstreams but do not race writes against the same branch head.
