from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPainter, QPen, QPainterPath, QPolygonF, QBrush, QColor
from PyQt5.QtCore import QRect, QPoint, Qt
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W
from styles import (
    color_foreground, color_top, color_top_inactive, color_mid,
    color_mid_inactive, color_bot, color_bot_inactive, styles_bind,
    styles_bind_inactive, color_background, ControlDisplayStyle
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
    instance: QWidget = None

    def __init__(self):
        super().__init__()
        self.setFixedSize(
            int(SCREEN_W * ControlDisplayStyle.REL_W),
            int(SCREEN_H * ControlDisplayStyle.REL_H)
        )
        self.labels: List[QLabel] = [None, None, None]
        self.drawLabel(RotaryEncoder.TOP)
        self.drawLabel(RotaryEncoder.MIDDLE)
        self.drawLabel(RotaryEncoder.BOTTOM)
        if (ControlDisplay.instance is not None):
            print("Multiple of ControlDisplay exist! Please only have one")
        ControlDisplay.instance = self

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(color_foreground, ControlDisplayStyle.LINE_WIDTH)
        painter.setPen(pen)

        # Border
        # Add LINE_WIDTH to extend outside of screen so only top and left
        # border is visible
        rect = QRect(0, 0, self.width() + ControlDisplayStyle.LINE_WIDTH,
                     self.height() + ControlDisplayStyle.LINE_WIDTH)
        painter.fillRect(rect, color_background)
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
            ControlDisplayStyle.PADDING,
            ControlDisplayStyle.PADDING + enc.index * 
            (2 * ControlDisplayStyle.RADIUS + ControlDisplayStyle.MARGIN)
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
            ControlDisplayStyle.PADDING + ControlDisplayStyle.MARGIN
            + ControlDisplayStyle.RADIUS,
            ControlDisplayStyle.RADIUS + enc.index *
            (2 * ControlDisplayStyle.RADIUS + ControlDisplayStyle.MARGIN)
        )
        label.move(topLeft)

    def setBind(enc: RotaryEncoderData, newBind: str) -> None:
        """Sets encoder binding and redraws control display.

        Should be called in any scenario that rebinds an encoder
        """
        enc.bind = newBind
        inst = ControlDisplay.instance
        inst.labels[enc.index].setText(newBind)
        active = enc.bind != ""
        inst.labels[enc.index].setStyleSheet(
                styles_bind if active else styles_bind_inactive)
        inst.labels[enc.index].adjustSize()
        inst.repaint()
