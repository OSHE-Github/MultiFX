from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QPolygon
from PyQt5.QtCore import QPoint


class Cursor(QWidget):
    def __init__(self, position: int = 0):
        super().__init__()
        self.position = position % 3

    def paintEvent(self, event):
        arrow_color = QColor("black")
        self.setFixedSize(480, 800)

        painter = QPainter(self)
        x = 270
        y = 266
        width = 160
        arrowWidth = 30
        headOffset = 30
        adjusted_y = (y//2) + (y*self.position)

        # Line of arrow
        start = QPoint(x, adjusted_y)
        end = QPoint(x+width, adjusted_y)

        # Arrow head
        arrow_p1 = QPoint(
            x+headOffset+arrowWidth,
            adjusted_y + arrowWidth // 2
        )
        arrow_p2 = QPoint(
            x+headOffset+arrowWidth,
            adjusted_y - arrowWidth // 2
        )

        pen = QPen(arrow_color, 5)
        painter.setPen(pen)
        painter.drawLine(start, end)

        arrow_head = QPolygon([start, arrow_p1, arrow_p2])
        painter.setBrush(arrow_color)
        painter.drawPolygon(arrow_head)

    def changePointer(self, positon: int):
        self.position = positon
        self.update()
