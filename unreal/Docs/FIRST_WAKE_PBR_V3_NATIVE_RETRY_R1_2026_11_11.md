# First Wake V3 native material stage R1 — isolated retry

This **fresh, independent local worktree** exists solely because the first real UE5.8.4 material-stage run at #805 produced 30 local Texture2D packages, then failed its first material UV connection. Original worktree and failed native evidence must remain untouched. Do not reuse or overwrite those 30 assets, earlier local host HOLD receipt or logs.

- Source parent PR #805 commit: adf13287e69e0e25396a904a289eadda91b372e5.
- Isolated retry branch: review/ue58-vslice-lookdev-native-r1-20261111; root C:\TSTSS_V3_Retry_20261111\TSTSS_VSliceLookdev_20261111. Its last directory has the required strict ROOT_NAME for source-locking.
- Only code deltas for this retry: the branch name constants in private native-intake and guarded native-stage host. All game C++, original Config, source 115-actor map and patched source PBR material generator/texture byte hashes exactly match #805.
- Original native first-run failure reason: Unreal TextureSample UV input is named UVs, not Coordinates; the #805 source correction has regression protection. First-run 30 imported private packages remain in the other worktree.
- Binary custody: independently SHA-check and exclusive-copy precisely 321 private source-level imported Unreal mesh/module/map/receipt files. Never copy the failed V3 first-run output into R1.
- Real acceptance: native UE5.8.4 NullRHI only if >/=5.0 GiB actual free RAM, >/=14.0 GiB free disk, zero competing Editor/LiveCoding, clean source HEAD, no SaveGames, no preexisting result/derived map. A zero Unreal process exit is not success; require exact new saved map SHA and native first receipt, then an independent second Editor readback verifying 200 actors/30 Texture2Ds/10 UE material assets, collision/visual/7 story marker gate and original map/config unchanged.
- The original source looks are still review quality. Neither native map inventories nor D3D pixel diversity are equivalent to cinematic art approval or real PIE gameplay. Preserve Starbourne locked and Lyra post-splashdown only.

No private UE binary packages, owner-controlled SaveGames, earlier GPU captures or protected source maps are to be committed or deleted.
