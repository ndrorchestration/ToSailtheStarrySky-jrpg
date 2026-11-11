# First Wake V3 PBR genuine D3D11 review — four native cameras

**Review-only, not approved cinematics, not PIE.** Source parent [PR #806] is a real Unreal 5.8.4 derived saved World with separate independent native readback. Source exact map /Game/TSTSS/Review/Scenes/FirstWake_MaterialLookdev_20261111_REVIEW_V3 has SHA256 3e3d65e1e30b7620b6ddc4d47cf7b94e447d930a7f290818068ac50a51641815, **200 actors**, 30 native Texture2Ds, 10 compiled PBR Material assets, 18 inherited surface overrides, 84 visual-only architectural details and one new camera. Original 115-actor source and seven story interactions/collision preserved.

GPU source branch is review/ue58-vslice-lookdev-gpu-20261111, intended runtime worktree C:\TSTSS_V3_GPU_20261111\TSTSS_VSliceLookdev_20261111. This preserves the canonical #806 source and native source snapshots, and allows only one **uncommitted runtime-only** .uproject plugin addition: PythonAutomationTest true. No C++/Config changes. Existing older 115-actor GPU test registration is fail-closed outside its original runtime.

The guarded private importer copies/re-hashes **367 files**: 321 prior verified native module/mesh/World/receipt dependencies, 30 PBR Texture2D packages, 10 PBR Material packages, the exact new V3 .umap, and five native/custody stage/readback receipts. This intake is exclusive-create and never overwrites a prior source or a production level. Binary and GPU evidence stays local to NEONTIC, untracked.

The native test loads and introspects precisely the saved V3 scene, verifies PlayerStart, all seven milestone IDs, seven separate TextRender signs, original solid traversal floor and new NoCollision detail actors. It transiently hides ONLY the seven signs by applying the authored cinematic sign policy *in memory* before spawning four temporary cameras. The original .umap is never saved. Four planned views at native 1280×720:
- Harbor Establishing: camera (-2800,-2900,950) toward (-850,540,190)
- Engineering Open Quay: (470,840,420) toward (250,270,130)
- Aureate Boarding: (-2100,2500,600) toward (-850,980,185)
- Quay Paving Study: (-1450,-450,330) toward (-450,200,0)

Proof requires all four UE AutomationLibrary native screenshot tasks, named PythonAutomationTest controller SUCCESS and native child exit 0, four physically present valid CRC/DIM/SHA PNGs, matching native and host receipts, independently decoded nonblack pixels, preserved saved map SHA/source commit/Config, and native signature that only seven text signs were hidden. A source test, screenshot task scheduling, or a zero Editor exit alone is not acceptance.

Host prerequisites: installed UE5.8.4, exactly one plugin .uproject delta, source Git HEAD of the GPU review branch, independently verified native source stage/readback at exact #806 head, no output conflicts or user SaveGames, no competing UnrealEditor/LiveCoding, at least **6.5 GiB free actual physical RAM and 14 GiB disk**, one owned UnrealEditor-Cmd D3D11 child with bounded watchdog. No competing user process is killed; no production user session is closed.

Visual reviewer must compare original V2 baseline PNGs (before checkerboard replacement and architectural detail) with new V3 frames to inspect concrete surface improvements, texture UV frequency, normal orientation, facade/roof/pier trim, lighting/horizon continuity and whether actual developer text is absent in cinema capture. Pixel diversity does **not** prove art quality. Full PIE movement and seven E interactions, physical sea contact, animation, Ender/Ionia visual fidelity, Lyra after splashdown, SaveGame and Creator AAA signoff remain independent acceptance gates. Starbourne remains locked.

## First native GPU HOLD and exact visibility repair (retry R1)

The first native UE5.8.4 D3D11 automation process exited 255 with an explicit failure before any PNG frame or native capture receipt. Original map, Config and source HEAD remained unchanged. Unreal showed that TSTSSMilestoneActor has no is_hidden() method in cinematic helper first_wake_cinematic_sign_policy_v3.suppress_transient_only. The revised helper reads the native Actor hidden field via get_editor_property("hidden") instead. Real milestone actors remain visible, interactive and unmodified; only seven independent TextRender signs are transiently toggled for game-view-only screenshots.

All first-run failure evidence remains in Saved/FirstWakeMaterialLookdevV3 under original PBR_V3_GPU_UE584_D3D11_HostLog_20261111.log, PBR_V3_GPU_UE584_D3D11_HostReceipt_20261111.json and PBR_V3_GPU_AutomationReport_20261111. Do not overwrite or delete them.

R1 has entirely new screenshot output folder D3D11_PBR_V3_20261111_R1, host log PBR_V3_GPU_UE584_D3D11_HostLog_20261111_R1.log, host receipt PBR_V3_GPU_UE584_D3D11_HostReceipt_20261111_R1.json and automation report PBR_V3_GPU_AutomationReport_20261111_R1. A negative regression test refuses the nonexistent .is_hidden() API, checks the real reflected hidden field, and requires unique retry output paths. Full local source suite **342/342 PASS** before retry; native R1 capture not yet claimed.
