"""Styling data for MultiFX GUI components

Qt styling is very similar to CSS, though we can't designate a CSS file to it
without introducing a lot of parsing logic.

Qt stylesheet documentation:
https://doc.qt.io/qtforpython-6/overviews/qtwidgets-stylesheet.html

"""

font_family = "Kode Mono"

styles_indicator = f"""
    font: bold 13px;
    font-family: {font_family};
"""

styles_label = f"""
    font : bold 30px;
    font-family : {font_family};
"""
