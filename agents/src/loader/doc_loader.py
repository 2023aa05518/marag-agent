import os
import logging
from pathlib import Path
from typing import List, Dict

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import TokenTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import chromadb

# Setup logging
logger = logging.getLogger(__name__)

# Define data directory
base_dir = Path(__file__).parent
logger.debug(f"Base directory: {base_dir}")
data_dir = base_dir / "../../data"
logger.debug(f"Data directory: {data_dir}")

def load_pdf_documents() -> List[Document]:
    """Load all PDF documents from ./data folder"""
    logger.info("Loading PDF documents...")
    documents = []
    
    for pdf_file in data_dir.glob("*.pdf"):
        logger.debug(f"Loading file: {pdf_file.name}")
        loader = PyPDFLoader(str(pdf_file))
        pages = loader.load_and_split()
        
        # Add document name to metadata
        for page in pages:
            page.metadata["doc_name"] = pdf_file.stem
        
        documents.extend(pages)
    
    logger.info(f"Loaded {len(documents)} pages from {len(list(data_dir.glob('*.pdf')))} PDFs")
    return documents

def create_text_chunks(documents: List[Document]) -> List[Document]:
    """Create text chunks with sequential page numbering to avoid duplicates"""
    logger.info("Creating text chunks...")
    splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = []
    
    # Add sequential index to each document page
    for seq_idx, doc in enumerate(documents):
        doc.metadata["sequence_index"] = seq_idx
        doc.metadata["original_page_number"] = doc.metadata["page"]
        
        doc_chunks = splitter.split_documents([doc])
        
        # Generate unique chunk IDs using sequential index
        for chunk_idx, chunk in enumerate(doc_chunks):
            chunk.metadata.update({
                "chunk_index": chunk_idx,
                "sequence_index": seq_idx,
                "original_page_number": chunk.metadata["page"],
                "chunk_id": f"{chunk.metadata['doc_name']}_seq{seq_idx:03d}_chunk{chunk_idx}"
            })
        
        chunks.extend(doc_chunks)
    
    logger.info(f"Created {len(chunks)} text chunks")
    return chunks

def get_doc_collection(chunks: List[Document]) -> Dict:
    """Generate and return a document collection for ChromaDB."""
    logger.info("Generating document collection...")

    # Prepare data for ChromaDB
    texts = [chunk.page_content for chunk in chunks]
    ids = [chunk.metadata["chunk_id"] for chunk in chunks]
    metadatas = [
        {
            "doc_name": chunk.metadata["doc_name"],
            "page_number": chunk.metadata["page"],
            "chunk_index": chunk.metadata["chunk_index"],
        }
        for chunk in chunks
    ]

    logger.info("Document collection generated successfully")
    return {"ids": ids, "documents": texts, "metadatas": metadatas}

def write_to_db(doc_collection: Dict, collection):
    """Generate embeddings and store in ChromaDB"""
    logger.info("Storing documents to database...")

    # Generate embeddings
    # embeddings_model = HuggingFaceEmbeddings( model_name="sentence-transformers/all-MiniLM-L6-v2" )
    # embeddings = embeddings_model.embed_documents(doc_collection["documents"])

    try:
        # Store in ChromaDB
        collection.add(
            ids=doc_collection["ids"],
            documents=doc_collection["documents"],
            # embeddings=embeddings,
            metadatas=doc_collection["metadatas"],
        )

        logger.info(f"Successfully stored {len(doc_collection['ids'])} chunks in ChromaDB")
    except Exception as e:
        logger.error(f"Failed to store documents in ChromaDB: {e}", exc_info=True)
        raise

def setup_chromadb_client():
    """Setup ChromaDB client and collection"""
    logger.info("Creating ChromaDB client connection...")
    try:
        client = chromadb.HttpClient(
            host="localhost",
            port=8001,
            headers={"Authorization": "Bearer my-secret-token"},
            # tenant="default",
            # database="default"
        )
        heartbeat = client.heartbeat()
        logger.info(f"ChromaDB client created successfully! Server heartbeat: {heartbeat}")
        
        collection = client.get_or_create_collection(name="docs")
        logger.info("ChromaDB setup completed successfully")
        return client, collection
    except Exception as e:
        logger.error(f"Error creating ChromaDB client: {e}", exc_info=True)
        return None, None
    
def loader_pipeline():
    """Main execution pipeline"""
    logger.info("Starting PDF loader pipeline...")
    
    try:
        # Load PDFs
        documents = load_pdf_documents()
        
        # Create chunks
        chunks = create_text_chunks(documents)

        # Get doc collection
        doc_collection = get_doc_collection(chunks)
        
        # Setup ChromaDB
        client, collection = setup_chromadb_client()
        if client is None or collection is None:
            logger.error("Failed to setup ChromaDB. Exiting...")
            return
        
        # Write to database
        write_to_db(doc_collection, collection)
        
        logger.info("Pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Setup logging for standalone execution
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    loader_pipeline()
