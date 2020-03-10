import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

LOGGER_TAGS: List[Dict[str, str]] = [
                    {"name" : "ALL"  , "color" : "black"},
                    {"name" : "TRACE", "color" : "gray"},
                    {"name" : "DEBUG", "color" : "blue"},
                    {"name" : "INFO" , "color" : "green"},
                    {"name" : "WARN" , "color" : "darkMagenta"},
                    {"name" : "ERROR", "color" : "red"},
                    {"name" : "FATAL", "color" : "darkred"}
                ]


def  find_tag_by_name(name: str) -> dict:
    logger.debug("searching : " + name)
    for tag in LOGGER_TAGS:
        if tag["name"] == name:
            logger.debug("Find : " + tag["name"])
            return tag
