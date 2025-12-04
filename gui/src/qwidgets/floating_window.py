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
        self.title_label = QLabel(self.title, self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(FloatingWindowStyle.css_title)
        self.title_label.adjustSize()
        self.title_label.move(
            int(self.width() / 2 - self.title_label.width() / 2),
            int(((1 - FloatingWindowStyle.REL_H) / 2) * SCREEN_H)
            + FloatingWindowStyle.LINE_WIDTH,
        )
        self.top_continue = QLabel("...", self)
        self.top_continue.setStyleSheet(FloatingWindowStyle.css_options)
        self.top_continue.setAlignment(Qt.AlignCenter)
        self.top_continue.adjustSize()
        self.bottom_continue = QLabel("...", self)
        self.bottom_continue.setAlignment(Qt.AlignCenter)
        self.bottom_continue.setStyleSheet(FloatingWindowStyle.css_options)
        self.bottom_continue.adjustSize()
        group_x = int(self.width() / 2 - self.group.width() / 2)
        group_y = self.height() // 2 - self.group.height() // 2
        self.group.move(
            group_x,
            group_y
        )
        self.top_continue.move(
            group_x + self.group.width()//2 - self.top_continue.width() // 2,
            group_y - self.top_continue.height()
        )
        self.bottom_continue.move(
            group_x + self.group.width()//2 - self.top_continue.width() // 2,
            group_y + self.group.height() + self.top_continue.height()
        )
        self.update_continues()
        ControlDisplay.setBind(self.encoder, "select")

    def update_continues(self):
        n = len(self.group.items)
        self.top_continue.setHidden(self.group.window_top == 0)
        self.bottom_continue.setHidden(self.group.window_bottom >= n - 1)

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
                self.update_continues()
            case self.encoder.keyRight:
                self.group.goNext()
                self.update_continues()
            case self.encoder.keyPress | Qt.Key_R:
                self.callback(self.group.curItem().id)


class DialogItem(ScrollItem):
    def __init__(self, id: str):
        super().__init__(id)
        self.setFixedSize(180, 48)
        self.title_label = QLabel(self.id, self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(FloatingWindowStyle.css_options)
        self.title_label.adjustSize()
        self.title_label.move(
            self.width() // 2 - self.title_label.width() // 2,
            self.height() // 2 - self.title_label.height() // 2
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
