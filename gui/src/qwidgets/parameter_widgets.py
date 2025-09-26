"""All widgets pertaining to parameter display and controls"""

import os
import sys
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QTransform
from PyQt5.QtCore import Qt, QRect
from plugin_manager import Plugin, Parameter


class ParameterPanel(QWidget):
    paramCount = 3

    def __init__(
            self, background_color: str = "white", positon: int = 0,
            page: int = 0, plugin: Plugin = None):
        super().__init__()
        self.setFixedSize(480, 800)
        self.background_color = QColor(background_color)
        self.plugin = plugin
        self.position = positon
        self.page = page
        self.parameters = []
        self.initUI()

    def initUI(self):
        params = self.plugin.parameters
        # Change to be done dynamically
        for index in range(0, self.paramCount):
            try:
                parameter: Parameter = params[index + (self.page*3)]
                match parameter.mode:
                    case "dial":
                        dial = ParameterReadingRange(parameter)
                        dial.setParent(self)
                        dial.move(self.width()//2, (801//3) * index)
                        self.parameters.append(dial)
                    case "button":
                        button = ParameterReadingButton(parameter)
                        button.setParent(self)
                        button.move(self.width()//2, (801//3) * index)
                        self.parameters.append(button)
                    case "selector":
                        selector = ParameterReadingSlider(parameter)
                        selector.setParent(self)
                        selector.move(self.width()//2, (801//3) * index)
                        self.parameters.append(selector)
            except Exception as e:
                print(e)
                pass

    def updateParameter(self, position: int = 0):
        try:
            self.parameters[position].updateValue(
                self.plugin.parameters[position + (self.page * 3)]
            )
        except Exception as e:
            print(e)
            pass

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(QColor(self.background_color), 10)
        painter.setPen(pen)

        rect = QRect(
            (self.width()//2) - 7,
            (self.height()//3)*self.position + 5,
            15,
            self.height()//3 - 9
        )
        painter.fillRect(rect, self.background_color)


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
