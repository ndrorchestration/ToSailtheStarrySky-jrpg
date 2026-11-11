# First Wake vertical-slice 115-actor native GPU review

**Scope:** Native UE 5.8.4 D3D11 screenshot/evidence, not new source art, accepted cinematic lookdev, full vertical-slice integration, or in-game PIE. This is a separate review-only worktree stacked on draft PR #800; never merge automatically or promote Starbourne.

## Verified predecessor / source of truth

The previously independently verified First Wake scene is present **locally** in C:\TSTSS_VSliceObjectsNativeV2_20261110, at Git head f47656774d5bb0f163cef550eba09577e2ab8aef, saved map /Game/TSTSS/Review/Scenes/FirstWake_SliceObjects_20261110_REVIEW_V1, exact SHA-256 837e537ab91339f56af006782c8e7dba9ac981d36eb800eb3b2a10c97661bbbc. Native UE5.8.4 stage and independent reopen returned exit 0 in two separate Editor processes: **115 actors = 84 original harbor + 31 added visual props, all 22 imported unique StaticMeshes, seven native story milestone actors, one PlayerStart, no new prop collision**. Source & config hashes preserved. Existing authored assets and imported native binaries are review-only, unapproved, local and untracked.

## Isolated visual workspace

Visual QA source branch review/ue58-vslice-object-gpuqa-20261110, clean Git worktree C:\TSTSS_VSliceVisualQA_20261110, source base f47656774d5bb0f163cef550eba09577e2ab8aef. A SECOND disposable runtime-only worktree C:\TSTSS_VSliceVisualRuntime_20261110 uses a separately named local branch at the same commit; ONLY that runtime copy of .uproject has the PythonAutomationTest plugin enabled as an uncommitted, strictly verified deviation. The canonical game .uproject and all dependency-contract baselines remain unchanged. The same previously verified C++ module and protected Config are reused, without new gameplay code.

Authoring: unreal/Tools/intake_first_wake_slice_gpu_review.py copies into the disposable runtime worktree only the 92 privately verified parent packages and receipts, all 220 native object mesh/material package files, new saved review .umap and four actual UE stage/readback receipts, original native module and manifest. It rejects file provenance drift, restricted Starbourne/Submersible packages, path traversal, unexpected target/plugin changes, all prior output conflicts, and file hash differences. No original worktree file is moved or replaced. Binary scene packages remain local/untracked and are not included in PR.

Runtime: unreal/Content/Python/test_first_wake_slice_object_gpu_review.py registers one exact PythonAutomationTest named test with Unreal. The producer unreal/Tools/capture_first_wake_slice_objects_d3d11.py loads and validates the saved 115-actor World by exact map SHA and UE actor introspection, including 31 collision-disabled props, all seven milestones, 22 unique imported meshes, no Starbourne and one PlayerStart. It then creates **three transient unsaved review CameraActors** using verified look-at rotations:
- Harbor establishing: (-2800,-2900,950) to (-850,540,190) cm.
- Engineering: (-350,-1550,640) to (500,-70,260) cm.
- Aureate boarding: (-2100,2500,600) to (-850,980,185) cm.

The registered UE latent automation screenshot task requests 1280x720 real D3D11 frames, verifies three physical CRC-valid PNGs with exact dimensions, and independently checks that the saved World hash did not change. A task scheduling log is **not** screenshot or visual QA evidence.

Host: unreal/Tools/run_first_wake_slice_objects_d3d11.py --check returns only when the source Git worktree is clean, both source/runtime heads agree and ONLY the runtime project descriptor has the exact review-plugin delta, private custody verified, genuine saved map and compiled module available, installed UE 5.8.4, PythonAutomationTest registered, **>=6.5 GiB free physical RAM**, **>=14 GiB free disk**, no other UnrealEditor/UnrealEditor-Cmd/LiveCoding process, no saved games, and no existing output or report paths. --capture starts exactly ONE below-normal-priority Unrealeditor-Cmd D3D11 child with a 260-second watchdog and physical RAM protection; it will never kill another user Editor.

Success requires the named registered UE automation controller result Success plus 3 independent native PNG SHA/CRC/dimension checks matching the native receipt, an unchanged World map/config/source commit, Pillow decode and non-black pixel-diversity analysis. Status REAL_NATIVE_D3D11_FRAMES_PIXEL_QA_PASS_ART_APPROVAL_PENDING remains **review-only**: image aesthetics, gameplay E/WASD/PIE, physics, texturing, performance, realistic lighting, animation, and creator visual approval are not inferred from pixel files.

**No claimed results until actual run**. Hosted Linux source CI only checks the source tests, PNG fixture parser, negative controls and registration syntax; not the native Unreal/D3D11 execution. The Windows screenshot source and private .uasset/.umap are not public art approval. Independent screenshot visual comparison and native gameplay tests are next acceptance gates.


## Native D3D11 baseline — actual evidence, not approved visuals

At clean source commit 1e5bb133d1d51260a18bfa9f9bbfe2bb2b13394c, the first disposable GPU runtime mounted **321 private hash-verified asset/receipt/module files** and had only its disposable .uproject modified to enable the PythonAutomationTest plugin. The canonical source worktree passed **313/313** engine-free tests. The first separate UnrealEditor-Cmd process (PID 6228) genuinely ran D3D11, found the registered test, loaded the native 115-actor World and produced **three genuine 1280x720 PNG frames** with native CRC and SHA-256 verification. UE Automation Controller reported Test Completed Result={Success}; exit code 0.

Host receipt status REAL_NATIVE_D3D11_FRAMES_PIXEL_QA_PASS_ART_APPROVAL_PENDING; 3/3 PIL pixel diversity checks PASS, no all-black screenshot. Image names and SHA:
- FirstWakeObjects_Harbor_Establishing_UE584_D3D11_REVIEW.png — 6e6c3b7dff9fcb6d35a0e13d1a72722f660efa3ec3f21802c630e5d4cd58b5d0
- FirstWakeObjects_Engineering_Close_UE584_D3D11_REVIEW.png — fbebe955bcd43d5169e5c86e13c1d0c4e81aa6414f5d78a6925bebcd9f65395f
- FirstWakeObjects_Aureate_Boarding_UE584_D3D11_REVIEW.png — fd55f15c2fb7c1e5e5ca6d2c12922251e62ca59bbec8866c4eb2535ca1a7fd0f

Image quality is not promoted: actual native baseline shows simple blockout building walls/roofs, undeveloped dock materials and water proxy, interim ship art. The initial Engineering camera at (-350,-1550,640) aimed (500,-70,260) is obstructed by a large blank facade in the foreground; the test must not count this as creator-approved framing. First host receipt also inherited a stale native_gpu_render_verified=false field from preflight despite later successful D3D11 status and three validated files. The original receipt remains immutable; new code sets that flag True **only after** matching three native file hashes, UE automation controller success and independent pixel checks.

## V2 framing comparison candidate — separate output, not overwriting baseline

The V2 engineering camera is moved to open-quay side at (470,840,420), aimed at the actual prop cluster centered near (250,270,130) cm, so the EngineeringWorkbench, LiftResonator, PressureRegulator and HarmonicEngineCore can be evaluated without the foreground engineering facade. Harbor and Aureate camera poses are held as controls. Capture v2 uses a distinct new directory D3D11_FirstWakeObjects_20261110_V2 plus distinct host log, report and receipt path. Native map hash, 115 actors, all imported assets and protected Config are unchanged. This framing is a hypothesis until its **own real GPU frames** are produced and inspected. Do not overwrite or remove the first baseline.

The QA frontier after verified native captures remains visual composition, material and PBR improvement, ocean/water physics, and real interactive PIE traversal. D3D11 success does not establish AAA cinematic approval, cast animation, game controls or completed vertical slice.
