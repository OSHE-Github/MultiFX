"""Displays plugin overview for board. Replaces old BoxWidget"""
import os
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W
from styles import (styles_label, styles_indicator, color_foreground,
                    ScrollBarStyle, ControlDisplayStyle, color_background)
from utils import assets_dir
from qwidgets.navigation import ScrollItem
from qwidgets.controls import RotaryEncoder


class PluginBox(ScrollItem):
    def __init__(self, index: int, plugin_name="", bypass: int = 0):
        super().__init__(plugin_name)
        self.index = index
        self.plugin_name = plugin_name
        self.bypass = bypass
        self.hover_fill = RotaryEncoder.TOP.color
        self.unhover_fill = color_background
        # Make room for scroll bar and breadcrumbs
        self.setFixedSize(
            int((1 - ScrollBarStyle.REL_W) * SCREEN_W),
            int((1 - ControlDisplayStyle.REL_H) * SCREEN_H) // 3
        )
        self.initUI()

    def initUI(self):
        # Creating plugin name field
        self.label = QLabel(self.plugin_name, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(styles_label)
        # Adjust size after setting text
        self.label.adjustSize()
        self.label.move((
            self.width() - self.label.width()) // 2, self.height() // 2 - 20
        )

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(color_foreground, ScrollBarStyle.LINE_WIDTH)
        painter.setPen(pen)

        rect = QRect(0, 0, self.width()-1, self.height())
        fill_color = self.unhover_fill
        if self.hovered:
            fill_color = self.hover_fill
        painter.fillRect(rect, fill_color)
        painter.drawRect(rect)
        self.drawBypass()

    def updateBypass(self, bypass: int):
        self.bypass = bypass
        self.repaint()

    def drawBypass(self):
        PADDING = 6
        WIDTH = 32

        fill_color = RotaryEncoder.MIDDLE.color
        if (self.bypass == 1):
            fill_color = RotaryEncoder.MIDDLE.inactive

        rect = QRect(PADDING, PADDING, WIDTH, self.height() - 2 * PADDING)
        painter = QPainter(self)
        pen = QPen(color_foreground, ScrollBarStyle.LINE_WIDTH)
        painter.setPen(pen)

        painter.fillRect(rect, fill_color)
        painter.drawRect(rect)
