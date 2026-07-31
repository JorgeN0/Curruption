#!/usr/bin/env python3
"""Fail the build when the theme cannot render from the assets in the tree.

Four independent checks:

1. every required production asset exists and is a usable RGBA layer;
2. every Image("...") path the Plymouth modules load actually resolves;
3. the approved hyper-real artwork is still the immutable source reference;
4. the layer geometry hard-coded in 30-skull.script still matches the artwork.

Check 4 is the one that matters after any asset change: the dangling eye is
cut out of the scream frames at runtime, and that cut is only invisible while
the seam column stays in shadow and the right-hand margin stays black.
"""

import re
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
MODULES = ROOT / "theme/modules"
CONCEPT = ROOT / "preview/concepts/skull-hyperreal-approved.png"
APPROVED_SOURCE = ASSETS / "source/skull-gore-approved.png"
APPROVED_RUNTIME = ASSETS / "skull/skull-gore-approved.png"
FRAMES = ("scream-00", "scream-01", "scream-02")

REQUIRED = {
    "skull": (
        "skull", "skull-gore-approved", "scream-00", "scream-01",
        "scream-02", "head", "jaw", "teeth", "eye-sockets", "eyes",
        "eye-cores", "cracks",
    ),
    "eye": (
        "eye-surveillance", "eye-high-contrast", "eye-iris-mask",
        "eye-pupil-mask", "eye-target-red", "eye-tracked",
        "eye-corrupted", "eye-signal-lost",
    ),
    "effects": (
        "smoke", "smoke-02", "noise", "noise-fine", "noise-coarse",
        "film-grain", "scanlines", "dust-particles", "static-burst",
        "static-burst-02", "compression-blocks", "compression-blocks-02",
        "packet-loss", "horizontal-tear", "image-offset", "rgb-split-red",
        "rgb-split-white", "signal-loss", "signal-drop", "data-mosh",
        "vignette",
    ),
    "hud": (
        "brackets", "tracking-brackets-tight", "crosshair", "target-lock",
        "signal-bars-0", "signal-bars-1", "signal-bars-2", "signal-bars-3",
        "signal-bars-4", "signal-bars-5", "rec-indicator", "telemetry-panel",
        "status-panel", "error-rate", "frame-counter", "packet-indicators",
        "node-marker", "monitoring-grid",
    ),
}

IMAGE_CALL = re.compile(r'Image\(\s*"([^"]+)"\s*\)')
GEOMETRY = re.compile(
    r"Skull\.(SRC|EYE_COL|BULB_TOP|BULB_RIGHT|BULB_BOTTOM)\s*=\s*(\d+)\s*;"
)

# The seam the eye column is cut along must stay in shadow, and the margin the
# inboard slide uncovers must stay black. Measured in the shipped frames: seam
# mean 36-39 of 255, margin max 28 of 255.
SEAM_LIMIT = 70
MARGIN_LIMIT = 45
SLIDE = 4  # master pixels of inboard travel the runtime allows


def check_inventory(failures: list[str]) -> int:
    count = 0
    for group, names in REQUIRED.items():
        for name in names:
            count += 1
            path = ASSETS / group / f"{name}.png"
            if not path.is_file():
                failures.append(f"missing: {path.relative_to(ROOT)}")
                continue
            with Image.open(path) as image:
                if image.mode != "RGBA":
                    failures.append(f"not RGBA: {path.relative_to(ROOT)}")
                elif image.getchannel("A").getextrema()[1] == 0:
                    failures.append(f"empty alpha: {path.relative_to(ROOT)}")
    return count


def check_runtime_references(failures: list[str]) -> int:
    count = 0
    for module in sorted(MODULES.glob("*.script")):
        for reference in IMAGE_CALL.findall(module.read_text(encoding="utf-8")):
            count += 1
            if not (ASSETS / reference).is_file():
                failures.append(f"{module.name} loads a missing asset: {reference}")
    if count == 0:
        failures.append("no Image() references found in theme/modules/")
    return count


def check_concept_immutable(failures: list[str]) -> None:
    for path in (CONCEPT, APPROVED_SOURCE, APPROVED_RUNTIME, ASSETS / "skull/scream-00.png"):
        if not path.is_file():
            failures.append(f"missing: {path.relative_to(ROOT)}")
            return
    if CONCEPT.read_bytes() != APPROVED_SOURCE.read_bytes():
        failures.append(
            "assets/source/skull-gore-approved.png no longer matches "
            "preview/concepts/skull-hyperreal-approved.png; the approved concept "
            "is an immutable source reference"
        )
    if APPROVED_RUNTIME.read_bytes() != (ASSETS / "skull/scream-00.png").read_bytes():
        failures.append(
            "assets/skull/scream-00.png must be the closed-jaw approved skull, "
            "byte-identical to assets/skull/skull-gore-approved.png"
        )


def read_geometry(failures: list[str]) -> dict[str, int]:
    module = MODULES / "30-skull.script"
    values = {
        key: int(value)
        for key, value in GEOMETRY.findall(module.read_text(encoding="utf-8"))
    }
    expected = {"SRC", "EYE_COL", "BULB_TOP", "BULB_RIGHT", "BULB_BOTTOM"}
    if expected - values.keys():
        failures.append(
            "30-skull.script is missing geometry constants: "
            + ", ".join(sorted(expected - values.keys()))
        )
        return {}
    return values


def mean_max_luma(image: Image.Image, box: tuple[int, int, int, int]):
    """Mean and peak of the brightest channel, which is what reads as 'lit'."""
    red, green, blue = image.crop(box).convert("RGB").split()
    peak = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    return ImageStat.Stat(peak).mean[0], peak.getextrema()[1]


def check_layer_geometry(failures: list[str]) -> None:
    geometry = read_geometry(failures)
    if not geometry:
        return
    src = geometry["SRC"]

    bounds = (
        ("EYE_COL < BULB_RIGHT", geometry["EYE_COL"] < geometry["BULB_RIGHT"]),
        ("BULB_RIGHT <= SRC", geometry["BULB_RIGHT"] <= src),
        ("BULB_TOP < BULB_BOTTOM", geometry["BULB_TOP"] < geometry["BULB_BOTTOM"]),
        ("BULB_BOTTOM <= SRC", geometry["BULB_BOTTOM"] <= src),
        ("EYE_COL > SLIDE", geometry["EYE_COL"] > SLIDE),
    )
    for label, ok in bounds:
        if not ok:
            failures.append(f"30-skull.script geometry violates {label}")
    if failures:
        return

    for name in FRAMES:
        path = ASSETS / "skull" / f"{name}.png"
        if not path.is_file():
            failures.append(f"missing: {path.relative_to(ROOT)}")
            continue
        with Image.open(path) as image:
            if image.size != (src, src):
                failures.append(
                    f"{path.relative_to(ROOT)} is {image.size[0]}x{image.size[1]}, "
                    f"but 30-skull.script cuts a {src}x{src} master"
                )
                continue
            if image.getchannel("A").getextrema()[0] != 255:
                failures.append(
                    f"{path.relative_to(ROOT)} must be fully opaque: the runtime "
                    "lays opaque tiles over it"
                )
            copy = image.copy()

        seam_mean, _ = mean_max_luma(
            copy,
            (geometry["EYE_COL"] - 2, geometry["BULB_TOP"],
             geometry["EYE_COL"] + 2, geometry["BULB_BOTTOM"]),
        )
        if seam_mean > SEAM_LIMIT:
            failures.append(
                f"{name}: dangling-eye seam at x={geometry['EYE_COL']} is too bright "
                f"({seam_mean:.0f}/255); the mandible and the eyeball are no longer "
                "separated there"
            )
        _, margin_max = mean_max_luma(
            copy,
            (geometry["BULB_RIGHT"] - SLIDE, geometry["BULB_TOP"],
             geometry["BULB_RIGHT"], geometry["BULB_BOTTOM"]),
        )
        if margin_max > MARGIN_LIMIT:
            failures.append(
                f"{name}: the {SLIDE}px margin inside x={geometry['BULB_RIGHT']} is "
                f"not black (peak {margin_max}/255); sliding the eye column inboard "
                "would uncover artwork"
            )


def main() -> None:
    failures: list[str] = []
    assets = check_inventory(failures)
    references = check_runtime_references(failures)
    check_concept_immutable(failures)
    config = (ROOT / "config/theme.conf").read_text(encoding="utf-8")
    if "dangling_eye_enabled=1" in config:
        check_layer_geometry(failures)
    if failures:
        print("\n".join(failures), file=sys.stderr)
        raise SystemExit(1)
    print(
        f"Validated {assets} required production assets, {references} runtime asset "
        "references and the immutable hyper-real source. Gore-skull crop "
        "geometry is checked when independent dangling-eye motion is enabled."
    )


if __name__ == "__main__":
    main()
