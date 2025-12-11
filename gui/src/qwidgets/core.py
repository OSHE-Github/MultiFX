"""Core widgets for the MultiFX GUI"""

import os
from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QLine
from plugin_manager import PluginManager, Plugin
from modhostmanager import (
    connectToModHost, setUpPlugins, setUpPatch, verifyParameters,
    updateBypass, startModHost, patchThrough, removeFirst, removeMiddle,
    removeLast, removeFinal, add_plugin_end, swap_plugins_end,
    swap_plugins_final, swap_plugins_middle, swap_plugins_start, unpatchThrough
)
from styles import (
    styles_window, color_foreground,
    ScrollBarStyle, color_background, ControlDisplayStyle,
    BreadcrumbsBarStyle, styles_tabletitle, styles_tableitem
)
from utils import config_dir
from qwidgets.parameter_widgets import ParameterPanel
from qwidgets.controls import ControlDisplay, RotaryEncoder
from qwidgets.graphics_utils import SCREEN_H, SCREEN_W
from qwidgets.navigation import (
    BreadcrumbsBar, ScrollBar, ScrollItem, ScrollGroup
)
from qwidgets.floating_window import FloatingWindow, DialogItem
from qwidgets.plugin_box import PluginBox, AddPluginBox
from offboard import try_save

modhost = None


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

        self.reset_modhost()
        patchThrough(modhost)  # Bypass all before we load plugins

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

        # Restart mod-host so we can change profiles.
        # This is inefficient and can be improved, but it's easy.
        self.reset_modhost()
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
        self.reset_modhost()
        patchThrough(modhost)  # Bypass all before we load plugins
        self.stack.setCurrentWidget(self.start_screen)  # Switch back
        self.stack.removeWidget(self.board_window)
        self.start_screen.setFocus()
        BreadcrumbsBar.navBackward()
        ControlDisplay.setBind(RotaryEncoder.TOP, "select")
        ControlDisplay.setBind(RotaryEncoder.MIDDLE, "")
        ControlDisplay.setBind(RotaryEncoder.BOTTOM, "delete")

    def reset_modhost(self):
        """Starts or restarts modhost"""
        startModHost()

        global modhost
        modhost = connectToModHost()
        if modhost is None:
            print("Failed Closing...")
            exit(1)
            return


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

        self.pluginbox = BoxOfPlugins(self.plugins, self)

        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        key = event.key()

        match key:
            # handle footswitches/bypass
            case Qt.Key_R | RotaryEncoder.MIDDLE.keyPress:
                self.changeBypass(self.curIndex())
                if self.curIndex() is None:
                    self.restart_callback()
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
            # navigation
            case RotaryEncoder.TOP.keyLeft:
                self.pluginbox.scroll_group.goPrev()
            case RotaryEncoder.TOP.keyPress:
                cur = self.curItem()
                if type(cur) is PluginBox:
                    self.show_param_screen(self.curItem())
                if type(cur) is AddPluginBox:
                    self.show_add_plugin_screen()
            case RotaryEncoder.TOP.keyRight:
                self.pluginbox.scroll_group.goNext()
            case RotaryEncoder.MIDDLE.keyLeft:
                if self.swap_plugins(-1):
                    self.pluginbox.scroll_group.goPrev()
            case RotaryEncoder.MIDDLE.keyRight:
                if self.swap_plugins(1):
                    self.pluginbox.scroll_group.goNext()
            case RotaryEncoder.BOTTOM.keyPress:
                cur = self.curItem()
                if type(cur) is PluginBox:
                    self.remove_current_plugin()
                if type(cur) is AddPluginBox:
                    BreadcrumbsBar.navForward("SAVING...")
                    BreadcrumbsBar.instance.repaint()
                    try_save()
                    BreadcrumbsBar.navBackward()

    def swap_plugins(self, dist: int) -> bool:
        index = self.curIndex()
        # don't swap with add plugin widget
        if index is None:
            return False
        n = len(self.pluginbox.scroll_group.items)
        if index + dist < 0 or index + dist >= n-1:
            return
        items = self.pluginbox.boxes

        # swap in mod-host
        # default, swap forward
        instanceNumA = None
        pluginA = None
        instanceNumB = None
        pluginB = None
        beforePlugin = None
        beforeInstanceNum = None
        afterPlugin = None
        afterInstanceNum = None
        # when negative, swap backward
        if dist < 0:
            instanceNumB = items[index].instanceNum
            pluginB = items[index].plugin
            instanceNumA = items[index+dist].instanceNum
            pluginA = items[index+dist].plugin
            if index - 2 >= 0:
                beforeInstanceNum = self.pluginbox.scroll_group.items[index-2].instanceNum
                beforePlugin = self.pluginbox.scroll_group.items[index-2].plugin
            if index + 1 < n-1:  # adjust n for AppPluginBox
                afterInstanceNum = self.pluginbox.scroll_group.items[index+1].instanceNum
                afterPlugin = self.pluginbox.scroll_group.items[index+1].plugin
        else:  # swap forward
            instanceNumA = items[index].instanceNum
            pluginA = items[index].plugin
            instanceNumB = items[index+dist].instanceNum
            pluginB = items[index+dist].plugin
            if index - 1 >= 0:
                beforeInstanceNum = self.pluginbox.scroll_group.items[index-1].instanceNum
                beforePlugin = self.pluginbox.scroll_group.items[index-1].plugin
            if index + 2 < n-1:
                afterInstanceNum = self.pluginbox.scroll_group.items[index+2].instanceNum
                afterPlugin = self.pluginbox.scroll_group.items[index+2].plugin
        # call mod-host manager based on what we determined
        if beforeInstanceNum is None:
            if afterInstanceNum is None:
                swap_plugins_final(
                        modhost,
                        instanceNumA,
                        pluginA,
                        instanceNumB,
                        pluginB)
            else:
                swap_plugins_start(
                        modhost,
                        instanceNumA,
                        pluginA,
                        instanceNumB,
                        pluginB,
                        afterInstanceNum,
                        afterPlugin)
        else:
            if afterInstanceNum is None:
                swap_plugins_end(
                        modhost,
                        instanceNumA,
                        pluginA,
                        instanceNumB,
                        pluginB,
                        beforeInstanceNum,
                        beforePlugin)
            else:
                swap_plugins_middle(
                        modhost,
                        instanceNumA,
                        pluginA,
                        instanceNumB,
                        pluginB,
                        beforeInstanceNum,
                        beforePlugin,
                        afterInstanceNum,
                        afterPlugin)

        # swap visually
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

        return True

    def remove_current_plugin(self):
        index = self.curIndex()
        if index is None:  # don't remove AddPluginBox
            return
        n = len(self.pluginbox.scroll_group.items)
        if index >= n:
            return
        items = self.pluginbox.boxes

        # remove in mod-host
        if n == 2:  # use 2 because AddPluginBox will always stay
            removeFinal(modhost, items[index].instanceNum)
        elif index == n - 2:
            removeLast(modhost, items[index].instanceNum, items[index].plugin,
                       items[index-1].instanceNum, items[index-1].plugin)
        elif index == 0:
            removeFirst(modhost, items[index].instanceNum, items[index].plugin,
                        items[index+1].instanceNum, items[index+1].plugin)
        else:
            removeMiddle(modhost, items[index].instanceNum, items[index].plugin,
                         items[index-1].instanceNum, items[index-1].plugin,
                         items[index+1].instanceNum, items[index+1].plugin)

        # remove and adjust visuals
        # Prevent last item from sticking around
        items[index].hide()
        self.plugins.plugins.remove(items[index].plugin)
        items.pop(index)
        # reassign plugin-box indices
        for i in range(index, n - 2):
            items[i].index -= 1
        # skip scrollgroup logic when last item is removed
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

    def add_plugin(self, plugin: Plugin):
        self.curItem().unhover()
        # add plugin to board visual
        n = len(self.plugins.plugins)
        self.plugins.plugins.append(plugin)
        newbox = PluginBox(n, plugin, plugin.bypass)
        newbox.setParent(self.pluginbox.scroll_group)
        self.pluginbox.scroll_group.items.insert(n, newbox)
        self.pluginbox.scroll_group.repaint()
        self.pluginbox.scroll_group.drawItems()
        self.pluginbox.scroll_group.update_bar()
        # hover new item
        newbox.hover()
        self.pluginbox.scroll_group.pos = n
        # add to mod-host
        maxInstanceNum = n
        for item in self.pluginbox.scroll_group.items:
            if type(item) is AddPluginBox:
                continue
            if item.instanceNum > maxInstanceNum:
                maxInstanceNum = item.instanceNum
        add_plugin_end(
                modhost,
                maxInstanceNum,
                plugin,
                n-1,
                self.plugins.plugins[n-1]
        )

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(Qt.black, 10)
        painter.setPen(pen)

        rect = QRect(0, 0, self.width()-1, self.height())
        painter.drawRect(rect)

    def showEvent(self, event):
        self.setFocus()

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

    def show_param_screen(self, plugin: PluginBox):
        """Switch to the param screen for a plugin.
        Uses PluginBox for easier indexing.
        """
        self.param_window = ParameterPanel(plugin, self.mod_host_manager,
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

    def show_add_plugin_screen(self):
        self.add_plugin_window = PluginTable(self.plugins, self.back_to_board,
                                             self.add_plugin)
        MainWindow.stack.addWidget(self.add_plugin_window)
        MainWindow.stack.setCurrentWidget(self.add_plugin_window)
        BreadcrumbsBar.navForward("add plugin")
        ControlDisplay.setBind(RotaryEncoder.TOP, "add plugin")
        ControlDisplay.setBind(RotaryEncoder.MIDDLE, "")
        ControlDisplay.setBind(RotaryEncoder.BOTTOM, "back")

    def back_to_board(self):
        """Switches back to board screen from parameter screen"""
        MainWindow.stack.setCurrentWidget(self)
        if hasattr(self, 'param_window'):
            MainWindow.stack.removeWidget(self.param_window)
            del self.param_window
        if hasattr(self, 'add_plugin_window'):
            MainWindow.stack.removeWidget(self.add_plugin_window)
            del self.add_plugin_window
        BreadcrumbsBar.navBackward()
        self.curItem().hover()
        self.setFocusPolicy(Qt.StrongFocus)

    def curIndex(self) -> int | None:
        if self.pluginbox.scroll_group.curItem().id == AddPluginBox.ID:
            return None
        return self.pluginbox.scroll_group.curItem().index

    def curItem(self) -> PluginBox | AddPluginBox:
        index = self.curIndex()
        if index is not None:
            return self.pluginbox.scroll_group.items[self.curIndex()]
        else:
            return self.pluginbox.add_plugin_box


class BoxOfPlugins(QWidget):
    pluginsPerPage: int = 3

    def __init__(self, plugins: PluginManager, parent):
        super().__init__()
        self.setGeometry(
            0, 0, SCREEN_W,
            int((1 - ControlDisplayStyle.REL_H) * SCREEN_H)
        )
        self.plugins = plugins
        self.board_window = parent
        self.initGroup()
        self.setParent(parent)

    def initGroup(self):
        # Create scroll group
        self.boxes = []
        n = len(self.plugins.plugins)
        for i in range(0, n):
            plugin = self.plugins.plugins[i]
            box = PluginBox(i, plugin, plugin.bypass)
            box.board_window = self.board_window
            self.boxes.append(box)
        self.boxes[n-1].isLast = True
        self.add_plugin_box = AddPluginBox()
        self.boxes.append(self.add_plugin_box)
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
        # TODO: actually delete profile

    def get_json_files(self, directory):
        """Returns a list of all JSON files in the specified directory."""
        return [f for f in os.listdir(directory) if f.endswith('.json') and "all_plugins" not in f]


class PluginTable(QWidget):
    """Page for adding plugins to board"""
    LINE_W = 3
    COL2_REL_W = 1/8
    PADDING = 8
    PAGE_SIZE = 8

    def __init__(self, manager: PluginManager, back_callback, add_callback):
        super().__init__()
        self.setFixedSize(
            SCREEN_W,
            int((1 - BreadcrumbsBarStyle.REL_H) * SCREEN_H)
        )
        self.plugins = manager
        self.back_callback = back_callback
        self.add_callback = add_callback
        self.setFocusPolicy(Qt.StrongFocus)
        self.initUI()

    def initUI(self):
        self.col1title = QLabel("PLUGIN NAME", self)
        self.col1title.setStyleSheet(styles_tabletitle)
        self.col1title.adjustSize()
        self.col1title.move(self.PADDING, self.PADDING)
        self.col2title = QLabel("#", self)
        self.col2title.setStyleSheet(styles_tabletitle)
        self.col2title.adjustSize()
        self.col2title.move(
            int((1 - self.COL2_REL_W) * (1 - ScrollBarStyle.REL_W) *
                self.width()) + 2*self.PADDING, self.PADDING
        )
        self.start_y = 2*self.PADDING + self.col1title.height()
        self.end_x = int((1 - ScrollBarStyle.REL_W) * self.width())

        self.scroll_bar = ScrollBar(RotaryEncoder.TOP)
        self.scroll_bar.setParent(self)
        items = []
        # count number of plugins and place them in
        plugincounts = {}
        all_plugins = PluginManager.all_plugins()
        for plugin in all_plugins:
            plugincounts[plugin.name] = 0
        for plugin in self.plugins.plugins:
            plugincounts[plugin.name] += 1
        for key, value in sorted(plugincounts.items(), key=lambda x: x):
            actual_plugin = next((plugin for plugin in all_plugins if key == plugin.name), None)
            if actual_plugin is not None:
                items.append(PluginTableEntry(actual_plugin, value, self))
        self.scroll_group = ScrollGroup(
            self.PAGE_SIZE, RotaryEncoder.TOP, items, self.scroll_bar
        )
        self.scroll_group.setParent(self)
        self.scroll_group.update_bar()
        self.scroll_group.move(0, self.start_y)
        self.scroll_group.setFixedSize(
            self.end_x,
            int((1 - BreadcrumbsBarStyle.REL_H) * SCREEN_H - self.start_y)
        )
        self.scroll_bar.move(self.end_x, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(color_foreground, self.LINE_W)
        painter.setPen(pen)
        y = self.start_y
        bottom_line = QLine(0, y, self.end_x, y)
        painter.drawLine(bottom_line)
        x = self.col2title.x() - self.PADDING
        seperator = QLine(x, 0, x, y)
        painter.drawLine(seperator)

    def keyPressEvent(self, event):
        key = event.key()

        match key:
            case RotaryEncoder.BOTTOM.keyPress:
                self.back_callback()
            case RotaryEncoder.TOP.keyLeft:
                self.scroll_group.goPrev()
            case RotaryEncoder.TOP.keyPress:
                self.add_callback(self.scroll_group.curItem().plugin)
                self.back_callback()
            case RotaryEncoder.TOP.keyRight:
                self.scroll_group.goNext()


class PluginTableEntry(ScrollItem):
    def __init__(self, plugin: Plugin, count: int, table: PluginTable):
        super().__init__(plugin.name)
        self.hover_fill = RotaryEncoder.TOP.color
        self.unhover_fill = color_background
        self.line_width = 0  # prevent drawing rectagle edges
        self.table = table
        self.plugin = plugin
        self.setFixedSize(
            table.end_x,
            int((1 - BreadcrumbsBarStyle.REL_H) * SCREEN_H - table.start_y) //
            PluginTable.PAGE_SIZE
        )
        self.name_label = QLabel(plugin.name, self)
        self.name_label.setStyleSheet(styles_tableitem)
        self.name_label.adjustSize()
        # pad and center
        self.name_label.move(PluginTable.PADDING,
                             self.height()//2 - self.name_label.height()//2)

        self.count_label = QLabel(str(count), self)
        self.count_label.setStyleSheet(styles_tableitem)
        self.count_label.adjustSize()
        # pad and center
        self.count_label.move(self.table.col2title.x(),
                              self.height()//2 - self.count_label.height()//2)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(color_foreground, self.table.LINE_W)
        painter.setPen(pen)
        y = self.height()
        bottom_line = QLine(0, y, self.width(), y)
        painter.drawLine(bottom_line)
        x = self.table.col2title.x() - PluginTable.PADDING
        seperator = QLine(x, 0, x, y)
        painter.drawLine(seperator)
