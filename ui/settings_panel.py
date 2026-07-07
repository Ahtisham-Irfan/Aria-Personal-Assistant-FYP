from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider,
    QComboBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal


class SettingsPanel(QWidget):
    closed = Signal()
    settings_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        self.settings = {
            'voice_speed': 150,
            'voice_volume': 90,
            'language': 'English',
            'wake_word': 'Hey Aria',
            'dark_mode': True,
        }
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(
            "QWidget { background-color: #070B18; }"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Header ---
        header = QWidget()
        header.setFixedHeight(52)
        header.setStyleSheet(
            "background-color:#0D1425;"
            "border-bottom:1px solid #1E2D4A;"
        )
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 16, 0)

        title = QLabel("⚙  SETTINGS")
        title.setStyleSheet(
            "font-family:'Outfit';font-size:13px;"
            "font-weight:700;color:#EAF2FF;"
            "letter-spacing:2px;background:transparent;"
        )

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(
            "QPushButton{background:transparent;"
            "border:none;color:#4FD1FF;font-size:14px;}"
            "QPushButton:hover{color:#FF5F57;}"
        )
        close_btn.clicked.connect(self._close)

        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(close_btn)
        layout.addWidget(header)

        # --- Scroll ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        scroll.setStyleSheet(
            "QScrollArea{border:none;background:#070B18;}"
            "QScrollBar:vertical{width:4px;background:#070B18;}"
            "QScrollBar::handle:vertical{"
            "background:#1E2D4A;border-radius:2px;}"
        )

        content = QWidget()
        content.setStyleSheet("background:#070B18;")
        c = QVBoxLayout(content)
        c.setContentsMargins(16, 16, 16, 16)
        c.setSpacing(14)

        # APPEARANCE
        c.addWidget(self._sec("APPEARANCE"))
        theme_card = self._card()
        th = QHBoxLayout(theme_card)
        th.setContentsMargins(12, 12, 12, 12)
        tl = QLabel("🌙  Dark Mode")
        tl.setStyleSheet(
            "font-size:13px;color:#EAF2FF;background:transparent;"
        )
        self.theme_btn = QPushButton("ON")
        self.theme_btn.setFixedSize(52, 26)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self._toggle_style(self.theme_btn, True)
        self.theme_btn.clicked.connect(self._toggle_theme)
        th.addWidget(tl)
        th.addStretch()
        th.addWidget(self.theme_btn)
        c.addWidget(theme_card)

        # LANGUAGE
        c.addWidget(self._sec("LANGUAGE"))
        lang_card = self._card()
        ll = QVBoxLayout(lang_card)
        ll.setContentsMargins(12, 12, 12, 12)
        ll.setSpacing(8)
        lang_lbl = QLabel("🌐  Interface Language")
        lang_lbl.setStyleSheet(
            "font-size:13px;color:#EAF2FF;background:transparent;"
        )
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Urdu (اردو)"])
        self.lang_combo.setStyleSheet(self._cstyle())
        self.lang_combo.currentTextChanged.connect(
            lambda t: self.settings.update({
                'language': 'Urdu' if 'Urdu' in t else 'English'
            })
        )
        ll.addWidget(lang_lbl)
        ll.addWidget(self.lang_combo)
        c.addWidget(lang_card)

        # VOICE
        c.addWidget(self._sec("VOICE"))

        # Speed
        sp_card = self._card()
        sl = QVBoxLayout(sp_card)
        sl.setContentsMargins(12, 12, 12, 12)
        sl.setSpacing(8)
        sh = QHBoxLayout()
        sp_lbl = QLabel("🔊  Speaking Speed")
        sp_lbl.setStyleSheet(
            "font-size:13px;color:#EAF2FF;background:transparent;"
        )
        self.speed_val = QLabel("150 WPM")
        self.speed_val.setStyleSheet(
            "font-size:11px;color:#4FD1FF;"
            "font-family:'Outfit';background:transparent;"
        )
        sh.addWidget(sp_lbl)
        sh.addStretch()
        sh.addWidget(self.speed_val)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(80, 250)
        self.speed_slider.setValue(150)
        self._sslider(self.speed_slider)
        self.speed_slider.valueChanged.connect(
            lambda v: (
                self.speed_val.setText(f"{v} WPM"),
                self.settings.update({'voice_speed': v})
            )
        )
        hint = QHBoxLayout()
        for t, col in [
            ("🐢 Slow", "#2A4060"),
            ("Normal", "#4FD1FF"),
            ("Fast 🚀", "#2A4060")
        ]:
            lb = QLabel(t)
            lb.setStyleSheet(
                f"font-size:9px;color:{col};background:transparent;"
            )
            hint.addWidget(lb)
            if t != "Fast 🚀":
                hint.addStretch()
        sl.addLayout(sh)
        sl.addWidget(self.speed_slider)
        sl.addLayout(hint)
        c.addWidget(sp_card)

        # Volume
        vol_card = self._card()
        vl = QVBoxLayout(vol_card)
        vl.setContentsMargins(12, 12, 12, 12)
        vl.setSpacing(8)
        vh = QHBoxLayout()
        vl_lbl = QLabel("🎙  Voice Volume")
        vl_lbl.setStyleSheet(
            "font-size:13px;color:#EAF2FF;background:transparent;"
        )
        self.vol_val = QLabel("90%")
        self.vol_val.setStyleSheet(
            "font-size:11px;color:#4FD1FF;"
            "font-family:'Outfit';background:transparent;"
        )
        vh.addWidget(vl_lbl)
        vh.addStretch()
        vh.addWidget(self.vol_val)
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(90)
        self._sslider(self.vol_slider)
        self.vol_slider.valueChanged.connect(
            lambda v: (
                self.vol_val.setText(f"{v}%"),
                self.settings.update({'voice_volume': v})
            )
        )
        vl.addLayout(vh)
        vl.addWidget(self.vol_slider)
        c.addWidget(vol_card)

        # WAKE WORD
        c.addWidget(self._sec("WAKE WORD"))
        wk_card = self._card()
        wl = QVBoxLayout(wk_card)
        wl.setContentsMargins(12, 12, 12, 12)
        wl.setSpacing(8)
        wk_lbl = QLabel("🎤  Trigger Phrase")
        wk_lbl.setStyleSheet(
            "font-size:13px;color:#EAF2FF;background:transparent;"
        )
        self.wake_combo = QComboBox()
        self.wake_combo.addItems(
            ["Hey Aria", "Hi Aria", "Ok Aria", "Aria"]
        )
        self.wake_combo.setStyleSheet(self._cstyle())
        wl.addWidget(wk_lbl)
        wl.addWidget(self.wake_combo)
        c.addWidget(wk_card)

        # ABOUT
        c.addWidget(self._sec("ABOUT"))
        ab_card = self._card()
        al = QVBoxLayout(ab_card)
        al.setContentsMargins(12, 12, 12, 12)
        al.setSpacing(6)
        for text, col in [
            ("◈  Aria v1.0", "#EAF2FF"),
            ("By Ahmad Ali", "#4FD1FF"),
            ("UAF FYP · 2025", "#7C5CFF"),
            ("Windows 11 Assistant", "#2A4060"),
        ]:
            lb = QLabel(text)
            lb.setStyleSheet(
                f"font-size:12px;color:{col};background:transparent;"
            )
            al.addWidget(lb)
        c.addWidget(ab_card)
        c.addStretch()

        # Save button
        save_btn = QPushButton("💾  Save Settings")
        save_btn.setFixedHeight(44)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(
            "QPushButton{"
            "background-color:#4FD1FF;border:none;"
            "border-radius:10px;font-family:'Outfit';"
            "font-size:13px;font-weight:700;color:#070B18;}"
            "QPushButton:hover{background-color:#38B6E8;}"
            "QPushButton:pressed{background-color:#2A9FD0;}"
        )
        save_btn.clicked.connect(self._save)
        c.addWidget(save_btn)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _sec(self, text):
        l = QLabel(text)
        l.setStyleSheet(
            "font-family:'Outfit';font-size:10px;"
            "color:#4FD1FF;letter-spacing:3px;"
            "padding-top:4px;background:transparent;"
        )
        return l

    def _card(self):
        w = QWidget()
        w.setStyleSheet(
            "QWidget{"
            "background-color:#0D1830;"
            "border:1px solid #1E2D4A;"
            "border-radius:10px;}"
        )
        return w

    def _cstyle(self):
        return (
            "QComboBox{"
            "background-color:#12182B;"
            "border:1px solid #2A3555;"
            "border-radius:8px;"
            "padding:7px 12px;"
            "font-size:12px;color:#EAF2FF;"
            "font-family:'Outfit';}"
            "QComboBox:hover{border-color:#4FD1FF;}"
            "QComboBox::drop-down{border:none;width:24px;}"
            "QComboBox QAbstractItemView{"
            "background-color:#0D1830;"
            "border:1px solid #2A3555;"
            "color:#EAF2FF;"
            "selection-background-color:#1E2D4A;"
            "font-family:'Outfit';font-size:12px;}"
        )

    def _sslider(self, s):
        s.setStyleSheet(
            "QSlider::groove:horizontal{"
            "height:5px;background:#1E2D4A;border-radius:2px;}"
            "QSlider::handle:horizontal{"
            "width:16px;height:16px;"
            "background:#4FD1FF;border-radius:8px;"
            "margin:-6px 0;border:2px solid #EAF2FF;}"
            "QSlider::sub-page:horizontal{"
            "background:#4FD1FF;border-radius:2px;}"
        )

    def _toggle_style(self, btn, state):
        if state:
            btn.setText("ON")
            btn.setStyleSheet(
                "QPushButton{"
                "background-color:#4FD1FF;"
                "border:none;border-radius:13px;"
                "font-size:11px;font-weight:700;"
                "color:#070B18;}"
            )
        else:
            btn.setText("OFF")
            btn.setStyleSheet(
                "QPushButton{"
                "background-color:#12182B;"
                "border:1px solid #2A3555;"
                "border-radius:13px;"
                "font-size:11px;color:#2A4060;}"
            )

    def _toggle_theme(self):
        self.settings['dark_mode'] = \
            not self.settings['dark_mode']
        self._toggle_style(
            self.theme_btn,
            self.settings['dark_mode']
        )

    def _save(self):
        self.settings['wake_word'] = \
            self.wake_combo.currentText()
        self.settings_changed.emit(self.settings)
        self._close()

    def _close(self):
        self.hide()
        self.closed.emit()

    def load_settings(self, settings):
        self.settings.update(settings)
        self.speed_slider.setValue(
            settings.get('voice_speed', 150)
        )
        self.vol_slider.setValue(
            settings.get('voice_volume', 90)
        )
        self._toggle_style(
            self.theme_btn,
            settings.get('dark_mode', True)
        )