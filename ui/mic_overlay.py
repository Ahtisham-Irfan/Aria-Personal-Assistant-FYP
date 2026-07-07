from PySide6.QtWidgets import QWidget
from PySide6.QtCore import (
    Qt, QTimer, QPointF, QRectF, Signal
)
from PySide6.QtGui import (
    QPainter, QPen, QColor, QBrush,
    QRadialGradient, QFont, QConicalGradient,
    QPainterPath
)
import math
import random


class MicOverlay(QWidget):
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

        # Colors defined FIRST
        # before any method that uses them
        self.C_BG = QColor("#070B18")
        self.C_CYAN = QColor("#4FD1FF")
        self.C_VIOLET = QColor("#7C5CFF")
        self.C_INDIGO = QColor("#3B4DC8")
        self.C_TEXT = QColor("#EAF2FF")
        self.C_DIM = QColor(147, 164, 195, 100)

        # Animation state
        self._t = 0.0
        self._breathe = 0.0
        self._rot1 = 0.0
        self._rot2 = 0.0
        self._rot3 = 0.0
        self._visible = False

        # Waveform bars
        self._bars = [
            {
                'phase': (i / 28) * math.pi * 2,
                'speed': 1.5 + random.random() * 2.5,
                'amp': 0.5 + random.random() * 0.5,
                'h': 4.0,
            }
            for i in range(28)
        ]

        # Particles
        self._particles = []
        self._init_particles()

        # Thinking dots
        self._dots = [
            {'offset': i * 1.2}
            for i in range(4)
        ]

        self._timer = QTimer()
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._tick)



    def _init_particles(self):
        self._particles = []
        for _ in range(55):
            self._particles.append(
                self._make_particle()
            )

    def _make_particle(self):
        angle = random.random() * math.pi * 2
        orbit_r = 90 + random.random() * 75
        return {
            'angle': angle,
            'orbit_r': orbit_r,
            'orbit_speed': (
                random.random() - 0.5
            ) * 0.004,
            'size': 0.8 + random.random() * 2,
            'life': random.random(),
            'max_life': 0.6 + random.random() * 1.2,
            'color': (
                self.C_CYAN
                if random.random() > 0.5
                else self.C_VIOLET
            ),
        }

    def show_overlay(self):
        self._visible = True
        if self.parent():
            self.resize(self.parent().size())
        self.raise_()
        self.show()
        self._timer.start()
        self.update()

    def hide_overlay(self):
        self._visible = False
        self._timer.stop()
        self.hide()

    def resizeEvent(self, event):
        if self.parent():
            self.resize(self.parent().size())

    def _tick(self):
        self._t += 0.018
        self._breathe += 0.04
        self._rot1 += 0.012
        self._rot2 -= 0.009
        self._rot3 += 0.004

        # Update bars
        for b in self._bars:
            target = (
                6 + math.sin(
                    self._t * b['speed']
                    + b['phase']
                ) * 14 * b['amp']
                + math.sin(
                    self._t * 2.1
                    + b['phase'] * 1.3
                ) * 5
            )
            b['h'] += (target - b['h']) * 0.15

        # Update particles
        for p in self._particles:
            p['angle'] += p['orbit_speed']
            p['life'] += 0.008
            if p['life'] > p['max_life']:
                new = self._make_particle()
                p.update(new)

        self.update()

    def mousePressEvent(self, event):
        cx = self.width() // 2
        cy = self.height() // 2

        # Cancel button hit test
        btn_w, btn_h = 120, 34
        btn_x = cx - btn_w // 2
        btn_y = cy + 165
        if (
            btn_x <= event.x() <= btn_x + btn_w
            and btn_y <= event.y() <= btn_y + btn_h
        ):
            self.cancelled.emit()
            self.hide_overlay()

    def paintEvent(self, event):
        if not self._visible:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        w = self.width()
        h = self.height()
        cx = w // 2
        cy = h // 2

        # Background
        p.fillRect(0, 0, w, h, QColor(7, 11, 24, 230))

        # Radial bg glow
        bg_glow = QRadialGradient(
            QPointF(cx, cy), 240
        )
        bg_glow.setColorAt(
            0, QColor(79, 209, 255, 14)
        )
        bg_glow.setColorAt(
            0.5, QColor(60, 77, 200, 8)
        )
        bg_glow.setColorAt(
            1, QColor(7, 11, 24, 0)
        )
        p.setBrush(QBrush(bg_glow))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), 280, 280)

        self._draw_particles(p, cx, cy)
        self._draw_rings(p, cx, cy)
        self._draw_thinking_dots(p, cx, cy)
        self._draw_orb(p, cx, cy)
        self._draw_waveform(p, cx, cy)
        self._draw_text(p, cx, cy)
        self._draw_cancel_btn(p, cx, cy)

        p.end()

    def _draw_particles(self, p, cx, cy):
        p.setPen(Qt.NoPen)
        for pt in self._particles:
            px = cx + math.cos(
                pt['angle']
            ) * pt['orbit_r']
            py = cy + math.sin(
                pt['angle']
            ) * pt['orbit_r']

            life_frac = pt['life'] / pt['max_life']
            alpha = int(
                math.sin(life_frac * math.pi)
                * 200
            )
            c = QColor(pt['color'])
            c.setAlpha(alpha)
            p.setBrush(QBrush(c))
            size = pt['size']
            p.drawEllipse(
                QPointF(px, py), size, size
            )

    def _draw_rings(self, p, cx, cy):
        pulse = math.sin(self._breathe) * 6

        # Outer dashed ring
        p.save()
        p.translate(cx, cy)
        p.rotate(math.degrees(self._rot3))
        pen = QPen(QColor(79, 209, 255, 28))
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(
            QPointF(0, 0), 170 + pulse, 170 + pulse
        )
        p.restore()

        # Spinning arc 1 — cyan
        p.save()
        p.translate(cx, cy)
        p.rotate(math.degrees(self._rot1))
        pen1 = QPen(QColor(79, 209, 255, 160))
        pen1.setWidth(2)
        pen1.setStyle(Qt.SolidLine)
        pen1.setCapStyle(Qt.RoundCap)
        p.setPen(pen1)
        p.setBrush(Qt.NoBrush)
        p.drawArc(
            QRectF(-145, -145, 290, 290),
            0, 110 * 16
        )
        p.drawArc(
            QRectF(-145, -145, 290, 290),
            180 * 16, 80 * 16
        )
        p.restore()

        # Spinning arc 2 — violet (reverse)
        p.save()
        p.translate(cx, cy)
        p.rotate(math.degrees(self._rot2))
        pen2 = QPen(QColor(124, 92, 255, 140))
        pen2.setWidth(2)
        pen2.setCapStyle(Qt.RoundCap)
        p.setPen(pen2)
        p.drawArc(
            QRectF(-126, -126, 252, 252),
            60 * 16, 120 * 16
        )
        p.drawArc(
            QRectF(-126, -126, 252, 252),
            240 * 16, 80 * 16
        )
        p.restore()

        # Breathing ring
        br = 104 + math.sin(self._breathe) * 6
        alpha = int(
            (0.22 + math.sin(self._breathe) * 0.08)
            * 255
        )
        pen3 = QPen(QColor(79, 209, 255, alpha))
        pen3.setWidth(1)
        p.setPen(pen3)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), br, br)

        # Orbiting dots
        dot_data = [
            (self._rot1 * 1.3, 145, self.C_CYAN, 5),
            (
                self._rot1 * 1.3 + math.pi,
                145, self.C_CYAN, 4
            ),
            (-self._rot2 * 0.9, 126, self.C_VIOLET, 4),
            (
                -self._rot2 * 0.9 + math.pi * 0.7,
                126, self.C_VIOLET, 3
            ),
        ]
        for angle, r, color, size in dot_data:
            dx = cx + math.cos(angle) * r
            dy = cy + math.sin(angle) * r
            # Glow
            glow = QColor(color)
            glow.setAlpha(60)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(glow))
            p.drawEllipse(
                QPointF(dx, dy), size + 2, size + 2
            )
            # Dot
            p.setBrush(QBrush(color))
            p.drawEllipse(
                QPointF(dx, dy), size * 0.6, size * 0.6
            )

    def _draw_thinking_dots(self, p, cx, cy):
        positions = [
            (cx - 136, cy - 22),
            (cx + 136, cy - 22),
            (cx - 115, cy + 55),
            (cx + 115, cy + 55),
        ]
        for i, (px, py) in enumerate(positions):
            pulse = (
                math.sin(self._t * 1.8 + self._dots[i]['offset'])
                * 0.5 + 0.5
            )
            # Outer glow
            c = QColor(self.C_VIOLET)
            c.setAlpha(int(80 + pulse * 120))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(c))
            r = 2.5 + pulse * 1.5
            p.drawEllipse(QPointF(px, py), r, r)
            # Inner dot
            c2 = QColor(self.C_VIOLET)
            c2.setAlpha(int(180 + pulse * 60))
            p.setBrush(QBrush(c2))
            p.drawEllipse(QPointF(px, py), 1.5, 1.5)

    def _draw_orb(self, p, cx, cy):
        orb_r = 56 + math.sin(self._breathe) * 3

        # Glow layers
        for radius, alpha in [
            (82, 28), (65, 45), (50, 65)
        ]:
            glow = QRadialGradient(
                QPointF(cx, cy), radius
            )
            glow.setColorAt(
                0, QColor(79, 209, 255, alpha)
            )
            glow.setColorAt(
                1, QColor(79, 209, 255, 0)
            )
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(glow))
            p.drawEllipse(
                QPointF(cx, cy), radius, radius
            )

        # Main orb fill
        orb_fill = QRadialGradient(
            QPointF(cx - 8, cy - 8), 10,
            QPointF(cx, cy), orb_r
        )
        orb_fill.setColorAt(0, QColor("#1A2545"))
        orb_fill.setColorAt(0.6, QColor("#0D1830"))
        orb_fill.setColorAt(1, QColor("#07101F"))
        p.setBrush(QBrush(orb_fill))
        pen_orb = QPen(QColor(79, 209, 255, 130))
        pen_orb.setWidth(2)
        p.setPen(pen_orb)
        p.drawEllipse(
            QPointF(cx, cy), orb_r, orb_r
        )

        # Mic icon
        p.save()
        p.translate(cx, cy)
        pen_mic = QPen(self.C_CYAN)
        pen_mic.setWidth(3)
        pen_mic.setCapStyle(Qt.RoundCap)
        pen_mic.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen_mic)
        p.setBrush(Qt.NoBrush)

        # Body rounded rect
        body = QPainterPath()
        body.addRoundedRect(
            QRectF(-9, -22, 18, 24), 9, 9
        )
        p.drawPath(body)

        # Arc
        p.drawArc(
            QRectF(-15, -6, 30, 22),
            0, -180 * 16
        )

        # Stem
        p.drawLine(
            QPointF(0, 16), QPointF(0, 24)
        )

        # Base
        p.drawLine(
            QPointF(-10, 24), QPointF(10, 24)
        )
        p.restore()

    def _draw_waveform(self, p, cx, cy):
        bar_w = 5
        gap = 2.5
        n = len(self._bars)
        total_w = n * (bar_w + gap) - gap
        start_x = cx - total_w / 2
        base_y = cy + 95

        for i, b in enumerate(self._bars):
            h = max(3, b['h'])
            x = start_x + i * (bar_w + gap)

            life = math.sin(
                self._t * b['speed'] + b['phase']
            ) * 0.5 + 0.5
            alpha = int(100 + life * 140)

            # Glow bar
            glow_c = QColor(79, 209, 255, int(alpha * 0.35))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(glow_c))
            p.drawRoundedRect(
                QRectF(x - 0.5, base_y - h/2 - 0.5,
                       bar_w + 1, h + 1),
                2, 2
            )

            # Main bar
            bar_c = QColor(79, 209, 255, alpha)
            p.setBrush(QBrush(bar_c))
            p.drawRoundedRect(
                QRectF(x, base_y - h/2, bar_w, h),
                2, 2
            )

    def _draw_text(self, p, cx, cy):
        # "ARIA IS LISTENING"
        font = QFont("Outfit", 11)
        font.setLetterSpacing(
            QFont.AbsoluteSpacing, 5
        )
        p.setFont(font)
        pulse_a = int(
            (0.7 + math.sin(self._breathe) * 0.2)
            * 255
        )
        p.setPen(QColor(79, 209, 255, pulse_a))
        p.drawText(
            QRectF(cx - 180, cy - 175, 360, 28),
            Qt.AlignCenter,
            "ARIA IS LISTENING"
        )

        # "SPEAK NOW"
        font2 = QFont("Outfit", 9)
        font2.setLetterSpacing(
            QFont.AbsoluteSpacing, 4
        )
        p.setFont(font2)
        p.setPen(QColor(79, 209, 255, 90))
        p.drawText(
            QRectF(cx - 120, cy + 125, 240, 24),
            Qt.AlignCenter,
            "SPEAK NOW..."
        )

    def _draw_cancel_btn(self, p, cx, cy):
        btn_w, btn_h = 120, 34
        btn_x = cx - btn_w // 2
        btn_y = cy + 165

        # Button bg
        p.setBrush(QBrush(QColor(13, 20, 40, 200)))
        pen_btn = QPen(QColor(79, 209, 255, 55))
        pen_btn.setWidth(1)
        p.setPen(pen_btn)
        p.drawRoundedRect(
            QRectF(btn_x, btn_y, btn_w, btn_h),
            17, 17
        )

        # Button text
        font3 = QFont("Outfit", 10)
        font3.setLetterSpacing(
            QFont.AbsoluteSpacing, 3
        )
        p.setFont(font3)
        p.setPen(QColor(147, 164, 195, 180))
        p.drawText(
            QRectF(btn_x, btn_y, btn_w, btn_h),
            Qt.AlignCenter,
            "✕  CANCEL"
        )