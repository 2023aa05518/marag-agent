"""ChromaDB client and storage operations."""

import logging
from typing import Dict, Tuple, Optional

import chromadb

from .config import CHROMADB_CONFIG

logger = logging.getLogger(__name__)


class ChromaClient:
    """ChromaDB client for document storage operations."""
    
    def __init__(self):
        self.client = None
        self.collection = None
    
    def connect(self) -> bool:
        """Establish connection to ChromaDB."""
        logger.info("Connecting to ChromaDB...")
        try:
            self.client = chromadb.HttpClient(
                host=CHROMADB_CONFIG["host"],
                port=CHROMADB_CONFIG["port"],
                headers=CHROMADB_CONFIG["headers"]
            )
            heartbeat = self.client.heartbeat()
            logger.info(f"ChromaDB connected successfully! Server heartbeat: {heartbeat}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}", exc_info=True)
            return False
    
    def get_collection(self, collection_name: str = None) -> bool:
        """Get or create collection."""
        if not self.client:
            logger.error("No ChromaDB client connection")
            return False
        
        collection_name = collection_name or CHROMADB_CONFIG["collection_name"]
        try:
            self.collection = self.client.get_or_create_collection(name=collection_name)
            logger.info(f"Collection '{collection_name}' ready")
            return True
        except Exception as e:
            logger.error(f"Failed to get collection: {e}", exc_info=True)
            return False
    
    def store_documents(self, collection_data: Dict) -> bool:
        """Store documents in ChromaDB collection."""
        if not self.collection:
            logger.error("No collection available")
            return False
        
        logger.info("Storing documents to ChromaDB...")
        try:
            self.collection.add(
                ids=collection_data["ids"],
                documents=collection_data["documents"],
                metadatas=collection_data["metadatas"]
            )
            logger.info(f"Successfully stored {len(collection_data['ids'])} chunks")
            return True
        except Exception as e:
            logger.error(f"Failed to store documents: {e}", exc_info=True)
            return False


def setup_chroma_client() -> Tuple[Optional[ChromaClient], bool]:
    """Setup and return configured ChromaDB client."""
    client = ChromaClient()
    
    if not client.connect():
        return None, False
    
    if not client.get_collection():
        return None, False
    
    return client, True
