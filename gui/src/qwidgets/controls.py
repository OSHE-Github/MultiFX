from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPainter, QPen, QPainterPath, QPolygonF, QBrush, QColor
from PyQt5.QtCore import QRect, QPoint, Qt
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W
from styles import (
    color_foreground, color_top, color_top_inactive, color_mid,
    color_mid_inactive, color_bot, color_bot_inactive, styles_bind,
    styles_bind_inactive
)
from typing import List
from qwidgets.graphics_utils import Octagon


class RotaryEncoderData:
    def __init__(self, index: int, color: QColor, inactive: QColor,
                 binding: str):
        self.index = index
        self.color = color
        self.inactive = inactive
        self.bind = binding


class RotaryEncoder:
    TOP = RotaryEncoderData(0, color_top, color_top_inactive, "")
    MIDDLE = RotaryEncoderData(1, color_mid, color_mid_inactive, "")
    BOTTOM = RotaryEncoderData(2, color_bot, color_bot_inactive, "")


class ControlDisplay(QWidget):
    PADDING = 16
    RADIUS = 8
    MARGIN = 2

    REL_W = 1/5
    REL_H = 1/12

    def __init__(self):
        super().__init__()
        self.setFixedSize(
            int(SCREEN_W * self.REL_W),
            int(SCREEN_H * self.REL_H)
        )
        self.labels: List[QLabel] = [None, None, None]
        self.drawLabel(RotaryEncoder.TOP)
        self.drawLabel(RotaryEncoder.MIDDLE)
        self.drawLabel(RotaryEncoder.BOTTOM)

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(color_foreground, 5)
        painter.setPen(pen)

        # Border
        rect = QRect(0, 0, self.width(), self.height())
        painter.drawRect(rect)

        # Binding
        self.drawSymbol(RotaryEncoder.TOP)
        self.drawSymbol(RotaryEncoder.MIDDLE)
        self.drawSymbol(RotaryEncoder.BOTTOM)

    def drawSymbol(self, enc: RotaryEncoderData):
        """Draws the circle for an encoder's binding.

        Must be done in paintEvent.
        """

        color = enc.inactive if enc.bind == "" else enc.color

        painter = QPainter(self)
        pen = QPen(color, 1)
        painter.setPen(pen)
        brush = QBrush(color)

        # Encoder symbol
        center = QPoint(
            self.PADDING,
            self.PADDING + enc.index * (2 * self.RADIUS + self.MARGIN)
        )
        oct = Octagon(center, 8)
        path = QPainterPath()
        path.addPolygon(QPolygonF(oct))
        painter.fillPath(path, brush)

    def drawLabel(self, enc: RotaryEncoderData):
        """Draws label for an encoder's mapping

        Must be done outside paintEvent
        """

        active = enc.bind != ""
        display = enc.bind if active else "N/A"
        # Label
        label = QLabel(display, self)
        self.labels[enc.index] = label
        label.setAlignment(Qt.AlignLeft)
        label.setStyleSheet(styles_bind if active else styles_bind_inactive)
        label.adjustSize()
        topLeft = QPoint(
            self.PADDING + self.MARGIN + self.RADIUS,
            self.RADIUS + enc.index * (2 * self.RADIUS + self.MARGIN)
        )
        label.move(topLeft)
