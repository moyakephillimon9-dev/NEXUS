"""
NEXUS Logger Module

Centralized logging system for all NEXUS operations.
Logs are written to both console and persistent files.

Usage:
    from core.logger import get_logger, get_chat_logger, get_error_logger
    log = get_logger()
    log.info("Message")
    log.error("Error message")
"""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
LOG_FOLDER = Path(__file__).resolve().parent.parent / 'logs'
LOG_FOLDER.mkdir(exist_ok=True)

# Log file paths
MAIN_LOG_FILE = LOG_FOLDER / 'nexus.log'
ERROR_LOG_FILE = LOG_FOLDER / 'errors.log'
CHAT_LOG_FILE = LOG_FOLDER / 'chat.log'
PIPELINE_LOG_FILE = LOG_FOLDER / 'pipeline.log'
HEALTH_LOG_FILE = LOG_FOLDER / 'health.log'


class Logger:
    """Centralized NEXUS logging system."""
    
    def __init__(self, name="NEXUS", log_file=MAIN_LOG_FILE):
        self.name = name
        self.log_file = log_file
        self.logger = self._setup_logger(name, log_file)
    
    def _setup_logger(self, name, log_file):
        """Configure logger with file and console handlers."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        if logger.handlers:
            for handler in logger.handlers:
                logger.removeHandler(handler)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler with rotation (10 MB, keep 5 backups)
        try:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"[WARNING] Could not create file handler: {e}")
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)
    
    def debug(self, message):
        """Log debug message."""
        self.logger.debug(message)
    
    def critical(self, message):
        """Log critical message."""
        self.logger.critical(message)


class ChatLogger:
    """Specialized logger for chat interactions."""
    
    def __init__(self):
        self.logger = Logger("NEXUS-CHAT", CHAT_LOG_FILE)
    
    def log_message(self, role, content, owner_id=None):
        """Log a chat message."""
        snippet = content[:80] if len(content) > 80 else content
        self.logger.info(f"[{role.upper()}] Owner:{owner_id} | {snippet}")
    
    def log_error(self, error, message=None, owner_id=None):
        """Log a chat error."""
        self.logger.error(f"Chat Error | Owner:{owner_id} | Msg:{message} | {error}")


class PipelineLogger:
    """Specialized logger for pipeline execution."""
    
    def __init__(self):
        self.logger = Logger("NEXUS-PIPELINE", PIPELINE_LOG_FILE)
    
    def log_stage(self, task_id, stage_number, stage_name):
        """Log pipeline stage."""
        self.logger.info(f"[{task_id}] Stage {stage_number}: {stage_name}")
    
    def log_stage_error(self, task_id, stage_name, error):
        """Log stage error."""
        self.logger.error(f"[{task_id}] Stage Failed: {stage_name} | {error}")


class HealthLogger:
    """Specialized logger for system health."""
    
    def __init__(self):
        self.logger = Logger("NEXUS-HEALTH", HEALTH_LOG_FILE)
    
    def log_check(self, component, status, details=None):
        """Log health check."""
        msg = f"{component}: {status}"
        if details:
            msg += f" | {details}"
        self.logger.info(msg)


class ErrorLogger:
    """Specialized logger for critical errors."""
    
    def __init__(self):
        self.logger = Logger("NEXUS-ERROR", ERROR_LOG_FILE)
    
    def log_exception(self, exception, context=None):
        """Log exception with traceback."""
        msg = f"{type(exception).__name__}: {str(exception)}"
        if context:
            msg += f" | {context}"
        self.logger.error(msg, exc_info=True)
    
    def log_fatal(self, message):
        """Log fatal error."""
        self.logger.critical(f"FATAL: {message}")


def get_logger(name="NEXUS"):
    return Logger(name)

def get_chat_logger():
    return ChatLogger()

def get_pipeline_logger():
    return PipelineLogger()

def get_health_logger():
    return HealthLogger()

def get_error_logger():
    return ErrorLogger()
