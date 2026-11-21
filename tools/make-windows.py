#!/usr/bin/env python3
"""Write SkyLine's window style: four Aurorae window decorations (one per sky) with three round
buttons (close, minimize, maximize) like little colored dots.

Run from the repository root:  python3 tools/make-windows.py
Output: package/skyline-desktop/usr/share/aurorae/themes/SkyLine-<Mood>/

Aurorae draws window frames from SVG "frame" pieces (topleft, top, ... center). The frame here is
painted at 2x with Pillow and sliced into those pieces, so it stays sharp on HiDPI screens; the
buttons are plain vector circles.
"""
import base64
import importlib.util
import io
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "package/skyline-desktop/usr/share/aurorae/themes"

spec = importlib.util.spec_from_file_location("make_colors", ROOT / "tools/make-colors.py")
colors = importlib.util.module_from_spec(spec)
spec.loader.exec_module(colors)
PALETTES = colors.PALETTES

# Geometry, in pixels at 1x.
PAD = 12                    # shadow around the window
BORDER = 3                  # visible frame left/right/bottom
RADIUS = 10                 # rounded top corners
EDGE_TOP, TITLE, EDGE_BOTTOM = 7, 20, 7
TITLE_BAND = EDGE_TOP + TITLE + EDGE_BOTTOM
BUTTON = 20                 # button box; the dot inside is 13 px
DOT = 13
S = 2                       # render scale

DOTS = {  # button: (color, symbol)
    "close": ("#FF6F61", "close"),
    "minimize": ("#FFBE3D", "minimize"),
    "maximize": ("#4CC38A", "maximize"),
    "restore": ("#4CC38A", "restore"),
}


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def frame_image(fill, border, shadow_alpha, w=120, h=110):
    """The whole window frame (shadow + title + border) at scale S, RGBA."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if shadow_alpha:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(sh)
        d.rounded_rectangle((PAD * S, (PAD + 2) * S, W - PAD * S, H - (PAD - 2) * S),
                            radius=RADIUS * S, fill=(15, 17, 40, shadow_alpha))
        sh = sh.filter(ImageFilter.GaussianBlur(5 * S))
        img.alpha_composite(sh)
    win = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(win)
    box = (PAD * S, PAD * S, W - PAD * S - 1, H - PAD * S - 1)
    d.rounded_rectangle(box, radius=RADIUS * S, fill=hex_rgb(border) + (255,))
    inner = (box[0] + S, box[1] + S, box[2] - S, box[3] - S)
    d.rounded_rectangle(inner, radius=(RADIUS - 1) * S, fill=hex_rgb(fill) + (255,))
    # square bottom corners: the app's own content is square there
    d.rectangle((box[0], H - PAD * S - RADIUS * S, box[2], box[3]), fill=hex_rgb(border) + (255,))
    d.rectangle((inner[0], H - PAD * S - RADIUS * S, inner[2], inner[3]), fill=hex_rgb(fill) + (255,))
    img.alpha_composite(win)
    return img


def png_uri(im):
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def slices(img, left, top, right, bottom):
    """Cut a frame image into Plasma's nine frame pieces: name -> (x, y, w, h) at 1x and the image."""
    W, H = img.size[0] // S, img.size[1] // S
    xs = [(0, left), (left, W - right), (W - right, W)]
    ys = [(0, top), (top, H - bottom), (H - bottom, H)]
    names = [["topleft", "top", "topright"], ["left", "center", "right"],
             ["bottomleft", "bottom", "bottomright"]]
    out = {}
    for r, (y0, y1) in enumerate(ys):
        for c, (x0, x1) in enumerate(xs):
            # edges and the center are uniform, so a narrow strip is enough (it gets stretched)
            if c == 1:
                x0, x1 = x0 + (x1 - x0) // 2, x0 + (x1 - x0) // 2 + 4
            if r == 1:
                y0, y1 = y0 + (y1 - y0) // 2, y0 + (y1 - y0) // 2 + 4
            piece = img.crop((x0 * S, y0 * S, x1 * S, y1 * S))
            out[names[r][c]] = (x1 - x0, y1 - y0, piece)
    return out


def frame_svg_elements(prefix, pieces):
    parts, x = [], 0
    for name, (w, h, im) in pieces.items():
        parts.append(f'  <image id="{prefix}-{name}" x="{x}" y="0" width="{w}" height="{h}" '
                     f'preserveAspectRatio="none" xlink:href="{png_uri(im)}"/>')
        x += w + 2
    return parts


def decoration_svg(p):
    # The side pieces are wide enough to hold the rounded corner; the part past the visible border
    # sits under the window's content, so nobody sees it.
    side = PAD + RADIUS
    pieces = {}
    for state, fill, border, alpha in [
            ("decoration", p["header"], p["header_alt"], 95),
            ("decoration-inactive", p["header_inactive"], p["header_alt"], 55)]:
        img = frame_image(fill, border, alpha)
        pieces[state] = slices(img, side, PAD + TITLE_BAND, side, PAD + BORDER)
    # Maximized windows: a flat title band, no shadow, no side borders.
    for state, fill in [("decoration-maximized", p["header"]), ("decoration-maximized-inactive", p["header_inactive"])]:
        band = Image.new("RGBA", (12 * S, (TITLE_BAND + 2) * S), hex_rgb(fill) + (255,))
        pieces[state] = slices(band, 1, TITLE_BAND, 1, 1)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
             'width="400" height="400" version="1.1">']
    for prefix, pcs in pieces.items():
        lines.append(f'  <g id="{prefix}">')
        lines += frame_svg_elements(prefix, pcs)
        lines.append("  </g>")
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def symbol(kind, cx, cy, color):
    r = 3.0
    w = 'stroke="%s" stroke-width="1.6" stroke-linecap="round" fill="none"' % color
    if kind == "close":
        return (f'<path d="M{cx - r},{cy - r} L{cx + r},{cy + r} M{cx + r},{cy - r} L{cx - r},{cy + r}" {w}/>')
    if kind == "minimize":
        return f'<path d="M{cx - r - 0.5},{cy} L{cx + r + 0.5},{cy}" {w}/>'
    if kind == "maximize":
        return f'<path d="M{cx - r - 0.5},{cy} L{cx + r + 0.5},{cy} M{cx},{cy - r - 0.5} L{cx},{cy + r + 0.5}" {w}/>'
    return (f'<path d="M{cx - r},{cy + 0.5} L{cx},{cy - r + 0.5} L{cx + r},{cy + 0.5} M{cx - r},{cy + r} '
            f'L{cx + r},{cy + r}" {w}/>')  # restore: a small "up" chevron over a line


def button_svg(kind, p, night):
    color, sym = DOTS[kind]
    idle = "#4A4F7E" if night else "#D8CBC6" if p is PALETTES["Peach"] else "#C9D3E0"
    ink = "#14172B"
    c = BUTTON / 2
    rad = DOT / 2

    def dot(fill, with_symbol, ring=None):
        ring_attr = f' stroke="{ring}" stroke-width="1"' if ring else ""
        body = f'<circle cx="{c}" cy="{c}" r="{rad}" fill="{fill}"{ring_attr}/>'
        if with_symbol:
            body += symbol(sym, c, c, ink)
        return body

    states = {
        "active": dot(color, False),
        "hover": dot(color, True),
        "pressed": dot(darker(color), True),
        "inactive": dot(idle, False),
        "hover-inactive": dot(color, True),
        "pressed-inactive": dot(darker(color), True),
        "deactivated": dot(idle, False),
        "deactivated-inactive": dot(idle, False),
    }
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<svg xmlns="http://www.w3.org/2000/svg" width="{BUTTON * 9}" height="{BUTTON}" version="1.1">']
    for i, (state, body) in enumerate(states.items()):
        lines.append(f'  <g id="{state}-center" transform="translate({i * BUTTON},0)">'
                     f'<rect width="{BUTTON}" height="{BUTTON}" fill="none" stroke="none"/>{body}</g>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def darker(h):
    r, g, b = hex_rgb(h)
    return "#%02X%02X%02X" % (int(r * 0.82), int(g * 0.82), int(b * 0.82))


def rc(p):
    def c(h):
        return ",".join(str(v) for v in hex_rgb(h))
    return f"""[General]
ActiveTextColor={c(p["text"])}
InactiveTextColor={c(p["inactive"])}
TitleAlignment=Center
TitleVerticalAlignment=Center
Animation=150
ActiveTextShadowColor=0,0,0,0
InactiveTextShadowColor=0,0,0,0
UseTextShadow=false
Shadow=false
DecorationPosition=0

[Layout]
BorderLeft={BORDER}
BorderRight={BORDER}
BorderBottom={BORDER}
TitleEdgeTop={EDGE_TOP}
TitleEdgeBottom={EDGE_BOTTOM}
TitleEdgeLeft=10
TitleEdgeRight=10
TitleEdgeTopMaximized={EDGE_TOP}
TitleEdgeBottomMaximized={EDGE_BOTTOM}
TitleEdgeLeftMaximized=10
TitleEdgeRightMaximized=10
TitleBorderLeft=8
TitleBorderRight=8
TitleHeight={TITLE}
ButtonWidth={BUTTON}
ButtonHeight={BUTTON}
ButtonSpacing=2
ButtonMarginTop=0
ExplicitButtonSpacer=10
PaddingTop={PAD}
PaddingBottom={PAD}
PaddingLeft={PAD}
PaddingRight={PAD}
"""


def main():
    for mood, p in PALETTES.items():
        name = f"SkyLine-{mood}"
        d = OUT / name
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        night = mood == "Night"
        (d / "decoration.svg").write_text(decoration_svg(p))
        for kind in DOTS:
            (d / f"{kind}.svg").write_text(button_svg(kind, p, night))
        (d / f"{name}rc").write_text(rc(p))
        (d / "metadata.desktop").write_text(
            "[Desktop Entry]\n"
            f"Name=SkyLine {mood}\n"
            "Comment=SkyLine window style: three round buttons\n"
            "X-KDE-PluginInfo-Author=SkyLine\n"
            f"X-KDE-PluginInfo-Name={name}\n"
            "X-KDE-PluginInfo-Version=1.3\n"
            "X-KDE-PluginInfo-License=GPL-2.0-or-later\n"
            "X-KDE-ServiceTypes=KWin/Decoration\n")
        print("wrote", d.relative_to(ROOT))


if __name__ == "__main__":
    main()
