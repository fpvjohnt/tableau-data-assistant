"""
Logging utility for Tableau Data Assistant
Provides centralized logging with file rotation and custom formatters
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from datetime import datetime
import traceback

from config.settings import (
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE,
    LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
    LOGS_DIR
)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class AppLogger:
    """Application logger with file and console handlers"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str, level: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger instance

        Args:
            name: Logger name (usually __name__)
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level or LOG_LEVEL))
        logger.propagate = False

        # Remove existing handlers
        logger.handlers.clear()

        # File handler with rotation
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(LOG_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def log_exception(cls, logger: logging.Logger, exception: Exception, context: str = ""):
        """
        Log exception with full traceback

        Args:
            logger: Logger instance
            exception: Exception to log
            context: Additional context information
        """
        error_msg = f"{context}\n" if context else ""
        error_msg += f"Exception: {type(exception).__name__}: {str(exception)}\n"
        error_msg += f"Traceback:\n{traceback.format_exc()}"
        logger.error(error_msg)

    @classmethod
    def create_session_log(cls, session_id: str) -> Path:
        """
        Create a dedicated log file for a session

        Args:
            session_id: Unique session identifier

        Returns:
            Path to session log file
        """
        session_log_dir = LOGS_DIR / "sessions"
        session_log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = session_log_dir / f"session_{session_id}_{timestamp}.log"

        return log_file


# Convenience functions
def get_logger(name: str = __name__) -> logging.Logger:
    """Get a logger instance"""
    return AppLogger.get_logger(name)


def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {type(e).__name__}: {str(e)}")
            raise
    return wrapper


def log_execution_time(func):
    """Decorator to log function execution time"""
    def wrapper(*args, **kwargs):
        import time
        logger = get_logger(func.__module__)
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {str(e)}")
            raise
    return wrapper


# Initialize main application logger
app_logger = get_logger("tableau_assistant")
app_logger.info("=" * 80)
app_logger.info("Tableau Data Assistant - Logging initialized")
app_logger.info(f"Log file: {LOG_FILE}")
app_logger.info("=" * 80)
