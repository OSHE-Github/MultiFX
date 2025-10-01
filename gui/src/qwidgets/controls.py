from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QPainterPath, QPolygonF, QBrush, QColor
from PyQt5.QtCore import QRect, QPoint
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W
from styles import (
    color_foreground, color_top, color_top_inactive, color_mid,
    color_mid_inactive, color_bot, color_bot_inactive
)
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
    def __init__(self):
        super().__init__()
        self.setFixedSize(SCREEN_W // 6, SCREEN_H // 12)

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(color_foreground, 5)
        painter.setPen(pen)

        # Border
        rect = QRect(0, 0, self.width(), self.height())
        painter.drawRect(rect)

        # Binding
        self.drawBind(RotaryEncoder.TOP)
        self.drawBind(RotaryEncoder.MIDDLE)
        self.drawBind(RotaryEncoder.BOTTOM)

    def drawBind(self, enc: RotaryEncoderData):
        PADDING = 16
        RADIUS = 8
        MARGIN = 2

        painter = QPainter(self)
        color = enc.inactive if enc.bind == "" else enc.color
        pen = QPen(color, 1)
        painter.setPen(pen)
        brush = QBrush(color)

        center = QPoint(PADDING, PADDING + enc.index * (2 * RADIUS + MARGIN))
        oct = Octagon(center, 8)
        painter.drawPolygon(oct)
        path = QPainterPath()
        path.addPolygon(QPolygonF(oct))
        painter.fillPath(path, brush)
