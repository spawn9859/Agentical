"""Logging system for Agentical application."""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


class Logger:
    """Enhanced logging system with file rotation and formatting."""
    
    def __init__(self, name: str = "agentical", log_dir: str = "logs"):
        """Initialize logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files
        """
        self.name = name
        self.log_dir = log_dir
        self._logger = None
        self.setup_logger()
    
    def setup_logger(self) -> None:
        """Set up logging configuration."""
        # Create logs directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create logger
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler with rotation
        log_file = os.path.join(self.log_dir, f"{self.name}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._logger.critical(message, **kwargs)
    
    def log_action(self, action_type: str, details: dict) -> None:
        """Log desktop action with details.
        
        Args:
            action_type: Type of action (click, type, key, etc.)
            details: Action details dictionary
        """
        timestamp = datetime.now().isoformat()
        self.info(f"ACTION: {action_type} - {details}", extra={
            'action_type': action_type,
            'details': details,
            'timestamp': timestamp
        })
    
    def log_ai_decision(self, context: str, decision: str, confidence: float) -> None:
        """Log AI decision making.
        
        Args:
            context: Context of the decision
            decision: Decision made
            confidence: Confidence level (0-1)
        """
        self.info(f"AI_DECISION: {decision} (confidence: {confidence:.2f}) - {context}")
    
    def log_safety_check(self, action: str, result: str, reason: str) -> None:
        """Log safety check results.
        
        Args:
            action: Action being checked
            result: SAFE or UNSAFE
            reason: Reason for the result
        """
        level = logging.INFO if result == "SAFE" else logging.WARNING
        self._logger.log(level, f"SAFETY_CHECK: {result} - {action} - {reason}")
    
    def log_error_with_context(self, error: Exception, context: str) -> None:
        """Log error with additional context.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
        """
        self.error(f"ERROR in {context}: {str(error)}", exc_info=True)


# Global logger instance
logger = Logger()