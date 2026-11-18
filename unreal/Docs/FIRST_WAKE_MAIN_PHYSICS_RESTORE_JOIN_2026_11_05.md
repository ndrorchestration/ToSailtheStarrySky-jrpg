# First Wake: main-baseline physics and restore integration

Base: merged #780 at `b7fa63cf1d186854e0f733590bca938caf2a40bd`.
Selected source: #779 at `e9989df6cfb180bc6a8d3332ea0365387b5d121a`, including its launch-arm, consumed-marker and bounded water-telemetry lineage. This is a selective integration; unrelated sibling art/staging tools are not imported.

## Behavior

- The opt-in prototype hull stays dry with physics disabled before player-authorized launch. A new story/restore generation resets the hull and invalidates prior contact evidence. Physics still owns sea contact and flotation.
- Accepted, named PIE review markers release their Visibility ray. After successful F9 restore, completed milestones stay transparent and incomplete milestones regain interaction. Inspection stations use individual mask bits.
- Main's pass-through marker policy is preserved: restoring a marker never restores Pawn blocking. Rejected milestones still cannot advance story.
- Main's PIE F6 save binding, Shift+F5 protection, standalone F5, guarded F9, save schema, title mode and media dependencies are preserved. Cross-session Continue is not added or implied.
- Optional water frame telemetry and independent elapsed-time/post-flotation validators are included. No rounding or weakening of the two-second stability threshold.
- PIE interaction diagnostics distinguish missed rays, wrong targets, reach denial and successful interaction for the remaining Pressure-station investigation.

## Checks

315 Python tests passed in Linux. The portable physical adapter, input binding and save-handler harnesses passed, including mutation controls for prelaunch physics, stale contact after rewind, F5 shortcut conflicts and overwriting old saves. The source registry retains all 29 native test names. Native integration tests retain main's collision checks and add restore, consumed-marker and unrelated-actor cases.

Prior native #779 replay evidence is specific to that source and F5 binding; it is not a native result for this combined F6 branch. Exact-head Win64 build, 29 native automations, real F6 → advance → F9 → replay, and the full ten-stop route must be recorded separately. No private movie, save or review map has been copied into the public repository.

## Vertical-slice completion still open

Actual player-controlled flight/landing; persistent New Game/Continue with location and party; a player-controlled battle and usable class/equipment UI; finished ship/character assets; native harbor lighting and nonmirrored markers; audio/accessibility/performance review; packaged cold-start and save/restart acceptance. Preserve Ionia-first, Splashdown as Chapter 1 Act 1, approved art authority and locked Starbourne.
