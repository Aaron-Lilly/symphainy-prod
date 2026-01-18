"""
Clock Abstraction

Phase 0 Utility: Provides clock abstraction for determinism (testing, replay).

WHAT (Utility): I provide time abstraction for deterministic execution
HOW (Implementation): I use datetime with optional override for testing
"""

from datetime import datetime, timezone
from typing import Optional


class Clock:
    """
    Clock abstraction for deterministic time.
    
    Provides time operations with optional override for testing/replay.
    """
    
    def __init__(self, override_time: Optional[datetime] = None):
        """
        Initialize clock.
        
        Args:
            override_time: Optional override time for testing/replay
        """
        self._override_time = override_time
    
    def now(self) -> datetime:
        """
        Get current time (UTC).
        
        Returns:
            Current datetime in UTC, or override time if set
        """
        if self._override_time:
            return self._override_time
        return datetime.now(timezone.utc)
    
    def now_utc(self) -> datetime:
        """
        Get current time (UTC) - alias for now().
        
        Returns:
            Current datetime in UTC, or override time if set
        """
        return self.now()
    
    def now_iso(self) -> str:
        """
        Get current time as ISO string.
        
        Returns:
            Current datetime as ISO 8601 string
        """
        return self.now().isoformat()
    
    def parse_iso(self, iso_string: str) -> datetime:
        """
        Parse ISO 8601 string to datetime.
        
        Args:
            iso_string: ISO 8601 formatted datetime string
        
        Returns:
            Parsed datetime object
        
        Raises:
            ValueError: If string cannot be parsed
        """
        # Handle common ISO formats
        # Remove 'Z' suffix and replace with '+00:00' for UTC
        normalized = iso_string.replace('Z', '+00:00')
        
        # Try parsing with fromisoformat (Python 3.7+)
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            # Fallback: try parsing with strptime for common formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(iso_string, fmt)
                except ValueError:
                    continue
            
            # If all parsing fails, raise error
            raise ValueError(f"Unable to parse ISO string: {iso_string}")
    
    def set_override(self, override_time: Optional[datetime]):
        """
        Set time override (for testing/replay).
        
        Args:
            override_time: Override time or None to clear
        """
        self._override_time = override_time
    
    def clear_override(self):
        """Clear time override."""
        self._override_time = None


# Global clock instance
_global_clock: Optional[Clock] = None


def get_clock() -> Clock:
    """
    Get global clock instance.
    
    Returns:
        Global Clock instance
    """
    global _global_clock
    if _global_clock is None:
        _global_clock = Clock()
    return _global_clock


def set_clock(clock: Clock):
    """
    Set global clock instance (for testing).
    
    Args:
        clock: Clock instance to use
    """
    global _global_clock
    _global_clock = clock


def reset_clock():
    """Reset global clock to default."""
    global _global_clock
    _global_clock = Clock()
