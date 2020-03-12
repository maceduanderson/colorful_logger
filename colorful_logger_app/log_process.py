from PyQt5.QtGui import QTextDocument

from colorful_logger_app import LOGGER_TAGS, logger
from PyQt5.Qt import QTextBlock, QTextCursor, QTextBlockUserData


class LogUserData(QTextBlockUserData):
    tag = LOGGER_TAGS[0]

    def __init__(self, data=None):
        super(LogUserData, self).__init__()
        for tag in LOGGER_TAGS:
            if tag == data:
                self.tag = tag

    def get_data(self):
        return self.tag


def log_mark_block(block: QTextBlock, tag: dict) -> None:
    """mark a block with the selected tag"""
    block.setUserData(LogUserData(tag))


def log_filter_by_tag(document: QTextDocument, tag_selected: dict):
    """ Filter a document, setting visibility according to the tag """
    document: QTextDocument
    block: QTextBlock

    block = document.begin()
    while block.isValid():
        data = block.userData()
        if data is not None:
            tag: dict = data.get_data()
            if tag is not None:
                if tag_selected == LOGGER_TAGS[0]:
                    block.setVisible(True)
                elif tag != LOGGER_TAGS[0] and tag != tag_selected:
                    block.setVisible(False)
                else:
                    block.setVisible(True)
        block = block.next()


def log_search_document(document: QTextDocument, position: int, search_string: str):
    cursor: QTextCursor
    flag = QTextDocument.FindWholeWords
    cursor_doc = QTextCursor(document)
    cursor = document.find(search_string, cursor_doc, flag)
