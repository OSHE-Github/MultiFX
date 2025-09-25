import sys
import time
from PyQt5.QtWidgets import QApplication
from modhostmanager import startJackdServer
from qwidgets import MainWindow


def main():
    app = QApplication(sys.argv)
    startJackdServer()
    time.sleep(.1)
    main_window = MainWindow()
    main_window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
