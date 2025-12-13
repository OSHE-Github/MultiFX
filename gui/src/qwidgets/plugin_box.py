"""Displays plugin overview for board. Replaces old BoxWidget"""
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QPen
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W, Caret
from styles import (styles_label, color_foreground,
                    ScrollBarStyle, ControlDisplayStyle, color_background,
                    styles_sublabel, styles_proflabel)
from qwidgets.navigation import ScrollItem
from qwidgets.controls import RotaryEncoder, ControlDisplay
from plugin_manager import Plugin


class PluginBox(ScrollItem):
    def __init__(self, index: int, plugin: Plugin, bypass: int = 0):
        super().__init__(plugin.name)
        self.index = index
        # corresponds to instanceNum in plugin-manager. Should NOT change
        # when re-ordered
        self.instanceNum = index
        self.plugin = plugin
        self.plugin_name = plugin.name
        self.bypass = bypass
        self.hover_fill = RotaryEncoder.TOP.color
        self.unhover_fill = color_background
        self.preset_name = "preset name"
        # Make room for scroll bar and breadcrumbs
        self.setFixedSize(
            int((1 - ScrollBarStyle.REL_W) * SCREEN_W),
            int((1 - ControlDisplayStyle.REL_H) * SCREEN_H) // 3
        )
        self.isLast = False
        self.initUI()

    def unhover(self):
        super().unhover()
        self.setLabel(self.preset_name)

    def hover(self):
        super().hover()
        ControlDisplay.setBind(RotaryEncoder.TOP, "select")
        ControlDisplay.setBind(RotaryEncoder.MIDDLE, "bypass")
        ControlDisplay.setBind(RotaryEncoder.BOTTOM, "remove")
        self.setLabel(f"< {self.preset_name} >")

    def initUI(self):
        # Creating plugin name field
        self.label = QLabel(self.plugin_name, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(styles_label)
        # Adjust size after setting text
        self.label.adjustSize()
        self.label.move((
            self.width() - self.label.width()) // 2 + 16,
            self.height() // 2 - 20
        )
        self.preset_label = QLabel(self.preset_name, self)
        self.setLabel(self.preset_name)
        # TODO: Remove the below line once presets are working
        self.preset_label.hide()

    def setLabel(self, text: str):
        self.preset_label.setText(text)
        self.preset_label.setAlignment(Qt.AlignCenter)
        self.preset_label.setStyleSheet(styles_proflabel)
        self.preset_label.adjustSize()
        self.preset_label.move((
            self.width() - self.preset_label.width()) // 2 + 16,
            self.height() // 2 + 32
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

        if self.hovered:
            CARET_W = 20
            CARET_H = 12
            CARET_PADDING = 8
            outlinePen = QPen(color_background, 6)
            pen = QPen(RotaryEncoder.MIDDLE.color, 2)
            # draw carets
            if self.index != 0:
                top_caret = Caret(
                    QPoint(
                        self.width()//2 - CARET_W + 16,
                        CARET_PADDING + CARET_H
                    ), CARET_W, -CARET_H)
                painter.setPen(outlinePen)
                painter.drawPolygon(top_caret)
                painter.setPen(pen)
                painter.drawPolygon(top_caret)
            if not self.isLast:
                bottom_caret = Caret(
                    QPoint(
                        self.width()//2 - CARET_W + 16,
                        self.height() - CARET_PADDING - CARET_H
                    ), CARET_W, CARET_H)
                painter.setPen(outlinePen)
                painter.drawPolygon(bottom_caret)
                painter.setPen(pen)
                painter.drawPolygon(bottom_caret)

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


class AddPluginBox(ScrollItem):
    ID = "add plugin"

    def __init__(self):
        super().__init__("add plugin")
        self.hover_fill = RotaryEncoder.TOP.color
        self.unhover_fill = color_background
        # Make room for scroll bar and breadcrumbs
        self.setFixedSize(
            int((1 - ScrollBarStyle.REL_W) * SCREEN_W),
            int((1 - ControlDisplayStyle.REL_H) * SCREEN_H) // 3
        )
        self.initUI()

    def initUI(self):
        self.plus = QLabel("+")
        self.plus.setStyleSheet(styles_label)
        self.plus.setAlignment(Qt.AlignCenter)
        self.plus.adjustSize()
        self.plus.setParent(self)
        self.plus.move(
            self.width()//2 - self.plus.width()//2,
            self.height()//2 - self.plus.height()//2
        )

        self.label = QLabel(AddPluginBox.ID)
        self.label.setStyleSheet(styles_sublabel)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.adjustSize()
        self.label.setParent(self)
        self.label.move(
            self.width()//2 - self.label.width()//2,
            self.height()//2 + self.label.height()//2
        )

    def hover(self):
        super().hover()
        ControlDisplay.setBind(RotaryEncoder.TOP, "add plugin")
        ControlDisplay.setBind(RotaryEncoder.MIDDLE, "profiles")
        ControlDisplay.setBind(RotaryEncoder.BOTTOM, "save all")

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
