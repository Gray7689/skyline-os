#!/usr/bin/env python3
"""Render every SkyLine image (wallpapers, icons, boot and installer art).

Run from the repository root:  python3 tools/make-assets.py
Needs: rsvg-convert (librsvg2-bin) and Pillow.
All artwork is drawn here as SVG, so you can tweak colors and re-run.
"""
import os
import random
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
INC = ROOT / "config" / "includes.chroot"
OUT_ASSETS = ROOT / "assets"

# One palette per time of day. The same names are used by the color schemes and skyline-sky.
MOODS = {
    "Peach": dict(  # sunrise
        sky="#FFD8CC", body="#FFF0B8", body_kind="sun", sun_xy=(2960, 620), sun_r=190,
        cloud="#FFFFFF", cloud_op=0.95, hill_back="#FFC3B2", hill_front="#FFAD96",
        city="#4A4E7A", window="#FFD8CC", lit="#FFF0B8", lit_ratio=0.12,
        sparkle="#FFFFFF", sparkles=9, stars=0),
    "Sky": dict(  # day
        sky="#CDEBFF", body="#FFE48A", body_kind="sun", sun_xy=(2960, 520), sun_r=200,
        cloud="#FFFFFF", cloud_op=0.97, hill_back="#B5E8C9", hill_front="#8FD9AE",
        city="#4A5A8A", window="#CDEBFF", lit="#FFE48A", lit_ratio=0.04,
        sparkle="#FFFFFF", sparkles=6, stars=0),
    "Dusk": dict(  # sunset
        sky="#E4DBFF", body="#FFB8A0", body_kind="sun", sun_xy=(2900, 1020), sun_r=260,
        cloud="#FFFFFF", cloud_op=0.85, hill_back="#D3C6FF", hill_front="#BFAEFF",
        city="#4E3F7A", window="#E4DBFF", lit="#FFD9A8", lit_ratio=0.30,
        sparkle="#FFFFFF", sparkles=10, stars=0),
    "Night": dict(
        sky="#1B2150", body="#FFF0C2", body_kind="moon", sun_xy=(2960, 560), sun_r=170,
        cloud="#2B3266", cloud_op=0.9, hill_back="#262C5E", hill_front="#151838",
        city="#0C0F24", window="#1B2150", lit="#FFC85C", lit_ratio=0.45,
        sparkle="#FFFFFF", sparkles=12, stars=150),
}

W, H = 3840, 2160
BASE_Y = 1900  # building bottoms; hidden behind the front hill


def sparkle(x, y, s, fill, op=1.0):
    return (f'<path d="M{x} {y-s} Q{x} {y} {x+s} {y} Q{x} {y} {x} {y+s} '
            f'Q{x} {y} {x-s} {y} Q{x} {y} {x} {y-s} Z" fill="{fill}" opacity="{op}"/>')


def cloud(cx, cy, s, fill, op):
    return (f'<g fill="{fill}" opacity="{op}">'
            f'<circle cx="{cx-0.9*s:.0f}" cy="{cy:.0f}" r="{0.55*s:.0f}"/>'
            f'<circle cx="{cx-0.25*s:.0f}" cy="{cy-0.35*s:.0f}" r="{0.75*s:.0f}"/>'
            f'<circle cx="{cx+0.5*s:.0f}" cy="{cy-0.05*s:.0f}" r="{0.6*s:.0f}"/>'
            f'<rect x="{cx-1.45*s:.0f}" y="{cy:.0f}" width="{2.55*s:.0f}" height="{0.5*s:.0f}" rx="{0.25*s:.0f}"/>'
            f'</g>')


def buildings():
    """A fixed, hand-tuned-by-seed row of rounded buildings with one tall tower."""
    rnd = random.Random(7)
    out = []
    x = 560
    while x < 3260:
        w = rnd.randint(130, 230)
        h = rnd.randint(430, 860)
        out.append(dict(x=x, w=w, h=h, cap=rnd.random() < 0.3, tower=False))
        x += w + rnd.choice([0, 10, 18, 26])
    # the tall tower in the middle, like the logo
    mid = min(range(len(out)), key=lambda i: abs(out[i]["x"] + out[i]["w"] / 2 - 1920))
    out[mid].update(w=max(out[mid]["w"], 210), h=1240, tower=True, cap=True)
    return out


def wallpaper_svg(m):
    rnd = random.Random(11)
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    p.append('<defs><mask id="moon"><rect width="100%" height="100%" fill="#fff"/>'
             f'<circle cx="{m["sun_xy"][0]+80}" cy="{m["sun_xy"][1]-60}" r="{m["sun_r"]*0.9:.0f}" fill="#000"/></mask></defs>')
    p.append(f'<rect width="{W}" height="{H}" fill="{m["sky"]}"/>')
    # stars
    for _ in range(m["stars"]):
        sx, sy = rnd.randint(40, W - 40), rnd.randint(40, 1350)
        p.append(f'<circle cx="{sx}" cy="{sy}" r="{rnd.uniform(2, 5):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.35, 1):.2f}"/>')
    # sun or moon
    sx, sy = m["sun_xy"]
    r = m["sun_r"]
    if m["body_kind"] == "sun":
        p.append(f'<circle cx="{sx}" cy="{sy}" r="{r*1.55:.0f}" fill="{m["body"]}" opacity="0.25"/>')
        p.append(f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="{m["body"]}"/>')
    else:
        p.append(f'<circle cx="{sx}" cy="{sy}" r="{r*1.6:.0f}" fill="{m["body"]}" opacity="0.08"/>')
        p.append(f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="{m["body"]}" mask="url(#moon)"/>')
    # clouds
    for cx, cy, s in [(700, 520, 120), (1700, 330, 90), (3420, 1000, 110), (2330, 760, 70)]:
        p.append(cloud(cx, cy, s, m["cloud"], m["cloud_op"]))
    # sparkles
    spots = [(420, 900), (1180, 640), (1460, 980), (2120, 480), (2600, 300), (3560, 380),
             (3300, 760), (900, 260), (2480, 1100), (240, 420), (3700, 640), (1980, 1050)]
    for i in range(m["sparkles"]):
        x, y = spots[i % len(spots)]
        p.append(sparkle(x, y, 26 if i % 3 else 38, m["sparkle"], 0.9))
    # back hills
    for cx, cy, rx, ry in [(300, 1820, 1100, 330), (3500, 1800, 1150, 360), (1900, 1880, 1500, 260)]:
        p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{m["hill_back"]}"/>')
    # city
    for b in buildings():
        x, w, h = b["x"], b["w"], b["h"]
        top = BASE_Y - h
        p.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h+40}" rx="30" fill="{m["city"]}"/>')
        if b["cap"]:
            cw = w * 0.55
            p.append(f'<rect x="{x+(w-cw)/2:.0f}" y="{top-70}" width="{cw:.0f}" height="110" rx="24" fill="{m["city"]}"/>')
        if b["tower"]:
            p.append(f'<rect x="{x+w/2-9:.0f}" y="{top-260}" width="18" height="230" rx="9" fill="{m["city"]}"/>')
            p.append(f'<circle cx="{x+w/2:.0f}" cy="{top-262}" r="16" fill="{m["lit"]}"/>')
        # windows
        cols = max(1, int((w - 40) // 48))
        offset = (w - (cols * 26 + (cols - 1) * 22)) / 2
        y = top + 56
        while y < 1700:
            for c in range(cols):
                wx = x + offset + c * 48
                lit = rnd.random() < m["lit_ratio"]
                fill, op = (m["lit"], 1) if lit else (m["window"], 0.22)
                p.append(f'<rect x="{wx:.0f}" y="{y}" width="26" height="34" rx="8" fill="{fill}" opacity="{op}"/>')
            y += 64
    # front hill
    p.append(f'<path d="M0 1800 C 700 1660, 1300 1700, 1920 1740 S 3200 1680, {W} 1780 L{W} {H} L0 {H} Z" fill="{m["hill_front"]}"/>')
    p.append('</svg>')
    return "\n".join(p)


SKYLINE_PATH = ("M27 66 A6 6 0 0 1 33 60 L43 60 A6 6 0 0 0 49 54 L49 36 A6 6 0 0 1 55 30 "
                "L65 30 A6 6 0 0 1 71 36 L71 40 A6 6 0 0 0 77 46 L87 46 A6 6 0 0 1 93 52 "
                "L93 82 A6 6 0 0 1 87 88 L33 88 A6 6 0 0 1 27 82 Z")


def icon_svg(full=True, rounded=True):
    """The SkyLine logo: navy skyline on a peach sky. full=False drops clouds/sparkles for tiny sizes."""
    rx = 26 if rounded else 0
    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">',
         '<defs><clipPath id="c"><rect width="120" height="120" rx="%d"/></clipPath></defs>' % rx,
         '<g clip-path="url(#c)">',
         '<rect width="120" height="120" fill="#FFD8CC"/>',
         '<circle cx="92" cy="26" r="9" fill="#FFF0B8"/>']
    if full:
        p += ['<g fill="#FFFFFF">',
              '<circle cx="20" cy="29" r="5"/><circle cx="26" cy="25.5" r="6.5"/><circle cx="32" cy="29" r="5"/>',
              '<rect x="15" y="29" width="22" height="5" rx="2.5"/>',
              '<circle cx="101" cy="64" r="3.5"/><circle cx="105.5" cy="61.5" r="4.5"/><circle cx="110" cy="64" r="3.5"/>',
              '<rect x="97.5" y="64" width="16" height="3.5" rx="1.75"/>',
              '<path d="M40 41.5 Q40 44 42.5 44 Q40 44 40 46.5 Q40 44 37.5 44 Q40 44 40 41.5 Z"/>',
              '<path d="M76 16 Q76 18 78 18 Q76 18 76 20 Q76 18 74 18 Q76 18 76 16 Z"/>',
              '</g>',
              '<ellipse cx="10" cy="90" rx="26" ry="12" fill="#FFC3B2"/>',
              '<ellipse cx="108" cy="90" rx="30" ry="15" fill="#FFC3B2"/>']
    p += [f'<path fill="#23264A" d="{SKYLINE_PATH}"/>',
          '<path fill="#FFAD96" d="M0 90 C25 80 45 82 60 84 S100 80 120 88 L120 120 L0 120 Z"/>',
          '</g></svg>']
    return "".join(p)


def bar_svg(w, h, color):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">'
            f'<rect width="{w}" height="{h}" rx="{h/2}" fill="{color}"/></svg>')


def render(svg_text, out_png, width=None, height=None):
    out_png.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["rsvg-convert", "-f", "png", "-o", str(out_png)]
    if width:
        cmd += ["-w", str(width)]
    if height:
        cmd += ["-h", str(height)]
    subprocess.run(cmd, input=svg_text.encode(), check=True)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def cover(src, size, out, fmt="PNG"):
    """Scale-and-crop an image to exactly `size`, centered."""
    im = Image.open(src).convert("RGB")
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left, top = (im.width - tw) // 2, (im.height - th) // 2
    im = im.crop((left, top, left + tw, top + th))
    out.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "JPEG":
        im.save(out, fmt, quality=90)
    else:
        im.save(out, fmt, optimize=True)


def main():
    os.chdir(ROOT)
    wp_root = INC / "usr/share/wallpapers"
    for name, mood in MOODS.items():
        pkg = wp_root / f"SkyLine-{name}"
        big = pkg / "contents/images/3840x2160.png"
        render(wallpaper_svg(mood), big)
        cover(big, (1920, 1080), pkg / "contents/images/1920x1080.png")
        cover(big, (400, 225), pkg / "contents/screenshot.png")
        write(pkg / "metadata.json",
              '{\n  "KPlugin": {\n    "Authors": [{"Name": "SkyLine"}],\n'
              f'    "Id": "SkyLine-{name}",\n    "License": "CC-BY-SA-4.0",\n'
              f'    "Name": "SkyLine {name}"\n  }}\n}}\n')

    peach = wp_root / "SkyLine-Peach/contents/images/3840x2160.png"
    night = wp_root / "SkyLine-Night/contents/images/3840x2160.png"

    # Icons and logos
    write(INC / "usr/share/icons/hicolor/scalable/apps/skyline.svg", icon_svg(full=False))
    for size in (16, 22, 24, 32, 48, 64, 128, 256):
        render(icon_svg(full=size >= 64), INC / f"usr/share/icons/hicolor/{size}x{size}/apps/skyline.png", size, size)
    write(INC / "usr/share/pixmaps/skyline-logo.svg", icon_svg(full=True))
    render(icon_svg(full=True), INC / "usr/share/pixmaps/skyline-logo.png", 256, 256)

    # Look-and-feel (global theme) previews and splash logo
    laf = INC / "usr/share/plasma/look-and-feel/org.skyline.desktop/contents"
    cover(peach, (400, 225), laf / "previews/preview.png")
    cover(peach, (1920, 1080), laf / "previews/fullscreenpreview.jpg", "JPEG")
    write(laf / "splash/images/logo.svg", icon_svg(full=True))

    # Plymouth boot splash
    ply = INC / "usr/share/plymouth/themes/skyline"
    render(icon_svg(full=True), ply / "logo.png", 200, 200)
    render(bar_svg(240, 8, "#FFC3B2"), ply / "bar-bg.png")
    render(bar_svg(240, 8, "#23264A"), ply / "bar-fill.png")

    # Installer (Calamares) branding
    cal = INC / "etc/calamares/branding/skyline"
    render(icon_svg(full=True), cal / "logo.png", 256, 256)
    cover(peach, (800, 400), cal / "welcome.png")
    for i, name in enumerate(["Peach", "Sky", "Night"], start=1):
        cover(wp_root / f"SkyLine-{name}/contents/images/3840x2160.png", (800, 450), cal / f"slide{i}.png")

    # Live USB boot menu background (dark so the white menu text stays readable)
    cover(night, (640, 480), OUT_ASSETS / "boot-splash.png")
    print("SkyLine assets rendered.")


if __name__ == "__main__":
    main()
