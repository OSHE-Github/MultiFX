from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtCore import QRect
from plugin_manager import Plugin, Parameter
from qwidgets import (
    ParameterReadingRange, ParameterReadingButton, ParameterReadingSlider
)


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
