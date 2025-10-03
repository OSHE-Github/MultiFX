from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import QRect
from typing import List
from styles import color_foreground, color_background
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W
from qwidgets.controls import ControlDisplay


class BreadcrumbsBar(QWidget):
    """Bar on bottom of all screens that shows how teh user got to their
    current screen

    Shows maximum of 2 items, bolds and underlines the last item.
    """
    instance: QWidget = None
    crumbs: List[str] = []

    LINE_WIDTH = 3
    # Fill the left side of ControlDsplay
    REL_H = ControlDisplay.REL_H
    REL_W = 1 - ControlDisplay.REL_W

    def __init__(self, start: str):
        super().__init__()
        self.setFixedSize(
            int(SCREEN_W * self.REL_W),
            int(SCREEN_H * self.REL_H)
        )
        BreadcrumbsBar.crumbs = [start]
        if (BreadcrumbsBar.instance is not None):
            print("Multiple of BreadcrumbsBar exist! Please only have one")
        BreadcrumbsBar.instance = self

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(color_foreground, self.LINE_WIDTH)
        painter.setPen(pen)

        # Border
        rect = QRect(
            -self.LINE_WIDTH,  # Shift left to hide left line
            0,
            self.width() + 2 * self.LINE_WIDTH,  # Double to overlap
            self.height() + self.LINE_WIDTH,
        )
        painter.fillRect(rect, color_background)
        painter.drawRect(rect)
