import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QColor, Qt
from qwidgets import BoxOfJsons, Cursor


class PedalBoardSelectWindow(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.json_dir = os.path.dirname(os.path.abspath(__file__))
        # TODO: No relative linepaths
        self.json_files = self.get_json_files("../config/")
        self.board = BoxOfJsons(0, self.json_files)
        self.board.setParent(self)

        self.callback = callback

        self.mycursor = 0
        self.setGeometry(0, 0, 480, 800)

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
                selected_file = os.path.join(
                        f"{self.json_dir}/Json",
                        self.json_files[self.mycursor]
                )
                print(selected_file)
                self.callback(selected_file)
            case Qt.Key_E:
                self.mycursor = min(2, self.mycursor + 1)
                self.arrow.changePointer(self.mycursor)

    def get_json_files(self, directory):
        """Returns a list of all JSON files in the specified directory."""
        return [f for f in os.listdir(directory) if f.endswith('.json')]

    def showEvent(self, event):
        self.setFocus()
