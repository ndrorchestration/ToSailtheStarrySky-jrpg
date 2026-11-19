# Private Godot source — nested project handoff

**Authoritative owner:** To Sail the Starry Sky.  
**Read access:** owner-controlled private archive.  
**GitHub host status:** PRIVATE Git repository provisioning and push **NOT COMPLETED**. A public repository folder does not establish source confidentiality.

## Confirmed local candidate

- Native Godot 4.7.2 v0.8.1 candidate was prepared from the owner's existing v0.8.0 native source archive, with a separate reproducible local Git history.
- Local commit: `b0801fde1c32c90014362f55f354e4ec88dceaa0` on `private/celestial-v0.8.1`. **This is a LOCAL commit, not a GitHub-hosted commit.**
- Source-manifest SHA-256: `531f808944373be38532c270ae79257221c7d8ea90ee5ed139b0d19d210be090`.
- Both the actual `.git` source import ZIP and portable `.bundle` were saved under private ChatGPT Library `/To Sail the Starry Sky/Private Godot Source/`.
- Keep the already-published ZIP, tests, screenshots, and QA records immutable; do not infer Windows/GPU or creator-visual acceptance from software native tests.

## Project-root integration layout

```text
ToSailtheStarrySky-jrpg/
  godot/
    celestial_arc/                 # public-safe integration boundary
      README.md
      PRIVATE_SOURCE_HANDOFF.md
      private_native/             # OPTIONAL local PRIVATE checkout; gitignored here
```

To enable GitHub source collaboration while retaining the project relationship, provision a dedicated **PRIVATE** repository owned by `ndrorchestration` (suggested `ToSailtheStarrySky-native-private`). It is a confidential component **of this same game**. Mount it in the reserved path as a local sibling/checkout or, only after review, as a git submodule. All private source workflows and protected CI must run in the PRIVATE repository, not this public parent.

1. Create an uninitialized **private** GitHub repo (repository creation is not supported through the connected GitHub actions).
2. Import the verified local bundle/working copy from the project's private Library folder using its provided `PUSH_TO_PRIVATE_GITHUB.sh`, which refuses any destination not verified PRIVATE by GitHub CLI.
3. Read back the GitHub repo's visibility and compare remote commit/tree to the saved local receipt before calling source synchronization complete.
4. Update [#372](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/372) with **public-safe status only**, and save confidential implementation links, test artifacts and exact records in [the private Notion development plan](https://app.notion.com/p/405f5bad238b810999a1ddf012162e72).
5. Do not establish cross-repository CI, source publication, gitlinks/submodules, story/canon admission or mergers until visibility and access are reviewed.

**Current state:** project nested, source prepared and privately stored; hosted PRIVATE source and actual integrated Godot candidate remain separate gates.
