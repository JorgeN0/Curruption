# Design language

The screen is nearly black. Motion is slow and deliberate; only signal errors
move abruptly.

The register is surveillance paranoia: an intrusion in progress, seen through
the attacker's own interface. Something traces the machine, sweeps for a
subject, reconstructs one, confirms it, is noticed, and loses the link. Then
the eye that was watching the whole time looks back.

The palette is black (`#000000`), dark grey (`#1A1A1A`), white, pale bone, the
dark burgundy of the approved blood, and the single failure accent `#FF0033`.
No audio, no dialogue, no logo, no branding, no title.

## Typography

Monospace only, in three weights that do different jobs.

The **HUD readout** is the attacker's interface: regular weight, tight, and
deliberately subordinate to the subject. It reports, it does not announce.

The **two story beats** — `SIGNAL LOST` and `BIG BROTHER IS WATCHING` — are
the sequence speaking to the viewer, so they are set large, bold, and
letter-spaced. Monospace already sets an even rhythm; opening the tracking
further slows the eye down and stops the words reading as another status line.
Plymouth offers no tracking control, so the spacing is written into the
strings themselves.

Sizes step three times across the supported resolutions rather than being
rasterised once and scaled, so nothing is ever blurry. Neither weight competes
with the skull for the centre of the frame: the HUD sits above and beside it,
the story beats below.

## The reversal

For nine seconds the viewer is on the safe side of the glass, watching a
machine take a subject apart. The last beat moves them to the other side: the
interface fails, the corruption clears, and a human eye resolves out of the
static with its reticle on the reader. `BIG BROTHER IS WATCHING` sits under it,
steady while everything else on screen has failed.

The eye is deliberately *not* used at the start. Opening on it makes it a
logo; closing on it makes it the point.

## Gore direction

The v0.1 specification said "no gore". That direction was deliberately changed
by the project owner. `preview/concepts/skull-hyperreal-approved.png` is the
approved appearance and is treated as an immutable source reference:

- blood concentrated around the face and upper outer cranium;
- a relatively clean central forehead;
- no flesh hanging beneath the cheekbones;
- one freshly damaged viewer-right socket;
- one dangling bloodshot eyeball on a loose optic nerve, iris aimed downward;
- a completely empty viewer-left socket;
- a clean, centred silhouette on black.

The approved gore should read as a dark forensic surveillance image, not an
action-horror scene: no splatter, no exposed brain matter, no organs, no large
flesh masses. `scripts/validate_assets.py` fails the build if the approved
concept file is modified.

## The watcher

One anonymous monochrome human eye, held back until the link dies. It resolves
through four states — corrupted, recognition pass, clean, tracked — and then
does not move. Stillness is what makes it read as attention rather than as an
animation: everything else in the sequence is drifting, tearing or flickering,
and this is not.

It is sized to roughly half the screen width so it reads as a face looking out
of a feed, never as a full-screen splash, and it sits high enough to leave the
lower band clear for the caption.

## Layer order

1. black window background
2. low-opacity smoke
3. gore-skull head and jaw
4. socket trauma (authored into the skull artwork)
5. optic nerve
6. dangling eyeball
7. red ignition
8. surveillance HUD and state text
9. glitches and corruption
10. the watcher
11. film grain and scanlines
12. terminal signal-loss mask
13. `SIGNAL LOST` and `BIG BROTHER IS WATCHING`

The watcher sits *above* the corruption and *below* the finishing passes, so
it comes up through the interference rather than being cut to, and the
scanlines still run across it. The last beat is a monitor, not a photograph.

## Motion

**Skull.** Centred and front-facing. Slow reconstruction, then near-stillness.
Brief deterministic horizontal offsets during reconstruction and again during
corruption, and nothing in between: no constant floating, no smooth
screensaver drift.

**Jaw.** Authored rather than simulated. Three renders of the same subject at
increasing jaw travel are swapped in sequence, so the opening is anatomically
correct instead of a translated cut-out. It is deliberate and heavy, and once
the signal starts failing it does not recover.

**Dangling eyeball.** Carried by the three authored frames, which move it as
the jaw drops. An additional pendulum sway is available — the runtime cuts the
eyeball column out of whichever frame is live and re-lays it a few pixels
inboard — but it is off by default: the hyper-real masters tuck the eyeball
against the cheek with no black corridor beside it, so the cut shows. When it
is enabled the tile is never rotated, which keeps the iris aimed downward
through the whole swing.

**Red ignition.** Hard on, hard off, no fade. Only the empty viewer-left
socket lights. The viewer-right socket has its eye hanging out of it on the
optic nerve — there is nothing left in there to light up, and lighting it
anyway read as decoration rather than as a reaction.

**Reticle.** Sweeps the field in quantised steps during the trace, so it moves
like a machine searching rather than a cursor gliding, then settles once it
has something.

**Smoke.** Below 25% opacity, hard-capped by the runtime. Extremely slow,
background only, never obscuring the subject. Gone before the watcher, which
gets a clean black field to itself.

**Glitches.** Brief and deterministic. Every burst is a function of the frame
tick and `random_seed`, so the same configuration corrupts identically on
every machine. Nothing is allocated inside the refresh callback.

## Hyper-realism standard

Organic imagery must resemble photographed physical material rather than a
stylized render. Bone uses natural pores, mineral variation, sutures, chips,
and matte-to-satin roughness without carved or repeating ornament. Blood has
dark clotted volume, thin wet highlights, and dried edges. Orbital tissue,
optic nerve, sclera, veins, and gravity must remain anatomically credible.

Atmospheric assets use multi-scale density fields and photographic grain.
Surveillance HUD and corruption layers remain synthetic by design, but use
subpixel-safe geometry, irregular signal structure, restrained opacity, and no
decorative interface clutter.

The hyper-real skull uses three complete photographic scream states. Its
dangling eye remains visible but does not use the former cropped-tile sway:
natural bone crosses that crop boundary, and preserving the crop would create
a visible seam.

## Fear treatment

Fear comes from withheld information and attention. Organic masters keep their
authored anatomy but receive one deterministic grade across every pose:
desaturated color, cold narrow overhead exposure, deeper facial cavities, and
strong peripheral falloff. Smoke is reduced so darkness stays dominant.
Corruption is slightly stronger but remains brief; long unstable motion would
turn threat into spectacle. Red remains rare enough to feel diagnostic rather
than decorative.

## Why the corruption is split in two

Layers that fill the area they cover — noise, static, the terminal mask — are
drawn across the whole screen. A wash with a hard rectangular edge reads as a
box sitting on the picture instead of as damage to the signal. Layers that are
sparse — tears, packet strips, compression blocks, channel split, data-mosh —
stay in a fixed field centred on the subject, where there is no edge to see
and the damage stays where the story is.
