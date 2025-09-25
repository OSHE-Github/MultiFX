import os
import sys
from PyQt5.QtWidgets import QWidget, QLabel
from plugin_manager import Parameter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QTransform


class ParameterReadingRange(QWidget):
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
        image_path = os.path.join(script_dir, "Graphics/Dial.png")

        # Create Dial on screen
        self.dialImage = QPixmap(image_path)
        self.dial = QLabel(self)
        # rotate Dial
        angle = -140 + 280*(parameter.value)/(parameter.max-parameter.minimum)

        transformedPixelMap = self.dialImage.transformed(
            QTransform().rotate(angle)
        )

        self.dial.setPixmap(transformedPixelMap)
        self.dial.adjustSize()
        self.dial.move(
            (self.width() - transformedPixelMap.width()) // 2,
            self.height() // 6 + self.label.height() + self.value.height()+40 -
            (transformedPixelMap.height() // 2)
        )

    def updateValue(self, parameter: Parameter):
        self.value.setText(f"{parameter.value}")
        self.value.adjustSize()
        self.value.move(
            (self.width() - self.value.width()) // 2,
            self.height() // 6 + self.label.height()
        )

        angle = -140 + 280*(parameter.value)/(parameter.max-parameter.minimum)

        transformedPixelMap = self.dialImage.transformed(
            QTransform().rotate(angle)
        )

        self.dial.setPixmap(transformedPixelMap)
        self.dial.adjustSize()
        self.dial.move(
            (self.width() - transformedPixelMap.width()) // 2,
            self.height() // 6 + self.label.height() + self.value.height()+40 -
            (transformedPixelMap.height() // 2)
        )
