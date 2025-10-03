from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import QRect, Qt
from typing import List
from styles import (
    color_foreground, color_background, BreadcrumbsBarStyle, styles_crumbs
)
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W


class BreadcrumbsBar(QWidget):
    """Bar on bottom of all screens that shows how teh user got to their
    current screen

    Shows maximum of 2 items, bolds and underlines the last item.
    """
    instance: QWidget = None
    crumbs: List[str] = []

    def __init__(self, start: str):
        super().__init__()
        self.setFixedSize(
            int(SCREEN_W * BreadcrumbsBarStyle.REL_W),
            int(SCREEN_H * BreadcrumbsBarStyle.REL_H)
        )
        BreadcrumbsBar.crumbs = [start]
        if (BreadcrumbsBar.instance is not None):
            print("Multiple of BreadcrumbsBar exist! Please only have one")
        BreadcrumbsBar.instance = self
        self.drawLabel()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(color_foreground, BreadcrumbsBarStyle.LINE_WIDTH)
        painter.setPen(pen)

        # Border
        rect = QRect(
            -BreadcrumbsBarStyle.LINE_WIDTH,  # Shift left to hide left line
            0,
            self.width() + 2 * BreadcrumbsBarStyle.LINE_WIDTH,  # Overlap
            self.height() + BreadcrumbsBarStyle.LINE_WIDTH,
        )
        painter.fillRect(rect, color_background)
        painter.drawRect(rect)

    def labelText() -> str:
        """Returns formatted string for crumbs"""
        ltext = ">"
        crumbs = BreadcrumbsBar.crumbs
        n = len(crumbs)
        if n > 1:
            ltext = f"> {crumbs[n - 2]} > <b><u>{crumbs[n - 1]}</b></u>"
        elif n == 1:
            ltext = f"> <b><u>{crumbs[n - 1]}</b></u>"
        return ltext

    def drawLabel(self):
        self.label = QLabel(BreadcrumbsBar.labelText(), self)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet(styles_crumbs)
        self.label.adjustSize()
        self.label.move(
            BreadcrumbsBarStyle.PADDING,
            self.height() // 2 - self.label.height() // 2
        )

    def navForward(newScreen: str):
        BreadcrumbsBar.crumbs.append(newScreen)
        BreadcrumbsBar.instance.label.setText(BreadcrumbsBar.labelText())
        BreadcrumbsBar.instance.label.adjustSize()

    def navBackward():
        crumbs = BreadcrumbsBar.crumbs
        crumbs.pop(len(crumbs) - 1)
        BreadcrumbsBar.instance.label.setText(BreadcrumbsBar.labelText())
        BreadcrumbsBar.instance.label.adjustSize()
