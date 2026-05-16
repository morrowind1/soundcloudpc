import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSystemTrayIcon, QMenu,
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QFrame
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import Qt, QUrl, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QKeySequence, QShortcut, QFont

def make_icon(color="#ff5500"):
    px = QPixmap(64, 64)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(color))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(0, 0, 64, 64)
    p.setPen(QColor("white"))
    font = QFont("Arial", 28, QFont.Weight.Bold)
    p.setFont(font)
    p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "SC")
    p.end()
    return QIcon(px)

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(42)
        self.setStyleSheet("""
            QWidget {
                background: #111111;
                border-bottom: 1px solid #ff5500;
            }
        """)
        self._drag_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(8)

        logo = QLabel("🟠 SoundCloud")
        logo.setStyleSheet("color: #ff5500; font-weight: 700; font-size: 14px; border: none;")
        layout.addWidget(logo)

        layout.addStretch()

        for text, slot, color in [
            ("─", parent.showMinimized, "#555"),
            ("□", self._toggle_max, "#555"),
            ("✕", parent.close, "#e74c3c"),
        ]:
            btn = QPushButton(text)
            btn.setFixedSize(32, 26)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(slot)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {color};
                    border: none; font-size: 14px; font-weight: bold;
                    border-radius: 6px;
                }}
                QPushButton:hover {{ background: #2a2a2a; color: white; }}
            """)
            layout.addWidget(btn)

    def _toggle_max(self):
        if self.parent.isMaximized() or self.parent.isFullScreen():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._toggle_max()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and not self.parent.isMaximized():
            self._drag_pos = e.globalPosition().toPoint()

    def mouseMoveEvent(self, e):
        if self._drag_pos and not self.parent.isMaximized():
            delta = e.globalPosition().toPoint() - self._drag_pos
            self.parent.move(self.parent.pos() + delta)
            self._drag_pos = e.globalPosition().toPoint()

    def mouseReleaseEvent(self, e):
        self._drag_pos = None


class PlayerBar(QWidget):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.setFixedHeight(48)
        self.setStyleSheet("""
            QWidget { background: #0d0d0d; border-top: 1px solid #222; }
            QPushButton {
                background: #1a1a1a; color: #ccc;
                border: 1px solid #2a2a2a; border-radius: 8px;
                padding: 6px 16px; font-size: 13px;
            }
            QPushButton:hover { background: #ff5500; color: white; border-color: #ff5500; }
            QLabel { color: #555; font-size: 11px; border: none; }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)

        hint = QLabel("Горячие клавиши:")
        layout.addWidget(hint)

        buttons = [
            ("⏮ Назад", self._back),
            ("⏪ Перемотать", self._seek_back),
            ("⏯ Пауза/Плей", self._toggle_play),
            ("⏩ Вперёд", self._seek_fwd),
            ("⏭ Далее", self._forward),
            ("🔃 Обновить", self._reload),
        ]
        for label, slot in buttons:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        layout.addStretch()

        hotkeys = QLabel("Space = пауза  |  ← →  = перемотка  |  Ctrl+R = обновить")
        layout.addWidget(hotkeys)

    def _toggle_play(self):
        self.browser.page().runJavaScript("""
            var btn = document.querySelector('.playControl, button[title*="Play"], button[title*="Pause"]');
            if(btn) btn.click();
        """)

    def _back(self):
        self.browser.page().runJavaScript("""
            var btn = document.querySelector('.skipControl__previous, button[title*="Previous"]');
            if(btn) btn.click();
        """)

    def _forward(self):
        self.browser.page().runJavaScript("""
            var btn = document.querySelector('.skipControl__next, button[title*="Next"]');
            if(btn) btn.click();
        """)

    def _seek_back(self):
        self.browser.page().runJavaScript("""
            var audio = document.querySelector('audio');
            if(audio) audio.currentTime = Math.max(0, audio.currentTime - 10);
        """)

    def _seek_fwd(self):
        self.browser.page().runJavaScript("""
            var audio = document.querySelector('audio');
            if(audio) audio.currentTime += 10;
        """)

    def _reload(self):
        self.browser.reload()


class SoundCloudApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SoundCloud")
        self.setMinimumSize(1000, 650)
        self.resize(1280, 820)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowMinMaxButtonsHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)

        icon = make_icon()
        self.setWindowIcon(icon)

        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet("background: #111;")
        vbox = QVBoxLayout(central)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        self.title_bar = TitleBar(self)
        vbox.addWidget(self.title_bar)

        from PyQt6.QtWebEngineCore import QWebEngineSettings
        profile = QWebEngineProfile("soundcloud_profile", self)
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        )
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

        page = QWebEnginePage(profile, self)
        settings = page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        self.browser = QWebEngineView()
        self.browser.setPage(page)
        self.browser.setUrl(QUrl("https://soundcloud.com"))

        vbox.addWidget(self.browser, 1)

        self.player_bar = PlayerBar(self.browser)
        vbox.addWidget(self.player_bar)

        QShortcut(QKeySequence("Space"),      self, self.player_bar._toggle_play)
        QShortcut(QKeySequence("Left"),       self, self.player_bar._seek_back)
        QShortcut(QKeySequence("Right"),      self, self.player_bar._seek_fwd)
        QShortcut(QKeySequence("Ctrl+Left"),  self, self.player_bar._back)
        QShortcut(QKeySequence("Ctrl+Right"), self, self.player_bar._forward)
        QShortcut(QKeySequence("Ctrl+R"),     self, self.player_bar._reload)
        QShortcut(QKeySequence("Alt+Left"),   self, self.browser.back)
        QShortcut(QKeySequence("Alt+Right"),  self, self.browser.forward)

        self._setup_tray(icon)

    def _setup_tray(self, icon):
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("SoundCloud")

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { background: #1a1a1a; color: #eee; border: 1px solid #ff5500; }
            QMenu::item:selected { background: #ff5500; }
        """)

        actions = [
            ("▶/⏸  Пауза / Плей",  self.player_bar._toggle_play),
            ("⏭  Следующий трек",  self.player_bar._forward),
            ("⏮  Предыдущий трек", self.player_bar._back),
            (None, None),
            ("🪟  Показать окно",   self._show_window),
            ("❌  Выход",           QApplication.quit),
        ]
        for label, slot in actions:
            if label is None:
                menu.addSeparator()
            else:
                act = menu.addAction(label)
                act.triggered.connect(slot)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, e):
        e.ignore()
        self.hide()
        self.tray.showMessage(
            "SoundCloud",
            "Приложение свёрнуто в трей. Двойной клик — чтобы открыть.",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )


if __name__ == "__main__":
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--autoplay-policy=no-user-gesture-required "
        "--enable-gpu-rasterization "
        "--enable-zero-copy "
        "--ignore-gpu-blocklist "
        "--disable-dev-shm-usage "
        "--num-raster-threads=4"
    )
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QSG_RENDER_LOOP"] = "threaded"
    app = QApplication(sys.argv)
    app.setApplicationName("SoundCloud")
    app.setQuitOnLastWindowClosed(False)

    window = SoundCloudApp()
    window.show()
    sys.exit(app.exec())