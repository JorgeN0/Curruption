# Curruption

Curruption is an original, silent Plymouth boot theme: an intrusion in
progress, seen through the attacker's own interface. Something traces the
machine, sweeps for a subject, reconstructs a skull out of a damaged signal,
confirms it, gets noticed, and loses the link — and then the eye that was
watching the whole time resolves out of the static and looks back.

10 seconds, 30 fps, ending on total black.

No audio, no dialogue, no logos, no branding, no copyrighted interface
reproductions.

## Preview

Open `preview/index.html` in a browser, or serve the repository root:

```bash
python3 -m http.server 8080
```

Then visit `http://localhost:8080/preview/`. Space plays and pauses, the arrow
keys step one frame, `r` replays, and the slider scrubs. The linked asset
library page shows every production layer.

The preview mirrors the Plymouth timing and geometry but composites a canvas
rather than sprites; it is a development approximation, not the source of
runtime truth.

## Build and install

Linux with Plymouth is required for the real theme.

```bash
./scripts/build.sh
sudo ./installer/install.sh
sudo ./installer/install.sh --set-default
```

`install.sh` never changes the active theme unless you pass `--set-default`,
because switching themes rebuilds the initramfs.

On Arch-family systems, run diagnostics before activation:

```bash
sudo ./installer/install.sh --diagnose
```

This checks Plymouth runtime/plugin availability, initramfs integration
(`mkinitcpio`/`dracut`), and kernel cmdline splash flags, then prints likely
failure mode classification and log collection commands.

Test without rebooting:

```bash
sudo plymouthd --debug --tty=/dev/tty1
sudo plymouth show-splash
sleep 6
sudo plymouth quit
```

Remove it with `sudo ./installer/uninstall.sh`, after selecting another theme.

## Configuration

Everything user-facing lives in `config/theme.conf`, which is compiled into
`theme/modules/00-config.script` by `scripts/build.py`. Run `./scripts/build.sh`
after a change, then reinstall. The generated `theme/curruption.script` is
committed so the theme can also be installed without a Python toolchain.

| Setting | Default | Effect |
|---|---:|---|
| `animation_duration` | 10.0 | wall-clock point at which everything blanks |
| `animation_speed` | 1.0 | stretches or compresses the whole timeline (0.55 gives a ~5.5 s cut) |
| `refresh_rate` | 30 | ticks per second the script plugin is driven at |
| `compat_profile` | 0 | 1 enables a stricter fallback path (no `SetRefreshRate`, no font arg in `Image.Text`; pair with `refresh_rate=50`) |
| `gore_enabled` | 1 | 0 falls back to the clean skull layers |
| `jaw_open_distance` | 42 | how far into the authored scream frames the jaw travels |
| `blood_overlay_opacity` | 1.0 | crack/blood tracery overlay only; the approved blood is baked into the artwork |
| `dangling_eye_enabled` | 1 | independent eyeball sway |
| `dangling_eye_sway` | 0.035 | peak swing in radians, about two degrees |
| `dangling_eye_speed` | 0.8 | 1.0 is roughly a 1.6 second period |
| `big_brother_eye_enabled` | 1 | the closing watcher; 0 ends on black instead |
| `eye_duration` | 0.30 | red ignition length, hard on and hard off, empty socket only |
| `smoke_density` | 0.18 | hard-capped at 0.24 by the runtime |
| `glitch_intensity` | 0.72 | scales every corruption layer |
| `film_grain` | 0.12 | scanlines and constant grain; 0 skips the scanline layer |
| `vignette_opacity` | 0.45 | 0 skips the only screen-sized image in the theme |
| `hud_enabled` | 1 | all tracking furniture and state text |
| `random_seed` | 31991 | every glitch derives from this, so corruption is reproducible |

## Layout

- `assets/` — original artwork and procedural textures
- `config/` — user-facing settings
- `theme/modules/` — independent Plymouth animation systems
- `scripts/` — asset and theme build tools
- `preview/` — browser-based timing preview and asset library
- `installer/` — Linux installer and uninstaller
- `docs/` — design, timing, and asset notes

## Runtime systems

`scripts/build.py` concatenates `theme/modules/*.script` in filename order into
the installable theme. Each module owns one system and nothing else:

| Module | Responsibility |
|---|---|
| `00-config.script` | generated from `config/theme.conf` |
| `10-core.script` | clock, geometry, layout anchors, timeline constants, helpers |
| `20-smoke.script` | background atmosphere |
| `30-skull.script` | gore skull and the authored jaw |
| `35-dangling-eye.script` | eyeball and optic nerve, independent of the jaw |
| `40-eyes.script` | red ignition, empty socket only |
| `45-bigbrother.script` | the closing watcher |
| `50-hud.script` | tracking furniture and state text |
| `60-glitch.script` | corruption, grain, terminal mask |
| `70-timing.script` | orchestration, story labels, Plymouth lifecycle |

Every image is decoded and scaled once at load time. The refresh callback only
moves sprites, sets opacity, and swaps between images that already exist.

## Validation

```bash
python3 scripts/validate_assets.py
python3 scripts/build.py
node --check preview/preview.js
node --check preview/assets.js
```

`validate_assets.py` checks the required inventory, resolves every asset path
the modules load, confirms the approved concept is unmodified, and re-checks
the gore-skull layer geometry against all three scream frames.

See [docs/DESIGN.md](docs/DESIGN.md), [docs/TIMING.md](docs/TIMING.md) and
[docs/ASSET_CATALOG.md](docs/ASSET_CATALOG.md). For Arch-specific setup and
validation, see [docs/ARCH_PLYMOUTH_TROUBLESHOOTING.md](docs/ARCH_PLYMOUTH_TROUBLESHOOTING.md).
