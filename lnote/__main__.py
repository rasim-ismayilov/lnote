import sys
import os

def main():
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QIcon
    from .window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName('LNote')
    app.setApplicationVersion('1.0.0')
    app.setOrganizationName('LNote')

    # Load icon if bundled next to the package
    icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.svg')
    icon_path = os.path.normpath(icon_path)
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    # Open files passed on the command line
    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            window.open_file(arg)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
