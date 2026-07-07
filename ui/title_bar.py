from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt


class TitleBar(QWidget):
    """
    Top status bar: app name, live status pill
    (Active / Listening / Speaking / Processing...)
    and the theme toggle button.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(52)
        self.setObjectName("TitleBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(10)

        self.logo_label = QLabel("◈  ARIA")
        self.logo_label.setStyleSheet(
            "font-family:'Outfit';font-size:15px;"
            "font-weight:700;color:#4FD1FF;"
            "letter-spacing:2px;background:transparent;"
        )

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(
            "color:#3DDC97;font-size:12px;background:transparent;"
        )

        self.status_label = QLabel("Active")
        self.status_label.setStyleSheet(
            "font-family:'Outfit';font-size:12px;"
            "color:#93A4C3;background:transparent;"
        )

        self.theme_btn = QPushButton("◑ Theme")
        self.theme_btn.setFixedHeight(30)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setStyleSheet(
            "QPushButton{"
            "background-color:#12182B;"
            "border:1px solid #2A3555;"
            "border-radius:15px;"
            "font-family:'Outfit';font-size:11px;"
            "color:#4FD1FF;padding:0 14px;}"
            "QPushButton:hover{"
            "background-color:#1A2238;"
            "border-color:#4FD1FF;}"
        )
        self.theme_btn.clicked.connect(self._on_theme_clicked)

        layout.addWidget(self.logo_label)
        layout.addSpacing(12)
        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.theme_btn)

    def _on_theme_clicked(self):
        if self.parent_window and hasattr(
            self.parent_window, 'toggle_theme'
        ):
            self.parent_window.toggle_theme()

    def set_status(self, text, color="#3DDC97"):
        self.status_label.setText(text)
        self.status_dot.setStyleSheet(
            f"color:{color};font-size:12px;background:transparent;"
        )
