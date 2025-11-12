"""
Logging Utilities

Structured logging setup for FRS platform.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    rich_tracebacks: bool = True
) -> logging.Logger:
    """
    Setup logging with Rich formatting

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for file logging
        rich_tracebacks: Enable rich tracebacks

    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger("frs_platform")
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler with Rich formatting
    console_handler = RichHandler(
        rich_tracebacks=rich_tracebacks,
        markup=True,
        show_time=True,
        show_path=False
    )
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        "%(message)s",
        datefmt="[%X]"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler if log_file specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "frs_platform") -> logging.Logger:
    """
    Get logger instance

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
