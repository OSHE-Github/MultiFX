"""Core widgets for the MultiFX GUI"""

import os
from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QColor, QPainter, QPen, QPolygon, QPixmap
from PyQt5.QtCore import Qt, QPoint, QRect
from plugin_manager import PluginManager, Parameter, Plugin
from modhostmanager import (
    startModHost, connectToModHost, setUpPlugins, setUpPatch, verifyParameters,
    updateBypass, quitModHost
)
from styles import (
    styles_indicator, styles_label, styles_window, color_foreground,
    styles_error, ScrollBarStyle, color_background, ControlDisplayStyle
)
from utils import config_dir, assets_dir
from qwidgets.parameter_widgets import ParameterPanel
from qwidgets.controls import ControlDisplay, RotaryEncoder
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W
from qwidgets.navigation import (
    BreadcrumbsBar, ScrollBar, ScrollItem, ScrollGroup
)
from qwidgets.floating_window import FloatingWindow, DialogItem
from qwidgets.plugin_box import PluginBox, AddPluginBox


class MainWindow(QWidget):
    stack: QStackedWidget = None

    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, SCREEN_W, SCREEN_H)

        self.stack = QStackedWidget(self)
        MainWindow.stack = self.stack
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.stack)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(styles_window)

        # Control Display
        self.controlDisplay = ControlDisplay()
        self.controlDisplay.move(
            SCREEN_W - self.controlDisplay.width(),
            SCREEN_H - self.controlDisplay.height()
        )
        self.controlDisplay.setParent(self)

        # Breadcrumbs
        self.breadcrumbs = BreadcrumbsBar("profile select")
        self.breadcrumbs.move(
            0,
            SCREEN_H - self.controlDisplay.height()
        )
        self.breadcrumbs.setParent(self)

        # Create selection screen
        self.start_screen = ProfileSelectWindow(self.launch_board)
        self.stack.addWidget(self.start_screen)

        self.board_window = None  # Placeholder for later

        self.show()

    def launch_board(self, selected_profile):
        """Called when a JSON file is selected to load the board"""
        # Loading the profile takes a little, here for feedback
        BreadcrumbsBar.navForward("LOADING PLUGINS...")
        self.repaint()

        board = PluginManager()
        selected_json = selected_profile + ".json"
        json_path = os.path.join(config_dir, selected_json)
        board.initFromJSON(json_path)
        startModHost()
        modhost = connectToModHost()
        if modhost is None:
            print("Failed Closing...")
            return
        setUpPlugins(modhost, board)
        setUpPatch(modhost, board)
        verifyParameters(modhost, board)

        # Remove old board window if it exists
        if self.board_window is not None:
            self.stack.removeWidget(self.board_window)
            self.board_window.deleteLater()

        # Create new board window and add it to the stack
        self.board_window = BoardWindow(
            board,
            mod_host_manager=modhost,
            restart_callback=self.show_start_screen,
        )
        self.stack.addWidget(self.board_window)
        self.stack.setCurrentWidget(self.board_window)  # Switch view
        self.board_window.setFocus()

        # Update breadcrumbs
        BreadcrumbsBar.navBackward()
        BreadcrumbsBar.navForward("view plugins")

    def show_start_screen(self):
        """Switch back to the start screen."""
        self.stack.setCurrentWidget(self.start_screen)  # Switch back
        self.stack.removeWidget(self.board_window)
        self.start_screen.setFocus()
        BreadcrumbsBar.navBackward()
        ControlDisplay.setBind(RotaryEncoder.TOP, "select")
        ControlDisplay.setBind(RotaryEncoder.MIDDLE, "")
        ControlDisplay.setBind(RotaryEncoder.BOTTOM, "delete")


class BoardWindow(QWidget):
    def __init__(
            self, manager: PluginManager, mod_host_manager, restart_callback):
        super().__init__()
        self.plugins = manager
        self.mod_host_manager = mod_host_manager
        self.restart_callback = restart_callback
        self.backgroundColor = color_background

        self.param_page = 0
        self.current = "plugins"

        self.setGeometry(0, 0, SCREEN_W, SCREEN_H)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), color_background)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.pluginbox = BoxOfPlugins(self.plugins)
        self.pluginbox.setParent(self)

        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        key = event.key()

        match key:
            case Qt.Key_R | RotaryEncoder.MIDDLE.keyPress:
                self.changeBypass(self.curIndex())
            case Qt.Key_F:
                self.changeBypass(0)
            case Qt.Key_G:
                self.changeBypass(1)
            case Qt.Key_H:
                self.changeBypass(2)
            case Qt.Key_J:
                self.changeBypass(3)
            case Qt.Key_K:
                self.changeBypass(4)
            case Qt.Key_L:
                self.changeBypass(5)

        match self.current:
            case "plugins":
                match key:
                    case RotaryEncoder.TOP.keyLeft:
                        self.pluginbox.scroll_group.goPrev()
                    case RotaryEncoder.TOP.keyPress:
                        self.show_param_screen(self.curItem())
                        # self.openParamPage()
                    case RotaryEncoder.TOP.keyRight:
                        self.pluginbox.scroll_group.goNext()
                    case RotaryEncoder.MIDDLE.keyLeft:
                        if self.swap_plugins(-1):
                            self.pluginbox.scroll_group.goPrev()
                    case RotaryEncoder.MIDDLE.keyPress:
                        if self.curIndex() is None:
                            self.restart_callback()
                    case RotaryEncoder.MIDDLE.keyRight:
                        if self.swap_plugins(1):
                            self.pluginbox.scroll_group.goNext()
                    case RotaryEncoder.BOTTOM.keyPress:
                        self.remove_current_plugin()

            case "parameters":
                match key:
                    case Qt.Key_Q:
                        self.decreaseParameter(0)
                    case Qt.Key_W:
                        self.closeParamPage()
                    case Qt.Key_E:
                        self.increaseParameter(0)
                    case Qt.Key_A:
                        self.decreaseParameter(1)
                    case Qt.Key_S:
                        self.pageUpParameters()
                    case Qt.Key_D:
                        self.increaseParameter(1)
                    case Qt.Key_Z:
                        self.decreaseParameter(2)
                    case Qt.Key_X:
                        self.pageDownParameters()
                    case Qt.Key_C:
                        self.increaseParameter(2)

    def swap_plugins(self, dist: int) -> bool:
        index = self.curIndex()
        # don't swap with add plugin widget
        if index is None:
            return False
        n = len(self.pluginbox.scroll_group.items)
        if index + dist < 0 or index + dist >= n:
            return
        items = self.pluginbox.boxes
        temp = items[index]
        other = items[index + dist]
        if other.id == AddPluginBox.ID:
            return
        temp.unhover()
        temp.index = index + dist
        items[index+dist].index = index
        items[index] = other
        items[index+dist] = temp
        temp.isLast = temp.index == n - 2
        other.isLast = other.index == n - 2

        self.pluginbox.scroll_group.drawItems()
        # TODO: swap in mod-host

        return True

    def remove_current_plugin(self):
        index = self.curIndex()
        if index is None:
            return
        n = len(self.pluginbox.scroll_group.items)
        if index >= n:
            return
        items = self.pluginbox.boxes
        # Prevent last item from sticking around
        items[index].hide()
        items.pop(index)
        # reassign plugin-box indices
        for i in range(index, n - 2):
            items[i].index -= 1
        # cleared group
        if n == 1:
            return
        # adjust to new position
        if index < n - 1:
            items[index].hover()
        if self.pluginbox.scroll_group.window_top != 0 or index == n - 1:
            self.pluginbox.scroll_group.goPrevEdge()
        self.pluginbox.scroll_group.repaint()
        self.pluginbox.scroll_group.drawItems()
        self.pluginbox.scroll_group.update_bar()
        # TODO: remove plugins in mod-host

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(Qt.black, 10)
        painter.setPen(pen)

        rect = QRect(0, 0, self.width()-1, self.height())
        painter.drawRect(rect)

    def showEvent(self, event):
        self.setFocus()

    def openParamPage(self):
        index = self.pluginbox.scroll_group.curItem().index
        try:
            self.param_page = 0
            self.plugin = self.plugins.plugins[index]
            self.paramPanel = ParameterPanel(
                    self.backgroundColor,
                    self.pluginbox.scroll_group.curItem().index,
                    self.param_page,
                    self.plugin
            )
            self.paramPanel.setParent(self)
            self.paramPanel.show()
            self.update()
            self.current = "parameters"

            self.pageNum.setText("Pgn " + str(self.param_page))
            self.pageNum.adjustSize()
            self.pageNum.move(
                    self.width() - self.pageNum.width() - 25,
                    self.height() - 25
            )
            self.update()
        except Exception as e:
            print(e)
            pass

    def closeParamPage(self):
        self.paramPanel.deleteLater()
        self.paramPanel.hide()
        self.paramPanel = None
        self.update()
        self.current = "plugins"
        self.plugin = None

        self.pageNum.setText("Pgn " + str(self.page))
        self.pageNum.adjustSize()
        self.pageNum.move(
            self.width()-self.pageNum.width()-25, self.height()-25
        )
        self.update()

    def changeBypass(self, position):
        if position is None:
            return
        try:
            # get the value of bypass from the plugin our cursor is currently
            # on
            plugin = self.plugins.plugins[position]
            bypass = plugin.bypass

            # flip value
            bypass = bypass ^ 1
            plugin.bypass = bypass
            updateBypass(self.mod_host_manager, position, plugin)
            self.pluginbox.updateBypass(position, bypass)
        except Exception as e:
            print(e)
            pass

    def pageUpParameters(self):
        if (self.param_page == 0):
            self.param_page = self.param_page + 1
            self.paramPanel.deleteLater()
            del self.paramPanel
            self.paramPanel = ParameterPanel(
                    self.backgroundColor,
                    self.curIndex(),
                    self.param_page,
                    self.plugin
            )
            self.paramPanel.setParent(self)
            self.paramPanel.show()

            self.pageNum.setText("Pgn " + str(self.param_page))
            self.pageNum.adjustSize()
            self.pageNum.move(
                    self.width() - self.pageNum.width() - 25,
                    self.height()-25
            )
            self.update()

    def pageDownParameters(self):
        if (self.param_page == 1):
            self.param_page = self.param_page - 1
            self.paramPanel.deleteLater()
            del self.paramPanel
            self.paramPanel = ParameterPanel(
                    self.backgroundColor,
                    self.curIndex(),
                    self.param_page,
                    self.plugin
            )
            self.paramPanel.setParent(self)
            self.paramPanel.show()

            self.pageNum.setText("Pgn " + str(self.param_page))
            self.pageNum.adjustSize()
            self.pageNum.move(
                    self.width() - self.pageNum.width() - 25,
                    self.height()-25
            )
            self.update()

    def show_param_screen(self, plugin: PluginBox):
        """Switch to the param screen for a plugin.
        Uses PluginBox for easier indexing.
        """
        self.param_window = ParameterPanel(
            color_background, 0, plugin, self.mod_host_manager,
            self.back_to_board)
        MainWindow.stack.addWidget(self.param_window)
        MainWindow.stack.setCurrentWidget(self.param_window)
        BreadcrumbsBar.navForward(plugin.id)
        ControlDisplay.setBind(RotaryEncoder.TOP, "presets")
        if len(plugin.plugin.parameters) > 3:
            ControlDisplay.setBind(RotaryEncoder.MIDDLE, "next page")
        else:
            ControlDisplay.setBind(RotaryEncoder.MIDDLE, "")
        ControlDisplay.setBind(RotaryEncoder.BOTTOM, "back")

    def back_to_board(self):
        """Switches back to board screen from parameter screen"""
        MainWindow.stack.setCurrentWidget(self)
        MainWindow.stack.removeWidget(self.param_window)
        del self.param_window
        BreadcrumbsBar.navBackward()
        self.curItem().hover()

    def curIndex(self) -> int | None:
        if self.pluginbox.scroll_group.curItem().id == AddPluginBox.ID:
            return None
        return self.pluginbox.scroll_group.curItem().index

    def curItem(self) -> PluginBox | AddPluginBox:
        return self.pluginbox.scroll_group.items[self.curIndex()]


class BoxOfPlugins(QWidget):
    pluginsPerPage: int = 3

    def __init__(self, plugins: PluginManager):
        super().__init__()
        self.setGeometry(
            0, 0, SCREEN_W,
            int((1 - ControlDisplayStyle.REL_H) * SCREEN_H)
        )
        self.boxes = []
        # Create scroll group
        n = len(plugins.plugins)
        for i in range(0, n):
            plugin = plugins.plugins[i]
            box = PluginBox(i, plugin, plugin.bypass)
            self.boxes.append(box)
        self.boxes[n-1].isLast = True
        self.boxes.append(AddPluginBox())
        self.scroll_bar = ScrollBar(RotaryEncoder.TOP)
        self.scroll_bar.setParent(self)
        self.scroll_group = ScrollGroup(
            BoxOfPlugins.pluginsPerPage, RotaryEncoder.TOP,
            self.boxes, self.scroll_bar
        )
        self.scroll_group.setParent(self)
        self.scroll_group.update_bar()
        self.scroll_bar.move(int((1 - ScrollBarStyle.REL_W) * self.width()), 0)

    def updateBypass(self, position: int, bypass):
        # NOTE: this used to be a bare try-except with nothing in the except
        # block. I hope this wasn't meant to error out as a feature.
        try:
            self.boxes[position].updateBypass(bypass)
        except Exception as e:
            print(e)
            pass


class ProfileSelectWindow(FloatingWindow):
    def __init__(self, callback):
        self.json_dir = os.path.dirname(config_dir)
        self.json_files = self.get_json_files(config_dir)
        self.json_files.sort()

        self.callback = callback

        # Floating window
        dialog_items = []
        for p in self.json_files:
            item = DialogItem(p.replace(".json", ""))
            dialog_items.append(item)
        scroll_group = ScrollGroup(4, RotaryEncoder.TOP, dialog_items)
        super().__init__("SELECT PROFILE", scroll_group, RotaryEncoder.TOP,
                         callback)
        ControlDisplay.setBind(RotaryEncoder.BOTTOM, "delete")

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        key = event.key()

        match key:
            case RotaryEncoder.BOTTOM.keyPress:
                self.remove_profile()

    def remove_profile(self):
        # TODO: Prompt to confirm
        index = self.group.pos
        items = self.group.items
        n = len(items)
        if index >= n:
            return
        # Prevent last item from sticking around
        items[index].hide()
        items.pop(index)
        # cleared group
        if n == 1:
            return
        # adjust to new position
        if index < n - 1:
            items[index].hover()
        if self.group.window_top != 0 or index == n - 1:
            self.group.goPrevEdge()
        self.group.repaint()
        self.group.drawItems()
        super().update_continues()
        # TODO: actually delete plugin

    def get_json_files(self, directory):
        """Returns a list of all JSON files in the specified directory."""
        return [f for f in os.listdir(directory) if f.endswith('.json')]
