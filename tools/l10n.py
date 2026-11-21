#!/usr/bin/env python3
"""SkyLine translation helper.

    python3 tools/l10n.py check      list text that has no Italian yet (exit 1 if any)
    python3 tools/l10n.py wrap       wrap known English text in the Python apps with tr(...)
    python3 tools/l10n.py mo         build the .mo files the Plasma widgets (QML i18n) read
    python3 tools/l10n.py strings    print every translatable string found

The translations live in package/skyline-desktop/usr/share/skyline/l10n/<lang>.json:
{"English text": "translated text"}. Python apps use tr("..."), shell tools t "..." / tf "...",
Plasma widgets i18n("...").
"""
import ast
import io
import json
import re
import struct
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "package/skyline-desktop"
L10N = PKG / "usr/share/skyline/l10n"
PY_FILES = [PKG / "usr/bin" / n for n in ("skyline-settings", "skyline-assistant", "skyline-setup")] + \
    [PKG / "usr/lib/skyline" / n for n in ("skyline_common.py", "skyline_ai.py", "skyline_qt.py")]
SH_FILES = [p for p in (PKG / "usr/bin").iterdir() if p.is_file() and p.read_bytes()[:40].find(b"sh") > 0 and
            b"python" not in p.read_bytes()[:40]] + \
    [PKG / "usr/lib/skyline" / n for n in ("install-apps", "install-nvidia", "ensure-nonfree", "install-claude")]
QML_DIRS = [PKG / "usr/share/plasma/plasmoids"]
LANGS = ["it"]


def load(lang):
    return json.loads((L10N / f"{lang}.json").read_text(encoding="utf-8"))


def string_groups(source):
    """Yield (start, end, value) for runs of adjacent plain string literals (no f-strings)."""
    toks = list(tokenize.generate_tokens(io.StringIO(source).readline))
    i = 0
    while i < len(toks):
        if toks[i].type == tokenize.STRING:
            j = i
            parts = []
            ok = True
            while j < len(toks) and toks[j].type in (tokenize.STRING, tokenize.NL, tokenize.COMMENT):
                if toks[j].type == tokenize.STRING:
                    if re.match(r"(?i)^[rbu]*f", toks[j].string):
                        ok = False
                    parts.append(toks[j])
                j += 1
            # trim trailing NL/COMMENT
            last = max(k for k in range(i, j) if toks[k].type == tokenize.STRING)
            if ok:
                try:
                    value = "".join(ast.literal_eval(t.string) for t in parts)
                    if isinstance(value, str):
                        yield toks[i], toks[last], value, toks[i - 1] if i else None
                except (ValueError, SyntaxError):
                    pass
            i = last + 1
        else:
            i += 1


def py_tr_strings(source):
    found = set()
    for start, end, value, prev in string_groups(source):
        if prev is not None and prev.string == "(":
            # look two tokens back for tr
            pass
    for m in re.finditer(r"\btr\(\s*((?:\"(?:[^\"\\]|\\.)*\"\s*)+)\)", source):
        try:
            found.add(ast.literal_eval("(" + m.group(1) + ")"))
        except (ValueError, SyntaxError):
            pass
    return found


def sh_strings(source):
    found = set()
    for m in re.finditer(r'(?<![\w-])tf? "((?:[^"\\]|\\.)*)"', source):
        found.add(m.group(1).replace('\\"', '"').replace("\\\\", "\\"))
    return found


def qml_strings(source):
    found = set()
    for m in re.finditer(r'\bi18n(p?)\(\s*"((?:[^"\\]|\\.)*)"(?:\s*,\s*"((?:[^"\\]|\\.)*)")?', source):
        found.add(m.group(2).replace('\\"', '"'))
        if m.group(1) and m.group(3):
            found.add(m.group(3).replace('\\"', '"'))
    return found


def all_strings():
    out = {}
    for f in PY_FILES:
        for s in py_tr_strings(f.read_text()):
            out.setdefault(s, set()).add(f.name)
        # page titles in the setup are translated at display time
        if f.name == "skyline-setup":
            for m in re.finditer(r'^    title = "(.*)"$', f.read_text(), re.M):
                out.setdefault(m.group(1), set()).add(f.name)
    for f in SH_FILES:
        for s in sh_strings(f.read_text()):
            out.setdefault(s, set()).add(f.name)
    for d in QML_DIRS:
        for f in d.rglob("*.qml"):
            for s in qml_strings(f.read_text()):
                out.setdefault(s, set()).add(f.parent.parent.parent.name)
    return out


def wrap(table):
    """Wrap string groups whose value is a known English key with tr(...)."""
    changed = 0
    for f in PY_FILES:
        src = f.read_text()
        lines = src.splitlines(keepends=True)
        offsets = [0]
        for line in lines:
            offsets.append(offsets[-1] + len(line))
        edits = []
        for start, end, value, prev in string_groups(src):
            if value not in table:
                continue
            a = offsets[start.start[0] - 1] + start.start[1]
            b = offsets[end.end[0] - 1] + end.end[1]
            if src[max(0, a - 3):a].endswith("tr("):
                continue
            # never translate config names: "--group", "Icons" / "--key", "Theme"
            if re.search(r'"--(group|key|file)",\s*$', src[max(0, a - 40):a]):
                continue
            # nor dictionary keys or values compared with ==
            if re.match(r"\s*:", src[b:b + 3]) or re.search(r"(==|!=)\s*$", src[max(0, a - 5):a]):
                continue
            edits.append((a, b))
        for a, b in sorted(edits, reverse=True):
            src = src[:a] + "tr(" + src[a:b] + ")" + src[b:]
            changed += 1
        f.write_text(src)
    return changed


def write_mo(table, path):
    """Minimal GNU .mo writer (what msgfmt makes)."""
    keys = sorted(k for k in table if table[k])
    ids = b"".join(k.encode() + b"\0" for k in keys)
    strs = b"".join(table[k].encode() + b"\0" for k in keys)
    header_entry = ("", "Content-Type: text/plain; charset=UTF-8\nPlural-Forms: nplurals=2; plural=(n != 1);\n")
    entries = [header_entry] + [(k, table[k]) for k in keys]
    n = len(entries)
    o_ids = 7 * 4
    o_strs = o_ids + n * 8
    data_start = o_strs + n * 8
    id_blob, str_blob = b"", b""
    id_tab, str_tab = [], []
    for k, v in entries:
        kb = k.encode()
        id_tab.append((len(kb), data_start + len(id_blob)))
        id_blob += kb + b"\0"
    str_start = data_start + len(id_blob)
    for k, v in entries:
        vb = v.encode()
        str_tab.append((len(vb), str_start + len(str_blob)))
        str_blob += vb + b"\0"
    out = struct.pack("<7I", 0x950412DE, 0, n, o_ids, o_strs, 0, 0)
    for length, off in id_tab:
        out += struct.pack("<2I", length, off)
    for length, off in str_tab:
        out += struct.pack("<2I", length, off)
    out += id_blob + str_blob
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out)
    del ids, strs


def plural_pairs(source):
    pairs = []
    for m in re.finditer(r'\bi18np\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"', source):
        pairs.append((m.group(1), m.group(2)))
    return pairs


def build_mo():
    for lang in LANGS:
        table = load(lang)
        for widget in sorted((PKG / "usr/share/plasma/plasmoids").iterdir()):
            src = "\n".join(f.read_text() for f in widget.rglob("*.qml"))
            wanted = {s: table[s] for s in qml_strings(src) if s in table}
            # plural entries: msgid "one\0many" -> "uno\0tanti"
            for one, many in plural_pairs(src):
                if one in table and many in table:
                    wanted.pop(one, None)
                    wanted.pop(many, None)
                    wanted[one + "\0" + many] = table[one] + "\0" + table[many]
            out = PKG / f"usr/share/locale/{lang}/LC_MESSAGES/plasma_applet_{widget.name}.mo"
            write_mo(wanted, out)
            print(f"wrote {out.relative_to(ROOT)} ({len(wanted)} strings)")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "strings":
        for s, where in sorted(all_strings().items()):
            print(f"{s!r}  <- {', '.join(sorted(where))}")
    elif cmd == "wrap":
        print("wrapped", wrap(load("it")), "strings")
    elif cmd == "mo":
        build_mo()
    else:
        bad = 0
        for lang in LANGS:
            table = load(lang)
            for s, where in sorted(all_strings().items()):
                if s not in table:
                    print(f"[{lang}] missing: {s!r}  <- {', '.join(sorted(where))}")
                    bad += 1
                elif s.count("{") != table[s].count("{") or s.count("%") != table[s].count("%"):
                    print(f"[{lang}] placeholders differ: {s!r} -> {table[s]!r}")
                    bad += 1
        print("all text translated" if not bad else f"{bad} problems")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
