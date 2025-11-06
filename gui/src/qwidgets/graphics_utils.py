"""Common miscelaneous utilities and constants for graphical widgets"""
from PyQt5.QtGui import QPolygon
from PyQt5.QtCore import QPoint
import math

SCREEN_W = 480  # in px
SCREEN_H = 800  # in px


def Octagon(center: QPoint, radius: int) -> QPolygon:
    points = []
    rad = 2 * math.pi / 8
    for i in range(0, 8):
        points.append(QPoint(
            round(center.x() + math.cos(rad * i) * radius),
            round(center.y() + math.sin(rad * i) * radius)
        ))

    return QPolygon(points)


def Caret(start: QPoint, width: int, height: int) -> QPolygon:
    points = [start, start + QPoint(width//2, height),
              start + QPoint(width, 0), start + QPoint(width//2, height)]
    return QPolygon(points)
