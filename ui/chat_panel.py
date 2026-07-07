import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLabel, QPushButton,
    QLineEdit, QSizePolicy, QFileDialog, QMenu
)
from PySide6.QtCore import Qt, QDateTime, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QAction


class MicButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(42, 42)
        self.setCursor(Qt.PointingHandCursor)
        self._hovered = False

    def enterEvent(self, e):
        self._hovered = True
        self.update()

    def leaveEvent(self, e):
        self._hovered = False
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.translate(self.width()/2, self.height()/2)
        if self._hovered:
            p.setBrush(QColor("#1A2545"))
            p.setPen(QPen(QColor("#4FD1FF"), 1))
        else:
            p.setBrush(QColor("#12182B"))
            p.setPen(QPen(QColor("#2A3555"), 1))
        p.drawEllipse(QRectF(-15,-15,30,30))
        col = QColor("#4FD1FF") if self._hovered else QColor("#2A4060")
        pen = QPen(col, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(-3.5,-9,7,11),3.5,3.5)
        p.drawArc(QRectF(-6,-3,12,10),0,-180*16)
        p.drawLine(QPointF(0,7),QPointF(0,9))
        p.drawLine(QPointF(-3.5,9),QPointF(3.5,9))
        p.end()


class AttachButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(42, 42)
        self.setCursor(Qt.PointingHandCursor)
        self._hovered = False

    def enterEvent(self, e):
        self._hovered = True
        self.update()

    def leaveEvent(self, e):
        self._hovered = False
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.translate(self.width()/2, self.height()/2)
        if self._hovered:
            p.setBrush(QColor("#1A2545"))
            p.setPen(QPen(QColor("#4FD1FF"), 1))
        else:
            p.setBrush(QColor("#12182B"))
            p.setPen(QPen(QColor("#2A3555"), 1))
        p.drawEllipse(QRectF(-15,-15,30,30))
        col = QColor("#4FD1FF") if self._hovered else QColor("#4FD1FF")
        pen = QPen(col, 2, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawLine(QPointF(-4,6),QPointF(4,6))
        p.drawLine(QPointF(4,6),QPointF(4,-4))
        p.drawArc(QRectF(-4,-8,8,8),0,180*16)
        p.drawLine(QPointF(-4,-4),QPointF(-4,8))
        p.drawArc(QRectF(-2,4,12,8),90*16,180*16)
        p.end()


class ChatBubble(QWidget):
    def __init__(self, text, is_user=False, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(4)

        time_str = QDateTime.currentDateTime().toString("hh:mm AP")
        sender = "You" if is_user else "Aria"
        align = Qt.AlignRight if is_user else Qt.AlignLeft

        time_label = QLabel(f"{sender}  {time_str}")
        time_label.setAlignment(align)
        time_label.setStyleSheet(
            "font-family:'Outfit';font-size:10px;"
            "color:#2A4060;letter-spacing:0.5px;padding:0 4px;"
        )

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0,0,0,0)
        row_layout.setSpacing(8)

        avatar = QLabel()
        avatar.setFixedSize(30,30)
        avatar.setAlignment(Qt.AlignCenter)
        if is_user:
            avatar.setText("U")
            avatar.setStyleSheet(
                "background-color:#4FD1FF;color:#070B18;"
                "border-radius:8px;font-family:'Outfit';"
                "font-size:13px;font-weight:700;"
            )
        else:
            avatar.setText("◈")
            avatar.setStyleSheet(
                "background-color:#0D1830;color:#4FD1FF;"
                "border:1px solid #1E2D4A;"
                "border-radius:8px;font-size:14px;"
            )

        msg = QLabel(text)
        msg.setWordWrap(True)
        msg.setMaximumWidth(440)
        msg.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if is_user:
            msg.setStyleSheet(
                "background-color:#4FD1FF;"
                "color:#070B18;"
                "border-radius:12px;"
                "border-bottom-right-radius:3px;"
                "padding:10px 16px;"
                "font-family:'Outfit';font-size:13px;"
                "font-weight:500;"
            )
        else:
            msg.setStyleSheet(
                "background-color:#0D1830;"
                "color:#EAF2FF;"
                "border-radius:12px;"
                "border-bottom-left-radius:3px;"
                "padding:10px 16px;"
                "font-family:'Outfit';font-size:13px;"
                "border:1px solid #1E2D4A;"
            )

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        if is_user:
            row_layout.addWidget(spacer)
            row_layout.addWidget(msg)
            row_layout.addWidget(avatar)
        else:
            row_layout.addWidget(avatar)
            row_layout.addWidget(msg)
            row_layout.addWidget(spacer)

        layout.addWidget(time_label)
        layout.addWidget(row)


class TypingIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(8)
        av = QLabel("◈")
        av.setFixedSize(30,30)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(
            "background-color:#0D1830;color:#4FD1FF;"
            "border:1px solid #1E2D4A;"
            "border-radius:8px;font-size:14px;"
        )
        self.dots = QLabel("Aria is thinking ●")
        self.dots.setStyleSheet(
            "background-color:#0D1830;color:#2A4060;"
            "border-radius:12px;border-bottom-left-radius:3px;"
            "padding:10px 16px;font-family:'Outfit';font-size:13px;"
            "border:1px solid #1E2D4A;"
        )
        sp = QWidget()
        sp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(av)
        layout.addWidget(self.dots)
        layout.addWidget(sp)
        self._step = 0
        self._t = QTimer()
        self._t.timeout.connect(self._tick)
        self._t.start(400)

    def _tick(self):
        opts = ["Aria is thinking ●  ","Aria is thinking ●● ","Aria is thinking ●●●"]
        self.dots.setText(opts[self._step % 3])
        self._step += 1

    def stop(self):
        self._t.stop()


class ChatPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._typing_widget = None
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(
            "QScrollArea{border:none;background-color:#070B18;}"
            "QScrollBar:vertical{width:4px;background:#070B18;}"
            "QScrollBar::handle:vertical{background:#1E2D4A;border-radius:2px;}"
            "QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0px;}"
        )

        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background-color:#070B18;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(20,20,20,20)
        self.chat_layout.setSpacing(14)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.chat_container)

        date_lbl = QLabel("TODAY")
        date_lbl.setAlignment(Qt.AlignCenter)
        date_lbl.setStyleSheet(
            "font-family:'Outfit';font-size:10px;"
            "color:#1E2D4A;letter-spacing:3px;padding:4px 0;"
        )
        self.chat_layout.addWidget(date_lbl)
        self.add_aria_message(
            "Hello! I am Aria 😊\n"
            "📎 Drag & drop any file or image here and I will analyze it!\n"
            "🎤 Click mic or say Hey Aria to speak."
        )

        # Input area
        input_widget = QWidget()
        input_widget.setFixedHeight(72)
        input_widget.setStyleSheet(
            "QWidget{background-color:#0D1425;"
            "border-top:1px solid #1E2D4A;}"
        )
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(12,12,12,12)
        input_layout.setSpacing(8)

        self.attach_btn = AttachButton()
        self.attach_btn.mousePressEvent = \
            lambda e: self._show_attach_menu()

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Ask Aria anything...")
        self.text_input.setFixedHeight(42)
        self.text_input.setStyleSheet(
            "QLineEdit{"
            "background-color:#12182B;"
            "border:1px solid #2A3555;"
            "border-radius:12px;"
            "padding:8px 18px;"
            "font-family:'Outfit';font-size:13px;"
            "color:#EAF2FF;}"
            "QLineEdit:focus{border-color:#4FD1FF;"
            "background-color:#1A2238;}"
        )
        self.text_input.returnPressed.connect(
            self.send_message
        )

        self.mic_btn = MicButton()
        self.mic_btn.mousePressEvent = \
            lambda e: self.on_mic_pressed()

        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedSize(80, 42)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setStyleSheet(
            "QPushButton{"
            "background-color:#4FD1FF;border:none;"
            "border-radius:12px;font-family:'Outfit';"
            "font-size:13px;font-weight:700;color:#070B18;}"
            "QPushButton:hover{background-color:#38B6E8;}"
            "QPushButton:pressed{background-color:#2A9FD0;}"
        )
        self.send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.attach_btn)
        input_layout.addWidget(self.text_input)
        input_layout.addWidget(self.mic_btn)
        input_layout.addWidget(self.send_btn)

        layout.addWidget(self.scroll_area)
        layout.addWidget(input_widget)

        from ui.mic_overlay import MicOverlay
        self.mic_overlay = MicOverlay(self)
        self.mic_overlay.hide()
        self.mic_overlay.cancelled.connect(
            self.on_overlay_cancelled
        )

    def _show_attach_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu{background-color:#0D1830;"
            "border:1px solid #4FD1FF;"
            "border-radius:10px;padding:6px;}"
            "QMenu::item{color:#EAF2FF;"
            "font-family:'Outfit';font-size:13px;"
            "padding:8px 16px;border-radius:6px;}"
            "QMenu::item:selected{background-color:#1E2D4A;}"
        )
        for label, func in [
            ("🖼  Image / Photo", self._attach_image),
            ("📄  PDF Document", self._attach_pdf),
            ("📝  Word Document", self._attach_word),
            ("📋  Text / Code File", self._attach_text),
            ("📁  Any File", self._attach_any),
        ]:
            a = QAction(label, self)
            a.triggered.connect(func)
            menu.addAction(a)

        pos = self.attach_btn.mapToGlobal(
            self.attach_btn.rect().topLeft()
        )
        from PySide6.QtCore import QPoint
        menu.exec(pos - QPoint(0, menu.sizeHint().height()))

    def _attach_image(self):
        p, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if p: self._process_file(p)

    def _attach_pdf(self):
        p, _ = QFileDialog.getOpenFileName(
            self, "Select PDF", "", "PDF (*.pdf)"
        )
        if p: self._process_file(p)

    def _attach_word(self):
        p, _ = QFileDialog.getOpenFileName(
            self, "Select Word", "",
            "Word (*.docx *.doc)"
        )
        if p: self._process_file(p)

    def _attach_text(self):
        p, _ = QFileDialog.getOpenFileName(
            self, "Select File", "",
            "Text/Code (*.txt *.py *.js *.html *.css *.json *.csv)"
        )
        if p: self._process_file(p)

    def _attach_any(self):
        p, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*)"
        )
        if p: self._process_file(p)

    def _process_file(self, file_path):
        self.add_user_message(
            f"📎 {os.path.basename(file_path)}"
        )
        self.show_typing()
        if hasattr(self.parent_window, 'analyze_file'):
            self.parent_window.analyze_file(file_path)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self.chat_container.setStyleSheet(
                "background-color:#0D1830;"
                "border:2px dashed #4FD1FF;"
            )

    def dragLeaveEvent(self, e):
        self.chat_container.setStyleSheet(
            "background-color:#070B18;"
        )

    def dropEvent(self, e):
        self.chat_container.setStyleSheet(
            "background-color:#070B18;"
        )
        for url in e.mimeData().urls():
            fp = url.toLocalFile()
            if fp:
                self._process_file(fp)

    def on_mic_pressed(self):
        self.mic_overlay.show_overlay()
        if hasattr(self.parent_window, 'left_panel'):
            panel = self.parent_window.left_panel
            if not panel.is_listening:
                panel.toggle_listening()

    def on_overlay_cancelled(self):
        self.mic_overlay.hide_overlay()
        if hasattr(self.parent_window, 'speech'):
            self.parent_window.speech.stop_listening()
        if hasattr(self.parent_window, 'left_panel'):
            panel = self.parent_window.left_panel
            if panel.is_listening:
                panel.toggle_listening()

    def stop_overlay(self):
        self.mic_overlay.hide_overlay()

    def add_user_message(self, text):
        b = ChatBubble(text, is_user=True)
        self.chat_layout.addWidget(b)
        self.scroll_to_bottom()

    def add_aria_message(self, text):
        self.hide_typing()
        b = ChatBubble(text, is_user=False)
        self.chat_layout.addWidget(b)
        self.scroll_to_bottom()

    def show_typing(self):
        self.hide_typing()
        self._typing_widget = TypingIndicator()
        self.chat_layout.addWidget(self._typing_widget)
        self.scroll_to_bottom()

    def hide_typing(self):
        if self._typing_widget:
            self._typing_widget.stop()
            self._typing_widget.setParent(None)
            self._typing_widget = None

    def send_message(self):
        text = self.text_input.text().strip()
        if not text:
            return
        self.add_user_message(text)
        self.text_input.clear()
        self.show_typing()
        QTimer.singleShot(
            800, lambda: self._dispatch(text)
        )

    def _dispatch(self, text):
        if (
            self.parent_window
            and hasattr(self.parent_window, 'handle_command')
        ):
            self.parent_window.handle_command(text)
        else:
            self.hide_typing()
            self.add_aria_message(
                "I am not connected to the command processor."
            )

    def scroll_to_bottom(self):
        QTimer.singleShot(
            100,
            lambda: self.scroll_area
            .verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )
        )

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'mic_overlay'):
            self.mic_overlay.resize(self.size())