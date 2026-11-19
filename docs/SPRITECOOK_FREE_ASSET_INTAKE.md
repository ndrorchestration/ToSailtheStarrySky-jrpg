# SpriteCook free-credit intake — First Wake
**Status:** Candidate workflow only. No authenticated SpriteCook account, generated art or native Godot acceptance was established on 2026-10-30.

Production task: https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/606
**Ready-to-run Codex instructions:** [SPRITECOOK_FREE_CODEX_RUNBOOK.md](SPRITECOOK_FREE_CODEX_RUNBOOK.md). Use this as the current operational setup source; only the account authorization must be performed by the owner.

## Current free-tier constraints
Official pricing: https://www.spritecook.ai/pricing

- **40 credits every 30 days, $0**, with 8–12 credits per single image depending on model. Read the exact quote and account balance *before* each generation. One active generation at a time.
- Free: standard PNG/ZIP downloads; API/MCP access; public-gallery-visible artwork; commercial use.
- Paid-only: dedicated Godot export, full asset packs, private generations, 2K/4K. Native Godot can import free PNGs without paid export.
- **No account upgrades, paid top-ups, auto-retries, metered browser automation or unofficial payments.** Do not send private creator reference images or unreleased spoilers to a public gallery.
- A generated grid does not necessarily mean the individual sprite tiles were correctly extracted. Inspect all transparent exports before use.
- The **24-credit nine-item Mini Pack** is available with free credits, but generates **pixel art** rather than the project's preferred detailed 2D HUD treatment; do not run it by default. Source: https://www.spritecook.ai/game-asset-pack-generator .
- SpriteCook has a free downloadable **browser-based sheet slicer** at https://www.spritecook.ai/sprite-sheet-slicer , useful for free PNG splitting when an actual sheet is produced.

## Execution order
1. Account owner installs official **SpriteCook Codex plugin** (Codex Plugins -> SpriteCook -> Install -> sign in in browser) per https://www.spritecook.ai/codex . Do not assert completion until tool is connected and balance is readable. The plugin was not available in the current ChatGPT tool connection; linked Windows development PCs were offline.
2. Pin the native Godot candidate SHA separately. Read AGENTS.md, docs/CHARACTER_AND_ART_AUTHORITY.md, docs/VISUAL_BIBLE.md, and issue #606.
3. Ask SpriteCook for live balance and **exact single-image quote**. Submit only an affordable free-credit request, preferably 8-credit model if legible, else at most 12. One image / one variation. Stop rather than upgrading or retrying automatically.
4. **First artifact**: an excellent, readable brass-and-ivory aetheric engineering control glyph for existing First Wake inspection interactions. Attempt multi-glyph sheet only if SpriteCook can give well-separated art without a paid full-pack feature. No new game mechanics, dialogue text, or private art reference.
5. Prompt style: "High-quality hand-painted 2D solarpunk sky-fantasy JRPG instrument asset, real aged brass, ivory enamel, navy shadow, restrained silver-teal illumination; physically plausible use wear, crisp readable silhouette at 960×640 gameplay resolution, isolated transparent background, no letters, characters, neon or watermark." Reuse *public-safe* style asset ID when actually available.
6. Download PNG using free download. Record exact provider asset ID, source URL, prompt, quoted and actually debited credits, license/provenance. Never put an API token or private details in GitHub.
7. Run the safe offline intake script (below) and stage on isolated branch; do not replace approved art. Attach genuine Godot screenshot and inspect layout/overlap at native game scale. Only with review proceed to next asset: dialogue/UI accents, inventory/repair props, then Five Lights icons when their actual UI consumer exists.

## Staging downloaded PNGs (after a real generation)
The local-only script uses Python standard library and **does not perform any API call or spend credits**.

```sh
python scripts/spritecook_intake.py \
  --png /path/to/actual-spritecook-download.png \
  --slug first-wake-engine-glyph \
  --asset-id ACTUAL_PROVIDER_ASSET_ID \
  --source-url https://app.spritecook.ai/assets/ACTUAL_PROVIDER_ASSET_ID \
  --prompt-file /path/to/public-safe-prompt.txt \
  --credit-cost 8 --balance-before 40 --balance-after 32
```

**Numbers above are placeholders; use exact observed values.** If credit balance is not available, omit cost and both balances; the resulting manifest records that debit is unverified. Default output is assets/spritecook-candidates/ with a PNG and matching provenance JSON. It never overwrites an existing candidate.

All outputs are **CANDIDATE_NOT_APPROVED** until creator signoff and actual native Godot rendering review. Do not merge this documentation as proof that art was generated, tested inside the game, accepted or released.