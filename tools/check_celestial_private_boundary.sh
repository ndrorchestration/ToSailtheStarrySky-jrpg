#!/usr/bin/env bash
set -euo pipefail

# Public GitHub trees cannot contain the owner-private native checkout.
# This is only a scoped path gate. Review and repository access control remain mandatory.
forbidden="$(git ls-files --   'godot/celestial_arc/private_native/**'   'godot/celestial_arc/private_source/**'   'godot/celestial_arc/private_artifacts/**'   'godot/celestial_arc/private_evidence/**'   'godot/celestial_arc/.local_private/**'   'godot/celestial_arc/secrets/**'   'godot/celestial_arc/keys/**'   'godot/celestial_arc/*.bundle'   'godot/celestial_arc/*.age'   'godot/celestial_arc/*.enc'   'godot/celestial_arc/*_PRIVATE*.zip' )"
if [[ -n "$forbidden" ]]; then
  echo "BLOCK: private celestial source/evidence path is tracked in a PUBLIC Git tree:" >&2
  printf '%s\n' "$forbidden" >&2
  exit 1
fi

echo "PASS: no tracked reserved private-source paths in public celestial_arc directory"
