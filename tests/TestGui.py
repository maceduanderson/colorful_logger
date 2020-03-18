import unittest

from PyQt5.QtGui import QTextDocument, QTextBlock
from PyQt5.QtWidgets import QApplication

from colorful_logger_app.logger_gui import MainWindow

app = QApplication([])


class TestLogArea(unittest.TestCase):

    def setUp(self) -> None:
        self.window = MainWindow()
        self.n_lines = 0
        with open("fake_logs.txt") as file:
            for line in file.readlines():
                self.window.log_area.appendPlainText(line.rstrip("\n"))
                self.n_lines += 1

    def test_insert_text(self):
        doc: QTextDocument
        block: QTextBlock

        new_line = "New Line"
        lines = self.window.log_area.document().blockCount()
        self.assertEqual(lines, self.n_lines, "Expected [{0}], find [{1}]".format(lines, self.n_lines))
        self.window.log_area.appendPlainText(new_line)
        lines = self.window.log_area.document().blockCount()
        self.assertEqual(lines, self.n_lines + 1, "Expected [{0}], find [{1}]".format(lines, self.n_lines + 1))

        doc = self.window.log_area.document()
        block = doc.lastBlock()
        self.assertIn(new_line, block.text(), "Expected [{0}], found [{1}]".format(new_line, block.text()))

    def test_button_clear(self):
        pass


if __name__ == '__main__':
    unittest.main()
