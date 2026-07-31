#!/usr/bin/env sh
# Remove the installed theme. The active theme is never changed here: leaving
# a dangling default would leave the machine without a splash, so the user is
# told to switch first.
set -eu

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

DEST="/usr/share/plymouth/themes/curruption"
if [ ! -d "$DEST" ]; then
  echo "Curruption is not installed."
  exit 0
fi

if command -v plymouth-set-default-theme >/dev/null 2>&1; then
  current="$(plymouth-set-default-theme 2>/dev/null || true)"
  if [ "$current" = "curruption" ]; then
    echo "Curruption is still the default theme." >&2
    echo "Select another theme first, for example:" >&2
    echo "  sudo plymouth-set-default-theme -R spinner" >&2
    exit 1
  fi
fi

rm -rf -- "$DEST"
echo "Removed $DEST."
