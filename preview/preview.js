// Development approximation of the Plymouth sequence.
//
// The timeline, the geometry constants and the deterministic hash are copied
// from theme/modules/ so the two stay in step. This is not the source of
// runtime truth: Plymouth composites sprites, this composites a canvas, and
// the two will never be pixel-identical. It exists to iterate on timing
// without rebooting.

const CANVAS_W = 1920;
const CANVAS_H = 1080;
const RATE = 30;
const SEED = 31991;

// theme/modules/10-core.script
const T = {
  blackOut: 0.22,
  acquireIn: 0.22, acquireOut: 1.30,
  traceIn: 0.32, traceOut: 0.92,
  scanIn: 0.50, scanOut: 1.50,
  subjectIn: 0.95, subjectOut: 1.55,
  skullIn: 1.10, skullFormed: 2.20,
  linkIn: 1.90, linkOut: 3.10,
  lockIn: 3.30, lockOut: 4.60,
  swayIn: 4.00, swayFull: 5.00,
  jawIn: 4.60, jawOut: 5.90,
  matchIn: 4.75, matchOut: 5.55,
  igniteIn: 5.30,
  corruptIn: 5.90, corruptOut: 6.70,
  breachIn: 5.95, breachOut: 6.55,
  lostIn: 6.60, lostOut: 7.20,
  moshIn: 7.00, moshOut: 7.70,
  watchIn: 7.55, watchText: 7.95, watchOut: 9.70,
  blackIn: 9.70, end: 10.00,
};

// config/theme.conf
const CFG = {
  smokeDensity: 0.18,
  glitchIntensity: 0.72,
  filmGrain: 0.12,
  vignetteOpacity: 0.45,
  eyeDuration: 0.30,
  danglingEyeSway: 0.035,
  danglingEyeSpeed: 0.8,
  jawOpenDistance: 42,
  bloodOverlayOpacity: 1.0,
  // Off in config/theme.conf: the hyper-real masters leave no black corridor
  // beside the eyeball, and the three authored frames already move it.
  danglingEyeEnabled: 0,
};

// theme/modules/30-skull.script, re-derived from the hyper-real masters.
const SKULL = { src: 560, eyeCol: 352, bulbTop: 352, bulbRight: 432, bulbBottom: 440 };
// Viewer-left socket darkness centroid, and the ignition tile that covers it.
const SOCKET = { size: 204, dx: 102, dy: 149 };

const canvas = document.querySelector("#boot");
const ctx = canvas.getContext("2d");
const replay = document.querySelector("#replay");
const toggle = document.querySelector("#toggle");
const scrub = document.querySelector("#scrub");
const clock = document.querySelector("#time");

const SOURCES = {
  scream0: "skull/scream-00.png",
  scream1: "skull/scream-01.png",
  scream2: "skull/scream-02.png",
  cracks: "skull/cracks.png",
  glow: "skull/eyes.png",
  cores: "skull/eye-cores.png",

  eyeClean: "eye/eye-surveillance.png",
  eyeHarsh: "eye/eye-high-contrast.png",
  eyeTracked: "eye/eye-tracked.png",
  eyeCorrupted: "eye/eye-corrupted.png",

  smokeA: "effects/smoke.png",
  smokeB: "effects/smoke-02.png",
  noise: "effects/noise.png",
  tear: "effects/horizontal-tear.png",
  offset: "effects/image-offset.png",
  packet: "effects/packet-loss.png",
  mosh: "effects/data-mosh.png",
  splitRed: "effects/rgb-split-red.png",
  splitWhite: "effects/rgb-split-white.png",
  blockA: "effects/compression-blocks.png",
  blockB: "effects/compression-blocks-02.png",
  staticA: "effects/static-burst.png",
  scanlines: "effects/scanlines.png",
  mask: "effects/signal-loss.png",
  vignette: "effects/vignette.png",

  grid: "hud/monitoring-grid.png",
  brackets: "hud/brackets.png",
  bracketsTight: "hud/tracking-brackets-tight.png",
  crosshair: "hud/crosshair.png",
  targetLock: "hud/target-lock.png",
  rec: "hud/rec-indicator.png",
  node: "hud/node-marker.png",
  telemetry: "hud/telemetry-panel.png",
  status: "hud/status-panel.png",
  errorRate: "hud/error-rate.png",
  frameCounter: "hud/frame-counter.png",
  packets: "hud/packet-indicators.png",
};
for (let level = 0; level <= 5; level += 1) {
  SOURCES[`bars${level}`] = `hud/signal-bars-${level}.png`;
}

const img = {};
for (const [key, path] of Object.entries(SOURCES)) {
  const image = new Image();
  image.src = `../assets/${path}`;
  img[key] = image;
}

// --- helpers, mirrored from 10-core.script ---------------------------------

const clamp = (v, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, v));
const ramp = (t, a, b) => (b <= a ? (t < a ? 0 : 1) : clamp((t - a) / (b - a)));
const hold = (t, a, b) => (t >= a && t < b ? 1 : 0);
const ease = (v) => {
  const x = clamp(v);
  return x * x * (3 - 2 * x);
};

function hash(n) {
  const h = (((n + SEED) * 71) % 991) * 113 + n * 29;
  return Math.abs(h % 1009);
}
const hashSign = (n) => (hash(n) % 3) - 1;
const flicker = (n, salt) => (hash(n * 7 + salt) % 19 < 3 ? 0.22 : 1);

const layout = {
  left: CANVAS_W * 0.055,
  right: CANVAS_W - CANVAS_W * 0.055,
  top: CANVAS_H * 0.075,
  bottom: CANVAS_H - CANVAS_H * 0.075,
};
const cx = CANVAS_W / 2;
const cy = CANVAS_H / 2;
const ox = Math.round(cx - SKULL.src / 2);
const oy = Math.round(cy - SKULL.src / 2);

let tick = 0;
let jitter = 0;
let jitterPrev = 0;

function draw(image, x, y, w, h, alpha) {
  if (!image.complete || alpha <= 0.004) return;
  ctx.globalAlpha = clamp(alpha);
  ctx.drawImage(image, x, y, w ?? image.width, h ?? image.height);
  ctx.globalAlpha = 1;
}

function drawCentred(image, centreX, centreY, w, alpha) {
  if (!image.complete) return;
  const h = (image.height * w) / image.width;
  draw(image, centreX - w / 2, centreY - h / 2, w, h, alpha);
}

// Mirrors ui_font / story_font / watch_font in 10-core.script. The preview
// canvas is the 1920x1080 reference, so these are the scale > 0.72 tier.
const FONTS = {
  ui: "21px 'Courier New', monospace",
  story: "bold 34px 'Courier New', monospace",
  watch: "bold 42px 'Courier New', monospace",
};

function label(text, y, alpha, font = FONTS.ui, tone = "#dcdcdc") {
  if (alpha <= 0.004) return;
  ctx.globalAlpha = clamp(alpha);
  ctx.fillStyle = tone;
  ctx.font = font;
  ctx.textAlign = "center";
  ctx.fillText(text, cx, y);
  ctx.globalAlpha = 1;
}

// --- systems ---------------------------------------------------------------

function smoke(t) {
  const level =
    ramp(t, T.acquireIn, T.skullIn) *
    Math.min(CFG.smokeDensity, 0.24) *
    (1 - ramp(t, T.moshIn, T.watchIn));
  drawCentred(img.smokeA, cx + Math.sin(t * 0.16) * 26, cy + Math.sin(t * 0.11) * 15, 1000, level);
  drawCentred(img.smokeB, cx - Math.sin(t * 0.13 + 1.7) * 21, cy - Math.sin(t * 0.09 + 0.6) * 12, 1000, level * 0.62);
}

// The watcher: held back to the very end, then still.
function bigBrother(t) {
  if (t < T.watchIn || t >= T.watchOut) return;
  const w = Math.min(CANVAS_W * 0.52, CANVAS_H * 0.74);

  // Offsets from watchIn, as in 45-bigbrother.script.
  let frame = img.eyeCorrupted;
  if (t >= T.watchIn + 0.28) frame = img.eyeHarsh;
  if (t >= T.watchIn + 0.48) frame = img.eyeClean;
  if (t >= T.watchIn + 0.9) frame = img.eyeTracked;

  let level = ramp(t, T.watchIn, T.watchIn + 0.13);
  if (t < T.watchIn + 0.48) level *= flicker(tick, 5);

  drawCentred(frame, cx, cy - CANVAS_H * 0.06, w, level);
}

// Returns the live skull state so the dangling eye can follow it.
function skull(t) {
  const build = ease(ramp(t, T.skullIn, T.skullFormed));
  let reveal = ramp(t, T.skullIn, T.skullIn + 0.3) * (1 - ramp(t, T.moshIn, T.watchIn));
  if (t < T.skullFormed) reveal *= flicker(tick, 3);

  let unstable = (1 - build) * 26;
  if (t > T.corruptIn) unstable = ramp(t, T.corruptIn, T.moshIn) * 20;
  jitterPrev = jitter;
  jitter = hash(tick) % 7 < 2 ? hashSign(tick * 5) * unstable : 0;

  const x = ox + jitter;
  const y = oy + (1 - build) * 22;

  let open = ease(ramp(t, T.jawIn, T.jawIn + 0.42));
  open += ease(ramp(t, T.jawOut, T.lostIn)) * 0.12;
  open += ease(ramp(t, T.lostIn, T.lostIn + 0.32)) * 0.22;
  const stage = open * clamp(CFG.jawOpenDistance / 42);

  let index = 0;
  if (stage >= 0.3) index = 1;
  if (stage >= 0.72) index = 2;
  if (t < T.skullFormed && hash(tick * 3) % 5 === 0) index = 1;
  const frame = [img.scream0, img.scream1, img.scream2][index];

  draw(frame, x, y, SKULL.src, SKULL.src, reveal);
  draw(img.cracks, x, y, SKULL.src, SKULL.src, reveal * 0.28 * CFG.bloodOverlayOpacity);
  return { x, y, reveal, frame };
}

function danglingEye(t, state) {
  if (!CFG.danglingEyeEnabled) return;
  if (state.reveal <= 0.004 || !state.frame.complete) return;
  const w = SKULL.bulbRight - SKULL.eyeCol;
  const h = SKULL.bulbBottom - SKULL.bulbTop;

  let amp = ease(ramp(t, T.swayIn, T.swayFull)) * 0.86;
  amp += ease(ramp(t, T.jawIn, T.jawOut)) * 0.14;
  const phase = (t - T.swayIn) * CFG.danglingEyeSpeed * 3.93;
  const amplitude = Math.min(CFG.danglingEyeSway * 108, 4);
  // Inboard only: sliding outward would uncover the bulb's own edge.
  const swing = -amp * amplitude * (1 - Math.cos(phase)) * 0.5;
  const drag = jitterPrev * 0.62 - jitter;

  ctx.globalAlpha = clamp(state.reveal);
  ctx.drawImage(
    state.frame,
    SKULL.eyeCol, SKULL.bulbTop, w, h,
    state.x + SKULL.eyeCol + swing + drag, state.y + SKULL.bulbTop, w, h,
  );
  ctx.globalAlpha = 1;
}

// Empty viewer-left socket only: the other one has its eye hanging out of it.
// Crops the left half of the two-glow artwork, as 40-eyes.script does.
function ignition(t, state) {
  const lit = hold(t, T.igniteIn, T.igniteIn + CFG.eyeDuration);
  if (!lit) return;
  for (const [image, alpha] of [[img.glow, 0.85], [img.cores, 1]]) {
    if (!image.complete) continue;
    ctx.globalAlpha = alpha;
    ctx.drawImage(image, 0, 0, 128, 128,
      state.x + SOCKET.dx, state.y + SOCKET.dy, SOCKET.size, SOCKET.size);
    ctx.globalAlpha = 1;
  }
}

function hud(t) {
  let live = ramp(t, T.acquireIn, T.acquireIn + 0.12) * (1 - ramp(t, T.lostIn, T.moshIn));
  if (t > T.corruptIn) live *= flicker(tick, 7);
  if (live <= 0.004) return;

  draw(img.grid, cx - 450, cy - 450, 900, 900, live * 0.08);

  let bracket = img.brackets;
  let size = 880;
  if (t >= T.subjectIn) size = 760;
  if (t >= T.linkIn) size = 660;
  if (t >= T.lockIn) size = 575;
  if (t >= T.lockIn + 0.55) {
    bracket = img.bracketsTight;
    size = 495;
  }
  const frameShow =
    ramp(t, T.subjectIn - 0.35, T.subjectIn - 0.2) *
    (1 - ramp(t, T.corruptIn, T.corruptIn + 0.4));
  draw(bracket, cx - size / 2 + jitter * 0.3, cy - size / 2, size, size, live * frameShow * 0.7);

  // The reticle sweeps the field looking for a subject, in quantised steps so
  // it moves like a machine, then settles on what it found.
  let cross = 0;
  let crossX = cx;
  if (t < T.skullIn) {
    cross = ramp(t, T.scanIn, T.scanIn + 0.12);
    const step = Math.floor(ramp(t, T.scanIn, T.subjectIn) * 7) / 7;
    crossX = cx + (step - 0.5) * CANVAS_W * 0.54;
  } else {
    cross = ramp(t, T.lockIn, T.lockIn + 0.1) * (1 - ramp(t, T.lockOut, T.lockOut + 0.25));
  }
  draw(img.crosshair, crossX - 125, cy - 125, 250, 250, live * cross * 0.32);
  const lockShow =
    ramp(t, T.lockIn + 0.55, T.lockIn + 0.64) * (1 - ramp(t, T.lockOut, T.lockOut + 0.22));
  draw(img.targetLock, cx - 150, cy - 150, 300, 300, live * lockShow * 0.62);

  let level = 1;
  if (t >= T.scanIn) level = 3;
  if (t >= T.skullFormed) level = 5;
  if (t >= T.corruptIn) level = 3;
  if (t >= T.lostIn) level = 1;
  if (t >= T.moshIn) level = 0;
  draw(img[`bars${level}`], layout.right - 180, layout.top, 180, 48, live * 0.78);
  draw(img.packets, layout.right - 320, layout.top + 70, 320, 52,
    live * ramp(t, T.traceIn, T.traceIn + 0.2) * 0.6);
  draw(img.rec, layout.left, layout.top, 150, 44, live * flicker(tick, 13) * 0.9);
  draw(img.frameCounter, layout.left, layout.bottom - 64, 280, 64, live * 0.55);
  draw(img.node, cx + 300, cy - CANVAS_H * 0.16, 110, 110,
    live * ramp(t, T.scanIn, T.scanIn + 0.15) * (1 - ramp(t, T.skullIn, T.skullIn + 0.3)) * 0.6);
  draw(img.telemetry, layout.left, cy - 90, 420, 180,
    live * ramp(t, T.linkIn, T.linkIn + 0.15) * (1 - ramp(t, T.corruptIn, T.corruptIn + 0.3)) * 0.58);
  draw(img.status, layout.right - 420, cy - 112, 420, 224,
    live * ramp(t, T.lockIn, T.lockIn + 0.15) * (1 - ramp(t, T.corruptOut, T.lostIn)) * 0.52);
  draw(img.errorRate, layout.right - 360, layout.bottom - 112, 360, 112,
    live * ramp(t, T.corruptIn, T.corruptIn + 0.1) * 0.72);

  let text = "";
  if (t >= T.traceIn && t < T.traceOut) text = "TRACE INITIATED";
  else if (t >= T.subjectIn && t < T.subjectOut) text = "SUBJECT ACQUIRED";
  else if (t >= T.linkIn && t < T.linkOut) text = "VISUAL LINK ESTABLISHED";
  else if (t >= T.lockIn && t < T.lockOut) text = "TARGET LOCKED";
  else if (t >= T.matchIn && t < T.matchOut) text = "BIOMETRIC MATCH";
  else if (t >= T.breachIn && t < T.breachOut) text = "CONNECTION COMPROMISED";
  if (text) label(text, cy + 345, live * 0.92);
}

function glitch(t) {
  if (t >= T.blackIn) return;
  const g = CFG.glitchIntensity;
  const field = Math.round(512 * 1.4);
  const fx = Math.round(cx - field / 2);
  const fy = Math.round(cy - field / 2);
  const slide = hashSign(tick * 3) * 16;

  const acquire =
    ramp(t, T.acquireIn, T.acquireIn + 0.06) * (1 - ramp(t, T.acquireOut - 0.25, T.acquireOut));
  const sweep =
    ramp(t, T.scanIn, T.scanIn + 0.08) * (1 - ramp(t, T.scanOut - 0.3, T.scanOut));
  const rebuild =
    ramp(t, T.skullIn, T.skullIn + 0.06) * (1 - ramp(t, T.skullFormed - 0.35, T.skullFormed));
  // Both fall away again before the watcher resolves, or the corruption they
  // drive would sit on top of the last beat.
  const decay = ramp(t, T.corruptIn, T.corruptOut) * (1 - ramp(t, T.lostOut, T.moshOut));
  const collapse =
    ramp(t, T.moshIn, T.moshIn + 0.12) * (1 - ramp(t, T.watchIn, T.watchIn + 0.3));

  const hit = hash(tick) % 23 < 2 ? 1 : 0;
  const strong = hash(tick * 5) % 7 < 3 ? 1 : 0;

  // Washes cover the screen; sparse marks stay a field centred on the subject.
  let grain = CFG.filmGrain * 0.5 * ramp(t, T.acquireIn, T.scanIn);
  if (t >= T.watchIn) grain = CFG.filmGrain * 0.8;
  const burst = acquire * 0.16 + rebuild * 0.3 + decay * 0.55 + collapse * 0.45;
  draw(img.noise, 0, 0, CANVAS_W, CANVAS_H, grain + (burst * 0.62 + hit * 0.12) * g);
  draw(img.staticA, 0, 0, CANVAS_W, CANVAS_H, (decay * 0.3 + collapse * 0.52) * hit * g);

  draw(hash(tick * 7) % 2 ? img.blockB : img.blockA, fx, fy, field, field,
    (rebuild * 0.5 + decay * 0.45) * strong * g);
  draw(img.packet, fx + slide, fy, field, field, (acquire * 0.55 + collapse * 0.7) * strong * g);
  draw(img.tear, fx + slide * 1.6, fy, field, field, (sweep * 0.55 + decay * 0.55) * strong * g);
  draw(img.offset, fx - slide * 1.2, fy, field, field, (sweep * 0.5 + decay * 0.4) * hit * g);

  const split = (decay * 0.55 + collapse * 0.45) * hit * g;
  draw(img.splitRed, fx + 9, fy, field, field, split * 0.8);
  draw(img.splitWhite, fx - 6, fy, field, field, split * 0.6);
  draw(img.mosh, fx + slide * 0.8, fy, field, field,
    ramp(t, T.moshIn, T.moshIn + 0.1) * (1 - ramp(t, T.watchIn, T.watchIn + 0.25)) * g * 0.85);

}

// Layers above the watcher (Z 89-95 in 60-glitch.script), drawn after it.
// Scanlines and lens falloff run through the last beat: it is still a
// monitor, not a photograph.
function finish(t) {
  if (t >= T.blackIn) return;
  if (CFG.filmGrain > 0) {
    const finish = CFG.filmGrain * (1 - ramp(t, T.blackIn - 0.15, T.blackIn));
    if (finish > 0.004 && img.scanlines.complete) {
      ctx.globalAlpha = finish;
      ctx.fillStyle = ctx.createPattern(img.scanlines, "repeat") ?? "transparent";
      ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
      ctx.globalAlpha = 1;
    }
  }
  if (CFG.vignetteOpacity > 0) {
    draw(img.vignette, 0, 0, CANVAS_W, CANVAS_H,
      CFG.vignetteOpacity * ramp(t, T.acquireIn, T.scanIn) *
      (1 - ramp(t, T.blackIn - 0.2, T.blackIn)));
  }
  // Wipes the disintegrating subject, then pulls back so the watcher resolves
  // up through it rather than being cut to.
  draw(img.mask, 0, 0, CANVAS_W, CANVAS_H,
    ramp(t, T.moshIn + 0.1, T.moshOut - 0.2) * (1 - ramp(t, T.watchIn + 0.05, T.watchIn + 0.4)));
}

// --- clock -----------------------------------------------------------------

let elapsed = 0;
let last = performance.now();
let playing = true;

function render(t) {
  tick = Math.floor(t * RATE);
  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
  if (t >= T.blackIn) return;

  // Draw order mirrors the Z stack in theme/modules/: subject, HUD, then the
  // corruption washes and marks, then the watcher above them, then the
  // finishing passes and the two story labels on top of everything.
  smoke(t);
  const state = skull(t);
  danglingEye(t, state);
  ignition(t, state);
  hud(t);
  glitch(t);
  bigBrother(t);
  finish(t);
  // Letter-spaced, as in 70-timing.script: it slows the eye down and stops
  // the words reading as a status line.
  label("S I G N A L   L O S T", cy + 345,
    hold(t, T.lostIn, T.lostOut) * flicker(tick, 11), FONTS.story, "#ebebeb");
  // Steady, not flickering: everything else has failed, and this has not.
  label("B I G   B R O T H E R   I S   W A T C H I N G", layout.bottom,
    ramp(t, T.watchText, T.watchText + 0.35) * (1 - ramp(t, T.watchOut - 0.08, T.watchOut)),
    FONTS.watch, "#ffffff");
}

function frame(now) {
  const delta = (now - last) / 1000;
  last = now;
  if (playing) elapsed = Math.min(elapsed + delta, T.end);
  if (playing && elapsed >= T.end) playing = false;

  render(elapsed);
  scrub.value = String(elapsed.toFixed(2));
  clock.textContent = `${elapsed.toFixed(2)} / ${T.end.toFixed(2)}`;
  toggle.textContent = playing ? "Pause" : "Play";
  requestAnimationFrame(frame);
}

function restart() {
  elapsed = 0;
  last = performance.now();
  playing = true;
}

replay.addEventListener("click", restart);
toggle.addEventListener("click", () => {
  if (!playing && elapsed >= T.end) restart();
  else playing = !playing;
});
scrub.addEventListener("input", () => {
  playing = false;
  elapsed = Number(scrub.value);
});
document.addEventListener("keydown", (event) => {
  if (event.key === "r") restart();
  if (event.key === " ") {
    event.preventDefault();
    playing = !playing;
  }
  if (event.key === "ArrowLeft") {
    playing = false;
    elapsed = clamp(elapsed - 1 / RATE, 0, T.end);
  }
  if (event.key === "ArrowRight") {
    playing = false;
    elapsed = clamp(elapsed + 1 / RATE, 0, T.end);
  }
});

Promise.all(Object.values(img).map((image) => image.decode().catch(() => {}))).then(() => {
  last = performance.now();
  requestAnimationFrame(frame);
});
