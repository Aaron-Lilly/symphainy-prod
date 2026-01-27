"""
Structured Logging (JSON)

Phase 0 Utility: Provides structured JSON logging for all platform components.

WHAT (Utility): I provide structured JSON logging
HOW (Implementation): I use Python logging with JSON formatter
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(str, Enum):
    """Log categories for taxonomy."""
    PLATFORM = "platform"
    DOMAIN = "domain"
    AGENT = "agent"
    INFRASTRUCTURE = "infrastructure"


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    
    Formats log records as JSON with consistent structure.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, "category"):
            log_data["category"] = record.category
        
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        
        if hasattr(record, "saga_id"):
            log_data["saga_id"] = record.saga_id
        
        if hasattr(record, "event_id"):
            log_data["event_id"] = record.event_id
        
        if hasattr(record, "tenant_id"):
            log_data["tenant_id"] = record.tenant_id
        
        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id
        
        if hasattr(record, "metadata"):
            log_data["metadata"] = record.metadata
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None,
            }
        
        return json.dumps(log_data, default=str)


class StructuredLogger:
    """
    Structured logger with JSON output.
    
    Provides structured logging with consistent JSON format.
    """
    
    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        category: Optional[LogCategory] = None
    ):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (typically module/service name)
            level: Log level
            category: Log category (platform, domain, agent, infrastructure)
        """
        self.name = name
        self.category = category or LogCategory.PLATFORM
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value.upper())
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Add JSON formatter handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def _log(
        self,
        level: LogLevel,
        message: str,
        session_id: Optional[str] = None,
        saga_id: Optional[str] = None,
        event_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Any] = None
    ):
        """Internal log method with structured fields."""
        extra = {
            "category": self.category.value,
        }
        
        if session_id:
            extra["session_id"] = session_id
        if saga_id:
            extra["saga_id"] = saga_id
        if event_id:
            extra["event_id"] = event_id
        if tenant_id:
            extra["tenant_id"] = tenant_id
        if trace_id:
            extra["trace_id"] = trace_id
        if metadata:
            extra["metadata"] = metadata
        
        log_method = getattr(self.logger, level.value.lower())
        log_method(message, extra=extra, exc_info=exc_info)
    
    def debug(
        self,
        message: str,
        session_id: Optional[str] = None,
        saga_id: Optional[str] = None,
        event_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log debug message."""
        self._log(
            LogLevel.DEBUG,
            message,
            session_id=session_id,
            saga_id=saga_id,
            event_id=event_id,
            tenant_id=tenant_id,
            trace_id=trace_id,
            metadata=metadata
        )
    
    def info(
        self,
        message: str,
        session_id: Optional[str] = None,
        saga_id: Optional[str] = None,
        event_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log info message."""
        self._log(
            LogLevel.INFO,
            message,
            session_id=session_id,
            saga_id=saga_id,
            event_id=event_id,
            tenant_id=tenant_id,
            trace_id=trace_id,
            metadata=metadata
        )
    
    def warning(
        self,
        message: str,
        session_id: Optional[str] = None,
        saga_id: Optional[str] = None,
        event_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log warning message."""
        self._log(
            LogLevel.WARNING,
            message,
            session_id=session_id,
            saga_id=saga_id,
            event_id=event_id,
            tenant_id=tenant_id,
            trace_id=trace_id,
            metadata=metadata
        )
    
    def error(
        self,
        message: str,
        session_id: Optional[str] = None,
        saga_id: Optional[str] = None,
        event_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Any] = None
    ):
        """Log error message."""
        self._log(
            LogLevel.ERROR,
            message,
            session_id=session_id,
            saga_id=saga_id,
            event_id=event_id,
            tenant_id=tenant_id,
            trace_id=trace_id,
            metadata=metadata,
            exc_info=exc_info
        )
    
    def critical(
        self,
        message: str,
        session_id: Optional[str] = None,
        saga_id: Optional[str] = None,
        event_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Any] = None
    ):
        """Log critical message."""
        self._log(
            LogLevel.CRITICAL,
            message,
            session_id=session_id,
            saga_id=saga_id,
            event_id=event_id,
            tenant_id=tenant_id,
            trace_id=trace_id,
            metadata=metadata,
            exc_info=exc_info
        )


def get_logger(
    name: str,
    level: LogLevel = LogLevel.INFO,
    category: Optional[LogCategory] = None
) -> StructuredLogger:
    """
    Get structured logger instance.
    
    Args:
        name: Logger name (typically module/service name)
        level: Log level
        category: Log category (platform, domain, agent, infrastructure)
    
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name=name, level=level, category=category)
