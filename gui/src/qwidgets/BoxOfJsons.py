from PyQt5.QtWidgets import QWidget
from qwidgets import BoxWidget


# TODO: Rename this when its clearer what it does
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
                print(e)
                self.boxes.append(box)
