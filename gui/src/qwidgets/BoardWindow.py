from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtCore import Qt, QRect
from plugin_manager import PluginManager, Parameter
from qwidgets import BoxOfPlugins, Cursor, ParameterPanel
from modhostmanager import quitModHost, updateParameter, updateBypass


class BoardWindow(QWidget):
    def __init__(
            self, manager: PluginManager, mod_host_manager, restart_callback
    ):
        super().__init__()
        self.plugins = manager
        self.mod_host_manager = mod_host_manager
        self.restart_callback = restart_callback
        self.backgroundColor = "#E2C290"

        self.rcount = 0

        self.mycursor = 0
        self.page = 0
        self.param_page = 0
        self.current = "plugins"

        self.setGeometry(0, 0, 480, 800)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#E2C290"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.pluginbox = BoxOfPlugins(self.page, self.plugins)
        self.pluginbox.setParent(self)

        self.arrow = Cursor(self.mycursor)
        self.arrow.setParent(self)
        self.arrow.raise_()

        self.pageNum = QLabel("Pgn " + str(self.page), self)
        self.pageNum.adjustSize()
        self.pageNum.move(
            self.width()-self.pageNum.width()-25, self.height()-25
        )

        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        key = event.key()

        match key:
            case Qt.Key_R:
                self.changeBypass(self.mycursor + (3 * self.page))
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

        if key == Qt.Key_R:
            self.rcount += 1
            if self.rcount >= 7:
                self.rcount = 0
                quitModHost(self.mod_host_manager)
                self.restart_callback()
        else:
            self.rcount = 0

        match self.current:
            case "plugins":
                match key:
                    case Qt.Key_Q:
                        self.mycursor = max(0, self.mycursor - 1)
                        self.arrow.changePointer(self.mycursor)
                    case Qt.Key_W:
                        self.openParamPage()
                    case Qt.Key_E:
                        self.mycursor = min((2), self.mycursor + 1)
                        self.arrow.changePointer(self.mycursor)
                    case Qt.Key_S:
                        self.pageUpPlugins()
                    case Qt.Key_X:
                        self.pageDownPlugins()

            case "parameters":
                match key:
                    case Qt.Key_Q:
                        self.descreaseParameter(0)
                    case Qt.Key_W:
                        self.closeParamPage()
                    case Qt.Key_E:
                        self.increaseParameter(0)
                    case Qt.Key_A:
                        self.descreaseParameter(1)
                    case Qt.Key_S:
                        self.pageUpParameters()
                    case Qt.Key_D:
                        self.increaseParameter(1)
                    case Qt.Key_Z:
                        self.descreaseParameter(2)
                    case Qt.Key_X:
                        self.pageDownParameters()
                    case Qt.Key_C:
                        self.increaseParameter(2)

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(Qt.black, 10)
        painter.setPen(pen)

        rect = QRect(0, 0, self.width()-1, self.height())
        painter.drawRect(rect)

    def showEvent(self, event):
        self.setFocus()

    def descreaseParameter(self, position: int):
        params = self.plugin.parameters
        try:
            parameter: Parameter = params[position + 3*(self.param_page)]
            parameter.setValue(round(max(
                parameter.minimum, parameter.value - parameter.increment), 2)
            )
            if updateParameter(
                    self.mod_host_manager,
                    self.mycursor + 3*self.page,
                    parameter
            ) != 0:
                print("Failed to update")
                pass
            self.paramPanel.updateParameter(position)
            self.update()
        except Exception as e:
            print(e)
            pass

    def increaseParameter(self, position: int):
        params = self.plugin.parameters
        try:
            parameter: Parameter = params[position + 3*(self.param_page)]
            parameter.setValue(round(min(
                parameter.max, parameter.value + parameter.increment), 2)
            )
            if updateParameter(
                    self.mod_host_manager,
                    self.mycursor + 3*self.page,
                    parameter
            ) != 0:
                print("Failed to update")
                pass
            self.paramPanel.updateParameter(position)
            self.update()
        except Exception as e:
            print(e)
            pass

    def openParamPage(self):
        try:
            self.param_page = 0
            self.plugin = self.plugins.plugins[self.mycursor + (3 * self.page)]
            self.paramPanel = ParameterPanel(
                    self.backgroundColor,
                    self.mycursor,
                    self.param_page,
                    self.plugin
            )
            self.paramPanel.setParent(self)
            self.paramPanel.show()
            self.arrow.hide()
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
        self.arrow.show()
        self.update()
        self.current = "plugins"
        self.plugin = None

        self.pageNum.setText("Pgn " + str(self.page))
        self.pageNum.adjustSize()
        self.pageNum.move(
            self.width()-self.pageNum.width()-25, self.height()-25
        )
        self.update()

    def pageUpPlugins(self):
        if (self.page == 0):
            self.page = self.page + 1
            self.pluginbox.deleteLater()
            del self.pluginbox
            self.pluginbox = BoxOfPlugins(self.page, self.plugins)
            self.pluginbox.setParent(self)
            self.pluginbox.show()

            self.pageNum.setText("Pgn " + str(self.page))
            self.pageNum.adjustSize()
            self.pageNum.move(
                self.width()-self.pageNum.width()-25, self.height()-25
            )
            self.update()

    def pageDownPlugins(self):
        if (self.page == 1):
            self.page = self.page - 1
            self.pluginbox.deleteLater()
            del self.pluginbox
            self.pluginbox = BoxOfPlugins(self.page, self.plugins)
            self.pluginbox.setParent(self)
            self.pluginbox.show()

            self.pageNum.setText("Pgn " + str(self.page))
            self.pageNum.adjustSize()
            self.pageNum.move(
                self.width()-self.pageNum.width()-25, self.height()-25
            )
            self.update()

    def changeBypass(self, position):
        try:
            # get the value of bypass from the plugin our cursor is currently
            # on
            plugin = self.plugins.plugins[position]
            bypass = plugin.bypass

            # flip value
            bypass = bypass ^ 1
            plugin.bypass = bypass
            updateBypass(self.mod_host_manager, position, plugin)
            self.pluginbox.updateBypass(self.page, position, bypass)
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
                    self.mycursor,
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
                    self.mycursor,
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
