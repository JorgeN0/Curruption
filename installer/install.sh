#!/usr/bin/env sh
# Install Curruption into the system Plymouth theme directory.
#
# The active theme is never changed unless --set-default is passed explicitly.
set -eu

usage() {
  cat >&2 <<'EOF'
usage: install.sh [--set-default] [--diagnose]

  --set-default  set curruption as default theme and rebuild initramfs
  --diagnose     print Arch/Linux Plymouth diagnostics and failure classification
EOF
  exit 2
}

SET_DEFAULT=0
DIAGNOSE=0
for arg in "$@"; do
  case "$arg" in
    --set-default) SET_DEFAULT=1 ;;
    --diagnose) DIAGNOSE=1 ;;
    *) usage ;;
  esac
done

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
DEST="/usr/share/plymouth/themes/curruption"

WARNINGS=0
ERRORS=0
INITRAMFS_TOOL="unknown"
IS_ARCH=0
HAS_PLYMOUTH=0
HAS_SCRIPT_PLUGIN=0
HAS_INITRAMFS_HOOK=0
CMDLINE_HAS_SPLASH=0
CMDLINE_FORCES_OFF=0

warn() {
  WARNINGS=$((WARNINGS + 1))
  echo "WARN: $*" >&2
}

fail() {
  ERRORS=$((ERRORS + 1))
  echo "ERROR: $*" >&2
}

detect_arch() {
  if [ ! -f /etc/os-release ]; then
    return
  fi
  os_id="$(sed -n 's/^ID=//p' /etc/os-release | head -n 1 | tr -d '"')"
  os_like="$(sed -n 's/^ID_LIKE=//p' /etc/os-release | head -n 1 | tr -d '"')"
  case "$os_id $os_like" in
    *arch*|*manjaro*|*endeavouros*|*garuda*|*artix*) IS_ARCH=1 ;;
  esac
}

detect_initramfs_tool() {
  if command -v mkinitcpio >/dev/null 2>&1 && [ -f /etc/mkinitcpio.conf ]; then
    INITRAMFS_TOOL="mkinitcpio"
    return
  fi
  if command -v dracut >/dev/null 2>&1; then
    INITRAMFS_TOOL="dracut"
    return
  fi
  if command -v update-initramfs >/dev/null 2>&1; then
    INITRAMFS_TOOL="update-initramfs"
    return
  fi
}

check_plymouth_runtime() {
  if command -v plymouthd >/dev/null 2>&1 && command -v plymouth >/dev/null 2>&1; then
    HAS_PLYMOUTH=1
  else
    fail "plymouth runtime is missing. Install plymouth before installing this theme."
  fi

  if ! command -v plymouth-set-default-theme >/dev/null 2>&1; then
    warn "plymouth-set-default-theme not found. Theme activation must be done manually."
  fi

  for path in \
    /usr/lib/plymouth/script.so \
    /usr/lib64/plymouth/script.so \
    /lib/plymouth/script.so \
    /usr/lib/plymouth/plugins/script.so \
    /usr/lib64/plymouth/plugins/script.so
  do
    if [ -f "$path" ]; then
      HAS_SCRIPT_PLUGIN=1
      break
    fi
  done
  if [ "$HAS_SCRIPT_PLUGIN" -eq 0 ]; then
    fail "Plymouth script plugin (script.so) not found; script themes cannot load."
  fi
}

check_initramfs_integration() {
  case "$INITRAMFS_TOOL" in
    mkinitcpio)
      hooks_line="$(grep -E '^[[:space:]]*HOOKS=' /etc/mkinitcpio.conf | tail -n 1 || true)"
      case " $hooks_line " in
        *" plymouth "*)
        HAS_INITRAMFS_HOOK=1
          ;;
        *)
          if [ "$IS_ARCH" -eq 1 ]; then
            fail "mkinitcpio is active but HOOKS in /etc/mkinitcpio.conf does not include plymouth."
          else
            warn "mkinitcpio HOOKS does not include plymouth."
          fi
          ;;
      esac
      ;;
    dracut)
      if [ -d /usr/lib/dracut/modules.d/50plymouth ] ||
         [ -d /usr/lib/dracut/modules.d/90plymouth ]; then
        HAS_INITRAMFS_HOOK=1
      else
        if [ "$IS_ARCH" -eq 1 ]; then
          fail "dracut is active but plymouth module is missing."
        else
          warn "dracut plymouth module was not found."
        fi
      fi
      ;;
    update-initramfs)
      HAS_INITRAMFS_HOOK=1
      ;;
    *)
      warn "No supported initramfs tool detected (mkinitcpio/dracut/update-initramfs)."
      ;;
  esac
}

check_cmdline() {
  CMDLINE="$(cat /proc/cmdline 2>/dev/null || true)"
  case "$CMDLINE" in
    *"plymouth.enable=0"*|*"nosplash"*)
      CMDLINE_FORCES_OFF=1
      ;;
  esac
  case "$CMDLINE" in
    *" splash "*|splash\ *|*" splash"|splash)
      CMDLINE_HAS_SPLASH=1
      ;;
  esac

  if [ "$CMDLINE_FORCES_OFF" -eq 1 ]; then
    if [ "$IS_ARCH" -eq 1 ]; then
      fail "kernel cmdline disables splash (nosplash or plymouth.enable=0)."
    else
      warn "kernel cmdline disables splash (nosplash or plymouth.enable=0)."
    fi
  fi
  if [ "$CMDLINE_HAS_SPLASH" -eq 0 ]; then
    warn "kernel cmdline is missing splash; Plymouth may not appear during boot."
  fi
}

run_diagnostics() {
  echo "== Curruption Plymouth diagnostics =="
  echo "Detected initramfs tool: $INITRAMFS_TOOL"
  if [ "$IS_ARCH" -eq 1 ]; then
    echo "Detected distro family: Arch"
  else
    echo "Detected distro family: non-Arch"
  fi
  echo "Kernel cmdline: $(cat /proc/cmdline 2>/dev/null || echo unavailable)"

  echo
  echo "Failure classification:"
  if [ "$HAS_PLYMOUTH" -eq 0 ] || [ "$HAS_SCRIPT_PLUGIN" -eq 0 ]; then
    echo "- likely script/plugin failure (missing plymouth runtime or script plugin)."
  fi
  if [ "$HAS_INITRAMFS_HOOK" -eq 0 ] || [ "$CMDLINE_FORCES_OFF" -eq 1 ] || [ "$CMDLINE_HAS_SPLASH" -eq 0 ]; then
    echo "- likely \"theme never appears\" (initramfs integration or cmdline issue)."
  fi
  if [ "$ERRORS" -eq 0 ] && [ "$HAS_PLYMOUTH" -eq 1 ] && [ "$HAS_SCRIPT_PLUGIN" -eq 1 ] &&
     [ "$HAS_INITRAMFS_HOOK" -eq 1 ] && [ "$CMDLINE_HAS_SPLASH" -eq 1 ] &&
     [ "$CMDLINE_FORCES_OFF" -eq 0 ]; then
    echo "- runtime path looks valid; if splash appears then exits early, inspect boot logs."
  fi

  echo
  echo "Collect logs:"
  echo "  sudo journalctl -b 0 | grep -Ei 'plymouth|drm|initramfs'"
  echo "  sudo plymouthd --debug --debug-file=/tmp/plymouth-debug.log --tty=/dev/tty1"
  echo "  sudo plymouth show-splash; sleep 6; sudo plymouth quit"
  echo "  sudo cat /tmp/plymouth-debug.log"
}

rebuild_initramfs() {
  case "$INITRAMFS_TOOL" in
    mkinitcpio) mkinitcpio -P ;;
    dracut) dracut --regenerate-all --force ;;
    update-initramfs) update-initramfs -u -k all ;;
    *)
      return 1
      ;;
  esac
}

activation_hint() {
  case "$INITRAMFS_TOOL" in
    mkinitcpio)
      echo "sudo plymouth-set-default-theme curruption && sudo mkinitcpio -P"
      ;;
    dracut)
      echo "sudo plymouth-set-default-theme curruption && sudo dracut --regenerate-all --force"
      ;;
    update-initramfs)
      echo "sudo plymouth-set-default-theme curruption && sudo update-initramfs -u -k all"
      ;;
    *)
      echo "sudo plymouth-set-default-theme curruption  # then rebuild your initramfs manually"
      ;;
  esac
}

detect_arch
detect_initramfs_tool
check_plymouth_runtime
check_initramfs_integration
check_cmdline

if [ "$DIAGNOSE" -eq 1 ]; then
  run_diagnostics
  if [ "$SET_DEFAULT" -eq 0 ]; then
    exit 0
  fi
fi

if [ "$SET_DEFAULT" -eq 1 ] && [ "$ERRORS" -ne 0 ]; then
  echo "Refusing to activate while preflight errors are present. Run with --diagnose and fix the errors first." >&2
  exit 1
fi

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
  plymouth-set-default-theme curruption
  if rebuild_initramfs; then
    echo "Curruption is now the default theme and initramfs has been rebuilt via $INITRAMFS_TOOL."
  else
    echo "Curruption was set as default, but initramfs rebuild is manual on this system." >&2
    echo "Run: $(activation_hint)" >&2
    exit 1
  fi
else
  echo "Preflight summary: $ERRORS errors, $WARNINGS warnings."
  echo "Enable with: $(activation_hint)"
  if [ "$ERRORS" -ne 0 ]; then
    echo "Resolve preflight errors before activation (hint: sudo ./installer/install.sh --diagnose)." >&2
  fi
fi
