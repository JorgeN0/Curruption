#!/usr/bin/env sh
# Validate the asset tree and compile theme/modules/ into the installable
# theme. Asset regeneration is deliberately opt-in: the approved concept-06
# artwork and the scream frames are authored, and process_assets.py rewrites
# the procedural layers in place.
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

case "${1-}" in
  "")
    ;;
  --assets)
    echo "Regenerating procedural assets..."
    python3 "$ROOT/scripts/process_assets.py"
    ;;
  *)
    echo "usage: $0 [--assets]" >&2
    exit 2
    ;;
esac

python3 "$ROOT/scripts/validate_assets.py"
python3 "$ROOT/scripts/build.py"
