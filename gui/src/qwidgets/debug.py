"""This file should contain widgets that will not be used in prod"""

from qwidgets.navigation import ScrollItem
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QRect


class GenericScrollItem(ScrollItem):
    def __init__(self, id: str):
        super().__init__()
        self.id = id
        self.hovered: bool = False
        self.setFixedSize(250, 200)

    def hover(self):
        print(f"hovered {self.id}")
        self.hovered = True
        self.repaint()

    def unhover(self):
        print(f"unhovered {self.id}")
        self.hovered = False
        self.repaint()

    def select(self):
        print(f"selected {id}")

    def paintEvent(self, event):
        print("PAINTED GENERIC ITEM")
        painter = QPainter(self)

        pen = QPen(QColor.fromRgb(255, 255, 255), 10)
        painter.setPen(pen)

        rect = QRect(0, 0, self.width()-1, self.height())
        fill_color = QColor.fromRgb(255, 255, 0)
        if self.hovered:
            fill_color = QColor.fromRgb(0, 255, 255)

        painter.fillRect(rect, fill_color)
        painter.drawRect(rect)
