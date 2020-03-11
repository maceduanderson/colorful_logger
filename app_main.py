import logging
import sys

from PyQt5.QtWidgets import QApplication

from colorful_logger_app.logger_gui import MainWindow

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(levelname)-8s : %(message)s")
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()