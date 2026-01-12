# Advanced Logging and Monitoring System
"""
Sophisticated logging infrastructure providing comprehensive monitoring,
performance tracking, and intelligent log management capabilities.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json

class IntelligentLogManager:
    """
    Advanced logging orchestrator providing enterprise-grade logging capabilities
    with intelligent log rotation, structured logging, and performance monitoring.
    """
    
    # Default logging configuration
    DEFAULT_LOG_FORMAT = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    DEFAULT_BACKUP_COUNT = 5
    
    # Log level mappings
    LOG_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    @classmethod
    def configure_service_logger(
        cls,
        service_name: str,
        log_file_path: Optional[str] = None,
        log_level: str = "INFO",
        enable_console: bool = True,
        structured_logging: bool = True
    ) -> logging.Logger:
        """
        Configure a comprehensive logger for a specific service with advanced features.
        
        Args:
            service_name: Unique identifier for the service
            log_file_path: Optional custom log file path
            log_level: Logging verbosity level
            enable_console: Whether to enable console output
            structured_logging: Whether to use structured JSON logging
            
        Returns:
            Configured logger instance ready for use
        """
        # Create logger instance
        logger = logging.getLogger(service_name)
        logger.setLevel(cls.LOG_LEVELS.get(log_level.upper(), logging.INFO))
        
        # Clear existing handlers to prevent duplicates
        logger.handlers.clear()
        
        # Configure file logging
        if log_file_path:
            file_handler = cls._create_file_handler(log_file_path, structured_logging)
            logger.addHandler(file_handler)
        
        # Configure console logging
        if enable_console:
            console_handler = cls._create_console_handler(structured_logging)
            logger.addHandler(console_handler)
        
        # Add performance monitoring capability
        logger = cls._enhance_with_performance_monitoring(logger)
        
        return logger
    
    @classmethod
    def _create_file_handler(cls, log_file_path: str, structured_logging: bool) -> logging.Handler:
        """
        Create an intelligent file handler with rotation and compression capabilities.
        """
        # Ensure log directory exists
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure rotating file handler
        file_handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=cls.DEFAULT_MAX_BYTES,
            backupCount=cls.DEFAULT_BACKUP_COUNT,
            encoding='utf-8'
        )
        
        # Set appropriate formatter
        if structured_logging:
            formatter = cls._create_structured_formatter()
        else:
            formatter = logging.Formatter(
                fmt=cls.DEFAULT_LOG_FORMAT,
                datefmt=cls.DEFAULT_DATE_FORMAT
            )
        
        file_handler.setFormatter(formatter)
        return file_handler
    
    @classmethod
    def _create_console_handler(cls, structured_logging: bool) -> logging.Handler:
        """
        Create an enhanced console handler with color support and intelligent formatting.
        """
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Set appropriate formatter
        if structured_logging:
            formatter = cls._create_structured_formatter()
        else:
            # Enhanced console formatter with colors (if supported)
            formatter = cls._create_colored_formatter()
        
        console_handler.setFormatter(formatter)
        return console_handler
    
    @classmethod
    def _create_structured_formatter(cls) -> logging.Formatter:
        """
        Create a structured JSON formatter for machine-readable logs.
        """
        class StructuredFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                    'service': record.name,
                    'level': record.levelname,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # Add exception information if present
                if record.exc_info:
                    log_data['exception'] = self.formatException(record.exc_info)
                
                # Add any extra fields
                for key, value in record.__dict__.items():
                    if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                                   'filename', 'module', 'lineno', 'funcName', 'created', 
                                   'msecs', 'relativeCreated', 'thread', 'threadName', 
                                   'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                        log_data[key] = value
                
                return json.dumps(log_data)
        
        return StructuredFormatter()
    
    @classmethod
    def _create_colored_formatter(cls) -> logging.Formatter:
        """
        Create a colored formatter for enhanced console readability.
        """
        # Color codes for different log levels
        colors = {
            'DEBUG': '\033[36m',      # Cyan
            'INFO': '\033[32m',       # Green
            'WARNING': '\033[33m',    # Yellow
            'ERROR': '\033[31m',      # Red
            'CRITICAL': '\033[35m',   # Magenta
            'RESET': '\033[0m'        # Reset
        }
        
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                # Add color codes if terminal supports them
                if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
                    color = colors.get(record.levelname, colors['RESET'])
                    record.levelname = f"{color}{record.levelname}{colors['RESET']}"
                
                return super().format(record)
        
        return ColoredFormatter(
            fmt=cls.DEFAULT_LOG_FORMAT,
            datefmt=cls.DEFAULT_DATE_FORMAT
        )
    
    @classmethod
    def _enhance_with_performance_monitoring(cls, logger: logging.Logger) -> logging.Logger:
        """
        Enhance logger with performance monitoring capabilities.
        """
        # Add custom methods for performance tracking
        def log_performance(message: str, duration: float, **kwargs):
            extra_data = {
                'performance_metric': True,
                'duration_ms': round(duration * 1000, 2),
                **kwargs
            }
            logger.info(f"[PERFORMANCE] {message}", extra=extra_data)
        
        def log_business_event(event_type: str, event_data: Dict[str, Any]):
            extra_data = {
                'business_event': True,
                'event_type': event_type,
                'event_data': event_data
            }
            logger.info(f"[BUSINESS_EVENT] {event_type}", extra=extra_data)
        
        # Attach methods to logger
        logger.log_performance = log_performance
        logger.log_business_event = log_business_event
        
        return logger
    
    @classmethod
    def create_system_logger(cls, component_name: str = "system") -> logging.Logger:
        """
        Create a standardized system logger with intelligent defaults.
        
        Args:
            component_name: Name of the system component
            
        Returns:
            Configured system logger
        """
        log_directory = Path("logs")
        log_directory.mkdir(exist_ok=True)
        
        log_file_path = log_directory / f"{component_name}_operations.log"
        
        return cls.configure_service_logger(
            service_name=f"system.{component_name}",
            log_file_path=str(log_file_path),
            log_level="INFO",
            enable_console=True,
            structured_logging=True
        )

# Legacy compatibility function
def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    Legacy compatibility wrapper for the original setup_logger function.
    Maintains backward compatibility while using the new intelligent log manager.
    """
    level_name = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL"
    }.get(level, "INFO")
    
    return IntelligentLogManager.configure_service_logger(
        service_name=name,
        log_file_path=log_file,
        log_level=level_name,
        enable_console=False,
        structured_logging=False
    )

# Example usage demonstration
if __name__ == "__main__":
    # Create an example logger
    test_logger = IntelligentLogManager.create_system_logger("test_component")
    
    # Demonstrate logging capabilities
    test_logger.info("System initialization completed")
    test_logger.log_performance("Database query execution", 0.125, query_type="SELECT")
    test_logger.log_business_event("user_registration", {"user_id": 12345, "source": "web"})
    test_logger.warning("Configuration fallback applied")
    test_logger.error("Authentication failure detected")
