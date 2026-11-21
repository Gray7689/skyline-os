"""SkyLine translations.

English is written in the code. Other languages live in /usr/share/skyline/l10n/<lang>.json,
a plain {"English text": "translated text"} map that anyone can edit or extend.

The language is KDE's own setting (System Settings > Region & Language, or SkyLine's setup),
so SkyLine and the rest of the desktop always agree.

    tr("Hello")                      -> "Ciao" when the desktop is in Italian
    python3 skyline_i18n.py "Hello"  -> the same, for shell scripts
    python3 skyline_i18n.py --lang   -> "it"
"""
import json
import os
import pwd
import subprocess
import sys
from pathlib import Path

DATA_ROOT = Path(os.environ.get("SKYLINE_DATA_ROOT", "/"))
L10N_DIR = DATA_ROOT / "usr/share/skyline/l10n"
LANGUAGES = {"en": "English", "it": "Italiano"}


def _home():
    """The desktop user's home, also when a tool runs as root through pkexec or sudo."""
    if os.getuid() == 0:
        uid = os.environ.get("PKEXEC_UID")
        user = os.environ.get("SUDO_USER")
        try:
            if uid:
                return Path(pwd.getpwuid(int(uid)).pw_dir)
            if user:
                return Path(pwd.getpwnam(user).pw_dir)
        except (KeyError, ValueError):
            pass
    return Path.home()


def _config_dir():
    if os.getuid() == 0 and (os.environ.get("PKEXEC_UID") or os.environ.get("SUDO_USER")):
        return _home() / ".config"
    return Path(os.environ.get("XDG_CONFIG_HOME", str(_home() / ".config")))


def _short(value):
    value = (value or "").split(":")[0].split(".")[0].split("@")[0]
    value = value.split("_")[0].split("-")[0].lower()
    return "" if value in ("c", "posix") else value


def language():
    """Two-letter language code: KDE's language setting first, then the environment."""
    forced = os.environ.get("SKYLINE_LANG")
    if forced:
        return _short(forced) or "en"
    try:
        section = ""
        for line in (_config_dir() / "plasma-localerc").read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("["):
                section = line
            elif section == "[Translations]" and line.startswith("LANGUAGE="):
                found = _short(line.split("=", 1)[1])
                if found:
                    return found
    except OSError:
        pass
    for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        found = _short(os.environ.get(var, ""))
        if found:
            return found
    return "en"


_table = None


def _load():
    global _table
    if _table is None:
        _table = {}
        lang = language()
        if lang != "en":
            try:
                _table = json.loads((L10N_DIR / f"{lang}.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                _table = {}
    return _table


def tr(text):
    """Translate English `text` into the desktop's language (unchanged if there's no translation)."""
    return _load().get(text) or text


def reload():
    """Forget the cached table, after the language changed."""
    global _table
    _table = None


def set_language(lang):
    """Switch the whole desktop's language (KDE apps follow after logging out and back in)."""
    if lang not in LANGUAGES:
        return False
    def kw(group, key, value):
        cmd = ["kwriteconfig6", "--file", "plasma-localerc", "--group", group, "--key", key]
        try:
            subprocess.run(cmd + ([value] if value else ["--delete"]), timeout=10,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (OSError, subprocess.TimeoutExpired):
            pass
    if lang == "en":
        kw("Translations", "LANGUAGE", "en_US")
        kw("Formats", "LANG", "")
    else:
        kw("Translations", "LANGUAGE", f"{lang}:en_US")
        # Dates and numbers too, if this computer has the locale.
        try:
            have = subprocess.run(["locale", "-a"], capture_output=True, text=True, timeout=10).stdout.lower()
        except (OSError, subprocess.TimeoutExpired):
            have = ""
        full = {"it": "it_IT"}.get(lang, lang)
        if f"{full.lower()}.utf8" in have:
            kw("Formats", "LANG", f"{full}.UTF-8")
    os.environ.pop("SKYLINE_LANG", None)
    os.environ["LANGUAGE"] = f"{lang}:en_US" if lang != "en" else "en_US"
    reload()
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--lang":
        print(language())
    elif len(sys.argv) > 1:
        sys.stdout.write(tr(sys.argv[1]))
