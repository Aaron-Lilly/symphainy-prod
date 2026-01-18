"""
Retry Helpers - Exponential Backoff and Retry Logic

Provides retry logic with exponential backoff for resilient operations.

WHAT (Utility Role): I provide retry logic for resilient operations
HOW (Utility Implementation): I use exponential backoff and configurable retry strategies
"""

import asyncio
import random
from typing import Callable, Any, Optional, Dict, Type, Tuple
from utilities import get_logger


async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None
) -> Any:
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Base for exponential backoff (default: 2.0)
        jitter: Whether to add random jitter to delays (default: True)
        retryable_exceptions: Tuple of exception types to retry on (default: all exceptions)
        on_retry: Optional callback function called on each retry (retry_num, exception)
    
    Returns:
        Function result
    
    Raises:
        Last exception if all retries fail
    """
    logger = get_logger("retry_helpers")
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except retryable_exceptions as e:
            last_exception = e
            
            if attempt < max_retries:
                # Calculate delay with exponential backoff
                delay = min(
                    initial_delay * (exponential_base ** attempt),
                    max_delay
                )
                
                # Add jitter if enabled
                if jitter:
                    jitter_amount = delay * 0.1 * random.random()
                    delay = delay + jitter_amount
                
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                # Call retry callback if provided
                if on_retry:
                    try:
                        on_retry(attempt + 1, e)
                    except Exception as callback_error:
                        logger.error(f"Error in retry callback: {callback_error}")
                
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")
                raise
    
    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Retry logic failed unexpectedly")


def get_retry_strategy_for_ingestion_type(ingestion_type: str) -> Dict[str, Any]:
    """
    Get retry strategy for specific ingestion type.
    
    Different ingestion types may need different retry strategies:
    - EDI: May need more retries due to network/partner issues
    - API: May need fewer retries but longer delays
    - Upload: Standard retry strategy
    
    Args:
        ingestion_type: Ingestion type ("upload", "edi", "api")
    
    Returns:
        Dictionary with retry strategy parameters
    """
    strategies = {
        "upload": {
            "max_retries": 3,
            "initial_delay": 1.0,
            "max_delay": 30.0,
            "exponential_base": 2.0
        },
        "edi": {
            "max_retries": 5,  # More retries for EDI (network/partner issues)
            "initial_delay": 2.0,
            "max_delay": 60.0,
            "exponential_base": 2.0
        },
        "api": {
            "max_retries": 3,
            "initial_delay": 1.5,
            "max_delay": 45.0,
            "exponential_base": 2.5  # Faster backoff for API
        }
    }
    
    return strategies.get(ingestion_type.lower(), strategies["upload"])
