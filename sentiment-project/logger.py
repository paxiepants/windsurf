"""
Logging module for the sentiment analysis project.
Provides centralized logging configuration and utilities.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from config import config


class ColoredFormatter(logging.Formatter):
    """
    Colored log formatter for console output.
    Uses ANSI color codes for better readability.
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        """Format log record with colors"""
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_to_file: bool = True,
    log_to_console: bool = True
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.

    Args:
        name: Logger name (usually __name__ of the module)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console

    Returns:
        logging.Logger: Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name)

    # Set log level
    level = level or config.LOG_LEVEL
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    file_formatter = logging.Formatter(config.LOG_FORMAT)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # File handler (rotating)
    if log_to_file:
        try:
            file_handler = RotatingFileHandler(
                config.LOG_PATH,
                maxBytes=config.LOG_MAX_BYTES,
                backupCount=config.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create file handler: {e}")

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        logging.Logger: Configured logger instance
    """
    return setup_logger(name)


class LoggerMixin:
    """
    Mixin class that provides logging capabilities to any class.
    Usage: class MyClass(LoggerMixin): ...
    """

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return get_logger(name)


def log_function_call(func):
    """
    Decorator to log function calls with arguments and return values.

    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            ...
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__}(args={args}, kwargs={kwargs})")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} raised {type(e).__name__}: {e}")
            raise
    return wrapper


def log_exception(logger: logging.Logger, exc: Exception, message: str = ""):
    """
    Log an exception with full traceback.

    Args:
        logger: Logger instance
        exc: Exception to log
        message: Additional message to include
    """
    if message:
        logger.error(f"{message}: {exc}", exc_info=True)
    else:
        logger.error(f"Exception occurred: {exc}", exc_info=True)


# Create module-level logger
module_logger = get_logger(__name__)


if __name__ == "__main__":
    # Test logging functionality
    test_logger = get_logger("test")

    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.critical("This is a critical message")

    # Test exception logging
    try:
        1 / 0
    except Exception as e:
        log_exception(test_logger, e, "Division by zero test")

    print(f"\nLog file created at: {config.LOG_PATH}")
