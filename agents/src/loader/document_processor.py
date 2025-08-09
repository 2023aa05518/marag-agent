"""Pure document processing: loading and chunking PDFs."""

import logging
from pathlib import Path
from typing import List, Dict, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import TokenTextSplitter
from langchain.schema import Document

from .config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


class DocumentProcessor:
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents: List[Document] = []
        self.chunks: List[Document] = []
    
    def load_pdfs(self, data_path: Path = DATA_DIR) -> 'DocumentProcessor':
        """Load all PDF documents from specified directory."""
        logger.info(f"Loading PDF documents from {data_path}")
        self.documents = []
        
        for pdf_file in data_path.glob("*.pdf"):
            logger.debug(f"Loading file: {pdf_file.name}")
            loader = PyPDFLoader(str(pdf_file))
            pages = loader.load_and_split()
            
            for page in pages:
                page.metadata["doc_name"] = pdf_file.stem
            
            self.documents.extend(pages)
        
        logger.info(f"Loaded {len(self.documents)} pages from {len(list(data_path.glob('*.pdf')))} PDFs")
        return self
    
    def create_chunks(self) -> 'DocumentProcessor':
        """Create text chunks with sequential indexing."""
        if not self.documents:
            raise ValueError("No documents loaded. Call load_pdfs() first.")
        
        logger.info("Creating text chunks...")
        splitter = TokenTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        self.chunks = []
        
        for seq_idx, doc in enumerate(self.documents):
            doc.metadata["sequence_index"] = seq_idx
            doc.metadata["original_page_number"] = doc.metadata["page"]
            
            doc_chunks = splitter.split_documents([doc])
            
            for chunk_idx, chunk in enumerate(doc_chunks):
                chunk.metadata.update({
                    "chunk_index": chunk_idx,
                    "sequence_index": seq_idx,
                    "original_page_number": chunk.metadata["page"],
                    "chunk_id": f"{chunk.metadata['doc_name']}_seq{seq_idx:03d}_chunk{chunk_idx}"
                })
            
            self.chunks.extend(doc_chunks)
        
        logger.info(f"Created {len(self.chunks)} text chunks")
        return self
    
    def prepare_data(self) -> Dict:
        """Prepare document data for ChromaDB storage."""
        if not self.chunks:
            raise ValueError("No chunks available. Call create_chunks() first.")
        
        logger.info("Preparing collection data...")
        
        texts = [chunk.page_content for chunk in self.chunks]
        ids = [chunk.metadata["chunk_id"] for chunk in self.chunks]
        metadatas = [
            {
                "doc_name": chunk.metadata["doc_name"],
                "page_number": chunk.metadata["page"],
                "chunk_index": chunk.metadata["chunk_index"],
            }
            for chunk in self.chunks
        ]
        
        logger.info("Collection data prepared successfully")
        return {"ids": ids, "documents": texts, "metadatas": metadatas}
    
    def process_pdfs(self, data_path: Path = DATA_DIR) -> Dict:
        return self.load_pdfs(data_path).create_chunks().prepare_data()
