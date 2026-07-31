# Claude implementation brief: Curruption Plymouth animation

## Mission

Finish the existing **Curruption** project as a production-quality Plymouth
boot animation for Linux.

Do not rebuild the repository from scratch. The project already contains:

- a working modular Plymouth script scaffold;
- deterministic asset-generation and validation scripts;
- 55 validated production PNG assets;
- a browser timing preview;
- installation scripts;
- design and timing documentation;
- an approved final gore-skull concept.

The required outcome is a silent 4–6 second boot sequence that feels like a
corrupted surveillance transmission. The system detects an unknown subject,
reconstructs it, realizes it is being observed, and loses the signal.

## Approved visual direction

Use this image as the current approved hyper-real skull appearance:

```text
preview/concepts/skull-hyperreal-approved.png
```

Concept 06 is approved because it has:

- blood concentrated around the face and upper outer cranium;
- a relatively clean central forehead;
- no flesh hanging beneath the cheekbones;
- one freshly damaged viewer-right eye socket;
- one dangling bloodshot eyeball on a loose optic nerve;
- a downward-looking iris and pupil;
- a completely empty viewer-left socket;
- a clean, centered silhouette on black.

The approved skull also has three aligned scream-reference PNGs:

```text
assets/skull/scream-00.png  # closed/tense
assets/skull/scream-01.png  # half-open transition
assets/skull/scream-02.png  # fully open scream
```

Use them as pose and timing references. The runtime should still prefer its
independently animated jaw tiles so the scream remains smooth and lightweight.

Do not use concepts 01–05 as production art. They remain comparison history.

## Important design update

The original v0.1 specification said “no gore.” The user has deliberately
changed that direction. Concept 06 is now the authoritative skull design.

The animation must still avoid gratuitous splatter, exposed brain matter,
organs, or large flesh masses. The approved gore should feel like a dark
forensic surveillance image, not an action-horror scene.

## Existing project structure

```text
assets/
  source/             generated source masters
  skull/              current clean skull layers
  eye/                Big Brother surveillance-eye family
  effects/            noise, smoke, grain, signal corruption
  hud/                tracking and telemetry elements
config/
  theme.conf          user-facing animation configuration
docs/
installer/
preview/
scripts/
  process_assets.py   deterministic asset builder
  validate_assets.py  required-asset validation
  build.py            Plymouth module compiler
theme/
  modules/            independent Plymouth systems
  curruption.script   generated runtime
  curruption.plymouth theme descriptor
```

Read these files before editing:

```text
README.md
docs/DESIGN.md
docs/TIMING.md
docs/ASSET_CATALOG.md
config/theme.conf
scripts/process_assets.py
scripts/validate_assets.py
scripts/build.py
theme/modules/*.script
preview/preview.js
installer/install.sh
```

## Productionize concept 06

Concept 06 is currently a flattened preview on black. Convert it into reusable
Plymouth-ready PNG layers without damaging the approved appearance.

The approved flattened image has already been promoted into the runtime as:

```text
assets/source/skull-gore-approved.png
assets/skull/skull-gore-approved.png
```

`theme/modules/30-skull.script` now loads it instead of the clean skull. The
legacy jaw sprite is temporarily hidden because compositing it over the
flattened master would duplicate anatomy. Replace this temporary flattened
runtime state with the independent layers below.

Create at minimum:

```text
assets/skull-gore/skull-gore-master.png
assets/skull-gore/head.png
assets/skull-gore/jaw.png
assets/skull-gore/teeth.png
assets/skull-gore/socket-trauma.png
assets/skull-gore/eyeball.png
assets/skull-gore/optic-nerve.png
assets/skull-gore/blood-overlay.png
assets/skull-gore/cracks-blood.png
```

Requirements:

- RGBA PNG output;
- transparent background;
- aligned canvases with identical logical origin;
- no visible matte or black fringe;
- the jaw must animate independently;
- the eyeball and optic nerve must animate independently;
- the viewer-left socket must remain empty;
- the eyeball’s downward gaze must be preserved;
- the clean side silhouette beneath both cheekbones must be preserved;
- use sensible Plymouth dimensions rather than the full concept resolution;
- keep the approved flattened concept as an immutable source reference.

If automatic extraction cannot produce clean anatomical edges, prefer careful
manual masking or a small number of convincing layers over many poor layers.

Add the new required files to `scripts/validate_assets.py` and installation
copy logic. Update `docs/ASSET_CATALOG.md` and the browser asset catalog.

## Existing Big Brother eye assets

The opening surveillance motif is already available under:

```text
assets/eye/
```

States include:

```text
eye-surveillance.png
eye-high-contrast.png
eye-iris-mask.png
eye-pupil-mask.png
eye-target-red.png
eye-tracked.png
eye-corrupted.png
eye-signal-lost.png
```

Use the eye briefly near the beginning. It should establish that the system is
watching before the skull reconstruction begins. Do not display it as a logo or
full-screen static splash.

## Required layer order

Use the following conceptual render order:

1. pure black background;
2. low-opacity smoke;
3. Big Brother surveillance eye;
4. gore-skull head;
5. gore-skull jaw;
6. socket trauma;
7. optic nerve;
8. dangling eyeball;
9. optional red eye ignition/glow;
10. surveillance HUD;
11. glitches and corruption;
12. film grain and scanlines;
13. terminal signal-loss mask.

The dangling eye must remain anatomically attached to the viewer-right socket.
When moving it, animate the eyeball and nerve as a coordinated system.

## Canonical timeline

Target duration: **5.2 seconds**  
Target cadence: **30 FPS**

| Time | Event |
|---:|---|
| 0.00–0.30 | complete black |
| 0.30–0.82 | tiny packet noise and acquisition marks |
| 0.42–1.05 | Big Brother eye intercepted |
| 0.72–1.12 | eye feed tears and disappears |
| 1.10–1.85 | gore skull reconstructs from unstable fragments |
| 1.32–2.18 | `VISUAL LINK ESTABLISHED` appears briefly |
| 2.35–3.10 | tracking brackets tighten; `TARGET LOCKED` |
| 2.75–3.45 | dangling eyeball begins a subtle heavy sway |
| 3.08–3.24 | jaw crosses the half-open scream reference |
| 3.24–3.68 | jaw reaches the fully open scream reference |
| 3.55–3.85 | red eye ignition/glow, hard on/off, no fade |
| 3.88–4.30 | signal corruption accelerates |
| 4.28–4.68 | `SIGNAL LOST` |
| 4.48–4.94 | data-mosh, packet loss, static and disintegration |
| 4.94–5.20 | total black for display-manager handoff |

All textual states must be small, white, monospace, and short-lived.

## Motion direction

### Skull

- centered and front-facing;
- slow reconstruction and minimal drift;
- brief deterministic horizontal offsets during corruption;
- no constant floating or smooth “screensaver” motion.

### Jaw

- opens independently;
- deliberate and heavy;
- maximum opening should remain anatomically plausible;
- return or collapse can be interrupted by signal loss.

### Dangling eyeball

- begins almost still;
- uses a small, slow pendulum-like sway;
- slight delayed movement relative to the skull suggests weight;
- never spins;
- iris remains visibly aimed downward;
- motion amplitude must remain subtle enough for Plymouth.

Plymouth scripting has limited physics support. A deterministic sine-based
offset is acceptable. Do not build a physics engine.

### Smoke

- opacity below 25%;
- extremely slow;
- background only;
- never obscures the skull.

### Glitches

Use the existing assets in `assets/effects/`:

- horizontal tearing;
- image offsets;
- packet loss;
- red/white channel split;
- compression blocks;
- static bursts;
- coarse and fine noise;
- data-mosh;
- signal-drop and signal-loss masks.

Glitches should be brief and deterministic. Avoid allocating images during
every refresh callback.

## Color and typography

Base palette:

```text
#000000 black
#1A1A1A dark gray
#FFFFFF white/bone
#FF0033 red accent
dark burgundy for approved blood
```

Typography:

- monospace only;
- small white labels;
- no large title;
- no logo;
- no branding;
- no copyright text;
- no sound or dialogue.

## Runtime architecture

Keep the independent system structure. Extend it rather than replacing it:

```text
00-config.script
10-core.script
20-smoke.script
30-skull.script
40-eyes.script
50-hud.script
60-glitch.script
70-timing.script
```

Adding a dedicated module is encouraged:

```text
35-dangling-eye.script
```

Responsibilities should remain separate:

- configuration;
- timing/state;
- smoke;
- Big Brother feed;
- skull/jaw;
- dangling eye/optic nerve;
- red ignition;
- HUD;
- corruption;
- final shutdown.

`scripts/build.py` must continue compiling ordered modules into
`theme/curruption.script`.

## Configuration

Preserve existing values and add configurable gore-eye controls:

```text
gore_enabled=1
dangling_eye_enabled=1
dangling_eye_sway=0.035
dangling_eye_speed=0.8
jaw_open_distance=42
blood_overlay_opacity=1.0
big_brother_eye_enabled=1
```

Every new setting must compile into `00-config.script`.

## Browser preview

Update `preview/preview.js` to match the Plymouth timing and new gore assets.
The browser preview is a development approximation, not the source of runtime
truth.

Add:

- Big Brother eye opening state;
- approved gore skull;
- independently moving jaw;
- dangling eye sway;
- the viewer-right socket trauma;
- red ignition;
- final signal collapse.

Include a replay control and keep the existing asset-library page working.

## Plymouth performance rules

- preload all images once;
- reuse sprites;
- never decode or create images inside the refresh callback;
- avoid large full-screen RGBA assets when a small tiled asset works;
- minimize simultaneously visible 1024×1024 layers;
- keep deterministic behavior through `random_seed`;
- scale assets using screen dimensions;
- finish on complete black;
- do not block Plymouth’s boot-progress lifecycle;
- do not assume a fixed 1920×1080 display.

## Installation

Preserve:

```text
./scripts/build.sh
sudo ./installer/install.sh
sudo plymouth-set-default-theme -R curruption
```

The installer must:

- validate assets before installation;
- install all required subdirectories;
- preserve safe shell quoting;
- avoid changing the active theme without explicit user action.

## Validation

Run locally:

```bash
python3 scripts/process_assets.py
python3 scripts/validate_assets.py
python3 scripts/build.py
node --check preview/preview.js
node --check preview/assets.js
```

On Linux with Plymouth installed:

```bash
sudo ./installer/install.sh
sudo plymouthd --debug --tty=/dev/tty1
sudo plymouth show-splash
sleep 6
sudo plymouth quit
```

Also test through a real reboot after the non-reboot preview succeeds.

Test at:

- 1920×1080;
- 1366×768;
- 2560×1440;
- at least one portrait or unusual aspect ratio if possible.

## Acceptance criteria

The implementation is done only when:

- concept 06 is faithfully represented by layered runtime assets;
- the Big Brother eye appears before skull reconstruction;
- the jaw and dangling eyeball animate independently;
- the dangling eyeball looks downward;
- only the viewer-right socket contains the hanging eye;
- the viewer-left socket stays empty;
- no flesh hangs beneath either cheekbone;
- the entire animation lasts 4–6 seconds;
- the final frame is total black;
- all asset validation passes;
- the browser preview matches the Plymouth sequence;
- the theme installs and renders inside Plymouth;
- no frame drops are visible on target hardware;
- the display manager handoff is clean;
- documentation reflects the finished behavior.

## Do not do

- Do not replace the project with a GIF or video.
- Do not implement the animation as hundreds of frame images.
- Do not flatten every visual system into one asset.
- Do not overwrite concept 06.
- Do not introduce sound.
- Do not add logos, branding, slogans, or copyrighted interface copies.
- Do not add additional gore beyond the approved concept without direction.
- Do not remove the Big Brother eye sequence.
- Do not claim Plymouth validation unless it was actually tested on Linux.

## Final handoff report

When finished, report:

1. files added and changed;
2. new runtime layers;
3. final animation timeline;
4. configuration options;
5. validation commands and results;
6. tested Linux/Plymouth versions and resolutions;
7. any remaining limitations.

---

# Implementation status

Everything above is the original brief and is kept for reference. This section
records what was actually built and where it diverges.

## The jaw is authored, not extracted

The brief asked for concept 06 to be masked into `assets/skull-gore/*.png`
layers. That did not happen, and should not: the project owner supplied
`assets/skull/scream-00.png`, `scream-01.png` and `scream-02.png` — three
renders of the approved subject at increasing jaw travel, sharing one 560x560
canvas and one origin. Swapping authored frames gives a correct mandible arc,
correct shadow inside the mouth, and correct blood behaviour, none of which a
masked cut-out of a closed-jaw render can produce.

`scream-00.png` is byte-identical to `skull-gore-approved.png`, so the
sequence still starts on the approved image exactly. The validator enforces
that, and enforces that the approved source still matches concept 06.

No new asset files were created or modified.

## The dangling eye is a runtime cut, off by default

Three keyframes lock the eyeball to the jaw, and the brief requires the two to
animate independently. The runtime can cut a column out of whichever frame is
live and re-lay it a few pixels inboard, so it flexes independently of the
jaw while the tile stays unrotated and the iris stays aimed downward. On the
hyper-real artwork this column is x 352–432 / y 352–440, re-derived after the
production art replaced the flat concept — the eyeball there sits close enough
to the cheek that the crop seam only just clears bone. `dangling_eye_enabled`
defaults to 0 for that reason: the three authored frames already move the
eyeball on their own, and the crop is an opt-in for a wider swing rather than
the default. `scripts/validate_assets.py` re-checks the seam and margin
against the artwork whenever it is enabled.

## Module layout

`35-dangling-eye.script` was added as suggested. `45-bigbrother.script` was
also added — under that later number, not `25-`, because the brief's "Big
Brother eye" beat was redirected mid-project from an opening interception to
the closing watcher, so it now loads after the systems it appears on top of.

## Corruption is split in two

Layers that fill the area they cover — noise, static, terminal mask — are
drawn across the whole screen as a 2x2 grid of sprites sharing one
quarter-screen image. A wash with a hard rectangular edge reads as a box
sitting on the picture, not as damage to the signal. Sparse layers — tears,
packet strips, compression blocks, channel split, data-mosh — stay in a fixed
field centred on the subject, where there is no edge to see.

Scanlines are a third case: periodic in y, uniform in x, so one screen-wide
strip stacked down the display is exact. Scaling the 8x8 tile to the full
screen, as the previous runtime did, stretched two hairlines into two bands.

## Plymouth script has no function-local scoping — this was a real bug

Cross-checked against Plymouth's own bundled `themes/script/script.script`
(canonical, ships with Plymouth) and a live Arch theme
(`jtyr/plymouth-theme-arch-breeze`): a bare `x = 1;` assigned inside a `fun`
writes the **global** `x`. Function-local scoping only exists via an explicit
`local.x;` declaration before first use — the reference script demonstrates
this exact pattern (`local.box; local.lock; local.entry;` before using them as
bare names for the rest of that function).

`scripts/build.py` concatenates all ten modules into one script. Every module
was originally written with bare scratch variables — `level`, `state`,
`frame`, `size`, and so on — on the assumption that a `fun` body gets its own
scope, which Plymouth's language does not provide. Concatenated, a same-named
scratch variable in two different modules' `Update()` functions is the same
global storage. In this codebase every affected read happened to be preceded
by a write in the same call, so nothing was visibly broken by it, but that was
incidental, not designed, and a future edit could easily have broken it
silently with no error message on a real boot.

Fixed by declaring every function-body scratch variable `local.` in all ten
modules — 43 functions checked, matched against parameter lists so real
parameters (which are correctly call-scoped without any declaration) weren't
mistakenly re-declared. Verified two ways: a script that parses every `fun`
block and confirms no bare assignment lacks either a parameter binding or a
preceding `local.` declaration, and a structural brace/paren/bracket balance
check on the rebuilt `theme/curruption.script`. Both pass clean.

Also fixed while cross-checking the canonical reference:
`Plymouth.SetMessageFunction` is not a real registration function —
`Plymouth.SetDisplayMessageFunction` is the name Plymouth's own script theme
uses. (The Arch Breeze theme referenced above uses the wrong name too, for
whatever that's worth; it evidently doesn't hard-fail the theme load, but the
confirmed-correct name is used here.)

## Not verified

**The theme has not been run under Plymouth on Linux.** It was developed on
Windows. Structure, geometry, asset references and timing were verified
offline, the composition was checked by replicating the module maths in a
throwaway renderer, and the script language usage was cross-checked against
Plymouth's own bundled reference theme and a live Arch theme — but no claim is
made about actual Plymouth behaviour, because none of that is the same as
running it.

Things worth checking on a real Linux boot before this is called done:

- `Image.Crop`, `Plymouth.SetRefreshRate` and the `font` argument to
  `Image.Text` are all used and all confirmed to exist in Plymouth's script
  language, but confirmation came from documentation and reference themes, not
  from executing this script. If a particular Plymouth build lacks `Crop`,
  `gore_enabled=0` in `config/theme.conf` is the documented fallback.
- the clock counts refresh ticks and divides by `refresh_rate`. If a build
  ignores `SetRefreshRate`, the sequence runs fast or slow until that setting
  is corrected to the rate the build actually uses.
- resolution testing at 1920x1080, 1366x768, 2560x1440 and one portrait panel.
- whether `local.` declarations are accepted by every Plymouth version in the
  wild, not just the one the reference theme was written against. The syntax
  is confirmed from Plymouth's own upstream example, which is the strongest
  evidence available without a real boot, but it is evidence, not a test.
