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
        print(f"hovered {id}")
        self.hovered = True
        self.repaint()

    def unhover(self):
        print(f"unhovered {id}")
        self.hovered = False
        self.repaint()

    def select(self):
        print(f"selected {id}")

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(QColor.fromRgb(255, 255, 255), 10)
        painter.setPen(pen)

        rect = QRect(0, 0, self.width()-1, self.height())
        painter.drawRect(rect)

        color = QColor.fromRgb(0, 255, 255) if self.hovered else QColor.fromRgb(0,0,0)

        painter.fillRect(rect, color)
