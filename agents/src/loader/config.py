"""Configuration settings for document loading and processing."""

from pathlib import Path
from typing import Dict, Any

# Directory paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "../../data"

# Text processing settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# ChromaDB settings
CHROMADB_CONFIG = {
    "host": "localhost",
    "port": 8001,
    "headers": {"Authorization": "Bearer my-secret-token"},
    "collection_name": "docs"
}

# Logging format
LOG_FORMAT = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
