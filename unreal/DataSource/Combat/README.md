# Combat data sources (templates only)

Header-only CSV templates matching `FTSTSSActionDefRow` and `FTSTSSCharacterBaselineRow`
(`Source/ToSailTheStarrySky/Public/TSTSSCombatData.h`). They deliberately contain **no rows**:
canonical spells, techniques, stats and equipment must come from creator-approved sources.

- Enum columns take the enumerator name (`Spell`, `Enemy`, `Water`, `CreatorApproved`, ...).
- `Learners` uses UE array syntax: `("Ender","Lyra")`.
- Import via Content Browser > Import as DataTable with the matching row struct.
- Mark rows `Placeholder` or `Proposed` until the creator approves them. Shipping validation
  (`bShipping = true`) rejects every row that is not `CreatorApproved`.
