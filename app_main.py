import logging
import sys

from PyQt5.QtWidgets import QApplication

from colorful_logger_app.constants import *
from colorful_logger_app.logger_gui import MainWindow

__author__ = APP_AUTHOR
__license__ = APP_LICENCE
__version__ = APP_VERSION
__email__ = APP_AUTHOR_EMAIL
__status__ = APP_STATUS

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(levelname)-8s : %(message)s")
    app = QApplication([])
    window = MainWindow()
    window.show()
    with open(fake_log_dev_path) as file:
        for line in file.readlines():
            window.log_area.appendPlainText(line.rstrip("\n"))
    app.exec()