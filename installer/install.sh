#!/usr/bin/env sh
# Install Curruption into the system Plymouth theme directory.
#
# The active theme is never changed unless --set-default is passed explicitly,
# because switching themes rebuilds the initramfs and is the user's call.
set -eu

usage() {
  echo "usage: $0 [--set-default]" >&2
  exit 2
}

SET_DEFAULT=0
case "${1-}" in
  "") ;;
  --set-default) SET_DEFAULT=1 ;;
  *) usage ;;
esac
[ "$#" -le 1 ] || usage

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
DEST="/usr/share/plymouth/themes/curruption"

python3 "$ROOT/scripts/build.py"
python3 "$ROOT/scripts/validate_assets.py"

if [ ! -f "$ROOT/theme/curruption.script" ]; then
  echo "theme/curruption.script was not generated; aborting." >&2
  exit 1
fi

install -d "$DEST" "$DEST/skull" "$DEST/eye" "$DEST/effects" "$DEST/hud"
install -m 0644 "$ROOT/theme/curruption.plymouth" "$DEST/curruption.plymouth"
install -m 0644 "$ROOT/theme/curruption.script" "$DEST/curruption.script"

for group in skull eye effects hud; do
  count=$(find "$ROOT/assets/$group" -maxdepth 1 -type f -name '*.png' | wc -l)
  if [ "$count" -eq 0 ]; then
    echo "No PNGs found in assets/$group; aborting." >&2
    exit 1
  fi
  find "$ROOT/assets/$group" -maxdepth 1 -type f -name '*.png' \
    -exec install -m 0644 '{}' "$DEST/$group/" ';'
done

echo "Installed Curruption to $DEST"

if [ "$SET_DEFAULT" -eq 1 ]; then
  if ! command -v plymouth-set-default-theme >/dev/null 2>&1; then
    echo "plymouth-set-default-theme not found; set the theme manually." >&2
    exit 1
  fi
  plymouth-set-default-theme -R curruption
  echo "Curruption is now the default theme and the initramfs has been rebuilt."
else
  echo "Enable with: sudo plymouth-set-default-theme -R curruption"
fi
