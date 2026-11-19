# Aureate Wake — stacked-branch reconciliation gate (2026-10-31)

Status: integration review, **NOT an approved merge or Unreal Engine build**.

## Verified current source and CI
- Foundation PR #608 head at inspection: `503ed82ff6a87e8e6b15a798ff9d9ec17da17490`.
- Ship PR #610 head before this document: `16fdf88ab79dc8a91879d282d51ba40c3cb7e78f`.
- PR #608 engine-free inventory run `41179375813`: completed/success.
- PR #610 engine-free ship source contract run `41179379729`: completed/success.
- Both are static/CI checks; no UE 5.8 Win64 compilation, render or in-game validation evidenced.
- GitHub compare from ship branch to foundation reported **diverged, ahead 123 / behind 32** (direction is foundation relative to ship). These counters include commits and are not a count of conflicting files.

## Integration dependency risks
1. Parent foundation has advanced since the ship branch was first stacked. Source-only workflow success can use PR merge context and **does not prove** #610's own branch contains every parent script.
2. Review current foundation implementations of `TSTSSWaterLandingGate`, `TSTSSWaterContactAdapter`, and First Wake story state before wiring `AureateWakeWaterObserverComponent`. Do not create competing event authorities. Keep the one-way chain physical overlap/velocity → accepted story milestone → Seaborne presentation.
3. Test the ship actor with scene-authored collider, water volume and correct velocity source. A source assert cannot prove actual physical dynamics.
4. Preserve four persistent wings, the tucked Submersible form, the two Seaborne hydrofoils, hidden Orbiter and approved character/ship art. Preview cube geometry is **not** artistic acceptance.
5. Do not merge #610 directly to protected main. Resolve the **parent #608 integration first**, with review of conflicts and changed test names. Avoid force-push or blind automatic integration.

## Fast, safe reconciliation procedure
- Freeze exact commit SHAs in an isolated local checkout; do not reconcile in a shared moving worktree.
- Inspect merge-base and diff in both directions, then trial merge foundation into a **temporary integration branch**. Resolve conflicts while preserving #610-specific ship files and current #608 gameplay/save/physics authority.
- Re-run both engine-free checks against the integration result, then on a real UE 5.8 Windows machine run `unreal/Tools/Verify-Unreal.ps1` and a renderer-enabled First Wake water scene.
- Review integration diff and test evidence before updating the stacked PR, and require creator art approval separately.
- If no UE workstation is available, leave changes as an unpromoted integration candidate; never label source checks as an engine test.

**Do not auto-merge or release on the basis of this document.**
