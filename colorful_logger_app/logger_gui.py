'''
Created on 2 de mar de 2020

@author: AndersonMacedo
'''
import logging

import serial
import serial.tools.list_ports_windows
from PyQt5.Qt import QRect, QThread, pyqtSlot, QStandardItem, QColor, QTextDocument, QRegularExpression, QTextCursor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QBrush, QFont
from PyQt5.QtWidgets import *
from serial.serialutil import SerialException

from colorful_logger_app import LOGGER_TAGS, find_tag_by_name
from colorful_logger_app.log_process import log_filter_by_tag, log_mark_block

logger = logging.getLogger(__name__)

LOG_HEADER_SIZE = 35


class SerialListenerWorker(QThread):
    """Listen the serial connection and send the data to the main window"""
    signal = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.serial_handler = None

    def __del__(self):
        if self.serial_handler and self.serial_handler.isOpen():
            self.serial_handler.close()
        self.terminate()

    def run(self):
        while self.serial_handler.isOpen():
            msg = self.serial_handler.readline()
            if msg != "":
                self.signal.emit(msg.decode().strip())
            self.sleep(0)


class SerialDialog(QDialog):
    """Create a dialog interface for connecting and disconnecting from the serial interface"""

    def __init__(self, parent=None):
        super(SerialDialog, self).__init__(parent)

        self.serial_handler = serial.Serial()

        self.form_layout = QFormLayout(self)
        self.form_layout.setFormAlignment(Qt.AlignLeft)
        self.form_layout.setLabelAlignment(Qt.AlignLeft)
        self.form_layout.setContentsMargins(2, 2, 2, 2)

        # TODO more ports
        # TODO unix port sintax
        # TODO connect with text parameters

        baudrate_label = QLabel("Baudrate :")
        baudrates = ["9600", "19200", "38400", "57600", "115200"]
        self.baudrate_combo = QComboBox()
        model = self.baudrate_combo.model()
        for baudrate in baudrates:
            item = QStandardItem(baudrate)
            model.appendRow(item)
        self.baudrate_combo.setCurrentText("115200")
        logger.debug("baudrate  ok")

        port_label = QLabel("Porta :")
        logger.debug("Listing ports")
        ports = ["COM" + str(i) for i in range(0,11)]
        self.ports_combo = QComboBox()
        model = self.ports_combo.model()
        for port in ports:
            item = QStandardItem(port)
            model.appendRow(item)
        self.ports_combo.setCurrentText("COM5")
        logger.debug("port ok")

        parity_label = QLabel("Paridade :")
        paritys = ["None", "Even", "Odd"]
        self.paritys_combo = QComboBox()
        model = self.paritys_combo.model()
        for parity in paritys:
            item = QStandardItem(parity)
            model.appendRow(item)
        self.paritys_combo.setCurrentText("None")

        stop_bits_label = QLabel("Stop Bits :")
        stop_bits = ["1", "1.5", "2"]
        self.stop_bits_combo = QComboBox()
        model = self.stop_bits_combo.model()
        for stop_bit in stop_bits:
            item = QStandardItem(stop_bit)
            model.appendRow(item)
        self.stop_bits_combo.setCurrentText("1")

        byte_size_label = QLabel("Byte Size :")
        byte_sizes = [str(i) for i in range(5, 9)]
        self.byte_sizes_combo = QComboBox()
        model = self.byte_sizes_combo.model()
        for byte_size in byte_sizes:
            item = QStandardItem(byte_size)
            model.appendRow(item)
        self.byte_sizes_combo.setCurrentText("8")

        self.widgets_list = [self.baudrate_combo, self.ports_combo, self.paritys_combo,
                             self.stop_bits_combo, self.byte_sizes_combo]

        self.message_box = QPlainTextEdit()
        self.message_box.setFixedHeight(60)
        self.message_box.setReadOnly(True)

        self.connect_button = QPushButton("Conectar")
        self.connect_button.clicked.connect(self.connect_to_serial)
        self.connect_button.setEnabled(True)

        self.disconnect_button = QPushButton("Desconectar")
        self.disconnect_button.clicked.connect(self.disconnect_from_serial)
        self.disconnect_button.setEnabled(False)

        self.form_layout.addRow(baudrate_label, self.baudrate_combo)
        self.form_layout.addRow(port_label, self.ports_combo)
        self.form_layout.addRow(parity_label, self.paritys_combo)
        self.form_layout.addRow(stop_bits_label, self.stop_bits_combo)
        self.form_layout.addRow(byte_size_label, self.byte_sizes_combo)
        self.form_layout.addRow(self.message_box)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.connect_button, alignment=Qt.AlignJustify)
        buttons_layout.addWidget(self.disconnect_button, alignment=Qt.AlignJustify)
        self.form_layout.addRow(buttons_layout)

    def connect_to_serial(self):
        """ Connect to the serial interface"""
        baudrate = self.baudrate_combo.currentText()
        port = self.ports_combo.currentText()
        parity = self.paritys_combo.currentText()
        stop_bit = self.stop_bits_combo.currentText()
        byte_size = self.byte_sizes_combo.currentText()

        self.serial_handler.port = port
        self.serial_handler.baudrate = int(baudrate)

        if parity == "Even":
            self.serial_handler.parity = serial.PARITY_EVEN
        elif parity == "Odd":
            self.serial_handler.parity = serial.PARITY_ODD
        elif parity == "None":
            self.serial_handler.parity = serial.PARITY_NONE

        if stop_bit == "1":
            self.serial_handler.stopbits = serial.STOPBITS_ONE
        elif stop_bit == "1.5":
            self.serial_handler.stopbits = serial.STOPBITS_ONE_POINT_FIVE
        elif stop_bit == "2":
            self.serial_handler.stopbits = serial.STOPBITS_TWO

        self.serial_handler.bytesize = int(byte_size)

        message = "Connecting to {0}\n" \
                  "Baudrate : {1}\n" \
                  "Parity : {2}\n" \
                  "Stop Bit : {3}\n" \
                  "Byte Size : {4}\n".format(port, baudrate, parity, stop_bit, byte_size)
        self.message_box.clear()
        self.message_box.appendPlainText(message)

        try:
            self.serial_handler.open()
        except (SerialException, IOError) as e:
            self.message_box.appendPlainText(str(e))
        except:
            self.message_box.appendPlainText("Connection Error")
        finally:
            if self.serial_handler.isOpen():
                if self.serial_handler.isOpen():
                    self.enable_all_widgets(False)
                self.message_box.appendPlainText("Connection Sucess")
                self.connect_button.setEnabled(False)
                self.disconnect_button.setEnabled(True)
            else:
                self.enable_all_widgets(True)
                self.connect_button.setEnabled(True)
                self.disconnect_button.setEnabled(False)
            self.done(0)

    def closeEvent(self, QCloseEvent):
        """if the user close the window send done(0)
         if connected otherwise done(1)"""
        if self.serial_handler.isOpen():
            self.done(0)
        else:
            self.done(1)

    def disconnect_from_serial(self):
        """disconnect from the serial interface send send done(1)"""
        self.message_box.appendPlainText("Disconnected from serial")
        self.enable_all_widgets(True)
        self.disconnect_button.setEnabled(False)
        self.connect_button.setEnabled(True)
        self.done(1)

    def enable_all_widgets(self, flag: bool):
        """Enable/disable all widgets(without buttons) of the dialog"""
        for widget in self.widgets_list:
            widget.setEnabled(flag)


class FilterPanel(QWidget):
    """ Create the area with the filters and find and clear buttons """
    filter_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super(FilterPanel, self).__init__(parent)

        self.form_layout = QFormLayout(parent)
        self.form_layout.setFormAlignment(Qt.AlignLeft)
        self.form_layout.setLabelAlignment(Qt.AlignLeft)
        self.form_layout.setContentsMargins(1, 0, 0, 1)

        self.filter_layout_1 = QHBoxLayout()

        self.filter_label = QLabel("Filtro :")

        self.filter_line = QLineEdit()

        self.log_types = QComboBox()
        model = self.log_types.model()
        for tag in LOGGER_TAGS:
            item = QStandardItem(tag['name'])
            item.setForeground(QColor(tag['color']))
            model.appendRow(item)

        self.log_types.colorCount()
        self.log_types.setCurrentText(LOGGER_TAGS[0]["name"])
        self.log_types.currentTextChanged.connect(self.get_log_type)

        self.filter_layout_1.addWidget(self.log_types)
        self.filter_layout_1.addWidget(self.filter_line)

        self.filter_layout_2 = QHBoxLayout()

        self.filter_search_button = QPushButton("Buscar")
        self.filter_clear_button = QPushButton("Apagar")

        self.filter_layout_2.addWidget(self.filter_search_button)
        self.filter_layout_2.addWidget(self.filter_clear_button)

        self.form_layout.addRow(self.filter_label, self.filter_layout_1)
        self.form_layout.addRow(self.filter_layout_2)

    def get_log_type(self):
        """Send a signal to the main window with the selected log tag"""
        self.filter_changed.emit(self.log_types.currentText())


class HighlighterTag(QSyntaxHighlighter):
    """
        Search for (ALL|DEBUG|INFO|ERROR|CRITICAL|FATAL) tags in the text
        inserted on the log area. Format the tag with the correspond color.
        See colorful_logger_app.LOGGER_TAGS
    """

    def __init__(self, parent):
        super(HighlighterTag, self).__init__(parent)

        self.highlight_rules = []
        for tag in LOGGER_TAGS:
            font = QFont()
            font.setBold(True)
            format_text = QTextCharFormat()
            format_text.setFont(font)
            format_text.setForeground(QBrush(QColor(tag["color"])))
            format_text.setFontUnderline(True)
            self.highlight_rules += [(QRegularExpression(tag["name"]), format_text)]

    def highlightBlock(self, p_str):
        if len(p_str) == 0:
            pass
        block = self.currentBlock()
        for rules, format_text in self.highlight_rules:
            # Search the tag in the firts LOG_HEADER_SIZE bytes of the string.
            # TODO: search for more rules like timestamp, line, func|module name

            match = rules.match(p_str[:LOG_HEADER_SIZE] if len(p_str) > LOG_HEADER_SIZE else p_str)
            if match.hasMatch():
                self.setFormat(match.capturedStart(), match.capturedLength(), format_text)
                tag_label = match.captured(0)
                log_mark_block(block, find_tag_by_name(tag_label))


class MainWindow(QMainWindow):
    """ Create the main
        Create the main window and setup all
        widgets needed.
     """

    def __init__(self):
        super(MainWindow, self).__init__()

        self.log_area = None                # :type QPlainTextEdit
        self.main_document = None           # :type QTextDocument
        self.serial_dialog = None           # :type SerialDialog
        self.serial_menu = None             # :type QMenu
        self.help_menu = None               # :type QMenu
        self.log_filter_widget = None       # :type QWidget
        self.log_filters = None             # :type FilterPanel
        self.last_search = str()
        self.last_search_cursor = QTextCursor()

        container = QWidget()
        self.setup_menu()
        self.setup_text_area()
        self.setup_footer_panel()
        self.setup_serial_dialog()

        self.first_search_flag = False

        self.serial_worker = SerialListenerWorker()
        self.serial_worker.signal.connect(self.add_line_to_log_area)

        self.log_area.appendPlainText("DEBUG - TESTE1")
        self.log_area.appendPlainText("ERROR - TESTE2")

        self.log_area_layout = QVBoxLayout()
        self.log_area_layout.setContentsMargins(0, 0, 0, 0)
        self.log_area_layout.addWidget(self.log_area)
        self.log_area_layout.addWidget(self.log_filter_widget)
        container.setLayout(self.log_area_layout)

        self.setCentralWidget(container)

        self.setWindowTitle("Beautiful Logger")
        self.setGeometry(QRect(100, 100, 800, 600))

    def closeEvent(self, event):
        self.serial_dialog.serial_handler.close()
        del self.serial_worker

    def setup_serial_dialog(self):
        """Setup the Serial Dialog interface"""
        self.serial_dialog = SerialDialog(self)

    def setup_menu(self):
        """Setup the menu"""
        self.serial_menu = self.menuBar().addMenu("Serial")
        self.help_menu = self.menuBar().addMenu("Help")

        action_serial_setup = QAction("Setup", self)
        action_serial_setup.triggered.connect(self.serial_setup)
        self.serial_menu.addAction(action_serial_setup)

        action_about_box = QAction("About", self)
        action_about_box.triggered.connect(self.about_box_show)
        self.help_menu.addAction(action_about_box)

    def setup_text_area(self):
        """Setup the log text area and the highlighter class"""
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.centerOnScroll()

        self.main_document = self.log_area.document()
        HighlighterTag(self.log_area.document())

    def setup_footer_panel(self):
        """Setup the footer area"""
        self.log_filter_widget = QWidget()
        self.log_filters = FilterPanel(self.log_filter_widget)
        self.log_filters.filter_changed.connect(self.filter_document)
        self.log_filters.filter_clear_button.clicked.connect(self.clear_log_area)
        self.log_filters.filter_search_button.clicked.connect(self.search_log_area)

    @pyqtSlot(str)
    def filter_document(self, msg: str):
        """Filter the log area with the selected tag.
           The log area will show only the lines with the selected tag
           or untagged lines.
        :type msg: str (ALL|DEBUG|INFO|ERROR|CRITICAL|FATAL)
        """
        tag = find_tag_by_name(msg)
        log_filter_by_tag(self.main_document, tag)

    def serial_setup(self):
        """
            Execute the serial dialog interface.
            If the the result (:type dialog_result : int)== 0 and the
            connection is successfully done, start the serial_worker thread
            If the the result (:type dialog_result : int) == 1, disconnection
            was requested, the worker is closed and the serial connection are closed
        """
        dialog_result = self.serial_dialog.exec()
        logger.debug("SerialDialog result : " + str(dialog_result))
        if dialog_result == 0:
            if self.serial_dialog.serial_handler.isOpen():
                self.serial_worker.serial_handler = self.serial_dialog.serial_handler
                self.serial_worker.start()
        elif dialog_result == 1:
            self.serial_worker.terminate()
            self.serial_dialog.serial_handler.close()

    def about_box_show(self):
        about_msg_box = QMessageBox(self)
        about_msg_box.addButton(QPushButton("OK"), QMessageBox.YesRole)
        about_msg_box.setWindowTitle("Colorful Logger")
        about_msg_box.setText("VERSION 0.1")
        #about_msg_box.about(self, ).show()
        about_msg_box.exec()

    @pyqtSlot(str)
    def add_line_to_log_area(self, log):
        """
        Add a string to the log area
        :param log: str
        """
        self.log_area.appendPlainText(log)

    def clear_log_area(self):
        """
        clear the log area
        """
        self.log_area.clear()

    def search_log_area(self):
        """ Search a word in log area.
        Keep last cursor and word used for iteration
        in the document.
        """

        cursor: QTextCursor
        doc : QTextDocument
        text : str

        text = self.log_filters.filter_line.text()
        doc = self.log_area.document()

        if len(text) == 0 or text != self.last_search:
            self.last_search_cursor = QTextCursor()
            self.last_search = text
            return

        cursor = self.last_search_cursor if not self.last_search_cursor.isNull() else QTextCursor(doc)
        cursor = doc.find(text, cursor)
        self.last_search_cursor = cursor
        logger.debug(cursor.selectedText())
