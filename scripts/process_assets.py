#!/usr/bin/env python3
"""Build Plymouth-ready reusable layers from the original source asset."""

from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter
import random

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/source/skull-chroma.png"
EYE_SOURCE = ROOT / "assets/source/big-brother-eye-master.png"
GORE_SOURCE = ROOT / "assets/source/skull-gore-approved.png"
SCREAM_SOURCES = (
    ROOT / "assets/source/skull-scream-00-closed.png",
    ROOT / "assets/source/skull-scream-01-mid.png",
    ROOT / "assets/source/skull-scream-02-open.png",
)
SKULL = ROOT / "assets/skull/skull.png"
OUT_SKULL = ROOT / "assets/skull"
OUT_EYE = ROOT / "assets/eye"
OUT_FX = ROOT / "assets/effects"
OUT_HUD = ROOT / "assets/hud"
PREVIEW = ROOT / "preview"


def save_layer(source: Image.Image, path: Path, keep_from: int | None = None,
               keep_until: int | None = None) -> None:
    layer = source.copy()
    alpha = layer.getchannel("A")
    draw = ImageDraw.Draw(alpha)
    if keep_from is not None:
        draw.rectangle((0, 0, alpha.width, keep_from), fill=0)
    if keep_until is not None:
        draw.rectangle((0, keep_until, alpha.width, alpha.height), fill=0)
    layer.putalpha(alpha)
    layer.thumbnail((560, 560), Image.Resampling.LANCZOS)
    layer.save(path, optimize=True)


def transparent(size: tuple[int, int]) -> Image.Image:
    return Image.new("RGBA", size, (0, 0, 0, 0))


def fear_grade(image: Image.Image) -> Image.Image:
    """Apply one consistent oppressive grade without altering authored detail."""
    rgba = image.convert("RGBA")
    rgb = rgba.convert("RGB")
    rgb = ImageEnhance.Color(rgb).enhance(.62)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.28)
    rgb = ImageEnhance.Brightness(rgb).enhance(.72)

    # Narrow overhead exposure: readable crown, quickly falling face and edges.
    w, h = rgb.size
    light = Image.new("L", (w, h))
    pixels = light.load()
    for y in range(h):
        for x in range(w):
            dx = (x - w*.5) / (w*.52)
            dy = (y - h*.28) / (h*.70)
            radial = max(0.0, min(1.0, 1.0 - (dx*dx*.54 + dy*dy*.46)))
            floor = .48 + radial*.52
            pixels[x, y] = int(255 * floor)
    graded = ImageChops.multiply(rgb, Image.merge("RGB", (light, light, light)))
    result = graded.convert("RGBA")
    result.putalpha(rgba.getchannel("A"))
    return result


def build_contact_sheet() -> None:
    files = []
    for group in (OUT_SKULL, OUT_EYE, OUT_FX, OUT_HUD):
        files.extend(sorted(group.glob("*.png")))
    columns, cell_w, cell_h = 6, 200, 180
    rows = (len(files) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), (0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(files):
        image = Image.open(path).convert("RGBA")
        image.thumbnail((180, 130), Image.Resampling.LANCZOS)
        x, y = (index % columns) * cell_w, (index // columns) * cell_h
        tile = Image.new("RGBA", (190, 140), (10, 10, 10, 255))
        tile.alpha_composite(image, ((190-image.width)//2, (140-image.height)//2))
        sheet.paste(tile.convert("RGB"), (x, y))
        draw.text((x+7, y+148), path.stem, fill=(210, 210, 210))
    PREVIEW.mkdir(parents=True, exist_ok=True)
    sheet.save(PREVIEW / "asset-sheet.png", optimize=True)


def anatomical_layers(skull: Image.Image) -> None:
    """Produce separately addressable anatomy and surface-detail layers."""
    w, h = skull.size
    teeth = transparent((w, h))
    teeth.paste(skull, (0, 0), skull)
    mask = Image.new("L", (w, h))
    ImageDraw.Draw(mask).rounded_rectangle(
        (int(w*.34), int(h*.625), int(w*.67), int(h*.755)),
        radius=28, fill=255
    )
    teeth.putalpha(Image.composite(teeth.getchannel("A"), Image.new("L", (w, h)), mask))
    teeth.thumbnail((560, 560), Image.Resampling.LANCZOS)
    teeth.save(OUT_SKULL / "teeth.png", optimize=True)

    sockets = transparent((560, 560))
    d = ImageDraw.Draw(sockets)
    d.ellipse((186, 205, 272, 294), fill=(0, 0, 0, 225))
    d.ellipse((288, 205, 374, 294), fill=(0, 0, 0, 225))
    sockets = sockets.filter(ImageFilter.GaussianBlur(5))
    sockets.save(OUT_SKULL / "eye-sockets.png", optimize=True)

    cracks = transparent((560, 560))
    cd = ImageDraw.Draw(cracks)
    rng = random.Random(1729)
    for origin in ((280, 92), (202, 180), (365, 152)):
        x, y = origin
        points = [(x, y)]
        for _ in range(7):
            x += rng.randrange(-13, 14)
            y += rng.randrange(12, 31)
            points.append((x, y))
        cd.line(points, fill=(15, 15, 15, 150), width=1)
        branch = points[rng.randrange(2, 5)]
        cd.line((branch[0], branch[1], branch[0]+rng.randrange(-24,25),
                 branch[1]+rng.randrange(12,31)), fill=(20, 20, 20, 105), width=1)
    cracks.save(OUT_SKULL / "cracks.png", optimize=True)


def big_brother_eye_layers() -> None:
    """Build the surveillance-eye master, masks, target, and failure states."""
    source = Image.open(EYE_SOURCE).convert("L")
    source.thumbnail((1024, 576), Image.Resampling.LANCZOS)
    canvas = Image.new("L", (1024, 576))
    canvas.paste(source, ((1024-source.width)//2, (576-source.height)//2))
    master = Image.merge("RGBA", (canvas, canvas, canvas, Image.new("L", canvas.size, 255)))
    master.save(OUT_EYE / "eye-surveillance.png", optimize=True)

    high_l = canvas.point(lambda value: 0 if value < 36 else min(255, int((value-36)*1.42)))
    high = Image.merge("RGBA", (high_l, high_l, high_l, Image.new("L", canvas.size, 255)))
    high.save(OUT_EYE / "eye-high-contrast.png", optimize=True)

    iris = transparent((1024, 576))
    iris_alpha = Image.new("L", iris.size)
    ia = ImageDraw.Draw(iris_alpha)
    ia.ellipse((409, 169, 615, 375), fill=225)
    iris_alpha = iris_alpha.filter(ImageFilter.GaussianBlur(8))
    iris_rgb = Image.new("RGBA", iris.size, (255, 255, 255, 0))
    iris_rgb.putalpha(iris_alpha)
    iris_rgb.save(OUT_EYE / "eye-iris-mask.png", optimize=True)

    pupil = transparent((1024, 576))
    pu = ImageDraw.Draw(pupil)
    pu.ellipse((469, 229, 555, 315), fill=(0, 0, 0, 245))
    pupil.save(OUT_EYE / "eye-pupil-mask.png", optimize=True)

    target = transparent((1024, 576))
    ta = ImageDraw.Draw(target)
    ta.ellipse((499, 259, 525, 285), outline=(255, 0, 51, 245), width=2)
    ta.ellipse((508, 268, 516, 276), fill=(255, 0, 51, 255))
    ta.line((512, 222, 512, 251), fill=(255, 0, 51, 190), width=1)
    ta.line((512, 293, 512, 322), fill=(255, 0, 51, 190), width=1)
    ta.line((462, 272, 491, 272), fill=(255, 0, 51, 190), width=1)
    ta.line((533, 272, 562, 272), fill=(255, 0, 51, 190), width=1)
    target.save(OUT_EYE / "eye-target-red.png", optimize=True)

    hud = master.copy()
    hd = ImageDraw.Draw(hud)
    c = (255,255,255,145)
    for x,y,sx,sy in ((48,42,1,1),(976,42,-1,1),(48,534,1,-1),(976,534,-1,-1)):
        hd.line((x,y,x+sx*95,y), fill=c, width=2)
        hd.line((x,y,x,y+sy*70), fill=c, width=2)
    hd.line((512,72,512,148), fill=(255,255,255,70), width=1)
    hd.line((512,396,512,504), fill=(255,255,255,70), width=1)
    hud.alpha_composite(target)
    hud.save(OUT_EYE / "eye-tracked.png", optimize=True)

    corrupted = master.copy()
    rng = random.Random(8128)
    for _ in range(26):
        y = rng.randrange(20, 556)
        height = rng.randrange(2, 18)
        shift = rng.randrange(-85, 86)
        band = corrupted.crop((0, y, 1024, min(576, y+height)))
        corrupted.paste(band, (shift, y))
        if shift > 0:
            ImageDraw.Draw(corrupted).rectangle((0,y,shift,y+height), fill=(0,0,0,255))
        else:
            ImageDraw.Draw(corrupted).rectangle((1024+shift,y,1024,y+height), fill=(0,0,0,255))
    corrupted.save(OUT_EYE / "eye-corrupted.png", optimize=True)

    dim = canvas.point(lambda value: int(value*.14))
    lost = Image.merge("RGBA", (dim, dim, dim, Image.new("L", canvas.size, 255)))
    ld = ImageDraw.Draw(lost)
    for y in range(0, 576, 13):
        ld.rectangle((0, y, 1023, y+2), fill=(0,0,0,225))
    lost.save(OUT_EYE / "eye-signal-lost.png", optimize=True)


def approved_gore_skull() -> None:
    """Publish the approved hyper-real master at Plymouth runtime dimensions."""
    source = fear_grade(Image.open(GORE_SOURCE))
    source.thumbnail((560, 560), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (560, 560), (0, 0, 0, 255))
    canvas.alpha_composite(source, ((560-source.width)//2, (560-source.height)//2))
    canvas.save(OUT_SKULL / "skull-gore-approved.png", optimize=True)
    for index, path in enumerate(SCREAM_SOURCES):
        frame = fear_grade(Image.open(path))
        frame.thumbnail((560, 560), Image.Resampling.LANCZOS)
        output = Image.new("RGBA", (560, 560), (0, 0, 0, 255))
        output.alpha_composite(frame, ((560-frame.width)//2, (560-frame.height)//2))
        output.save(OUT_SKULL / f"scream-{index:02d}.png", optimize=True)


def main() -> None:
    OUT_SKULL.mkdir(parents=True, exist_ok=True)
    OUT_EYE.mkdir(parents=True, exist_ok=True)
    OUT_FX.mkdir(parents=True, exist_ok=True)
    OUT_HUD.mkdir(parents=True, exist_ok=True)
    skull = Image.open(SKULL).convert("RGBA")
    # The overlap hides the separation seam while allowing independent motion.
    split = int(skull.height * 0.665)
    save_layer(skull, OUT_SKULL / "head.png", keep_until=split + 38)
    save_layer(skull, OUT_SKULL / "jaw.png", keep_from=split - 32)
    anatomical_layers(skull)
    big_brother_eye_layers()
    approved_gore_skull()

    glow = Image.new("RGBA", (256, 128))
    gd = ImageDraw.Draw(glow)
    for x in (72, 184):
        gd.ellipse((x - 33, 31, x + 33, 97), fill=(255, 0, 51, 55))
        gd.ellipse((x - 18, 46, x + 18, 82), fill=(255, 0, 51, 210))
        gd.ellipse((x - 7, 57, x + 7, 71), fill=(255, 238, 242, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(5))
    glow.save(OUT_SKULL / "eyes.png", optimize=True)
    core = transparent((256, 128))
    core_draw = ImageDraw.Draw(core)
    for x in (72, 184):
        core_draw.ellipse((x-13, 51, x+13, 77), fill=(255, 0, 51, 255))
        core_draw.ellipse((x-4, 60, x+4, 68), fill=(255, 255, 255, 255))
    core.save(OUT_SKULL / "eye-cores.png", optimize=True)

    rng = random.Random(31991)
    noise = Image.new("RGBA", (512, 512))
    noise.putdata([(255, 255, 255, rng.randrange(0, 70)) for _ in range(512 * 512)])
    noise.save(OUT_FX / "noise.png", optimize=True)

    fine = transparent((512, 512))
    fine.putdata([(255, 255, 255, rng.randrange(0, 28)) for _ in range(512 * 512)])
    fine.save(OUT_FX / "noise-fine.png", optimize=True)

    coarse_small = Image.new("RGBA", (128, 128))
    coarse_small.putdata([
        (255, 255, 255, rng.choice((0, 0, 18, 35, 70)))
        for _ in range(128 * 128)
    ])
    coarse_small.resize((512, 512), Image.Resampling.NEAREST).save(
        OUT_FX / "noise-coarse.png", optimize=True
    )

    film = Image.new("RGBA", (1024, 1024))
    film.putdata([(255, 255, 255, rng.randrange(0, 34)) for _ in range(1024 * 1024)])
    film = film.filter(ImageFilter.GaussianBlur(.28)).resize(
        (512, 512), Image.Resampling.LANCZOS
    )
    film.save(OUT_FX / "film-grain.png", optimize=True)

    scan = transparent((8, 8))
    sd = ImageDraw.Draw(scan)
    sd.line((0, 1, 8, 1), fill=(255, 255, 255, 25))
    sd.line((0, 5, 8, 5), fill=(0, 0, 0, 80))
    scan.save(OUT_FX / "scanlines.png", optimize=True)

    smoke = Image.new("L", (1024, 1024))
    for count, radius_range, blur, strength in (
        (28, (70, 190), 72, (5, 18)),
        (65, (24, 90), 34, (3, 13)),
        (110, (8, 38), 15, (1, 8)),
    ):
        field = Image.new("L", smoke.size)
        field_draw = ImageDraw.Draw(field)
        for _ in range(count):
            x, y = rng.randrange(80, 944), rng.randrange(70, 954)
            radius = rng.randrange(*radius_range)
            field_draw.ellipse(
                (x-radius, y-radius, x+radius, y+radius),
                fill=rng.randrange(*strength),
            )
        field = field.filter(ImageFilter.GaussianBlur(blur))
        smoke = Image.blend(smoke, field, .72)
    smoke = smoke.resize((512, 512), Image.Resampling.LANCZOS)
    rgba = Image.new("RGBA", smoke.size, (210, 210, 210, 0))
    rgba.putalpha(smoke)
    rgba.save(OUT_FX / "smoke.png", optimize=True)
    rgba.transpose(Image.Transpose.FLIP_LEFT_RIGHT).rotate(
        7, resample=Image.Resampling.BICUBIC
    ).save(OUT_FX / "smoke-02.png", optimize=True)

    dust = transparent((512, 512))
    dd = ImageDraw.Draw(dust)
    for _ in range(180):
        x, y, r = rng.randrange(512), rng.randrange(512), rng.choice((1, 1, 1, 2))
        a = rng.randrange(18, 85)
        dd.ellipse((x-r, y-r, x+r, y+r), fill=(255, 255, 255, a))
    dust.save(OUT_FX / "dust-particles.png", optimize=True)

    static = transparent((512, 512))
    static.putdata([
        (255, 255, 255, rng.choice((0, 0, 0, 40, 90, 150, 220)))
        for _ in range(512 * 512)
    ])
    static.save(OUT_FX / "static-burst.png", optimize=True)
    static.transpose(Image.Transpose.FLIP_TOP_BOTTOM).rotate(
        90
    ).save(OUT_FX / "static-burst-02.png", optimize=True)

    blocks = transparent((512, 512))
    bld = ImageDraw.Draw(blocks)
    for _ in range(74):
        x, y = rng.randrange(0, 480), rng.randrange(0, 500)
        bw, bh = rng.randrange(10, 95), rng.choice((3, 5, 8, 13, 21))
        tone = rng.choice((26, 70, 128, 210, 255))
        bld.rectangle((x, y, min(511, x+bw), min(511, y+bh)),
                      fill=(tone, tone, tone, rng.randrange(45, 180)))
    blocks.save(OUT_FX / "compression-blocks.png", optimize=True)
    blocks.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(
        OUT_FX / "compression-blocks-02.png", optimize=True
    )

    packets = transparent((512, 512))
    pd = ImageDraw.Draw(packets)
    for row in range(13):
        y = 20 + row * 37
        for _ in range(rng.randrange(2, 7)):
            x = rng.randrange(0, 480)
            width = rng.randrange(8, 68)
            pd.rectangle((x, y, x+width, y+rng.choice((2, 3, 5))),
                         fill=(255, 255, 255, rng.randrange(55, 190)))
    packets.save(OUT_FX / "packet-loss.png", optimize=True)

    tear = transparent((512, 512))
    td = ImageDraw.Draw(tear)
    for _ in range(22):
        y = rng.randrange(20, 492)
        x = rng.randrange(0, 180)
        length = rng.randrange(90, 420)
        td.rectangle((x, y, min(511, x+length), y+rng.randrange(1, 6)),
                     fill=(255, 255, 255, rng.randrange(65, 210)))
    tear.save(OUT_FX / "horizontal-tear.png", optimize=True)

    offset = transparent((512, 512))
    od = ImageDraw.Draw(offset)
    for _ in range(15):
        y = rng.randrange(10, 490)
        height = rng.randrange(3, 20)
        displacement = rng.choice((-1, 1)) * rng.randrange(18, 86)
        x0 = max(0, displacement)
        x1 = min(511, 511 + displacement)
        od.rectangle((x0, y, x1, y+height),
                     fill=(255, 255, 255, rng.randrange(35, 130)))
    offset.save(OUT_FX / "image-offset.png", optimize=True)

    red_split = transparent((512, 512))
    rsd = ImageDraw.Draw(red_split)
    white_split = transparent((512, 512))
    wsd = ImageDraw.Draw(white_split)
    for _ in range(24):
        y, x, length = rng.randrange(512), rng.randrange(80), rng.randrange(80, 430)
        rsd.rectangle((x+8, y, x+length+8, y+3), fill=(255, 0, 51, 155))
        wsd.rectangle((x, y, x+length, y+3), fill=(255, 255, 255, 125))
    red_split.save(OUT_FX / "rgb-split-red.png", optimize=True)
    white_split.save(OUT_FX / "rgb-split-white.png", optimize=True)

    loss = transparent((512, 512))
    ld = ImageDraw.Draw(loss)
    ld.rectangle((0, 0, 511, 511), fill=(0, 0, 0, 218))
    for _ in range(38):
        y = rng.randrange(512)
        ld.rectangle((0, y, 511, y+rng.randrange(1, 5)),
                     fill=(255, 255, 255, rng.randrange(8, 50)))
    loss.save(OUT_FX / "signal-loss.png", optimize=True)

    drop = transparent((512, 512))
    dp = ImageDraw.Draw(drop)
    for y in range(0, 512, 16):
        alpha = rng.choice((0, 0, 0, 55, 120, 210))
        dp.rectangle((0, y, 511, y+rng.randrange(2, 14)),
                     fill=(0, 0, 0, alpha))
    for _ in range(9):
        y = rng.randrange(512)
        dp.rectangle((0, y, 511, min(511, y+rng.randrange(12, 55))),
                     fill=(0, 0, 0, rng.randrange(170, 246)))
    drop.save(OUT_FX / "signal-drop.png", optimize=True)

    mosh = transparent((512, 512))
    md = ImageDraw.Draw(mosh)
    for _ in range(96):
        x, y = rng.randrange(0, 496), rng.randrange(0, 496)
        size = rng.choice((4, 8, 12, 16, 24))
        color = rng.choice(((255,255,255,90), (255,0,51,115), (26,26,26,210)))
        md.rectangle((x, y, min(511,x+size*rng.randrange(1,5)), min(511,y+size)),
                     fill=color)
    mosh.save(OUT_FX / "data-mosh.png", optimize=True)

    vignette = transparent((512, 512))
    va = Image.new("L", (512, 512))
    vp = va.load()
    for y in range(512):
        for x in range(512):
            dx, dy = (x-255.5)/255.5, (y-255.5)/255.5
            edge = max(0.0, min(1.0, (dx*dx + dy*dy - .22) / .78))
            vp[x, y] = int(225 * edge * edge)
    vignette.putalpha(va)
    vignette.save(OUT_FX / "vignette.png", optimize=True)

    brackets = Image.new("RGBA", (640, 640))
    bd = ImageDraw.Draw(brackets)
    c, m, length = (255, 255, 255, 170), 25, 70
    for x, y, sx, sy in ((m,m,1,1),(615,m,-1,1),(m,615,1,-1),(615,615,-1,-1)):
        bd.line((x, y, x + sx*length, y), fill=c, width=2)
        bd.line((x, y, x, y + sy*length), fill=c, width=2)
    brackets.save(OUT_HUD / "brackets.png", optimize=True)

    crosshair = transparent((256, 256))
    ch = ImageDraw.Draw(crosshair)
    ch.ellipse((59, 59, 197, 197), outline=(255, 255, 255, 145), width=2)
    ch.ellipse((111, 111, 145, 145), outline=(255, 0, 51, 200), width=2)
    ch.line((128, 20, 128, 104), fill=(255, 255, 255, 155), width=2)
    ch.line((128, 152, 128, 236), fill=(255, 255, 255, 155), width=2)
    ch.line((20, 128, 104, 128), fill=(255, 255, 255, 155), width=2)
    ch.line((152, 128, 236, 128), fill=(255, 255, 255, 155), width=2)
    crosshair.save(OUT_HUD / "crosshair.png", optimize=True)

    for level in range(6):
        bars = transparent((180, 48))
        bar_draw = ImageDraw.Draw(bars)
        for index in range(6):
            height = 8 + index * 6
            active = index < level
            color = (255, 255, 255, 210 if active else 45)
            bar_draw.rectangle((12+index*25, 42-height, 27+index*25, 42), fill=color)
        bars.save(OUT_HUD / f"signal-bars-{level}.png", optimize=True)

    rec = transparent((150, 44))
    rd = ImageDraw.Draw(rec)
    rd.rectangle((1, 1, 148, 42), outline=(255, 255, 255, 100), width=1)
    rd.ellipse((18, 15, 30, 27), fill=(255, 0, 51, 255))
    rd.line((43, 21, 118, 21), fill=(255, 255, 255, 175), width=2)
    rec.save(OUT_HUD / "rec-indicator.png", optimize=True)

    telemetry = transparent((420, 180))
    tel = ImageDraw.Draw(telemetry)
    tel.rectangle((1, 1, 418, 178), outline=(255, 255, 255, 110), width=1)
    for y, width in ((28,190), (54,330), (80,265), (132,145), (154,290)):
        tel.rectangle((24, y, 24+width, y+3), fill=(255,255,255,105))
    tel.rectangle((24, 105, 376, 109), fill=(255,255,255,35))
    for x in range(24, 377, 14):
        tel.rectangle((x, 104, x+rng.randrange(3,11), 110),
                      fill=(255,255,255,rng.randrange(80,190)))
    telemetry.save(OUT_HUD / "telemetry-panel.png", optimize=True)

    indicator = transparent((320, 52))
    ind = ImageDraw.Draw(indicator)
    for i in range(16):
        x = 8+i*19
        color = (255,0,51,210) if i in (4, 11) else (255,255,255,rng.randrange(50,170))
        ind.rectangle((x, 16, x+12, 34), fill=color)
    indicator.save(OUT_HUD / "packet-indicators.png", optimize=True)

    node = transparent((128, 128))
    nd = ImageDraw.Draw(node)
    nd.rectangle((25,25,103,103), outline=(255,255,255,130), width=1)
    nd.line((64,8,64,48), fill=(255,255,255,150), width=1)
    nd.line((64,80,64,120), fill=(255,255,255,150), width=1)
    nd.line((8,64,48,64), fill=(255,255,255,150), width=1)
    nd.line((80,64,120,64), fill=(255,255,255,150), width=1)
    nd.ellipse((59,59,69,69), fill=(255,0,51,235))
    node.save(OUT_HUD / "node-marker.png", optimize=True)

    grid = transparent((512, 512))
    gr = ImageDraw.Draw(grid)
    for n in range(32, 512, 32):
        gr.line((n, 0, n, 511), fill=(255,255,255,22), width=1)
        gr.line((0, n, 511, n), fill=(255,255,255,22), width=1)
    gr.line((256,0,256,511), fill=(255,255,255,65), width=1)
    gr.line((0,256,511,256), fill=(255,255,255,65), width=1)
    grid.save(OUT_HUD / "monitoring-grid.png", optimize=True)

    tight = transparent((420, 420))
    ti = ImageDraw.Draw(tight)
    color = (255,255,255,185)
    for x,y,sx,sy in ((12,12,1,1),(408,12,-1,1),(12,408,1,-1),(408,408,-1,-1)):
        ti.line((x,y,x+sx*54,y),fill=color,width=2)
        ti.line((x,y,x,y+sy*54),fill=color,width=2)
    tight.save(OUT_HUD / "tracking-brackets-tight.png", optimize=True)

    frame = transparent((280, 64))
    fr = ImageDraw.Draw(frame)
    fr.rectangle((1,1,278,62), outline=(255,255,255,95), width=1)
    for index in range(24):
        x = 14+index*10
        height = 18 if index % 5 == 0 else 9
        fr.line((x,44-height,x,44), fill=(255,255,255,120), width=1)
    fr.rectangle((14,49,177,52), fill=(255,255,255,80))
    fr.rectangle((183,49,245,52), fill=(255,0,51,170))
    frame.save(OUT_HUD / "frame-counter.png", optimize=True)

    error = transparent((360, 112))
    er = ImageDraw.Draw(error)
    er.rectangle((1,1,358,110), outline=(255,255,255,90), width=1)
    baseline = 82
    points = []
    for index in range(30):
        x = 15+index*11
        y = baseline-rng.randrange(2, 18)
        if index in (9,10,21): y = baseline-rng.randrange(39,67)
        points.append((x,y))
    er.line(points, fill=(255,255,255,155), width=2)
    for x,y in points:
        if y < baseline-35:
            er.ellipse((x-2,y-2,x+2,y+2), fill=(255,0,51,230))
    error.save(OUT_HUD / "error-rate.png", optimize=True)

    status = transparent((420, 224))
    st = ImageDraw.Draw(status)
    st.rectangle((1,1,418,222), outline=(255,255,255,100), width=1)
    st.rectangle((18,18,155,21), fill=(255,255,255,130))
    for row in range(4):
        y = 49+row*31
        st.rectangle((18,y,99,y+3), fill=(255,255,255,80))
        st.rectangle((122,y,360-rng.randrange(0,90),y+3),
                     fill=(255,255,255,rng.randrange(90,180)))
    st.rectangle((18,183,386,187), fill=(255,255,255,35))
    st.rectangle((18,183,277,187), fill=(255,0,51,150))
    status.save(OUT_HUD / "status-panel.png", optimize=True)

    lock = transparent((256, 256))
    lk = ImageDraw.Draw(lock)
    lk.arc((35,35,221,221), 205, 335, fill=(255,255,255,145), width=2)
    lk.arc((35,35,221,221), 25, 155, fill=(255,255,255,145), width=2)
    lk.rectangle((116,116,140,140), outline=(255,0,51,220), width=2)
    for x,y in ((128,18),(128,238),(18,128),(238,128)):
        lk.ellipse((x-2,y-2,x+2,y+2), fill=(255,255,255,175))
    lock.save(OUT_HUD / "target-lock.png", optimize=True)
    build_contact_sheet()


if __name__ == "__main__":
    main()
