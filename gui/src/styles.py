"""Styling data for MultiFX GUI components

Qt styling is very similar to CSS, though we can't designate a CSS file to it
without introducing a lot of parsing logic.

Qt stylesheet documentation:
https://doc.qt.io/qtforpython-6/overviews/qtwidgets-stylesheet.html

"""

from PyQt5.QtGui import QColor

font_family = "Kode Mono"

color_background = QColor.fromRgb(0, 0, 0)
color_inactive = QColor.fromRgb(102, 102, 102)
color_foreground = QColor.fromRgb(255, 255, 255)
color_error = QColor.fromRgb(255, 0, 0)

color_top = QColor.fromRgb(255, 0, 0)
color_top_inactive = QColor.fromRgb(102, 0, 0)
color_mid = QColor.fromRgb(0, 255, 0)
color_mid_inactive = QColor.fromRgb(0, 102, 0)
color_bot = QColor.fromRgb(0, 0, 255)
color_bot_inactive = QColor.fromRgb(0, 0, 102)

styles_window = f"""
    background: {color_background.name()};
"""

styles_indicator = f"""
    font: bold 13px;
    font-family: {font_family};
    color: {color_foreground.name()};
"""

styles_label = f"""
    font : bold 30px;
    font-family: {font_family};
    color: {color_foreground.name()};
    background: transparent;
"""

styles_bind = f"""
    font : 10px;
    font-family: {font_family};
    color: {color_foreground.name()};
    background: transparent;
"""

styles_bind_inactive = f"""
    font : 10px;
    font-family: {font_family};
    color: {color_inactive.name()};
    background: transparent;
"""

styles_error = f"""
    font: bold 10px;
    font-family: {font_family};
    color: {color_error.name()};
"""
