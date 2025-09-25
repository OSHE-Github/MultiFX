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


class BoxOfJsons(QWidget):
    def __init__(self, page: int, boards: list):
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
