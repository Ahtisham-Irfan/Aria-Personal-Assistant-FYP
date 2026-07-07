from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt


class _Bar(QWidget):
    """Tiny horizontal usage bar (CPU / RAM / Disk)."""

    def __init__(self, label, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        top = QHBoxLayout()
        self.name_label = QLabel(label)
        self.name_label.setStyleSheet(
            "font-family:'Outfit';font-size:9px;"
            "color:#2A4060;letter-spacing:1px;"
            "background:transparent;"
        )
        self.value_label = QLabel("0%")
        self.value_label.setStyleSheet(
            "font-family:'Outfit';font-size:9px;"
            "color:#4FD1FF;background:transparent;"
        )
        top.addWidget(self.name_label)
        top.addStretch()
        top.addWidget(self.value_label)

        self.track = QWidget()
        self.track.setFixedHeight(4)
        self.track.setStyleSheet(
            "background-color:#1E2D4A;border-radius:2px;"
        )
        track_layout = QHBoxLayout(self.track)
        track_layout.setContentsMargins(0, 0, 0, 0)

        self.fill = QWidget()
        self.fill.setFixedHeight(4)
        self.fill.setStyleSheet(
            "background-color:#4FD1FF;border-radius:2px;"
        )
        track_layout.addWidget(
            self.fill, 0, Qt.AlignLeft
        )
        track_layout.addStretch()

        layout.addLayout(top)
        layout.addWidget(self.track)

    def set_value(self, percent):
        percent = max(0, min(100, percent))
        self.value_label.setText(f"{percent:.0f}%")
        total_w = max(self.track.width(), 1)
        self.fill.setFixedWidth(
            int(total_w * percent / 100)
        )
        color = "#4FD1FF"
        if percent >= 85:
            color = "#FF5F57"
        elif percent >= 60:
            color = "#FFB84D"
        self.fill.setStyleSheet(
            f"background-color:{color};border-radius:2px;"
        )


class SystemMonitorWidget(QWidget):
    """
    Compact CPU / RAM / Disk usage widget shown in the
    left panel. Fed by modules/system_monitor.py via
    update_stats({'cpu':.., 'ram':.., 'disk':..}).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(8)

        self.cpu_bar = _Bar("CPU")
        self.ram_bar = _Bar("RAM")
        self.disk_bar = _Bar("DISK")

        layout.addWidget(self.cpu_bar)
        layout.addWidget(self.ram_bar)
        layout.addWidget(self.disk_bar)

    def update_stats(self, stats):
        self.cpu_bar.set_value(stats.get('cpu', 0))
        self.ram_bar.set_value(stats.get('ram', 0))
        self.disk_bar.set_value(stats.get('disk', 0))
