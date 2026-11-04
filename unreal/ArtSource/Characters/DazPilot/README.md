# Daz Studio Ender reference pilot — review only

**Status (November 3, 2026): source-side plan; Daz native execution not performed.** This branch adds no new Daz or Unreal 3D art and makes no purchases or gameplay changes.

## Objective and continuity

Develop a Daz-only reference study of Ender for *To Sail the Starry Sky*, to address limitations of the independently authored Unreal [draft Ender mesh (#643)](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/643).

Use [Ender's creator-approved visual reference](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/blob/1e54efdc313067c7361a74438fda201112167cca/art-staging/field/ender/approved-appearance-20261008.png) and the [character authority](../../../../docs/CHARACTER_AND_ART_AUTHORITY.md): 22-year-old, slender adult, expressive green eyes, short auburn/dark-copper hair, brass forehead goggles, olive waistcoat, cream embroidered shirt, practical boots/satchel and a full-length staff with centered wrap and brass ferrules. A later group image shows green hair, but **that conflict is not permission to override the approved individual look**. Respect the height ranking Reson > Aepex > Ender > Ionia > Lyra; numeric heights remain provisional.

## What is free and what is not

Daz Studio and [Genesis 9 Starter Essentials (SKU 86958)](https://www.daz3d.com/genesis-9-starter-essentials) are free as an initial software/content offering. Daz's [September 2026 licensing explanation](https://www.daz3d.com/blog/daz-3d-interactive-license) distinguishes **2D renders**, which are generally permitted under the standard terms, from using Daz-store **3D figure, hair, costume, rig, morph or texture data in a game**, which requires applicable product-specific Interactive Licenses. The free starter price grants no automatic 3D game use rights. Keep the Daz study private, and do not export Daz-store 3D data into TSTSS until licensing has been independently checked.

The official [Daz to Unreal Bridge](https://www.daz3d.com/unreal-bridge) advertises Unreal compatibility through **5.2** and cautions that it may not work with the latest Daz Studio. Our active Unreal 5.8.4 is unverified. Do not install or enable the bridge in the live TSTSS game project.

## Safe read-only installation audit

Daz DIM creates XML manifests for products it considers installed. Those files may contain user information. The script here reports **only two known product IDs** and never copies account metadata, file paths or package contents.

From an isolated checkout of this branch run:

```powershell
python unreal/ArtSource/Characters/DazPilot/dim_readiness_audit.py
python -m unittest discover -s unreal/ArtSource/Characters/DazPilot -p "test_dim_readiness_audit.py" -v
```

The default DIM archive is usually `C:\Users\Public\Documents\DAZ 3D\InstallManager\ManifestFiles`. If customized, supply `--manifest-dir "D:\MyDaz\ManifestFiles"`. Optionally pass `--studio-exe "C:\MyDaz\DAZStudio.exe"` for an executable existence check; neither switch launches Daz. For a private receipt use `--receipt "C:\tmp\ENDER_DAZ_NEW_RECEIPT.json"` with an unused path. The file is never overwritten.

A manifest report is **not** proof the character can be loaded or that licenses are held. No Daz installation status can yet be reported from this session: the connected Windows RDC was offline when checked.

## Next reversible Daz-only milestone

1. Allow Daz Install Manager to finish without interference; verify system memory before opening Studio. Do not run Daz Studio beside a memory-intensive Unreal session.
2. Open Daz Studio alone. Confirm Genesis 9 Starter Essentials in `People/Genesis 9`, load a default Genesis 9 figure, and record version, load/render errors and exact starter asset names.
3. In a *new private Daz scene*, adjust Ender's youthful anatomy, green eyes and copper hair against the approved reference. Work within installed free content; no unapproved paid downloads.
4. Capture front, profile, rear, three-quarter, and face/hand/staff close-ups with controlled lighting, plus reduced-size legibility checks. Record a noncanonical private .DUF source and 2D reference PNGs with hashes.
5. Compare with the [existing Ender Unreal lookdev findings](../ENDER_VISUAL_REVIEW.md). Check face and hairstyle likeness, realistic fabric, layers, anatomy, staff hand contact, fit and cinematic rendering.
6. Seek creator visual approval separately. For the game, prefer original, independently authored meshes and rigs informed by permitted 2D references unless each Daz source asset's interactive license is documented.

**Still unverified:** DIM update completion; Daz Studio/native Genesis 9 load; character reference renders; 5.8.4 bridge operation; interactive rights; creator acceptance. **No export to Unreal, canon changes, merge or release.**
