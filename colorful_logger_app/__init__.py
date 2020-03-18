import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

LOGGER_TAGS: List[Dict[str, str]] = [
    {"name": "ALL", "color": "black"},
    {"name": "TRACE", "color": "gray"},
    {"name": "DEBUG", "color": "blue"},
    {"name": "INFO", "color": "green"},
    {"name": "WARN", "color": "darkMagenta"},
    {"name": "ERROR", "color": "red"},
    {"name": "FATAL", "color": "darkred"}
]

DEFAULT_COLORS = ["black", "gray", "blue", "green", "darkMagenta", "red", "darkred", "yellow"]

LOGGER_TIMESTAMPS:  List[Dict[str, str]] = [
    {"name": "YYYY[:/]MM[:/]DD HH:MM:SS", "rule": "([0-9]{4})(\\:|\\/)([0-2]{2})(\\:|\\/)([0-9]{2}) ([0-9]{2})\\:(["
                                                  "0-9]{2})\\:([0-9]{2})"},
    {"name":"YYYY[:/]MM[:/]DD", "rule": "([0-9]{4})(\\:|\\/)([0-2]{2})(\\:|\\/)([0-9]{2})"},
    {"name":"HH:MM:SS", "rule": "([0-9]{2})\\:([0-9]{2})\\:([0-9]{2})"}]


def find_tag_by_name(name: str) -> dict:
    for tag in LOGGER_TAGS:
        if tag["name"] == name:
            return tag
