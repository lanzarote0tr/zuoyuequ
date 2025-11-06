import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

# A4 size in millimeters
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297

# Conversion: 1 inch = 25.4 mm, so 1 mm = dpi / 25.4 pixels
def mm_to_px(mm, dpi):
    return mm * dpi / 25.4

def main():
    app = QApplication(sys.argv)

    screen = app.primaryScreen()
    dpi = screen.logicalDotsPerInch() if screen else 96.0

    width_px = int(mm_to_px(A4_WIDTH_MM, dpi))
    height_px = int(mm_to_px(A4_HEIGHT_MM, dpi))

    window = QWidget()
    window.setWindowTitle(f"A4 Paper ({A4_WIDTH_MM}x{A4_HEIGHT_MM} mm, scrollable)")
    layout = QVBoxLayout(window)

    # Scroll area
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    # A4 page inside the scroll area
    page = QWidget()
    page.setFixedSize(width_px, height_px)
    page.setAutoFillBackground(True)

    pal = page.palette()
    pal.setColor(QPalette.Window, QColor("white"))
    page.setPalette(pal)
    page.setStyleSheet("QWidget { border: 1px solid #000; }")

    info = QLabel(f"DPI: {dpi:.2f}\nA4 size: {A4_WIDTH_MM}x{A4_HEIGHT_MM} mm -> {width_px}x{height_px} px")
    info.setAlignment(Qt.AlignCenter)

    scroll_area.setWidget(page)

    layout.addWidget(info)
    layout.addWidget(scroll_area)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

