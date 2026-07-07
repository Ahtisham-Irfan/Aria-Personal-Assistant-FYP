import os
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import Qt


class BottomBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(52)
        self._dark = True

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16,8,16,8)
        layout.setSpacing(8)

        self.buttons = []
        for text in [
            "⊞  Open App",
            "⊟  Search Files",
            "⚙  Settings",
            "⧉  Clipboard",
            "💡  Help",
        ]:
            btn = QPushButton(text)
            btn.setFixedHeight(34)
            btn.setCursor(Qt.PointingHandCursor)
            self.buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        self.ver_label = QLabel("ARIA v1.0  ·  WIN 11")
        layout.addWidget(self.ver_label)

        self.update_theme(True)

    def update_theme(self, is_dark):
        self._dark = is_dark
        if is_dark:
            self.setStyleSheet(
                "BottomBar{background-color:#070B18;"
                "border-top:1px solid #1E2D4A;}"
            )
            btn_style = (
                "QPushButton{"
                "background-color:#12182B;"
                "border:1px solid #2A3555;"
                "border-radius:10px;"
                "font-family:'Outfit';font-size:12px;"
                "color:#93A4C3;padding:0 14px;}"
                "QPushButton:hover{"
                "background-color:#1A2238;"
                "border-color:#4FD1FF;color:#4FD1FF;}"
                "QPushButton:pressed{"
                "background-color:#0D1425;}"
            )
            self.ver_label.setStyleSheet(
                "font-family:'Outfit';font-size:10px;"
                "color:#1E2D4A;letter-spacing:1px;"
                "background:transparent;"
            )
        else:
            self.setStyleSheet(
                "BottomBar{background-color:#FFFFFF;"
                "border-top:1px solid #C5D8F0;}"
            )
            btn_style = (
                "QPushButton{"
                "background-color:#EEF6FF;"
                "border:1px solid #C5D8F0;"
                "border-radius:10px;"
                "font-family:'Outfit';font-size:12px;"
                "color:#4A7090;padding:0 14px;}"
                "QPushButton:hover{"
                "background-color:#D8EEFF;"
                "border-color:#4FD1FF;color:#0099CC;}"
            )
            self.ver_label.setStyleSheet(
                "font-family:'Outfit';font-size:10px;"
                "color:#7090A0;letter-spacing:1px;"
                "background:transparent;"
            )

        for btn in self.buttons:
            btn.setStyleSheet(btn_style)

    def open_clipboard(self):
        try:
            import pyautogui
            pyautogui.hotkey('win', 'v')
        except Exception:
            try:
                os.system('start ms-settings:clipboard')
            except Exception:
                pass

    def open_help(self):
        if self.parent_window:
            self.parent_window.chat_panel\
                .add_aria_message(
                "📋 Available Commands:\n\n"
                "🗣 Voice: Click mic → Hey Aria → speak\n"
                "📱 Apps: open chrome / notepad\n"
                "🎵 Music: play attention / pause / stop\n"
                "🔍 Search: who is Elon Musk\n"
                "📁 Files: find file resume\n"
                "⏰ Reminder: remind me in 5 mins to...\n"
                "🔊 Volume: volume up / down / mute\n"
                "💻 System: shutdown / restart / lock\n"
                "📎 Drag & drop any file to analyze"
            )