"""PDF to ChromaDB indexing pipeline orchestration."""

import logging

from src.loader.config import LOG_DATE_FORMAT, LOG_FORMAT
from src.loader.document_processor import DocumentProcessor
from src.loader.chroma_client import setup_chroma_client

logger = logging.getLogger(__name__)


def pdf_to_chromadb_pipeline() -> bool:
    logger.info("Starting PDF to ChromaDB indexing pipeline...")
    
    try:
        processor = DocumentProcessor()
        collection_data = processor.process_pdfs()
        
        chroma_client, success = setup_chroma_client()
        if not success:
            logger.error("Failed to setup ChromaDB")
            return False
        
        if not chroma_client.store_documents(collection_data):
            logger.error("Failed to store documents")
            return False
        
        logger.info("PDF to ChromaDB pipeline completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    
    success = pdf_to_chromadb_pipeline()
    exit(0 if success else 1)
