from typing import Dict
from enum import Enum
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import QRect
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W
from styles import color_foreground


class RotaryEncoder(Enum):
    TOP = 0
    MIDDLE = 1
    BOTTOM = 2


class ControlDisplay(QWidget):
    # Display of mappings for display.
    # Empty strings will default to "N/A"
    # Keep string length <= 10 characters
    mappings: Dict[RotaryEncoder, str] = [
        {RotaryEncoder.TOP, ""},
        {RotaryEncoder.MIDDLE, ""},
        {RotaryEncoder.BOTTOM, ""}
    ]

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
