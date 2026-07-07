import ctypes
import os
import sys

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(0)
except Exception:
    pass

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Aria")
    app.setApplicationVersion("1.0")

    icon_path = os.path.join(
        os.path.dirname(__file__),
        'assets', 'aria.ico'
    )
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
