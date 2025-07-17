"""
Simple centralized logging configuration for the multi-agent MARAG system.
Clean, minimal setup that provides exactly what you need.
"""

import logging
import os


def setup_logging(log_level: str = None) -> None:
    """
    Setup basic logging configuration for the application.
    
    Args:
        log_level: Logging level (defaults to LOG_LEVEL env var or INFO)
    """
    # Get log level from environment or parameter
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Simple, clean logging setup
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Log configuration message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level}")
