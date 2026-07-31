// Groups mirror the folders under assets/ and the inventory enforced by
// scripts/validate_assets.py.
const groups = {
  "GORE SKULL / SCREAM FRAMES": ["scream-00","scream-01","scream-02","skull-gore-approved"],
  "SKULL / LAYERS": ["skull","head","jaw","teeth","eye-sockets","eyes","eye-cores","cracks"],
  "BIG BROTHER / EYE": ["eye-surveillance","eye-high-contrast","eye-iris-mask","eye-pupil-mask","eye-target-red","eye-tracked","eye-corrupted","eye-signal-lost"],
  "SIGNAL / CORRUPTION": ["noise","noise-fine","noise-coarse","film-grain","scanlines","static-burst","static-burst-02","compression-blocks","compression-blocks-02","packet-loss","horizontal-tear","image-offset","rgb-split-red","rgb-split-white","signal-loss","signal-drop","data-mosh","vignette"],
  "ATMOSPHERE": ["smoke","smoke-02","dust-particles"],
  "SURVEILLANCE / HUD": ["brackets","tracking-brackets-tight","crosshair","target-lock","signal-bars-0","signal-bars-1","signal-bars-2","signal-bars-3","signal-bars-4","signal-bars-5","rec-indicator","telemetry-panel","status-panel","error-rate","frame-counter","packet-indicators","node-marker","monitoring-grid"]
};
const FOLDERS = {
  "GORE SKULL / SCREAM FRAMES": "skull",
  "SKULL / LAYERS": "skull",
  "BIG BROTHER / EYE": "eye",
  "SIGNAL / CORRUPTION": "effects",
  "ATMOSPHERE": "effects",
  "SURVEILLANCE / HUD": "hud"
};
const root = document.querySelector("#catalog");
for (const [title,names] of Object.entries(groups)) {
  const section=document.createElement("section");
  section.innerHTML=`<h2>${title}</h2><div class="grid"></div>`;
  const grid=section.querySelector(".grid");
  for(const name of names) {
    const figure=document.createElement("figure");
    figure.innerHTML=`<div class="checker"><img src="../assets/${FOLDERS[title]}/${name}.png" alt="" loading="lazy"></div><figcaption>${name}.png</figcaption>`;
    grid.append(figure);
  }
  root.append(section);
}
