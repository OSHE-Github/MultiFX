import os
import sys
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen, QRect


class BoxWidget(QWidget):
    def __init__(self, indicator: int, plugin_name="", bypass: int = 0):
        super().__init__()
        self.plugin_name = plugin_name
        self.indicator = indicator
        self.bypass = bypass
        self.setFixedSize(240, 801//3)
        self.initUI()

    def initUI(self):
        # Creating plugin name field
        self.label = QLabel(self.plugin_name, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "font : bold 30px;"
            "font-family : Comic Sans MS;"
        )
        # Adjust size after setting text
        self.label.adjustSize()
        self.label.move((
            self.width() - self.label.width()) // 2, self.height() // 2 - 20
        )

        # Indicator Label
        self.indicator = QLabel(str(self.indicator), self)
        self.indicator.setStyleSheet(
            "font: bold 30px;"
            "font-family : Comic Sans MS;"
            )

        # Move to bottom-left corner
        self.indicator.adjustSize()
        self.indicator.move(30-self.indicator.width(), self.height()-45)

        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

        self.indicator_off_path = os.path.join(
            script_dir, "Graphics/IndicatorOff.png"
        )
        self.indicator_on_path = os.path.join(
            script_dir, "Graphics/IndicatorOn.png"
        )

        if (self.bypass == 0):
            indicator = QPixmap(self.indicator_on_path)
        else:
            indicator = QPixmap(self.indicator_off_path)

        self.indicator = QLabel(self)

        self.indicator.setPixmap(indicator)
        self.indicator.adjustSize()
        self.indicator.move((self.width() - self.indicator.width()) - 16, 16)

        if (self.bypass == 0):
            indicatorText = "On"
        else:
            indicatorText = "Off"

        self.indicator_text = QLabel(indicatorText, self)
        self.indicator_text.setStyleSheet(
            "font: bold 13px;"
            "font-family : Comic Sans MS;"
            )
        self.indicator_text.adjustSize()
        self.indicator_text.move(
            (self.width() - self.indicator.width()) - 16,
            16 + indicator.width()
        )

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(Qt.black, 10)
        painter.setPen(pen)

        rect = QRect(0, 0, self.width()-1, self.height())
        painter.drawRect(rect)

    def updateBypass(self, bypass: int):
        self.bypass = bypass

        if (self.bypass == 1):
            indicator = QPixmap(self.indicator_off_path)
        else:
            indicator = QPixmap(self.indicator_on_path)

        self.indicator.setPixmap(indicator)
        self.indicator.adjustSize()
        self.indicator.move((self.width() - self.indicator.width()) - 16, 16)

        if (self.bypass == 0):
            indicatorText = "On"
        else:
            indicatorText = "Off"

        self.indicator_text.setText(indicatorText)
        self.indicator_text.adjustSize()
        self.indicator_text.move(
            (self.width() - self.indicator.width()) - 16,
            16 + indicator.width()
        )
