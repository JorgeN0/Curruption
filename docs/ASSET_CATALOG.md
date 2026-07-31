# Asset catalog

All raster assets are original project material. Organic masters use
hyper-realistic forensic-photography direction; signal and HUD layers are
generated deterministically by `scripts/process_assets.py` at the fidelity
appropriate to real surveillance equipment.

`scripts/validate_assets.py` enforces the inventory below, checks that every
`Image("...")` path the Plymouth modules load resolves, and re-checks the
gore-skull layer geometry against the artwork.

The **Runtime** column says whether the theme loads the layer at boot. Layers
marked *library* are validated, catalogued and available, but not currently
composited; they exist so the sequence can be re-cut without new artwork.

## Gore skull

| Asset | Purpose | Runtime |
|---|---|---|
| `scream-00.png` | closed/tense scream state | yes |
| `scream-01.png` | half-open scream transition | yes |
| `scream-02.png` | fully open scream state | yes |
| `skull-gore-approved.png` | the approved hyper-real skull at runtime size | reference |
| `cracks.png` | crack and blood tracery overlay | yes |

The three scream frames share one 560x560 canvas and one origin. They *are*
the jaw animation: the runtime preloads all three and swaps between them, so
the opening is authored anatomy rather than a translated cut-out.

Two identities are enforced by the validator:

- `scream-00.png` is byte-identical to `skull-gore-approved.png`;
- `assets/source/skull-gore-approved.png` is byte-identical to
  `preview/concepts/skull-hyperreal-approved.png`, which is the immutable
  approved concept.

Coordinates the runtime depends on, in 560x560 master space:

| Region | Box | Used for |
|---|---|---|
| dangling-eye column | x 352–432, y 352–440 | independent eyeball sway (opt-in) |
| viewer-left socket | centroid (217, 251), ~100 px across | red ignition |

Only the empty viewer-left socket ignites, so `eyes.png` and `eye-cores.png`
are cropped to their left half and scaled to 204 px at load time. The
viewer-right socket has the eyeball hanging out of it and is never lit.

The eye column is cut at x=352, the shadowed gap between the mandible and the
hanging eyeball, and slides no more than four pixels inboard because x 428–432
is the only margin that is black in all three frames.

**`dangling_eye_enabled` defaults to 0.** In the hyper-real masters the
eyeball is nestled against the cheek with no black corridor beside it, so the
seam clears bone by only a few levels (peak 87 of 255) and the cut shows at
full travel. The three authored frames already move the eyeball on their own.
The constants above are kept correct so the opt-in path still works if a wider
swing is wanted, and the validator only checks them when it is enabled.

## Skull

| Asset | Purpose | Runtime |
|---|---|---|
| `skull.png` | full transparent master | library |
| `head.png` | upper skull animation layer | `gore_enabled=0` |
| `jaw.png` | independent jaw layer | `gore_enabled=0` |
| `teeth.png` | isolated teeth detail | library |
| `eye-sockets.png` | socket-darkening layer | library |
| `eyes.png` | red glow and bloom | yes |
| `eye-cores.png` | instantaneous bright ignition cores | yes |

The clean anatomical layers are the fallback path for a Plymouth build without
image cropping: set `gore_enabled=0` and the theme renders a static head with
a translated jaw and no dangling eye.

## The watcher

An original, anonymous surveillance image. It is the closing beat: the eye
resolves out of the static after the link dies and puts its own reticle on the
viewer, under the `BIG BROTHER IS WATCHING` caption.

The four runtime states are swapped in order as it resolves.

| Asset | Purpose | Runtime |
|---|---|---|
| `eye-corrupted.png` | emerging from the interference | yes, 1st |
| `eye-high-contrast.png` | recognition pass | yes, 2nd |
| `eye-surveillance.png` | clean, simply watching | yes, 3rd |
| `eye-tracked.png` | brackets and red reticle on the viewer | yes, 4th |
| `eye-signal-lost.png` | near-black terminal feed | library |
| `eye-iris-mask.png` | isolated iris tracking mask | library |
| `eye-pupil-mask.png` | independent pupil-darkening mask | library |
| `eye-target-red.png` | red pupil acquisition marker | library |

## Effects

| Asset | Purpose | Runtime |
|---|---|---|
| `smoke.png`, `smoke-02.png` | slow background atmosphere | yes |
| `noise.png` | corruption wash and constant grain | yes |
| `static-burst.png` | disintegration wash | yes |
| `signal-loss.png` | terminal blackout mask | yes |
| `scanlines.png` | 8x8 tile, stacked as screen-wide strips | `film_grain>0` |
| `horizontal-tear.png` | long displaced scan strips | yes |
| `image-offset.png` | displaced image slices | yes |
| `packet-loss.png` | missing horizontal packet strips | yes |
| `compression-blocks.png`, `-02.png` | alternating codec damage | yes |
| `rgb-split-red.png`, `rgb-split-white.png` | palette-safe channel split | yes |
| `data-mosh.png` | terminal pixel corruption | yes |
| `vignette.png` | surveillance lens falloff | `vignette_opacity>0` |
| `noise-fine.png`, `noise-coarse.png` | alternative noise scales | library |
| `film-grain.png` | fine finishing grain | library |
| `dust-particles.png` | sparse suspended particles | library |
| `static-burst-02.png` | alternate static frame | library |
| `signal-drop.png` | hard dropped-scan masks | library |

## HUD

| Asset | Purpose | Runtime |
|---|---|---|
| `brackets.png` | subject tracking frame, three preloaded sizes | yes |
| `tracking-brackets-tight.png` | locked-subject frame | yes |
| `crosshair.png` | acquisition reticle | yes |
| `target-lock.png` | final acquisition reticle | yes |
| `signal-bars-0.png`–`signal-bars-5.png` | discrete signal states | yes |
| `rec-indicator.png` | recording state | yes |
| `telemetry-panel.png` | transient telemetry container | yes |
| `status-panel.png` | compact monitoring state | yes |
| `error-rate.png` | signal error graph | yes |
| `frame-counter.png` | frame/timeline indicator | yes |
| `packet-indicators.png` | packet quality strip | yes |
| `node-marker.png` | surveillance node marker | yes |
| `monitoring-grid.png` | low-opacity analysis grid | yes |

Outside the authored gore skull, only black, grey, white, bone and `#FF0033`
appear in the final assets.

## Regenerating

`scripts/process_assets.py` rewrites the procedural layers in place, so it is
**not** run by `./scripts/build.sh` by default. Run it explicitly when you
want it:

```bash
./scripts/build.sh --assets
```

It does not touch the scream frames or the approved concept.
