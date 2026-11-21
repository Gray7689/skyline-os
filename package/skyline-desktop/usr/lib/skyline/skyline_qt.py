"""Qt pieces shared by SkyLine's apps (Settings, Setup, Puff): picture cards, headings, Puff himself."""
import math

import skyline_common as sk
from PyQt6.QtCore import QObject, QRect, QRectF, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import QFrame, QLabel, QScrollArea, QToolButton, QVBoxLayout, QWidget


class Worker(QObject):
    """Runs a slow function (network, nvidia-smi) off the UI thread."""
    done = pyqtSignal(object)

    def __init__(self, fn, *args):
        super().__init__()
        self.fn, self.args = fn, args

    def run(self):
        try:
            self.done.emit(self.fn(*self.args))
        except Exception as e:  # report instead of crashing the window
            self.done.emit(e)


def in_background(parent, fn, *args, then):
    thread = QThread(parent)
    worker = Worker(fn, *args)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.done.connect(then)
    worker.done.connect(thread.quit)
    thread.finished.connect(worker.deleteLater)
    parent._keep = getattr(parent, "_keep", []) + [(thread, worker)]
    thread.start()


CARD_STYLE = ("QToolButton { border: 2px solid transparent; border-radius: 12px; padding: 6px; }"
              "QToolButton:hover { border-color: palette(mid); }"
              "QToolButton:checked { border-color: palette(highlight); background: palette(alternate-base); }")


def rounded(pixmap, radius=10):
    out = QPixmap(pixmap.size())
    out.fill(Qt.GlobalColor.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(QRectF(out.rect()), radius, radius)
    p.setClipPath(path)
    p.drawPixmap(0, 0, pixmap)
    p.end()
    return out


def thumb(wallpaper, w=200, h=112):
    pm = QPixmap(str(sk.WALLPAPERS / wallpaper / "contents/screenshot.png"))
    if pm.isNull():
        pm = QPixmap(w, h)
        pm.fill(QColor("#FFD8CC"))
    return pm.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)


def auto_thumb(w=200, h=112):
    """Four skies in one picture, for 'Follow the time of day'."""
    out = QPixmap(w, h)
    p = QPainter(out)
    for i, wp in enumerate(["SkyLine-Peach", "SkyLine-Sky", "SkyLine-Dusk", "SkyLine-Night"]):
        part = thumb(wp, w, h)
        x = i * w // 4
        p.drawPixmap(x, 0, part, x, 0, w // 4 + 1, h)
    p.end()
    return out


def taskbar_thumb(style, w=160, h=90):
    pm = thumb("SkyLine-Peach", w, h)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    bar = QRectF(6, h - 20, w - 12, 14)
    fills = {"auto": QColor(255, 241, 236, 235), "black": QColor(20, 20, 24), "white": QColor(255, 255, 255),
             "glass": QColor(255, 255, 255, 110), "clear": QColor(0, 0, 0, 0)}
    p.setBrush(fills[style])
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(bar, 5, 5)
    icon = QColor("#FFFFFF") if style == "black" else QColor("#23264A")
    p.setBrush(icon)
    for i in range(5):
        p.drawRoundedRect(QRectF(12 + i * 13, h - 17, 8, 8), 2, 2)
    p.end()
    return pm


def card(text, pixmap, size):
    b = QToolButton()
    b.setText(text)
    b.setIcon(QIcon(rounded(pixmap)))
    b.setIconSize(size)
    b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
    b.setCheckable(True)
    b.setStyleSheet(CARD_STYLE)
    return b


def heading(text):
    label = QLabel(text)
    f = label.font()
    f.setPointSizeF(f.pointSizeF() * 1.5)
    f.setWeight(QFont.Weight.DemiBold)
    label.setFont(f)
    return label


def section(text):
    label = QLabel(text)
    f = label.font()
    f.setWeight(QFont.Weight.DemiBold)
    label.setFont(f)
    return label


def note(text):
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet("color: palette(placeholder-text);")
    return label


def page(*widgets):
    body = QWidget()
    v = QVBoxLayout(body)
    v.setContentsMargins(28, 24, 28, 24)
    v.setSpacing(12)
    for w in widgets:
        if isinstance(w, QWidget):
            v.addWidget(w)
        else:
            v.addLayout(w)
    v.addStretch(1)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setWidget(body)
    return scroll



# ------------------------------------------------------------------ Puff

PUFF = [
    "......oooo......",
    "...oooowwwwo....",
    "..owwwwwwwwwoo..",
    ".owwwwwwwwwwwwo.",
    "owwwwwwwwwwwwwwo",
    "owwweewwwweewwwo",
    "owwweewwwweewwwo",
    "owbbwwwwwwwwbbwo",
    "owwwwwmwwmwwwwwo",
    ".owwwwwmmwwwwwo.",
    "..oooooooooooo..",
]
PUFF_COLORS = {"o": "#23264A", "w": "#FFFFFF", "e": "#23264A", "m": "#23264A", "b": "#FFB3A6"}


class Puff(QWidget):
    """Puff the pixel cloud: bobs and blinks. busy=True makes him bob faster."""

    def __init__(self, pixel=5):
        super().__init__()
        self.pixel = pixel
        self.phase = 0.0
        self.blink = 0
        self.busy = False
        self.setFixedSize(16 * pixel + 4, 11 * pixel + 12)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(60)

    def tick(self):
        self.phase += 0.35 if self.busy else 0.12
        self.blink = self.blink - 1 if self.blink > 0 else (3 if int(self.phase * 10) % 70 == 0 else 0)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        dy = round((math.sin(self.phase) + 1) * 3)
        for y, row in enumerate(PUFF):
            for x, ch in enumerate(row):
                if ch == ".":
                    continue
                if ch == "e" and self.blink and y == 5:
                    ch = "w"
                p.fillRect(QRect(2 + x * self.pixel, 2 + dy + y * self.pixel, self.pixel, self.pixel),
                           QColor(PUFF_COLORS[ch]))
        p.end()
