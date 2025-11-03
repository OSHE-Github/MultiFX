"""Contains floating window widget"""
from qwidgets.navigation import ScrollGroup
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QRect
from styles import (color_foreground, FloatingWindowStyle, color_background)
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W
from qwidgets.navigation import ScrollItem
from qwidgets.controls import ControlDisplay, RotaryEncoder, RotaryEncoderData


class FloatingWindow(QWidget):
    def __init__(self, title: str, group: ScrollGroup,
                 encoder: RotaryEncoderData, callback):
        super().__init__()
        self.title = title
        self.group = group
        self.encoder = encoder
        self.callback = callback
        self.setFixedSize(SCREEN_W, SCREEN_H)
        group.setParent(self)
        self.initUI()
        self.setFocusPolicy(Qt.StrongFocus)

    def initUI(self):
        self.label = QLabel(self.title, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(FloatingWindowStyle.css_title)
        self.label.adjustSize()
        self.label.move(
            int(self.width() / 2 - self.label.width() / 2),
            int(((1 - FloatingWindowStyle.REL_H) / 2) * SCREEN_H)
            + FloatingWindowStyle.LINE_WIDTH,
        )
        self.group.move(
            int(self.width() / 2 - self.group.width() / 2),
            self.height() // 2 - self.group.height() // 2
        )
        ControlDisplay.setBind(self.encoder, "select")

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(color_foreground)
        pen.setWidth(FloatingWindowStyle.LINE_WIDTH)
        painter.setPen(pen)

        rect = QRect(
            int(((1 - FloatingWindowStyle.REL_W) / 2) * SCREEN_W),
            int(((1 - FloatingWindowStyle.REL_H) / 2) * SCREEN_H),
            int(FloatingWindowStyle.REL_W * SCREEN_W) - 2,
            int(FloatingWindowStyle.REL_H * SCREEN_H) - 2
        )
        painter.fillRect(rect, color_background)
        painter.drawRect(rect)

    def keyPressEvent(self, event):
        key = event.key()

        match key:
            case self.encoder.keyLeft:
                self.group.goPrev()
            case self.encoder.keyRight:
                self.group.goNext()
            case self.encoder.keyPress:
                self.callback(self.group.curItem().id)


class DialogItem(ScrollItem):
    def __init__(self, id: str):
        super().__init__(id)
        self.setFixedSize(180, 48)
        self.label = QLabel(self.id, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(FloatingWindowStyle.css_options)
        self.label.adjustSize()
        self.label.move(
            self.width() // 2 - self.label.width() // 2,
            self.height() // 2 - self.label.height() // 2
        )
        self.hover_fill = RotaryEncoder.TOP.color
        self.unhover_fill = color_background
        self.line_width = 0

    def hover(self):
        super().hover()

    def unhover(self):
        super().unhover()

    def select(self):
        print(f"selected {id}")
