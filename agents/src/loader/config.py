"""Configuration settings for document loading and processing."""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_required_env(key: str) -> str:
    """Get required environment variable or raise error if not found."""
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value

def get_required_int_env(key: str) -> int:
    """Get required integer environment variable or raise error if not found."""
    value = get_required_env(key)
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Environment variable '{key}' must be a valid integer, got: {value}")

# Directory paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / f"../../{get_required_env('LOADER_DATA_DIR')}"

# Text processing settings
CHUNK_SIZE = get_required_int_env('LOADER_CHUNK_SIZE')
CHUNK_OVERLAP = get_required_int_env('LOADER_CHUNK_OVERLAP')

# ChromaDB settings
CHROMADB_CONFIG = {
    "host": get_required_env('DB_CHROMA_HOST'),
    "port": get_required_int_env('DB_CHROMA_PORT'),
    "headers": {"Authorization": f"Bearer {get_required_env('DB_CHROMA_AUTH_TOKEN')}"},
    "collection_name": get_required_env('DB_CHROMA_COLLECTION')
}

# Logging format
LOG_FORMAT = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
