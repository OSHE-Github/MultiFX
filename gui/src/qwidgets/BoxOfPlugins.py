from PyQt5.QtWidgets import (
    QWidget
)
from plugin_manager import PluginManager, Plugin
import BoxWidget


class BoxOfPlugins(QWidget):
    def __init__(self, page: int, plugins: PluginManager):
        super().__init__()
        self.setFixedSize(480, 800)
        self.boxes = []
        for index in range(0, 3):
            try:
                plugin: Plugin = plugins.plugins[index + (3*(page))]
                box = BoxWidget(index + 3*page, plugin.name, plugin.bypass)
                box.setParent(self)
                box.move(0, (self.height()//3)*index)
                self.boxes.append(box)
            except Exception as e:
                box = BoxWidget(index + 3*page)
                box.setParent(self)
                box.move(0, (self.height()//3)*index)
                print(e)
                self.boxes.append(box)

    def updateBypass(self, page, position: int, bypass):
        # NOTE: this used to be a bare try-except with nothing in the except
        # block. I hope this wasn't meant to error out as a feature.
        try:
            self.boxes[position - (3*page)].updateBypass(bypass)
        except Exception as e:
            print(e)
            pass
