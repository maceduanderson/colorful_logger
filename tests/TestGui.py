import unittest

import PyQt5.QtTest as qtest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from colorful_logger_app.logger_gui import MainWindow
app = QApplication([])

class TestLogArea(unittest.TestCase):


    def setUp(self) -> None:
        self.window = MainWindow()
        self.window.log_area.appendPlainText("DEBUG - TESTE1")
        self.window.log_area.appendPlainText("INFO - TESTE2")
        self.window.log_area.appendPlainText("ERROR - TESTE3")
        self.window.show()

    def test_insert_text(self):
        text = self.window.log_area.toPlainText()
        self.assertIn("DEBUG - TESTE1", text)
        self.assertIn("INFO - TESTE2", text)
        self.assertIn("ERROR - TESTE3", text)

    def test_button_clear(self):
        pass


if __name__ == '__main__':
    unittest.main()
