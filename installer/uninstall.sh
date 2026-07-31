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

detect_initramfs_tool() {
  if command -v mkinitcpio >/dev/null 2>&1 && [ -f /etc/mkinitcpio.conf ]; then
    echo "mkinitcpio"
    return
  fi
  if command -v dracut >/dev/null 2>&1; then
    echo "dracut"
    return
  fi
  if command -v update-initramfs >/dev/null 2>&1; then
    echo "update-initramfs"
    return
  fi
  echo "unknown"
}

rebuild_hint() {
  case "$1" in
    mkinitcpio) echo "sudo mkinitcpio -P" ;;
    dracut) echo "sudo dracut --regenerate-all --force" ;;
    update-initramfs) echo "sudo update-initramfs -u -k all" ;;
    *) echo "# rebuild your initramfs manually" ;;
  esac
}

INITRAMFS_TOOL="$(detect_initramfs_tool)"

if command -v plymouth-set-default-theme >/dev/null 2>&1; then
  current="$(plymouth-set-default-theme 2>/dev/null || true)"
  if [ "$current" = "curruption" ]; then
    echo "Curruption is still the default theme." >&2
    echo "Select another theme first, for example:" >&2
    echo "  sudo plymouth-set-default-theme spinner" >&2
    echo "  $(rebuild_hint "$INITRAMFS_TOOL")" >&2
    exit 1
  fi
else
  echo "plymouth-set-default-theme not found; cannot verify active theme safely." >&2
  echo "Refusing uninstall to avoid removing the active splash theme." >&2
  exit 1
fi

rm -rf -- "$DEST"
echo "Removed $DEST."
