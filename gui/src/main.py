import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QStackedWidget
)
from PyQt5.QtGui import (
    QPixmap, QPainter, QPen, QColor, QTransform
)
from PyQt5.QtCore import Qt, QRect
from plugin_manager import PluginManager, Plugin, Parameter
import os
from modhostmanager import (
    startModHost, connectToModHost, updateParameter, updateBypass,
    quitModHost, setUpPatch, setUpPlugins, verifyParameters, startJackdServer
)


class BoardWindow(QWidget):
    def __init__(self, manager : PluginManager, mod_host_manager, restart_callback):
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


        self.setGeometry(0,0,480,800)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#E2C290"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.pluginbox = BoxofPlugins(self.page, self.plugins)
        self.pluginbox.setParent(self)

        self.arrow = Cursor(self.mycursor)
        self.arrow.setParent(self)
        self.arrow.raise_()

        self.pageNum = QLabel("Pgn " + str(self.page), self)
        self.pageNum.adjustSize()
        self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)

        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        key = event.key()

        match key:
            case Qt.Key_R:
                self.changeBypass(self.mycursor +(3* self.page))
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
    
    def showEvent(self,event):
        self.setFocus()

    def descreaseParameter(self, position : int):
        try:
            parameter : Parameter = self.plugin.parameters[position + 3*(self.param_page)]
            parameter.setValue(round(max(parameter.minimum, parameter.value - parameter.increment), 2))
            if updateParameter(self.mod_host_manager, self.mycursor + 3*self.page, parameter) != 0:
                print("Failed to update")
                pass
            self.paramPanel.updateParameter(position)
            self.update()
        except:
            pass

    def increaseParameter(self, position : int):
        try:
            parameter : Parameter = self.plugin.parameters[position + 3*(self.param_page)]
            parameter.setValue(round(min(parameter.max, parameter.value + parameter.increment), 2))
            if updateParameter(self.mod_host_manager, self.mycursor + 3*self.page, parameter) != 0:
                print("Failed to update")
                pass
            self.paramPanel.updateParameter(position)
            self.update()
        except:
            pass
    
    def openParamPage(self):
        try:
            self.param_page = 0
            self.plugin = self.plugins.plugins[self.mycursor + (3 * self.page)]
            self.paramPanel = ParameterPanel(self.backgroundColor, self.mycursor, self.param_page, self.plugin)
            self.paramPanel.setParent(self)
            self.paramPanel.show()
            self.arrow.hide()
            self.update()
            self.current = "parameters"

            self.pageNum.setText("Pgn " + str(self.param_page))
            self.pageNum.adjustSize()
            self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)
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
        self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)
        self.update()
    
    def pageUpPlugins(self):
        if(self.page == 0):
            self.page = self.page + 1
            self.pluginbox.deleteLater()
            del self.pluginbox
            self.pluginbox = BoxofPlugins(self.page, self.plugins)
            self.pluginbox.setParent(self)
            self.pluginbox.show()

            self.pageNum.setText("Pgn " + str(self.page))
            self.pageNum.adjustSize()
            self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)
            self.update()
    
    def pageDownPlugins(self):
        if(self.page == 1):
            self.page = self.page - 1
            self.pluginbox.deleteLater()
            del self.pluginbox
            self.pluginbox = BoxofPlugins(self.page, self.plugins)
            self.pluginbox.setParent(self)
            self.pluginbox.show()

            self.pageNum.setText("Pgn " + str(self.page))
            self.pageNum.adjustSize()
            self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)
            self.update()

    def changeBypass(self, position):
        try:
            #get the value of bypass from the plugin our cursor is currently on
            plugin = self.plugins.plugins[position]
            bypass = plugin.bypass

            #flip value
            bypass = bypass ^ 1
            plugin.bypass = bypass
            updateBypass(self.mod_host_manager, position, plugin)
            self.pluginbox.updateBypass(self.page,position, bypass)
        except:
            pass
    
    def pageUpParameters(self):
        if(self.param_page == 0):
            self.param_page = self.param_page + 1
            self.paramPanel.deleteLater()
            del self.paramPanel
            self.paramPanel = ParameterPanel(self.backgroundColor, self.mycursor, self.param_page, self.plugin)
            self.paramPanel.setParent(self)
            self.paramPanel.show()

            self.pageNum.setText("Pgn " + str(self.param_page))
            self.pageNum.adjustSize()
            self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)
            self.update()
    
    def pageDownParameters(self):
        if(self.param_page == 1):
            self.param_page = self.param_page - 1
            self.paramPanel.deleteLater()
            del self.paramPanel
            self.paramPanel = ParameterPanel(self.backgroundColor, self.mycursor, self.param_page, self.plugin)
            self.paramPanel.setParent(self)
            self.paramPanel.show()

            self.pageNum.setText("Pgn " + str(self.param_page))
            self.pageNum.adjustSize()
            self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)
            self.update()

class BoxofJsons(QWidget):
    def __init__(self,page : int, boards : list):
        super().__init__()
        self.setFixedSize(480, 800)
        self.boxes = []
        for index in range(0, 3):
            try:
                box = BoxWidget(index + 3*page, boards[index + 3*page])
                box.setParent(self)
                box.move(0, (self.height()//3)*index)
                self.boxes.append(box)
            except Exception as e:
                box = BoxWidget(index + 3*page)
                box.setParent(self)
                box.move(0, (self.height()//3)*index)
                self.boxes.append(box)

class PedalBoardSelectWindow(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.json_dir = os.path.dirname(os.path.abspath(__file__))
        # TODO: No relative linepaths
        self.json_files = self.get_json_files(f"../config/") 
        self.board = BoxofJsons(0, self.json_files)
        self.board.setParent(self)

        self.callback = callback

        self.mycursor = 0
        self.setGeometry(0,0,480,800)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#E2C290"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.arrow = Cursor(self.mycursor)
        self.arrow.setParent(self)
        self.arrow.raise_()

        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        key = event.key()
        
        match key:
            case Qt.Key_Q:
                self.mycursor = max(0, self.mycursor - 1)
                self.arrow.changePointer(self.mycursor)

            case Qt.Key_W:
                selected_file = os.path.join(f"{self.json_dir}/Json", self.json_files[self.mycursor])
                print(selected_file)
                self.callback(selected_file)
            
            case Qt.Key_E:
                self.mycursor = min(2, self.mycursor +1)
                self.arrow.changePointer(self.mycursor)
            
        

    def get_json_files(self,directory):
        """Returns a list of all JSON files in the specified directory."""
        return [f for f in os.listdir(directory) if f.endswith('.json')]

    def showEvent(self, event):
        self.setFocus()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 480, 800)

        self.stack = QStackedWidget(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.stack)

        # Create selection screen
        self.start_screen = PedalBoardSelectWindow(self.launch_board)
        self.stack.addWidget(self.start_screen)

        self.board_window = None  # Placeholder for later

        self.show()

    def launch_board(self, selected_json):
        """Called when a JSON file is selected to load the board"""
        board = PluginManager()
        board.initFromJSON(selected_json)
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
        self.board_window = BoardWindow(board, mod_host_manager=modhost, restart_callback=self.show_start_screen)
        self.stack.addWidget(self.board_window)
        self.stack.setCurrentWidget(self.board_window)  # Switch view
        self.board_window.setFocus()

    def show_start_screen(self):
        """Switch back to the start screen."""
        self.stack.setCurrentWidget(self.start_screen)  # Switch back
        self.start_screen.setFocus()


def main():
    app = QApplication(sys.argv)
    startJackdServer()
    time.sleep(.1)
    main_window = MainWindow()
    main_window.showFullScreen()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
