# Daily development log — review-only implementation

The proposed workflow is not active until reviewed and merged to the repository default branch. It does not authorize a merge, release, canon change, asset promotion, or bypass of an existing gate.

## How it works

At 11:00 UTC, safely after New York midnight year-round, GitHub Actions builds an evidence-index report for the previous full America/New_York calendar day. It records default-branch commits, recently updated PRs and issues, fix-labeled changes, experiments identified by titles, and GitHub Actions results. The record is stored at docs/devlog/YYYY-MM-DD.md on branch automation/daily-devlog, **never on protected main**. Re-running an unchanged report is a no-op.

Inspect generated records using the branch selector in GitHub (automation/daily-devlog). The source workflow is .github/workflows/daily-devlog.yml; pure JavaScript logic and tests live in tools/devlog. Only standard Node and GitHub Actions permissions are required.

Limitations: first 100 records per API category; this repository only; default-branch commits only; updated PRs are not necessarily completed work; CI is not Unreal native build, PIE, GPU, creator approval, or playable-slice evidence. GitHub-only logs cannot capture unpushed workstation activity or Notion-only work. No private sources should be published here.

The dedicated Notion [To Sail the Starry Sky — Game Development Log](https://app.notion.com/p/bec804bcc2874f4f961d6bbe1cfba3e7) is the game-specific human-facing journal. The [ecosystem overview](https://app.notion.com/p/b43e97712d2642c988704fdcf113a45f) is only an index/projection, not a second independent source of truth. The Notion log is not automatically populated by this repository-local workflow. Private gameplay spoilers and local native receipts are not imported into this public repository.

## AI From Zero content idea funnel

Each generated daily GitHub report now includes **AFZ story lead suggestions — review only** when a failed CI check, research/prototype PR, draft PR, or successful CI run provides a bounded prompt. These are rule-based suggestions (not a claim that a feature works or the AI has watched footage).

- The project-specific Notion game log exposes **AFZ Content Potential**, **AFZ Content Hook**, and a relation to **AFZ Story Leads**.
- The shared [AI From Zero — Dream Games Story & Episode Idea Pipeline](https://app.notion.com/p/3bcc35ed8f72418f9ed258368d624b70) captures ideas for separate **future** game-build diary playlists and general educational episodes.
- Review/transfer of suggestions to Notion is **manual** at present. Neither the scheduled reporter nor the draft PR creates a YouTube playlist, assigns an AFZ episode number, films footage, publishes content, or changes the game.
- Public-safe footage and exact source/native verification are required before recording any claim about a working or completed feature.

## Verification and activation

1. Run the unit tests in the draft PR and inspect the exact-head CI result.
2. Review the workflow and authorize a merge through existing repository protections.
3. After merge, inspect the first scheduled or manual workflow run, then its output branch and date-stamped record.
4. If the GitHub token lacks branch-creation permission or CI fails, retain the failure and repair on a review branch. Never bypass protected main or claim automation is operating before an actual hosted run.
