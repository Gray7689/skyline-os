#!/usr/bin/env python3
"""Write SkyLine's four KDE color schemes and the default kdeglobals for new users.

Run from the repository root:  python3 tools/make-colors.py
Edit the palettes below to retheme every app, window and panel at once.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INC = ROOT / "config" / "includes.chroot"

COMMON_FG = dict(negative="#D2384B", neutral="#B86E0A", positive="#2E8B57")

PALETTES = {
    "Peach": dict(name="SkyLine Peach (sunrise)", text="#23264A", inactive="#6F6884",
                  window="#FFF1EC", window_alt="#FBE4DC", view="#FFFFFF", view_alt="#FFF5F1",
                  button="#FFE6DD", button_alt="#FFD8CC", header="#FFD8CC", header_alt="#FFCBBB",
                  header_inactive="#FFE6DD", tooltip="#FFF8F5", selection="#F4977E", selection_fg="#23264A",
                  focus="#E0694F", hover="#F4977E", link="#B5462E", visited="#8A4F9E", **COMMON_FG),
    "Sky": dict(name="SkyLine Sky (day)", text="#1F2A44", inactive="#5F6B86",
                window="#F1F8FF", window_alt="#E2F0FC", view="#FFFFFF", view_alt="#F5FAFF",
                button="#E3F1FF", button_alt="#CDEBFF", header="#CDEBFF", header_alt="#BFE3FF",
                header_inactive="#E3F1FF", tooltip="#F7FBFF", selection="#8FC9FF", selection_fg="#1F2A44",
                focus="#2F7BD9", hover="#6FB6F5", link="#1F64B8", visited="#6B4FB8", **COMMON_FG),
    "Dusk": dict(name="SkyLine Dusk (sunset)", text="#2A2350", inactive="#6E6690",
                 window="#F7F3FF", window_alt="#ECE5FF", view="#FFFFFF", view_alt="#FAF7FF",
                 button="#EDE6FF", button_alt="#E4DBFF", header="#E4DBFF", header_alt="#D8CCFF",
                 header_inactive="#EDE6FF", tooltip="#FBF9FF", selection="#C3B0FF", selection_fg="#2A2350",
                 focus="#7C5CE0", hover="#A891FF", link="#5B3CC4", visited="#9A3E8F", **COMMON_FG),
    "Night": dict(name="SkyLine Night", text="#EEF0FF", inactive="#A2A7CC",
                  window="#1A1D36", window_alt="#1F2342", view="#14172B", view_alt="#191C34",
                  button="#262A4F", button_alt="#2E3360", header="#23264A", header_alt="#1F2244",
                  header_inactive="#1D2040", tooltip="#23264A", selection="#FFB547", selection_fg="#14172B",
                  focus="#FFB547", hover="#FFC978", link="#8FC9FF", visited="#C3B0FF",
                  negative="#FF6B7A", neutral="#FFB547", positive="#6FD39A"),
}

EFFECTS = """[ColorEffects:Disabled]
Color=56,56,56
ColorAmount=0
ColorEffect=0
ContrastAmount=0.65
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
ChangeSelectionColor=true
Color=112,111,110
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=false
IntensityAmount=0
IntensityEffect=0
"""


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def group(title, p, bg, bg_alt, fg=None, fg_inactive=None):
    fg = fg or p["text"]
    fg_inactive = fg_inactive or p["inactive"]
    rows = dict(
        BackgroundAlternate=bg_alt, BackgroundNormal=bg,
        DecorationFocus=p["focus"], DecorationHover=p["hover"],
        ForegroundActive=p["focus"], ForegroundInactive=fg_inactive,
        ForegroundLink=p["link"], ForegroundNegative=p["negative"],
        ForegroundNeutral=p["neutral"], ForegroundNormal=fg,
        ForegroundPositive=p["positive"], ForegroundVisited=p["visited"])
    return f"[{title}]\n" + "".join(f"{k}={rgb(v)}\n" for k, v in rows.items())


def color_groups(p):
    dark = "#23264A" if p is not PALETTES["Night"] else "#0F1124"
    return "\n".join([
        group("Colors:Button", p, p["button"], p["button_alt"]),
        group("Colors:Complementary", p, dark, "#2E3360", fg="#EEF0FF", fg_inactive="#A2A7CC"),
        group("Colors:Header", p, p["header"], p["header_alt"]),
        group("Colors:Header][Inactive", p, p["header_inactive"], p["header_alt"]),
        group("Colors:Selection", p, p["selection"], p["selection"], fg=p["selection_fg"], fg_inactive=p["selection_fg"]),
        group("Colors:Tooltip", p, p["tooltip"], p["window_alt"]),
        group("Colors:View", p, p["view"], p["view_alt"]),
        group("Colors:Window", p, p["window"], p["window_alt"]),
    ])


def wm(p):
    return ("[WM]\n"
            f"activeBackground={rgb(p['header'])}\nactiveBlend={rgb(p['header'])}\n"
            f"activeForeground={rgb(p['text'])}\ninactiveBackground={rgb(p['header_inactive'])}\n"
            f"inactiveBlend={rgb(p['header_inactive'])}\ninactiveForeground={rgb(p['inactive'])}\n")


def main():
    out_dir = INC / "usr/share/color-schemes"
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, p in PALETTES.items():
        scheme_id = f"SkyLine{key}"
        text = (EFFECTS + "\n" + color_groups(p) + "\n"
                f"[General]\nColorScheme={scheme_id}\nName={p['name']}\nshadeSortColumn=true\n\n"
                "[KDE]\ncontrast=4\n\n" + wm(p))
        (out_dir / f"{scheme_id}.colors").write_text(text)

    # New users start on the sunrise palette; skyline-sky then follows the clock.
    skel = INC / "etc/skel/.config/kdeglobals"
    skel.parent.mkdir(parents=True, exist_ok=True)
    p = PALETTES["Peach"]
    skel.write_text(
        "[KDE]\nLookAndFeelPackage=org.skyline.desktop\nwidgetStyle=Breeze\n\n"
        "[General]\nColorScheme=SkyLinePeach\n\n"
        "[Icons]\nTheme=breeze\n\n" + color_groups(p) + "\n" + wm(p))
    print("SkyLine color schemes written.")


if __name__ == "__main__":
    main()
