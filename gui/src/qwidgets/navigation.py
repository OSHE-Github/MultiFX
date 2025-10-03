from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import QRect, Qt, QPoint
from typing import List
from styles import (
    color_foreground, color_background, BreadcrumbsBarStyle, styles_crumbs
)
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W
from abc import abstractmethod
from enum import Enum
import itertools


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


class ScrollItem(QWidget):
    """Abstract class for items in ScrollGroup. Can be hovered and selected"""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def hover():
        pass

    @abstractmethod
    def unhover():
        pass

    @abstractmethod
    def select():
        pass


class PageMode(Enum):
    SCROLL = 0
    JUMP = 1


class ScrollGroup:
    """Class for grouping widgets in a scroll group and tracking
    scrolling window.

    Assumes widgets are all the same size.
    """

    def __init__(self, page_size: int, items: List[ScrollItem] = [],
                 page_mode: PageMode = PageMode.SCROLL):
        self.items = []
        self.pos: int = 0
        self.page_size = page_size
        # Index of first visible item
        self.window_top = 0
        # Index of last visible item
        self.window_bottom = page_size - 1
        self.page_mode = page_mode

    def curItem(self):
        return self.items[self.pos]

    def goNext(self) -> ScrollItem:
        if self.pos >= len(self.items) - 2:
            return
        self.curItem().unhover()
        self.pos += 1
        cur = self.curItem()
        cur.hover()
        if self.pos > self.window_bottom:
            match self.page_mode:
                case PageMode.SCROLL:
                    self.window_top += 1
                    self.window_bottom += 1
                case PageMode.JUMP:
                    self.window_top += self.page_size
                    self.window_bottom += self.page_size
            self.draw()
        return cur

    def goPrev(self) -> ScrollItem:
        if self.pos <= 0:
            return
        self.curItem().unhover()
        self.pos -= 1
        cur = self.curItem()
        cur.hover()
        if self.pos < self.window_top:
            match self.page_mode:
                case PageMode.SCROLL:
                    self.window_top -= 1
                    self.window_bottom -= 1
                case PageMode.JUMP:
                    self.window_top -= self.page_size
                    self.window_bottom -= self.page_size
            self.draw()
        return cur

    def draw(self):
        cursor = QPoint(0, 0)
        for item in itertools.islice(
                self.items, self.window_top, self.window_bottom):
            item.redraw()
            item.move(cursor)
            cursor = QPoint(cursor.x() + item.height(), cursor.y())
