from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import QByteArray
from ui.system_monitor_widget import SystemMonitorWidget


class AriaFace(QSvgWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 155)
        self._is_talking = False
        self._is_listening = False
        self._blink_state = False
        self._mouth_state = 0

        self._blink_timer = QTimer()
        self._blink_timer.timeout.connect(self._do_blink)
        self._blink_timer.start(4000)

        self._mouth_timer = QTimer()
        self._mouth_timer.timeout.connect(self._animate_mouth)
        self._render()

    def stop_all(self):
        try: self._blink_timer.stop()
        except: pass
        try: self._mouth_timer.stop()
        except: pass

    def _render(self):
        eye_ry = "1" if self._blink_state else "11"
        if self._is_talking:
            sizes = [1.5, 1.5, 1.5]
            sizes[self._mouth_state % 3] = 3.5
            d1, d2, d3 = sizes
        else:
            d1, d2, d3 = 2.5, 2.5, 2.5

        if self._is_listening:
            stroke = "#4FD1FF"
            hair1 = "#0D3A5C"
            hair2 = "#0F4A70"
            eye_color = "#4FD1FF"
        else:
            stroke = "#4FD1FF"
            hair1 = "#0A1E35"
            hair2 = "#0D3050"
            eye_color = "#4FD1FF"

        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="140" height="155" viewBox="0 0 140 155" xmlns="http://www.w3.org/2000/svg">
  <circle cx="70" cy="75" r="65" fill="none" stroke="{stroke}" stroke-width="0.5" opacity="0.12"/>
  <circle cx="70" cy="75" r="55" fill="none" stroke="{stroke}" stroke-width="0.5" opacity="0.08"/>
  <path d="M15 148 Q52 132 70 132 Q88 132 125 148" stroke="{stroke}" stroke-width="1" fill="#0D1830"/>
  <rect x="57" y="120" width="26" height="18" rx="4" fill="#0D1830" stroke="{stroke}" stroke-width="1"/>
  <line x1="65" y1="120" x2="65" y2="138" stroke="{stroke}" stroke-width="0.5" opacity="0.4"/>
  <line x1="75" y1="120" x2="75" y2="138" stroke="{stroke}" stroke-width="0.5" opacity="0.4"/>
  <ellipse cx="70" cy="72" rx="46" ry="52" fill="#0D1830" stroke="{stroke}" stroke-width="1.8"/>
  <ellipse cx="70" cy="32" rx="46" ry="20" fill="{hair1}"/>
  <ellipse cx="70" cy="26" rx="40" ry="14" fill="{hair2}"/>
  <ellipse cx="58" cy="24" rx="12" ry="6" fill="{stroke}" opacity="0.2"/>
  <ellipse cx="26" cy="62" rx="11" ry="24" fill="{hair1}"/>
  <ellipse cx="114" cy="62" rx="11" ry="24" fill="{hair1}"/>
  <ellipse cx="24" cy="74" rx="7" ry="9" fill="#0D1830" stroke="{stroke}" stroke-width="1"/>
  <ellipse cx="24" cy="74" rx="3.5" ry="5" fill="#070B18"/>
  <ellipse cx="116" cy="74" rx="7" ry="9" fill="#0D1830" stroke="{stroke}" stroke-width="1"/>
  <ellipse cx="116" cy="74" rx="3.5" ry="5" fill="#070B18"/>
  <path d="M46 55 Q56 50 65 54" stroke="{stroke}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.7"/>
  <path d="M75 54 Q84 50 94 55" stroke="{stroke}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.7"/>
  <ellipse cx="56" cy="67" rx="11" ry="{eye_ry}" fill="#070B18" stroke="{stroke}" stroke-width="1.5"/>
  <ellipse cx="84" cy="67" rx="11" ry="{eye_ry}" fill="#070B18" stroke="{stroke}" stroke-width="1.5"/>
  <circle cx="56" cy="67" r="7" fill="#0D2040"/>
  <circle cx="84" cy="67" r="7" fill="#0D2040"/>
  <circle cx="56" cy="67" r="4" fill="#070B18"/>
  <circle cx="84" cy="67" r="4" fill="#070B18"/>
  <circle cx="56" cy="67" r="3" fill="{eye_color}" opacity="0.95"/>
  <circle cx="84" cy="67" r="3" fill="{eye_color}" opacity="0.95"/>
  <circle cx="59" cy="64" r="2" fill="white" opacity="0.6"/>
  <circle cx="87" cy="64" r="2" fill="white" opacity="0.6"/>
  <path d="M67 79 Q70 83 73 79" stroke="{stroke}" stroke-width="1" fill="none" stroke-linecap="round" opacity="0.4"/>
  <ellipse cx="42" cy="82" rx="11" ry="7" fill="#7C5CFF" opacity="0.15"/>
  <ellipse cx="98" cy="82" rx="11" ry="7" fill="#7C5CFF" opacity="0.15"/>
  <rect x="52" y="90" width="36" height="12" rx="6" fill="#070B18" stroke="{stroke}" stroke-width="1"/>
  <circle cx="60" cy="96" r="{d1}" fill="{stroke}"/>
  <circle cx="70" cy="96" r="{d2}" fill="{stroke}"/>
  <circle cx="80" cy="96" r="{d3}" fill="{stroke}"/>
  <line x1="70" y1="22" x2="70" y2="8" stroke="{stroke}" stroke-width="1.5"/>
  <circle cx="70" cy="5.5" r="4" fill="{stroke}"/>
  <circle cx="70" cy="5.5" r="7" fill="none" stroke="{stroke}" stroke-width="0.8" opacity="0.4"/>
</svg>'''
        self.load(QByteArray(svg.encode('utf-8')))

    def _do_blink(self):
        self._blink_state = True
        self._render()
        QTimer.singleShot(150, self._end_blink)

    def _end_blink(self):
        self._blink_state = False
        self._render()

    def start_talking(self):
        self._is_talking = True
        self._mouth_timer.start(120)

    def stop_talking(self):
        self._is_talking = False
        self._mouth_timer.stop()
        self._mouth_state = 0
        self._render()

    def _animate_mouth(self):
        self._mouth_state += 1
        self._render()

    def set_listening(self, state):
        self._is_listening = state
        self._render()


class LeftPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedWidth(230)
        self.is_listening = False
        self._dark = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.face = AriaFace(self)

        self.name_label = QLabel("ARIA")
        self.name_label.setAlignment(Qt.AlignCenter)

        self.sub_label = QLabel("VIRTUAL ASSISTANT")
        self.sub_label.setAlignment(Qt.AlignCenter)

        self.divider = QWidget()
        self.divider.setFixedHeight(1)

        self.status_label = QLabel("Click mic to speak")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.monitor = SystemMonitorWidget(self)

        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Expanding
        )

        self.sys_info = QLabel("WIN 11  ·  OFFLINE ✓")
        self.sys_info.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.face, 0, Qt.AlignHCenter)
        layout.addWidget(self.name_label)
        layout.addWidget(self.sub_label)
        layout.addWidget(self.divider)
        layout.addWidget(self.status_label)
        layout.addWidget(self.monitor)
        layout.addWidget(spacer)
        layout.addWidget(self.sys_info)

        self.update_theme(True)

    def stop_all(self):
        self.face.stop_all()

    def update_theme(self, is_dark):
        self._dark = is_dark
        if is_dark:
            self.setStyleSheet("""
                LeftPanel {
                    background-color: #0D1425;
                    border-right: 1px solid #1E2D4A;
                }
            """)
            self.name_label.setStyleSheet("""
                font-family: 'Outfit';
                font-size: 20px; font-weight: 700;
                color: #EAF2FF; letter-spacing: 4px;
                background: transparent;
            """)
            self.sub_label.setStyleSheet("""
                font-family: 'Outfit'; font-size: 10px;
                color: #2A4060; letter-spacing: 2px;
                background: transparent;
            """)
            self.divider.setStyleSheet(
                "background-color: #1E2D4A;"
            )
            self.status_label.setStyleSheet("""
                font-family: 'Outfit'; font-size: 11px;
                color: #2A4060; letter-spacing: 1px;
                background: transparent;
            """)
            self.sys_info.setStyleSheet("""
                font-family: 'Outfit'; font-size: 10px;
                color: #1E2D4A; letter-spacing: 1px;
                background: transparent;
            """)
        else:
            self.setStyleSheet("""
                LeftPanel {
                    background-color: #F0F6FF;
                    border-right: 1px solid #C5D8F0;
                }
            """)
            self.name_label.setStyleSheet("""
                font-family: 'Outfit';
                font-size: 20px; font-weight: 700;
                color: #0D1830; letter-spacing: 4px;
                background: transparent;
            """)
            self.sub_label.setStyleSheet("""
                font-family: 'Outfit'; font-size: 10px;
                color: #4A7090; letter-spacing: 2px;
                background: transparent;
            """)
            self.divider.setStyleSheet(
                "background-color: #C5D8F0;"
            )
            self.status_label.setStyleSheet("""
                font-family: 'Outfit'; font-size: 11px;
                color: #4A7090; letter-spacing: 1px;
                background: transparent;
            """)
            self.sys_info.setStyleSheet("""
                font-family: 'Outfit'; font-size: 10px;
                color: #7090A0; letter-spacing: 1px;
                background: transparent;
            """)

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        self.face.set_listening(self.is_listening)
        if self.is_listening:
            self.status_label.setText("Listening...")
            self.status_label.setStyleSheet("""
                font-family: 'Outfit'; font-size: 11px;
                color: #4FD1FF; letter-spacing: 1px;
                background: transparent;
            """)
        else:
            self.status_label.setText("Click mic to speak")
            color = "#2A4060" if self._dark else "#4A7090"
            self.status_label.setStyleSheet(f"""
                font-family: 'Outfit'; font-size: 11px;
                color: {color}; letter-spacing: 1px;
                background: transparent;
            """)

    def start_talking(self):
        self.face.start_talking()
        self.status_label.setText("Speaking...")
        self.status_label.setStyleSheet("""
            font-family: 'Outfit'; font-size: 11px;
            color: #7C5CFF; letter-spacing: 1px;
            background: transparent;
        """)

    def stop_talking(self):
        self.face.stop_talking()
        self.status_label.setText("Click mic to speak")
        color = "#2A4060" if self._dark else "#4A7090"
        self.status_label.setStyleSheet(f"""
            font-family: 'Outfit'; font-size: 11px;
            color: {color}; letter-spacing: 1px;
            background: transparent;
        """)