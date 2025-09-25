import os
import sys
from PyQt5.QtWidgets import QWidget, QLabel
from plugin_manager import Parameter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen


class ParameterReadingSlider(QWidget):
    def __init__(self, parameter: Parameter):
        super().__init__()
        self.setFixedSize(240, 801//3)
        self.initUI(parameter)

    def initUI(self, parameter: Parameter):
        # Creating plugin name field
        self.label = QLabel(parameter.name, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "font : bold 30px;"
            "font-family : Comic Sans MS;"
            "background : transparent;"
        )

        self.label.adjustSize()
        self.label.move(
            (self.width() - self.label.width()) // 2,
            self.height() // 6
        )

        # Indicator Label
        self.value = QLabel(f"{parameter.value}", self)
        self.value.setStyleSheet(
            "font: bold 30px;"
            "font-family : Comic Sans MS;"
            )

        self.value.adjustSize()
        self.value.move(
            (self.width() - self.value.width()) // 2,
            self.height() // 6 + self.label.height()
        )

        # find path to Dial.png
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        slider = os.path.join(script_dir, "Graphics/Slider.png")
        sliderPix = QPixmap(slider)

        self.slider = QLabel(self)

        self.slider.setPixmap(sliderPix)
        self.slider.adjustSize()
        self.slider.move(
            ((self.width() - self.slider.width()) // 2) - 40 +
            80*(parameter.value // (parameter.max-parameter.minimum)),
            self.height() // 6 + self.label.height() + self.value.height()+15
        )

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(Qt.black, 10)
        painter.setPen(pen)

        painter.drawLine(
            ((self.width()) // 2)-40, self.height() // 6 + self.label.height()
            + self.value.height()+15 + self.slider.height()//2,
            ((self.width()) // 2)+40, self.height() // 6 + self.label.height()
            + self.value.height()+15 + self.slider.height()//2
        )

    def updateValue(self, parameter: Parameter):
        self.value.setText(f"{parameter.value}")
        self.value.adjustSize()
        self.value.move(
            (self.width() - self.value.width()) // 2,
            self.height() // 6 + self.label.height()
        )

        self.slider.move(
            ((self.width() - self.slider.width()) // 2) - 40 +
            80*(parameter.value // (parameter.max-parameter.minimum)),
            self.height() // 6 + self.label.height() + self.value.height()+15
        )
