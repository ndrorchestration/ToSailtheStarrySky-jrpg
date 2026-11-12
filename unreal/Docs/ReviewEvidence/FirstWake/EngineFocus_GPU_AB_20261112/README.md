# First Wake engine focus — GPU capture A/B (review only)

- Actual Unreal 5.8.4 render: D3D12, Intel Iris Xe, isolated review map, no null RHI, 12 November 2026.
- Source-locked map: /Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview; captured at commit e62a3d9b4d711ad95484d609b2e6282f6b4da673, SHA-256 9338c2abdebd7eeb19e50fb98733a9358d417f0633f8947aa9c6d48259c5e65a.
- A uses the 65 mm f/2.8 manual-focus CineCamera; B uses its same-transform 65 mm f/2.8 disabled-DOF counterpart.
- Frames: 810×540 PNG each (36×24 mm CineCamera filmback). Side-by-side composition labels genuine Unreal frames; not AI illustration or approved game artwork.
- Measured difference: average absolute RGB channel delta 1.137/255; 3.23% of grayscale-difference pixels exceed 8/255. Subtle and not visually approved.
- Current art is placeholder proxy geometry. This does not establish final Ender, Ionia or ship art, PIE, gameplay transitions, sound, or production performance.
- Safety: no game-map override, no playable-camera transition, no save-state mutation, no Starbourne unlock; focus receiver remains default disabled. PR draft/unmerged.

Retain both original PNG frames, the labeled comparison, native_gpu_evidence.json and capture_source_exact_e62a3d9.py for review provenance. The archived capture source is pinned to its tested earlier commit and output namespace; it is historical evidence, not a turnkey production renderer. Original session-local logs remain on Neontic in unreal/Saved/EngineFocusReviewV1.

## Visual findings and acceptance frontier

This is native GPU evidence of an implemented camera effect, **not** an approved look. The bright cyan foreground spans much of the lower frame and partially blocks the engine-instrument view; the background and yellow engine proxy have flat review materials, limited practical highlights, and little atmospheric separation. A global mean RGB delta of 1.137/255 is too subtle by itself to establish purposeful, readable bokeh. The framing contains clipped background review text.

The next safe improvement is a separately authored draft look-development variant with motivated engine/instrument practical lights, clear focal subject, foreground sightline clearance, material roughness/depth cues, and the same paired optical control. Re-capture in a real RHI with equal camera position, lens and exposure, then check player-view legibility and frame time before any visual approval. The existing authoritative presentation coordinator must continue to own story/weather cues; no new gameplay or player-camera authority is granted.