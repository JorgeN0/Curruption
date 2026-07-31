# Arch Linux Plymouth troubleshooting and validation

This runbook is for Arch-family systems where Curruption installs but does not
render as expected during boot.

## 1) Required packages

Install Plymouth and your initramfs toolchain first.

```bash
sudo pacman -S plymouth mkinitcpio
```

If you use dracut instead of mkinitcpio:

```bash
sudo pacman -S plymouth dracut
```

## 2) Reproduce and classify the failure mode

Run:

```bash
sudo /home/runner/work/Curruption/Curruption/installer/install.sh --diagnose
```

Classification guide:

- **Theme never appears**
  - Common causes: missing `plymouth` initramfs integration, missing `splash`
    kernel arg, or splash explicitly disabled.
- **Plymouth appears then exits early**
  - Common causes: boot completes before animation end, or handoff to prompt.
- **Script/plugin error**
  - Common causes: missing script plugin (`script.so`) or incomplete Plymouth
    runtime install.

## 3) Initramfs integration

### mkinitcpio

Ensure `plymouth` is in `HOOKS` in `/etc/mkinitcpio.conf`, then rebuild:

```bash
sudo mkinitcpio -P
```

### dracut

Ensure plymouth module is present (typically `/usr/lib/dracut/modules.d/50plymouth`)
and rebuild:

```bash
sudo dracut --regenerate-all --force
```

## 4) Bootloader/kernel cmdline requirements

Your kernel cmdline should include:

- `splash` (required for predictable Plymouth startup)

And should **not** include:

- `nosplash`
- `plymouth.enable=0`

Check current cmdline:

```bash
cat /proc/cmdline
```

## 5) Activate theme with initramfs rebuild

Prefer the installer activation path:

```bash
sudo /home/runner/work/Curruption/Curruption/installer/install.sh --set-default
```

It sets the default theme and rebuilds initramfs using the detected tool.

## 6) Compatibility fallback profile (older/stricter builds)

If your Plymouth build is strict about script features:

1. Edit `/home/runner/work/Curruption/Curruption/config/theme.conf`
2. Set:
   - `compat_profile=1`
   - `refresh_rate=50` (or your observed script tick rate)
3. Rebuild and reinstall:

```bash
cd /home/runner/work/Curruption/Curruption
./scripts/build.sh
sudo ./installer/install.sh --set-default
```

Fallback profile disables explicit `SetRefreshRate` requests and avoids passing
font names into `Image.Text`.

## 7) Validation checklist

- [ ] `sudo ./installer/install.sh --diagnose` reports no activation-blocking errors
- [ ] Initramfs rebuild command completed (`mkinitcpio -P` or dracut equivalent)
- [ ] `sudo plymouth-set-default-theme` reports `curruption`
- [ ] Local splash test works:
  ```bash
  sudo plymouthd --debug --debug-file=/tmp/plymouth-debug.log --tty=/dev/tty1
  sudo plymouth show-splash
  sleep 6
  sudo plymouth quit
  ```
- [ ] On reboot, splash shows during early boot instead of fallback/blank
- [ ] If a disk unlock prompt appears, it is readable and the animation yields
- [ ] No script/plugin errors in logs

## 8) Logs for unresolved failures

Collect:

```bash
sudo journalctl -b 0 | grep -Ei 'plymouth|drm|initramfs'
sudo cat /tmp/plymouth-debug.log
```

These are the fastest way to distinguish boot integration issues from theme
script runtime problems.
