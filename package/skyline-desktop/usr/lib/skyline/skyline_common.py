"""Shared helpers for SkyLine's apps (SkyLine Settings and the SkyLine Assistant).

Everything here calls the same command-line tools a user can run (skyline-sky, skyline-layout, ...),
so the apps, the Assistant and the terminal always agree.
"""
import json
import os
import re
import shlex
import shutil
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

from skyline_i18n import tr

# SKYLINE_DATA_ROOT lets developers run the apps from the repository without installing.
DATA_ROOT = Path(os.environ.get("SKYLINE_DATA_ROOT", "/"))
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "skyline"
STATE_DIR = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))) / "skyline"
WALLPAPERS = DATA_ROOT / "usr/share/wallpapers"
PREVIEWS = DATA_ROOT / "usr/share/skyline/previews"
LOGO = str(DATA_ROOT / "usr/share/skyline/logo.png")

VERSION_FALLBACK = "1.3.0"

APPS = {  # id: (name, short description)
    "claude": ("Claude", tr("AI assistant by Anthropic")),
    "discord": ("Discord", tr("Chat with friends and servers")),
    "steam": ("Steam", tr("Your game library")),
    "sober": (tr("Roblox player"), tr("Sober, unofficial")),
    "vinegar": ("Roblox Studio", tr("Vinegar, unofficial")),
    "prism": ("Minecraft", "Prism Launcher"),
    "spotify": ("Spotify", tr("Music")),
    "vscode": ("Visual Studio Code", tr("Code editor")),
    "obs": ("OBS Studio", tr("Record and stream")),
}

FLATPAK_IDS = {
    "discord": "com.discordapp.Discord",
    "steam": "com.valvesoftware.Steam",
    "sober": "org.vinegarhq.Sober",
    "vinegar": "org.vinegarhq.Vinegar",
    "prism": "org.prismlauncher.PrismLauncher",
    "spotify": "com.spotify.Client",
    "vscode": "com.visualstudio.code",
    "obs": "com.obsproject.Studio",
}


def installed_apps():
    """Set of SkyLine app ids that are already installed."""
    found = set()
    code, out = run("flatpak", "list", "--app", "--columns=application", timeout=20)
    if code == 0:
        have = set(out.split())
        found |= {k for k, v in FLATPAK_IDS.items() if v in have}
    code, out = run("dpkg-query", "-W", "-f=${Status}", "claude-desktop", timeout=10)
    if code == 0 and "install ok installed" in out:
        found.add("claude")
    return found


SKIES = {
    "auto": tr("Follow the time of day"),
    "sunrise": tr("Sunrise"),
    "day": tr("Day"),
    "dusk": tr("Dusk"),
    "night": tr("Night"),
}
SKY_WALLPAPER = {"sunrise": "SkyLine-Peach", "day": "SkyLine-Sky", "dusk": "SkyLine-Dusk", "night": "SkyLine-Night"}

LAYOUTS = {
    "classic": tr("Classic: one bar at the bottom"),
    "dock": tr("Dock: top bar and an app dock"),
    "minimal": tr("Minimal: one small floating bar"),
    "shell": tr("SkyLine Shell: top bar and a dock with Puff"),
}

TASKBARS = {
    "auto": tr("Follows the sky"),
    "black": tr("Black"),
    "white": tr("White"),
    "glass": tr("Glass (see-through)"),
    "clear": tr("Clear (invisible)"),
}

ACCENTS = {
    "none": None,
    "coral": "#E0694F",
    "sky": "#2F7BD9",
    "lavender": "#7C5CE0",
    "mint": "#2E9E6E",
    "sun": "#E6A21B",
    "pink": "#D9488F",
}
ACCENT_NAMES = {"none": tr("Sky"), "coral": tr("Coral"), "sky": tr("Blue"), "lavender": tr("Lavender"), "mint": tr("Mint"),
                "sun": tr("Sun yellow"), "pink": tr("Pink")}

STEAM_NATIVE_OPTION = "skyline-play %command%"
STEAM_FLATPAK_OPTION = ("__NV_PRIME_RENDER_OFFLOAD=1 __VK_LAYER_NV_optimus=NVIDIA_only "
                        "__GLX_VENDOR_LIBRARY_NAME=nvidia %command%")


# ---------------------------------------------------------------- settings files

def read_kv(path):
    """Read a simple key=value file (lines starting with # are comments)."""
    values = {}
    try:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()
    except OSError:
        pass
    return values


def sky_settings():
    s = read_kv(CONFIG_DIR / "sky.conf")
    s.setdefault("mode", "auto")
    s.setdefault("weather", "off")
    s.setdefault("accent", "none")
    return s


def taskbar_style():
    return read_kv(CONFIG_DIR / "taskbar.conf").get("style", "auto")


def current_layout():
    return read_kv(CONFIG_DIR / "layout.conf").get("layout", "classic")


def gamemode_on():
    return (STATE_DIR / "gamemode-on").exists()


# ---------------------------------------------------------------- running things

def start(*cmd):
    """Start a program in the background. Returns False if it couldn't start."""
    try:
        subprocess.Popen(list(cmd), start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False


def run(*cmd, timeout=180):
    """Run a program and wait. Returns (exit code, output)."""
    try:
        p = subprocess.run(list(cmd), capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def in_terminal(*cmd):
    """Run something in a Konsole window so the user sees what happens."""
    return start("konsole", "--hold", "-e", *cmd)


def skyline_version():
    code, out = run("dpkg-query", "-W", "-f=${Version}", "skyline-desktop", timeout=10)
    return out if code == 0 and out else VERSION_FALLBACK


def nvidia_status():
    """'none' (no NVIDIA card), 'missing' (card but no driver) or 'ok: <name>'."""
    code, out = run("lspci", timeout=10)
    if code != 0 or "nvidia" not in out.lower():
        return "none"
    if not shutil.which("nvidia-smi"):
        return "missing"
    code, out = run("nvidia-smi", "-L", timeout=15)
    if code != 0:
        return "missing"
    name = out.splitlines()[0].split(":", 1)[-1].split("(UUID")[0].strip() if out else "NVIDIA"
    return "ok: " + name


# ---------------------------------------------------------------- weather place lookup

def geocode(name):
    """Find a city with Open-Meteo. Returns (lat, lon, label) or None."""
    url = ("https://geocoding-api.open-meteo.com/v1/search?count=1&format=json&name="
           + urllib.parse.quote(name))
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.load(r)
    results = data.get("results") or []
    if not results:
        return None
    first = results[0]
    label = ", ".join(x for x in (first.get("name"), first.get("country")) if x)
    return float(first["latitude"]), float(first["longitude"]), label


# ---------------------------------------------------------------- opening apps by name

APP_DIRS = [
    Path("/usr/share/applications"),
    Path.home() / ".local/share/applications",
    Path("/var/lib/flatpak/exports/share/applications"),
    Path.home() / ".local/share/flatpak/exports/share/applications",
]

SHORTCUTS = {
    "settings": ["skyline-settings"],
    "skyline settings": ["skyline-settings"],
    "apps": ["skyline-apps"],
    "store": ["plasma-discover"],
    "discover": ["plasma-discover"],
    "terminal": ["konsole"],
    "konsole": ["konsole"],
    "files": ["dolphin"],
    "file manager": ["dolphin"],
    "browser": ["x-www-browser"],
    "system settings": ["systemsettings"],
}
SHORTCUTS_IT = {"impostazioni": "settings", "negozio": "store", "file": "files", "cartelle": "files",
                "gestore file": "files", "browser": "browser", "impostazioni di sistema": "system settings",
                "terminale": "terminal"}


def _desktop_entries():
    for d in APP_DIRS:
        if d.is_dir():
            yield from sorted(d.glob("*.desktop"))


def _parse_desktop(path):
    entry, in_main = {}, False
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("["):
                in_main = line.strip() == "[Desktop Entry]"
                continue
            if in_main and "=" in line:
                k, v = line.split("=", 1)
                entry.setdefault(k.strip(), v.strip())
    except OSError:
        pass
    return entry


def open_app(query):
    """Open an app by a friendly name ("files", "discord", "steam"...). Returns a message."""
    q = query.strip().lower()
    q = SHORTCUTS_IT.get(q, q)
    if q in SHORTCUTS:
        return (tr("Opening {app}.") if start(*SHORTCUTS[q]) else tr("I couldn't open {app}.")).format(app=query)
    best = None
    for path in _desktop_entries():
        e = _parse_desktop(path)
        if e.get("Type") != "Application" or e.get("NoDisplay", "").lower() == "true" or "Exec" not in e:
            continue
        name = e.get("Name", "").lower()
        if q == name:
            best = e
            break
        if best is None and (q in name or q in e.get("Keywords", "").lower()):
            best = e
    if not best:
        return tr("I couldn't find an app called {app}.").format(app=query)
    cmd = [part for part in shlex.split(best["Exec"]) if not re.fullmatch(r"%[a-zA-Z]", part)]
    if start(*cmd):
        return tr("Opening {app}.").format(app=best.get("Name", query))
    return tr("I couldn't open {app}.").format(app=query)


# ---------------------------------------------------------------- actions (shared by Settings and the Assistant)

def set_sky(mode):
    if mode not in SKIES:
        return tr("I don't know the sky '{name}'.").format(name=mode)
    start("skyline-sky", mode)
    if mode == "auto":
        return tr("Your sky now follows the time of day.")
    return tr("Sky set to {name}.").format(name=SKIES[mode].lower())


def keep_own_wallpaper(on):
    start("skyline-sky", "wallpaper", "mine" if on else "auto")
    return (tr("Got it: I'll never change your wallpaper, only the colors.") if on
            else tr("SkyLine may change the wallpaper again when you pick a sky."))


def set_layout(name):
    if name not in LAYOUTS:
        return tr("I don't know the layout '{name}'.").format(name=name)
    start("skyline-layout", name)
    return tr("Switching to the {name} layout.").format(name=LAYOUTS[name].split(":")[0])


def set_taskbar(style):
    if style not in TASKBARS:
        return tr("I don't know the taskbar style '{name}'.").format(name=style)
    start("skyline-taskbar", style)
    return tr("Taskbar set to: {name}. The desktop blinks for a second while it changes.").format(
        name=TASKBARS[style].lower())


def set_gamemode(on):
    start("skyline-gamemode", "on" if on else "off")
    return tr("Game Mode is on: maximum performance, notifications muted.") if on else tr("Game Mode is off.")


def set_weather(on, place=None):
    msg = ""
    if place:
        try:
            found = geocode(place)
        except OSError:
            return tr("I couldn't look up that place. Check your internet connection.")
        if not found:
            return tr("I couldn't find {place}.").format(place=place)
        lat, lon, label = found
        run("skyline-sky", "place", f"{lat:.4f}", f"{lon:.4f}", label, timeout=60)
        msg = tr("Weather place set to {place}.").format(place=label) + " "
    start("skyline-sky", "weather", "on" if on else "off")
    return msg + (tr("Your sky now shows the real weather.") if on else tr("Weather effects are off."))


def set_accent(name_or_hex):
    value = ACCENTS.get(name_or_hex, name_or_hex)
    if value is None or value == "none":
        start("skyline-sky", "accent", "none")
        return tr("Accent color now matches the sky.")
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", str(value)):
        return tr("I don't know the color '{name}'.").format(name=name_or_hex)
    start("skyline-sky", "accent", value)
    return tr("Accent color set to {name}.").format(name=ACCENT_NAMES.get(name_or_hex, name_or_hex))


def update_skyline():
    in_terminal("skyline-update", "install")
    return tr("Checking for a new SkyLine version in a terminal window. If there is one, it installs it "
              "(it may ask for your password).")


def install_apps(ids):
    wanted = [i for i in ids if i in APPS or i == "nvidia"]
    if not wanted:
        return tr("I don't know those apps. I can install: {apps}.").format(
            apps=", ".join(v[0] for v in APPS.values()))
    in_terminal("/usr/lib/skyline/install-apps", *wanted)
    names = [APPS[i][0] if i in APPS else tr("the NVIDIA driver") for i in wanted]
    return tr("Installing {apps} in a terminal window. It may ask for your password.").format(
        apps=", ".join(names))
