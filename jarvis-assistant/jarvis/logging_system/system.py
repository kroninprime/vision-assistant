"""Comprehensive logging and error handling system."""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger("jarvis")


class JarvisLogger:
    """Centralized logging for JARVIS system."""

    def __init__(self, log_dir: Path = None):
        self.log_dir = log_dir or Path("./logs")
        self.log_dir.mkdir(exist_ok=True)
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging with file and console handlers."""
        # File handler - all logs
        log_file = self.log_dir / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler - info and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Root logger
        root_logger = logging.getLogger("jarvis")
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """Get logger for specific module."""
        return logging.getLogger(f"jarvis.{name}")


class ErrorHandler:
    """Handle and recover from errors gracefully."""

    def __init__(self, learning_engine=None):
        self.learning_engine = learning_engine
        self.error_count = 0
        self.error_log = []

    def handle_error(self, error: Exception, context: str = "", recovery_action: str = None) -> str:
        """
        Handle error with logging and recovery suggestion.
        
        Args:
            error: The exception
            context: What was happening when error occurred
            recovery_action: Suggested recovery
        
        Returns:
            User-friendly error message
        """
        self.error_count += 1
        logger.error(f"Error in {context}: {error}", exc_info=True)

        error_info = {
            "error": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
        }
        self.error_log.append(error_info)

        # Record for learning
        if self.learning_engine:
            self.learning_engine.record_error_recovery(
                error_type=type(error).__name__,
                recovery_action=recovery_action or "Retry operation",
            )

        # Return friendly message
        user_message = f"I encountered an issue: {type(error).__name__}"
        if recovery_action:
            user_message += f". {recovery_action}"
        else:
            user_message += ". Please try again."

        return user_message

    def get_error_summary(self) -> str:
        """Get summary of recent errors."""
        if not self.error_log:
            return "No errors recorded"

        summary = f"Recent errors ({len(self.error_log)}):\n"
        for error in self.error_log[-5:]:
            summary += f"  • {error['error_type']} in {error['context']}\n"

        return summary


def create_logger_system(log_dir: Path = None) -> tuple[JarvisLogger, logging.Logger]:
    """Create and return logger system."""
    logger_system = JarvisLogger(log_dir)
    main_logger = logger_system.get_logger("main")
    return logger_system, main_logger
