import sys
import time
from PyQt5.QtWidgets import QApplication
import modhostmanager
from qwidgets.core import MainWindow
import offboard


def main():
    if offboard.try_load():
        print("Loaded data from USB drive!")
    app = QApplication(sys.argv)
    modhostmanager.startJackdServer()
    time.sleep(.5)
    modhostmanager.startModHost()
    main_window = MainWindow()
    main_window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
