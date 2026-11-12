# First Wake engine focus — GPU capture A/B (review only)

- Actual Unreal 5.8.4 render: D3D12, Intel Iris Xe, isolated review map, no null RHI, 12 November 2026.
- Source-locked map: /Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview; captured at commit e62a3d9b4d711ad95484d609b2e6282f6b4da673, SHA-256 9338c2abdebd7eeb19e50fb98733a9358d417f0633f8947aa9c6d48259c5e65a.
- A uses the 65 mm f/2.8 manual-focus CineCamera; B uses its same-transform 65 mm f/2.8 disabled-DOF counterpart.
- Frames: 810×540 PNG each (36×24 mm CineCamera filmback). Side-by-side composition labels genuine Unreal frames; not AI illustration or approved game artwork.
- Measured difference: average absolute RGB channel delta 1.137/255; 3.23% of grayscale-difference pixels exceed 8/255. Subtle and not visually approved.
- Current art is placeholder proxy geometry. This does not establish final Ender, Ionia or ship art, PIE, gameplay transitions, sound, or production performance.
- Safety: no game-map override, no playable-camera transition, no save-state mutation, no Starbourne unlock; focus receiver remains default disabled. PR draft/unmerged.

Retain both original PNG frames, the labeled comparison and native_gpu_evidence.json for review provenance. Source-locked capture scripts and native runtime logs remain on Neontic in unreal/Saved/EngineFocusReviewV1.