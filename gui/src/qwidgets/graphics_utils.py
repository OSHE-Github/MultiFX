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
