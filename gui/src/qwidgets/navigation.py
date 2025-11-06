from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QRect, Qt, QPoint
from typing import List
from styles import (
    color_foreground, color_background, BreadcrumbsBarStyle, styles_crumbs,
    ScrollBarStyle
)
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W
from enum import Enum
import itertools
from qwidgets.controls import RotaryEncoderData


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
    def __init__(self, id: str):
        super().__init__()
        self.id = id
        self.hovered: bool = False
        self.setFixedSize(250, 200)
        self.hover_fill = QColor.fromRgb(255, 255, 0)
        self.unhover_fill = QColor.fromRgb(0, 255, 255)
        self.line_width = 10

    def hover(self):
        self.hovered = True
        self.repaint()

    def unhover(self):
        self.hovered = False
        self.repaint()

    def select(self):
        print(f"selected {id}")

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor.fromRgb(255, 255, 255), self.line_width)

        painter.setPen(pen)

        rect = QRect(0, 0, self.width(), self.height())
        fill_color = self.unhover_fill
        if self.hovered:
            fill_color = self.hover_fill

        painter.fillRect(rect, fill_color)
        if (pen.width() != 0):
            painter.drawRect(rect)


class PageMode(Enum):
    SCROLL = 0
    JUMP = 1


class ScrollGroup(QWidget):
    """
    Class for grouping widgets in a scroll group and tracking
    scrolling window.

    Assumes widgets are all the same size.
    """

    def __init__(self, page_size: int,
                 encoder: RotaryEncoderData, items: List[ScrollItem] = [],
                 scroll_bar=None, page_mode: PageMode = PageMode.SCROLL):
        super().__init__()
        self.items = items
        self.pos: int = 0
        self.page_size = page_size
        # Index of first visible item
        self.window_top = 0
        # Index of last visible item
        self.window_bottom = page_size - 1
        self.page_mode = page_mode
        self.scroll_bar = scroll_bar
        self.encoder = encoder
        self.setFixedSize(items[0].width(), page_size * items[0].height())
        for item in items:
            item.setParent(self)
            item.hide()
        items[0].hover()
        self.drawItems()
        self.setFocusPolicy(Qt.StrongFocus)  # needed for input

    def hide_all(self):
        for item in self.items:
            item.hide()

    def curItem(self):
        return self.items[self.pos]

    def goNext(self) -> ScrollItem:
        if self.pos >= len(self.items) - 1:
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
            self.drawItems()
        self.update_bar()
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
            self.drawItems()
        self.update_bar()
        return cur

    def jump(self):
        self.window_top += self.page_size
        self.window_bottom += self.page_size
        n = len(self.items)
        if self.window_bottom > n:
            self.window_top = 0
            self.window_bottom = self.page_size - 1
        self.drawItems()
        self.update_bar()

    def goPrevEdge(self) -> ScrollItem:
        """Used for edge case where the last item is removed"""
        if self.pos <= 0:
            return
        if self.pos < len(self.items):
            self.curItem().unhover()
        self.pos -= 1
        cur = self.curItem()
        cur.hover()
        if self.window_top == 0:
            return
        match self.page_mode:
            case PageMode.SCROLL:
                self.window_top -= 1
                self.window_bottom -= 1
            case PageMode.JUMP:
                self.window_top -= self.page_size
                self.window_bottom -= self.page_size
        return cur

    def drawItems(self):
        self.hide_all()
        cursor = QPoint(0, 0)
        # draw all items in view
        for item in itertools.islice(
                self.items, self.window_top, self.window_bottom + 1):
            item.move(cursor)
            cursor = QPoint(cursor.x(), cursor.y() + item.height())
            item.show()

    def keyPressEvent(self, event):
        key = event.key()

        match key:
            case self.encoder.keyLeft:
                self.goPrev()
            case self.encoder.keyRight:
                self.goNext()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(color_foreground, 3)
        painter.setPen(pen)
        rect = QRect(0, 0, self.width(), self.height())
        # fill with blank for the case where items are removed
        painter.fillRect(rect, color_background)
        # painter.drawRect(rect)

    def update_bar(self):
        if not self.scroll_bar:
            return
        self.scroll_bar.drawFor(self)


class ScrollBar(QWidget):
    def __init__(self, encoder: RotaryEncoderData):
        super().__init__()
        self.encoder = encoder
        self.setFixedSize(
            int(ScrollBarStyle.REL_W * SCREEN_W)+1,
            int(ScrollBarStyle.REL_H * SCREEN_H)+1
        )
        # ratio of height used for drawing
        self.top = 0
        self.bottom = 1

    def drawFor(self, scroll_group: ScrollGroup):
        """Draws the scrollbar according to the state of a scroll group"""
        n = len(scroll_group.items)
        if n <= 1:
            self.top = 0
            self.bottom = 1
        else:
            self.top = scroll_group.window_top / n
            self.bottom = (scroll_group.window_bottom+1) / n
        self.update()

    def draw(self):
        painter = QPainter(self)
        fg_pen = QPen(color_foreground, BreadcrumbsBarStyle.LINE_WIDTH)
        inactive_pen = QPen(
                self.encoder.inactive, BreadcrumbsBarStyle.LINE_WIDTH)
        in_view_pen = QPen(self.encoder.color, BreadcrumbsBarStyle.LINE_WIDTH)

        backdrop = QRect(0, 0, self.width()-1, self.height()-1)
        painter.setPen(inactive_pen)
        painter.fillRect(backdrop, self.encoder.inactive)
        painter.setPen(in_view_pen)
        painter.drawRect(backdrop)

        in_view = QRect(
            0,
            int(self.top * self.height()),
            self.width()-1,
            int((self.bottom - self.top) * self.height())-1
        )
        painter.fillRect(in_view, self.encoder.color)
        painter.setPen(fg_pen)
        painter.drawRect(in_view)

    def paintEvent(self, event):
        self.draw()
