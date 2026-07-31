# Animation timing

The sequence is 10 seconds at a 30 fps target. The clock counts refresh ticks
rather than wall time, so the same frame lands on the same beat on every
machine. `theme/modules/10-core.script` holds these values in the `T`
namespace; `preview/preview.js` mirrors them. Change both together.

| Time | Event |
|---:|---|
| 0.00–0.22 | complete black |
| 0.22–1.30 | the system wakes: grid, telemetry, packet noise |
| 0.32–0.92 | `TRACE INITIATED` |
| 0.50–1.50 | reticle sweeps the field looking for a subject |
| 0.95–1.55 | `SUBJECT ACQUIRED` |
| 1.10–2.20 | gore skull reconstructs from unstable fragments |
| 1.90–3.10 | `VISUAL LINK ESTABLISHED` |
| 3.30–4.60 | tracking brackets close, `TARGET LOCKED` |
| 4.00–5.00 | dangling eyeball begins a slow heavy sway |
| 4.60–5.90 | jaw opens with slow weight |
| 4.75–5.55 | `BIOMETRIC MATCH` |
| 5.30–5.60 | red ignition, empty socket only, hard on and hard off |
| 5.90–6.70 | the intrusion is noticed and the link degrades |
| 5.95–6.55 | `CONNECTION COMPROMISED` |
| 6.60–7.20 | `SIGNAL LOST` |
| 7.00–7.70 | data-mosh, packet loss, static, disintegration |
| 7.55–9.70 | the watcher resolves out of the static, then holds |
| 7.95–9.70 | `BIG BROTHER IS WATCHING` |
| 9.70–10.00 | total black for the display-manager handoff |

## Where the weight sits

The opening runs fast on purpose. A trace that takes its time is a loading
screen; one that finds you inside a second is an intrusion. The whole
pre-reconstruction phase is 1.1 s.

The other end is where the sequence spends its time. The watcher holds for
2.15 s and the caption for 1.75 s — more than a fifth of the runtime on one
still image and one line of text. That imbalance is the design: everything
before it is the machine working, and the last two seconds are the thing that
was watching the machine.

The last 0.30 s is deliberately empty. Every system collapses to zero opacity
at 9.70, leaving only the black window, so the handoff to the display manager
cannot flash.

## The shape of it

An intrusion, not a title card. Something traces the machine, sweeps for a
subject, finds one, confirms it, gets noticed, loses the link — and is still
there afterwards.

The watcher is held back to the very end on purpose. Opening on a human eye
makes it a logo; closing on one makes it a reversal. Everything before 8.55 is
a machine looking at a subject; after 8.55 the eye puts its own reticle on the
person reading the screen.

## Overlaps are intentional

Four beats overlap their neighbours, and that is the point:

- the reticle sweep (0.50) is still running when the skull starts rebuilding
  at 1.10, so the machine appears to find the subject rather than cut to it;
- the sway starts (4.00) before the jaw moves (4.60), so the eyeball is
  already loose when the jaw drops rather than reacting to it;
- `SIGNAL LOST` (6.60) arrives before the data-mosh (7.00), so the label is
  read before the picture is destroyed;
- the watcher starts resolving (7.55) while the terminal mask is still up, so
  it comes through the interference instead of being cut to;
- the caption lands (full at 8.30) before the reticle snaps onto the viewer
  (8.45), so the words arrive first and the aim follows.

## Changing the length

`animation_speed` in `config/theme.conf` scales the whole timeline; the beats
keep their proportions. `animation_duration` is the wall-clock point at which
everything blanks — lowering it truncates the sequence rather than compressing
it. `refresh_rate` must match the rate Plymouth actually drives the script
plugin at, or the sequence runs fast or slow.

Ten seconds is longer than most boot splashes. If the machine finishes booting
first, Plymouth quits and the sequence is cut short wherever it happens to be;
nothing waits on it. Lower `animation_speed` to around 0.55 for a five-second
version of the same arc.
