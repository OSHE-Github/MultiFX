import os
import sys
from PyQt5.QtWidgets import QWidget, QLabel
from plugin_manager import Parameter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class ParameterReadingButton(QWidget):
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

        self.button_on_path = os.path.join(script_dir, "Graphics/BP.png")
        self.button_off_path = os.path.join(script_dir, "Graphics/BNP.png")

        # Create Dial on screen
        if (parameter.value == 0):
            button = QPixmap(self.button_off_path)
        else:
            button = QPixmap(self.button_on_path)

        self.button = QLabel(self)

        self.button.setPixmap(button)
        self.button.adjustSize()
        self.button.move(
            (self.width() - self.button.width()) // 2,
            self.height() // 6 + self.label.height() + self.value.height()+15
        )

    def updateValue(self, parameter: Parameter):
        self.value.setText(f"{parameter.value}")
        self.value.adjustSize()
        self.value.move(
            (self.width() - self.value.width()) // 2,
            self.height() // 6 + self.label.height()
        )

        if (parameter.value == 0):
            button = QPixmap(self.button_off_path)
        else:
            button = QPixmap(self.button_on_path)

        self.button.setPixmap(button)
        self.button.adjustSize()
        self.button.move(
            (self.width() - self.button.width()) // 2,
            self.height() // 6 + self.label.height() + self.value.height()+15
        )
