"""
Error Taxonomy

Phase 0 Utility: Provides error taxonomy (platform vs domain vs agent).

WHAT (Utility): I provide error classification for platform components
HOW (Implementation): I use exception hierarchy with taxonomy
"""

from enum import Enum
from typing import Optional, Dict, Any


class ErrorTaxonomy(str, Enum):
    """Error taxonomy categories."""
    PLATFORM = "platform"  # Infrastructure, runtime, system errors
    DOMAIN = "domain"      # Business logic, validation errors
    AGENT = "agent"        # Agent reasoning, planning errors


class PlatformError(Exception):
    """
    Platform-level error.
    
    Infrastructure, runtime, or system errors.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize platform error.
        
        Args:
            message: Error message
            error_code: Optional error code
            metadata: Optional error metadata
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.metadata = metadata or {}
        self.taxonomy = ErrorTaxonomy.PLATFORM
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "type": "PlatformError",
            "message": self.message,
            "error_code": self.error_code,
            "taxonomy": self.taxonomy.value,
            "metadata": self.metadata,
        }


class DomainError(Exception):
    """
    Domain-level error.
    
    Business logic or validation errors.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize domain error.
        
        Args:
            message: Error message
            error_code: Optional error code
            metadata: Optional error metadata
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.metadata = metadata or {}
        self.taxonomy = ErrorTaxonomy.DOMAIN
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "type": "DomainError",
            "message": self.message,
            "error_code": self.error_code,
            "taxonomy": self.taxonomy.value,
            "metadata": self.metadata,
        }


class AgentError(Exception):
    """
    Agent-level error.
    
    Agent reasoning or planning errors.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize agent error.
        
        Args:
            message: Error message
            error_code: Optional error code
            metadata: Optional error metadata
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.metadata = metadata or {}
        self.taxonomy = ErrorTaxonomy.AGENT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "type": "AgentError",
            "message": self.message,
            "error_code": self.error_code,
            "taxonomy": self.taxonomy.value,
            "metadata": self.metadata,
        }


def categorize_error(error: Exception) -> ErrorTaxonomy:
    """
    Categorize error by taxonomy.
    
    Args:
        error: Exception to categorize
    
    Returns:
        Error taxonomy category
    """
    if isinstance(error, PlatformError):
        return ErrorTaxonomy.PLATFORM
    elif isinstance(error, DomainError):
        return ErrorTaxonomy.DOMAIN
    elif isinstance(error, AgentError):
        return ErrorTaxonomy.AGENT
    else:
        # Default to platform for unknown errors
        return ErrorTaxonomy.PLATFORM
