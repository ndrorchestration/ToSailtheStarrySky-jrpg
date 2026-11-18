# Ender — isolated PIE scene preparation (November 18, 2026)

**Status: SOURCE PREPARED ONLY. This new script has NOT been run in Unreal on Neontic. Real PIE locomotion, foot planting and creator approval remain NOT ESTABLISHED.**

## Dependency and verified baseline

This is a follow-on branch from Ender draft PR #853, exact native-verified commit c4576432e3025993190d6a126e7198725368c007. Existing source-native evidence on that commit includes a successful UE5.8.4 Editor build and 38/38 native tests. Its private, Git-excluded Ender Blueprint BP_EnderLocomotionPreview_NONCANONICAL was actually saved on Neontic, with idle/walk/jog clips and PIE review opt-ins; original BP_EnderSlice_PIEReview and existing maps were unchanged.

Separate local native root-pose samples measured 152 animation tracks, idle root travel 0 cm, walk 454.163 cm over 1.5 seconds, and jog 1072.1934 cm over approximately 1.7667 seconds. These are NOT rendered playback results. The root-motion extraction setting was compiled and native automation tested, but not proven in actual locomotion.

## What the new, source-only script is intended to build

Source: unreal/Tools/stage_ender_private_pie_map.py.

The only new output packages allowed are under the Git-excluded review path /Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/:

- BP_EnderPIEGameMode_NONCANONICAL — GameMode Blueprint derived from the existing TSTSSGameMode, with Default Pawn Class pointing at the private, already staged Ender locomotion character.
- FirstWake_PreludeInteraction_V5_VisualReview.umap — a **private level clone with the original basename**, configured to override its GameMode to the new private Blueprint.

The same basename is deliberate. The existing C++ Ender animation preview authorizes that review scene name and the review package namespace, but rejects arbitrary new level names. The script uses the official Unreal 5.8 LevelEditorSubsystem.new_level_from_template route rather than overwriting the original map.

The script neither starts PIE nor writes the original map. It refuses existing private output collisions; checks the source-clean and Git-ignored boundaries, version 5.8.4, exact-current-head 38/38 native automation evidence, original private Blueprint SHA receipt, opt-in property values and clip references; hashes source map, source BP, private BP, project, and protected INI files before and after; and saves only new private GameMode and private level assets. After the save, the script **reopens the private level in the same editor session** and checks that the private map still reports the intended private GameMode class and its Default Pawn Class. The guarded host will not report stage PASS without an explicit true `private_editor_reload_verified` receipt field. This in-session read-back is an additional check, **not** a separate-process persistence or PIE gameplay proof.

**Risk:** because no new native editor run has been performed on this branch, UE Python/asset factory behavior and cloning/override functionality are NOT accepted. The script must run only through a resource watchdog on Neontic (starting RAM at least 6.5 GiB, disk at least 16.5 GiB, runtime floors at least 2.5 GiB and 14.3 GiB). A failed run can leave partial private-only outputs. Do not overwrite or delete them without reviewing the native failure report.

Official API references: [UE5.8 LevelEditorSubsystem](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/LevelEditorSubsystem), [UE5.8 World Settings](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-settings-in-unreal-engine), [UE5.8 GameMode setup](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-a-game-mode-in-unreal-engine).

## Next exact workflow

1. Read current GitHub and Neontic state and import this isolated branch without changing protected main or PR #853. Run engine-free tests first; hosted source-contract tests must pass at the exact updated head.
2. Run Verify-Unreal.ps1 against the **new source commit**, requiring a real Win64 Editor build and the complete 38/38 native automation receipt. The earlier c4576432 receipt must not be represented as exact-head native proof for this script.
3. Run the guarded native asset-preparation script with explicit TSTSS_PRIVATE_ENDER_PIE_MAP=1 only after source and resource gates pass. Verify both private assets, their actual GameMode/DefaultPawn assignments and original source SHA locks in a NEW Unreal process.
4. Open the newly prepared private cloned First Wake V5 level in Unreal Editor. Start standalone PIE from that review level. Verify actual controller possession of the cloned private Ender; capture logs for TSTSS_ENDER_PIE_POSSESSION_SAMPLE, TSTSS_ENDER_PIE_ANIM_TRIPLET_STAGED, TSTSS_ENDER_PIE_ROOT_EXTRACTION_REQUESTED and each ANIM_REQUESTED state. These log lines prove requests, not visually correct motion.
5. Observe real keyboard WASD and held Shift movement and compare capsule displacement against visible mesh-root displacement. Check 260 cm/s walk and 600 cm/s run targets, foot plant, standing idle, transition responsiveness, eyewear/staff attachments, third-person camera and Hilltonia quest/flyer modal restrictions. Capture native Lit screenshots or recording for creator review. The walk clip source speed is about 303 cm/s, so cadence and foot sliding must be separately evaluated even when root translation is suppressed.
6. Exit PIE, preserve exact head and complete log/receipt evidence, hash the original map and original private BP again, and leave all private licensed assets untracked. Do not merge, package or release until acceptance.

## Current blocker

Neontic's Remote Desktop Commander monthly tool usage limit has been reached. The device remains connected, but no additional local Unreal execution or file inspection could be performed through that connection. Do not claim this new branch produced the private map or live animation; it is SOURCE PREPARED. The original PR #853 stays draft/unmerged, and the verified native evidence at c4576432 remains intact.


## Guarded host command prepared (not executed)

The companion source-only host is at unreal/Tools/run_ender_private_pie_map_host.py. Once Neontic is available and the new branch's exact HEAD has passed a real native Win64 Editor build and all 38 native automations, use:

    python unreal\Tools\run_ender_private_pie_map_host.py --stage

The host refuses to run if another Unreal process owns the machine; it does not terminate unrelated applications. It launches a single owned UnrealEditor-Cmd subprocess, protects original .uproject/.ini/V5 .umap/original and cloned Blueprint source files with readonly flags and before/after SHA256 custody checks, checks Git exclusion on both intended private outputs, applies RAM/disk startup and runtime floors, stops ONLY its own child if resources fall below safety limits, and records a unique, nonoverwriting receipt. A successful result is PRIVATE_PIE_MAP_STAGE_PASS_NOT_PLAYBACK_ACCEPTED, which means the new private GameMode and private V5 clone were saved and the originals remained intact. It is not evidence that PIE movement or root-motion extraction looks or behaves correctly.

If either private output already exists or a partial failed receipt exists, do not delete or overwrite it automatically. Inspect the local native error, assess reversible correction, and decide whether a new isolated lane is necessary. Keep all assets private.
