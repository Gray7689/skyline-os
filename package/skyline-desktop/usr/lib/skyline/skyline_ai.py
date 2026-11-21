"""Puff's AI brain: talks to Claude, OpenAI, NVIDIA, Groq, Gemini, OpenRouter, Ollama or any
OpenAI-compatible server, and lets the model change SkyLine through tools.

The API key is stored only in ~/.config/skyline/assistant.conf (readable by the user alone).
"""
import configparser
import json
import os
import urllib.error
import urllib.request

import skyline_common as sk

CONF = sk.CONFIG_DIR / "assistant.conf"

# kind "anthropic" = Claude's own API; "openai" = the OpenAI chat-completions format most providers share.
PROVIDERS = {
    "claude": {"label": "Claude (Anthropic)", "kind": "anthropic", "url": "https://api.anthropic.com/v1",
               "model": "claude-haiku-5-5", "key": True},
    "openai": {"label": "OpenAI", "kind": "openai", "url": "https://api.openai.com/v1",
               "model": "", "key": True},
    "nvidia": {"label": "NVIDIA (build.nvidia.com)", "kind": "openai", "url": "https://integrate.api.nvidia.com/v1",
               "model": "meta/llama-3.3-70b-instruct", "key": True},
    "groq": {"label": "Groq", "kind": "openai", "url": "https://api.groq.com/openai/v1",
             "model": "llama-3.3-70b-versatile", "key": True},
    "gemini": {"label": "Google Gemini", "kind": "openai",
               "url": "https://generativelanguage.googleapis.com/v1beta/openai", "model": "", "key": True},
    "openrouter": {"label": "OpenRouter", "kind": "openai", "url": "https://openrouter.ai/api/v1",
                   "model": "openrouter/auto", "key": True},
    "ollama": {"label": "Ollama (on this computer, no key)", "kind": "openai", "url": "http://localhost:11434/v1",
               "model": "", "key": False},
    "custom": {"label": "Other OpenAI-compatible server", "kind": "openai", "url": "", "model": "", "key": True},
}

SYSTEM_PROMPT = (
    "You are Puff, a small friendly pixel cloud who lives in SkyLine OS, a cute and very customizable Linux "
    "desktop (Debian 13 + KDE Plasma 6). You chat with the user about anything, and you change their desktop "
    "with your tools. Never say a change happened unless a tool result confirms it. Keep replies short (one to "
    "four sentences), warm and simple. Reply in the user's language. If no tool can do something on the desktop, "
    "explain how to do it in KDE Plasma (for example: right-click the desktop, or open System Settings)."
)

TOOLS = [
    ("set_sky", "Change the desktop sky (wallpaper, colors, lock screen). 'auto' follows the time of day.",
     {"mode": {"type": "string", "enum": list(sk.SKIES)}}, ["mode"]),
    ("set_layout", "Change the desktop layout: classic (bar at the bottom), dock (top bar + app dock), minimal.",
     {"name": {"type": "string", "enum": list(sk.LAYOUTS)}}, ["name"]),
    ("set_taskbar", "Change the taskbar look: auto (follows the sky), black, white, glass (see-through), clear (invisible).",
     {"style": {"type": "string", "enum": list(sk.TASKBARS)}}, ["style"]),
    ("set_game_mode", "Turn Game Mode on or off (max performance, notifications muted).",
     {"on": {"type": "boolean"}}, ["on"]),
    ("set_weather", "Show the real weather (rain, snow, clouds) in the sky. Optionally set the city.",
     {"on": {"type": "boolean"}, "place": {"type": "string", "description": "City name, optional"}}, ["on"]),
    ("set_accent", "Set the accent color. 'none' matches the sky.",
     {"color": {"type": "string", "enum": list(sk.ACCENTS)}}, ["color"]),
    ("install_apps", "Install apps in a terminal window (may ask for the password). 'nvidia' is the graphics driver.",
     {"apps": {"type": "array", "items": {"type": "string", "enum": list(sk.APPS) + ["nvidia"]}}}, ["apps"]),
    ("open_app", "Open an app by name, for example files, terminal, browser, store, settings, discord, steam.",
     {"name": {"type": "string"}}, ["name"]),
]

SKIP_MODEL_WORDS = ("embed", "whisper", "tts", "dall-e", "image", "audio", "moderation", "rerank", "guard",
                    "transcribe", "realtime", "search", "vision-only", "clip")
PREFERRED_MODEL_WORDS = ("haiku", "mini", "flash", "llama-3.3-70b", "70b", "8b")


class AIError(Exception):
    pass


# ------------------------------------------------------------------ settings

def load():
    cfg = configparser.ConfigParser()
    cfg.read(CONF)
    sec = cfg["assistant"] if cfg.has_section("assistant") else {}
    provider = sec.get("provider", "off")
    info = PROVIDERS.get(provider, {})
    return {
        "provider": provider if provider in PROVIDERS else "off",
        "api_key": sec.get("api_key", ""),
        "model": sec.get("model", "") or info.get("model", ""),
        "url": sec.get("base_url", "") or info.get("url", ""),
    }


def save(provider, api_key, model, base_url=""):
    cfg = configparser.ConfigParser()
    cfg["assistant"] = {"provider": provider, "api_key": api_key.strip(), "model": model.strip(),
                        "base_url": base_url.strip()}
    sk.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    fd = os.open(CONF, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        cfg.write(f)
    os.chmod(CONF, 0o600)


def ready(cfg):
    """True when Puff has an AI to talk to."""
    info = PROVIDERS.get(cfg["provider"])
    return bool(info and cfg["model"] and cfg["url"] and (cfg["api_key"] or not info["key"]))


# ------------------------------------------------------------------ HTTP

def _request(url, headers, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        try:
            detail = json.loads(detail).get("error", detail)
            if isinstance(detail, dict):
                detail = detail.get("message", str(detail))
        except (ValueError, AttributeError):
            pass
        raise AIError(f"{e.code}: {str(detail)[:240]}") from e
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise AIError("Can't reach the AI service. Check your internet connection"
                      + (" and that Ollama is running." if "localhost" in url else ".")) from e


def _headers(cfg):
    if PROVIDERS[cfg["provider"]]["kind"] == "anthropic":
        return {"x-api-key": cfg["api_key"], "anthropic-version": "2023-06-01", "content-type": "application/json"}
    h = {"Content-Type": "application/json"}
    if cfg["api_key"]:
        h["Authorization"] = "Bearer " + cfg["api_key"]
    if cfg["provider"] == "openrouter":
        h["X-Title"] = "SkyLine Puff"
    return h


def list_models(cfg):
    """Model ids the provider offers, best guesses first."""
    data = _request(cfg["url"].rstrip("/") + "/models", _headers(cfg), timeout=20)
    ids = [m.get("id", "") for m in data.get("data", []) if m.get("id")]
    ids = [i for i in ids if not any(w in i.lower() for w in SKIP_MODEL_WORDS)]
    ids = [i.split("/", 1)[1] if cfg["provider"] == "gemini" and i.startswith("models/") else i for i in ids]

    def rank(model_id):
        low = model_id.lower()
        for n, word in enumerate(PREFERRED_MODEL_WORDS):
            if word in low:
                return (n, model_id)
        return (len(PREFERRED_MODEL_WORDS), model_id)

    return sorted(set(ids), key=rank)


# ------------------------------------------------------------------ chatting

def _anthropic_chat(cfg, history, run_tool, use_tools):
    tools = [{"name": n, "description": d, "input_schema": {"type": "object", "properties": p, "required": r}}
             for n, d, p, r in TOOLS]
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    for _ in range(4):
        body = {"model": cfg["model"], "max_tokens": 700, "system": SYSTEM_PROMPT, "messages": messages}
        if use_tools:
            body["tools"] = tools
        data = _request(cfg["url"].rstrip("/") + "/messages", _headers(cfg), body)
        content = data.get("content", [])
        uses = [b for b in content if b.get("type") == "tool_use"]
        text = " ".join(b.get("text", "") for b in content if b.get("type") == "text").strip()
        if not uses:
            return text or "Done!"
        messages.append({"role": "assistant", "content": content})
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": u["id"], "content": run_tool(u["name"], u.get("input", {}))}
            for u in uses]})
    return "Done!"


def _openai_chat(cfg, history, run_tool, use_tools, extra_system=""):
    tools = [{"type": "function", "function": {"name": n, "description": d,
              "parameters": {"type": "object", "properties": p, "required": r}}} for n, d, p, r in TOOLS]
    messages = [{"role": "system", "content": SYSTEM_PROMPT + extra_system}] + [
        {"role": m["role"], "content": m["content"]} for m in history]
    for _ in range(4):
        body = {"model": cfg["model"], "messages": messages}
        if use_tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"
        data = _request(cfg["url"].rstrip("/") + "/chat/completions", _headers(cfg), body)
        msg = data["choices"][0]["message"]
        calls = msg.get("tool_calls") or []
        if not calls:
            return (msg.get("content") or "Done!").strip()
        messages.append({"role": "assistant", "content": msg.get("content") or "", "tool_calls": calls})
        for c in calls:
            try:
                args = json.loads(c["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            messages.append({"role": "tool", "tool_call_id": c["id"],
                             "content": run_tool(c["function"]["name"], args)})
    return "Done!"


def chat(cfg, history, run_tool, local_actions=None):
    """Answer the conversation. If the model can't use tools, `local_actions()` performs simple
    requests itself and its result is passed to the model so Puff can mention it."""
    kind = PROVIDERS[cfg["provider"]]["kind"]
    try:
        if kind == "anthropic":
            return _anthropic_chat(cfg, history, run_tool, True)
        return _openai_chat(cfg, history, run_tool, True)
    except AIError as e:
        text = str(e).lower()
        tools_problem = str(e).startswith(("400", "404", "422")) and ("tool" in text or "function" in text)
        if not tools_problem:
            raise
    done = local_actions() if local_actions else None
    note = f"\nSkyLine already did this for the user: {done} Mention it briefly." if done else ""
    if kind == "anthropic":
        return _anthropic_chat(cfg, history, run_tool, False)
    return _openai_chat(cfg, history, run_tool, False, note)


def test(cfg):
    """One tiny message to check the key and model. Returns the reply."""
    return chat(cfg, [{"role": "user", "content": "Say hi in five words or fewer."}], lambda *_: "ok")


# ------------------------------------------------------------------ setup window (used by Puff and SkyLine Settings)

def setup_dialog(parent=None):
    """Ask for a provider, key and model. Returns True if the user saved."""
    from PyQt6.QtCore import QObject, QThread, pyqtSignal
    from PyQt6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QGridLayout, QHBoxLayout, QLabel,
                                 QLineEdit, QPushButton, QVBoxLayout)

    class Job(QObject):
        done = pyqtSignal(object)

        def __init__(self, fn, arg):
            super().__init__()
            self.fn, self.arg = fn, arg

        def run(self):
            try:
                self.done.emit(self.fn(self.arg))
            except Exception as e:
                self.done.emit(e)

    current = load()
    dlg = QDialog(parent)
    dlg.setWindowTitle("Connect an AI to Puff")
    dlg.setMinimumWidth(520)
    jobs = []

    intro = QLabel("Pick an AI service and paste your API key. Puff then chats with you about anything and "
                   "still changes your desktop when you ask. Your key is saved only on this computer, and your "
                   "messages to Puff go to the service you pick.")
    intro.setWordWrap(True)

    provider = QComboBox()
    for key, info in PROVIDERS.items():
        provider.addItem(info["label"], key)
    provider.setCurrentIndex(max(0, provider.findData(current["provider"])))
    api_key = QLineEdit(current["api_key"])
    api_key.setEchoMode(QLineEdit.EchoMode.Password)
    api_key.setPlaceholderText("Paste your API key")
    show = QPushButton("Show")
    show.setCheckable(True)
    show.toggled.connect(lambda on: api_key.setEchoMode(
        QLineEdit.EchoMode.Normal if on else QLineEdit.EchoMode.Password))
    url = QLineEdit(current["url"])
    url.setPlaceholderText("https://your-server/v1")
    model = QComboBox()
    model.setEditable(True)
    model.setCurrentText(current["model"])
    load_btn = QPushButton("Load models")
    status = QLabel("")
    status.setWordWrap(True)
    test_btn = QPushButton("Test")

    url_label = QLabel("Server URL")
    key_label = QLabel("API key")
    key_row = QHBoxLayout()
    key_row.addWidget(api_key, 1)
    key_row.addWidget(show)
    model_row = QHBoxLayout()
    model_row.addWidget(model, 1)
    model_row.addWidget(load_btn)

    form = QGridLayout()
    form.addWidget(QLabel("AI service"), 0, 0)
    form.addWidget(provider, 0, 1)
    form.addWidget(key_label, 1, 0)
    form.addLayout(key_row, 1, 1)
    form.addWidget(url_label, 2, 0)
    form.addWidget(url, 2, 1)
    form.addWidget(QLabel("Model"), 3, 0)
    form.addLayout(model_row, 3, 1)

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    off_btn = buttons.addButton("Turn AI off", QDialogButtonBox.ButtonRole.DestructiveRole)
    bottom = QHBoxLayout()
    bottom.addWidget(test_btn)
    bottom.addWidget(status, 1)

    layout = QVBoxLayout(dlg)
    layout.addWidget(intro)
    layout.addLayout(form)
    layout.addLayout(bottom)
    layout.addWidget(buttons)

    def chosen():
        key = provider.currentData()
        return {"provider": key, "api_key": api_key.text().strip(), "model": model.currentText().strip(),
                "url": url.text().strip() or PROVIDERS[key]["url"]}

    def provider_changed():
        info = PROVIDERS[provider.currentData()]
        custom_url = provider.currentData() in ("custom", "ollama")
        url_label.setVisible(custom_url)
        url.setVisible(custom_url)
        url.setText(info["url"] if provider.currentData() != current["provider"] else current["url"])
        key_label.setVisible(info["key"])
        api_key.setVisible(info["key"])
        show.setVisible(info["key"])
        if provider.currentData() != current["provider"]:
            model.clear()
            model.setCurrentText(info["model"])
        status.setText("")

    def background(fn, arg, then):
        thread = QThread(dlg)
        job = Job(fn, arg)
        job.moveToThread(thread)
        thread.started.connect(job.run)
        job.done.connect(then)
        job.done.connect(thread.quit)
        jobs.append((thread, job))
        thread.start()

    def models_loaded(result):
        load_btn.setEnabled(True)
        if isinstance(result, Exception):
            status.setText("Couldn't load models: " + str(result))
            return
        keep = model.currentText()
        model.clear()
        model.addItems(result)
        model.setCurrentText(keep if keep in result else (result[0] if result else keep))
        status.setText(f"{len(result)} models found. Pick one, then press Test.")

    def tested(result):
        test_btn.setEnabled(True)
        if isinstance(result, Exception):
            status.setText("Didn't work: " + str(result))
        else:
            status.setText("It works! Puff says: " + str(result)[:120])

    def do_load():
        load_btn.setEnabled(False)
        status.setText("Loading models…")
        background(list_models, chosen(), models_loaded)

    def do_test():
        cfg = chosen()
        if not ready(cfg):
            status.setText("Fill in the key and model first.")
            return
        test_btn.setEnabled(False)
        status.setText("Asking the AI…")
        background(test, cfg, tested)

    def do_save():
        cfg = chosen()
        if not ready(cfg):
            status.setText("Fill in the key and model first (press Load models to see them).")
            return
        save(cfg["provider"], cfg["api_key"], cfg["model"],
             cfg["url"] if cfg["provider"] in ("custom", "ollama") else "")
        dlg.accept()

    def do_off():
        save("off", "", "")
        dlg.reject()

    provider.currentIndexChanged.connect(provider_changed)
    load_btn.clicked.connect(do_load)
    test_btn.clicked.connect(do_test)
    buttons.accepted.connect(do_save)
    buttons.rejected.connect(dlg.reject)
    off_btn.clicked.connect(do_off)
    provider_changed()
    url.setText(current["url"] or PROVIDERS[provider.currentData()]["url"])
    saved = dlg.exec() == QDialog.DialogCode.Accepted
    for thread, _ in jobs:
        thread.quit()
        thread.wait(3000)
    return saved
