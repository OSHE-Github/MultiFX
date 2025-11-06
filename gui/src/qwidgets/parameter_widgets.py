"""All widgets pertaining to parameter display and controls"""

import os
import sys
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QTransform
from PyQt5.QtCore import Qt, QRect
from plugin_manager import Plugin, Parameter
from styles import (styles_label, BreadcrumbsBarStyle, ScrollBarStyle,
                    styles_paramlabel, styles_vallabel, color_background)
from modhostmanager import updateParameter
from qwidgets.graphics_utils import SCREEN_W, SCREEN_H
from qwidgets.controls import RotaryEncoder
from qwidgets.plugin_box import PluginBox
from qwidgets.navigation import ScrollItem, ScrollGroup, PageMode, ScrollBar
from utils import assets_dir


class ParameterPanel(QWidget):
    paramCount = 3

    def __init__(
            self, pluginbox: PluginBox = None,
            mod_host_manager=None, back_callback=None):
        super().__init__()
        self.setFixedSize(SCREEN_W, SCREEN_H)
        self.pluginbox = pluginbox
        self.plugin = pluginbox.plugin
        self.parameters = []
        self.top_param = 0
        self.mod_host_manager = mod_host_manager
        self.back_callback = back_callback
        self.setFocusPolicy(Qt.StrongFocus)
        self.initUI()

    def initUI(self):
        params = self.plugin.parameters
        # Change to be done dynamically
        for parameter in params:
            match parameter.mode:
                case "dial":
                    dial = ParameterReadingRange(parameter)
                    self.parameters.append(dial)
                case "button":
                    button = ParameterReadingButton(parameter)
                    self.parameters.append(button)
                case "selector":
                    selector = ParameterReadingSlider(parameter)
                    self.parameters.append(selector)
        self.scroll_bar = ScrollBar(RotaryEncoder.MIDDLE)
        self.scroll_bar.setParent(self)
        self.scroll_bar.move(int((1 - ScrollBarStyle.REL_W) * self.width()), 0)
        self.scroll_group = ScrollGroup(
                self.paramCount, RotaryEncoder.MIDDLE, self.parameters,
                self.scroll_bar, PageMode.JUMP
        )
        self.scroll_group.setParent(self)
        self.scroll_group.update_bar()

    def updateParameter(self, position: int = 0):
        try:
            self.parameters[position].updateValue(
                self.plugin.parameters[position])
        except Exception as e:
            print(e)
            pass

    def decreaseParameter(self, position: int):
        params = self.plugin.parameters
        try:
            parameter: Parameter = params[position]
            parameter.setValue(round(max(
                parameter.minimum, parameter.value - parameter.increment), 2)
            )
            res = updateParameter(
                    self.mod_host_manager,
                    self.pluginbox.index,
                    parameter
            )
            if res != 0:
                print("Failed to update")
                pass
            self.updateParameter(position)
            self.update()
        except Exception as e:
            print(e)
            pass

    def increaseParameter(self, position: int):
        params = self.plugin.parameters
        try:
            parameter: Parameter = params[position]
            parameter.setValue(round(min(
                parameter.max, parameter.value + parameter.increment), 2)
            )
            if updateParameter(
                    self.mod_host_manager,
                    self.pluginbox.index,
                    parameter
            ) != 0:
                print("Failed to update")
                pass
            self.updateParameter(position)
            self.update()
        except Exception as e:
            print(e)
            pass

    def keyPressEvent(self, event):
        key = event.key()

        match key:
            case RotaryEncoder.TOP.keyLeft:
                self.decreaseParameter(self.top_param)
            case RotaryEncoder.TOP.keyPress:
                # TODO: presets page
                """"""
            case RotaryEncoder.TOP.keyRight:
                self.increaseParameter(self.top_param)
            case RotaryEncoder.MIDDLE.keyLeft:
                self.decreaseParameter(self.top_param+1)
            case RotaryEncoder.MIDDLE.keyPress:
                self.scroll_group.jump()
                self.top_param = self.scroll_group.window_top
            case RotaryEncoder.MIDDLE.keyRight:
                self.increaseParameter(self.top_param+1)
            case RotaryEncoder.BOTTOM.keyLeft:
                self.decreaseParameter(self.top_param+2)
            case RotaryEncoder.BOTTOM.keyPress:
                self.back_callback()
            case RotaryEncoder.BOTTOM.keyRight:
                self.increaseParameter(self.top_param+2)


class ParameterReadingButton(ScrollItem):
    def __init__(self, parameter: Parameter):
        super().__init__(parameter.name)
        self.setFixedSize(int((1 - ScrollBarStyle.REL_W) * SCREEN_W),
                          int((1 - BreadcrumbsBarStyle.REL_H) * SCREEN_H)//3)
        self.initUI(parameter)
        self.unhover_fill = color_background
        self.hover_fill = color_background
        self.line_width = 0

    def initUI(self, parameter: Parameter):
        # Creating plugin name field
        self.label = QLabel(parameter.name, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(styles_paramlabel)

        self.label.adjustSize()
        self.label.move(
            (self.width() - self.label.width()) // 2,
            self.height() // 6
        )

        # Indicator Label
        self.value = QLabel(f"{parameter.value}", self)
        self.value.setStyleSheet(styles_vallabel)

        self.value.adjustSize()
        self.value.move(
            (self.width() - self.value.width()) // 2,
            self.height() // 6 + self.label.height()
        )

        self.button_on_path = os.path.join(assets_dir, "BP.png")
        self.button_off_path = os.path.join(assets_dir, "BNP.png")

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


class ParameterReadingRange(ScrollItem):
    def __init__(self, parameter: Parameter):
        super().__init__(parameter.name)
        self.setFixedSize(int((1 - ScrollBarStyle.REL_W) * SCREEN_W),
                          int((1 - BreadcrumbsBarStyle.REL_H) * SCREEN_H)//3)
        self.initUI(parameter)
        self.unhover_fill = color_background
        self.hover_fill = color_background
        self.line_width = 0

    def initUI(self, parameter: Parameter):
        # Creating plugin name field
        self.label = QLabel(parameter.name, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(styles_paramlabel)

        self.label.adjustSize()
        self.label.move(
            (self.width() - self.label.width()) // 2,
            self.height() // 6
        )

        # Indicator Label
        self.value = QLabel(f"{parameter.value}", self)
        self.value.setStyleSheet(styles_vallabel)

        self.value.adjustSize()
        self.value.move(
            (self.width() - self.value.width()) // 2,
            self.height() // 6 + self.label.height()
        )

        image_path = os.path.join(assets_dir, "Dial.png")

        # Create Dial on screen
        self.dialImage = QPixmap(image_path)
        self.dial = QLabel(self)
        # rotate Dial
        ratio = ((parameter.value - parameter.minimum) /
                 (parameter.max - parameter.minimum))
        angle = -140 + 280 * ratio

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

        self.min_label = QLabel(str(parameter.minimum), self)
        self.min_label.setStyleSheet(styles_vallabel)
        self.min_label.adjustSize()
        self.min_label.move(
                self.width()//2 - 64 - self.min_label.width()//2,
                self.height()//2 + 64)
        self.max_label = QLabel(str(parameter.max), self)
        self.max_label.setStyleSheet(styles_vallabel)
        self.max_label.adjustSize()
        self.max_label.move(
                self.width()//2 + 64 - self.max_label.width()//2,
                self.height()//2 + 64)

    def updateValue(self, parameter: Parameter):
        self.value.setText(f"{parameter.value}")
        self.value.adjustSize()
        self.value.move(
            (self.width() - self.value.width()) // 2,
            self.height() // 6 + self.label.height()
        )

        ratio = ((parameter.value - parameter.minimum) /
                 (parameter.max - parameter.minimum))
        angle = -140 + 280 * ratio

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


class ParameterReadingSlider(ScrollItem):
    def __init__(self, parameter: Parameter):
        super().__init__(parameter.name)
        self.setFixedSize(int((1 - ScrollBarStyle.REL_W) * SCREEN_W),
                          int((1 - BreadcrumbsBarStyle.REL_H) * SCREEN_H)//3)
        self.initUI(parameter)
        self.unhover_fill = color_background
        self.hover_fill = color_background
        self.line_width = 0

    def initUI(self, parameter: Parameter):
        # Creating plugin name field
        self.label = QLabel(parameter.name, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(styles_paramlabel)

        self.label.adjustSize()
        self.label.move(
            (self.width() - self.label.width()) // 2,
            self.height() // 6
        )

        # Indicator Label
        self.value = QLabel(f"{parameter.value}", self)
        self.value.setStyleSheet(styles_vallabel)

        self.value.adjustSize()
        self.value.move(
            (self.width() - self.value.width()) // 2,
            self.height() // 6 + self.label.height()
        )

        slider = os.path.join(assets_dir, "Slider.png")
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
