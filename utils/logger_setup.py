"""
Logger setup utilities for the travel planner.
"""

import logging
import sys


def configure_travel_planner_logger() -> logging.Logger:
    logging.getLogger().setLevel(logging.CRITICAL)
    logger = logging.getLogger("travel_planner")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    log_formatter = logging.Formatter("%(levelname)s: %(message)s")
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    file_handler = logging.FileHandler("travel_planner.log", mode="w", encoding="utf-8")
    file_handler.setFormatter(log_formatter)

    logger.handlers.clear()
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger

