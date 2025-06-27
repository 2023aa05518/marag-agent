import os
from pathlib import Path
from typing import List, Dict

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import TokenTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
# import chromadb

# Define data directory
base_dir = Path(__file__).parent
print (f"base_dir = {base_dir}")
data_dir = base_dir / "../../data"
print(f"data_dir = {data_dir}")

def load_pdf_documents() -> List[Document]:
    """Load all PDF documents from ./data folder"""
    print("🔄 Loading PDF documents...")
    documents = []
    
    for pdf_file in data_dir.glob("*.pdf"):
        print(f"📄 Loading: {pdf_file.name}")
        loader = PyPDFLoader(str(pdf_file))
        pages = loader.load_and_split()
        
        # Add document name to metadata
        for page in pages:
            page.metadata["doc_name"] = pdf_file.stem
        
        documents.extend(pages)
    
    print(f"✅ Loaded {len(documents)} pages from {len(list(data_dir.glob('*.pdf')))} PDFs")
    return documents

def create_text_chunks(documents: List[Document]) -> List[Document]:
    """Create text chunks of size 300 with overlap 100"""
    print("🔄 Creating text chunks...")
    splitter = TokenTextSplitter(chunk_size=300, chunk_overlap=100)
    chunks = []
    
    for doc in documents:
        doc_chunks = splitter.split_documents([doc])
        
        # Add chunk metadata
        for idx, chunk in enumerate(doc_chunks):
            chunk.metadata.update({
                "chunk_index": idx,
                "chunk_id": f"{chunk.metadata['doc_name']}_page{chunk.metadata['page']}_chunk{idx}"
            })
        
        chunks.extend(doc_chunks)
    
    print(f"✅ Created {len(chunks)} text chunks")
    return chunks

def get_doc_collection(chunks: List[Document]) -> Dict:
    """Generate and return a document collection for ChromaDB."""
    print("🔄 Generating doc collection...")

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

    print("✅ Document collection generated")
    return {"ids": ids, "documents": texts, "metadatas": metadatas}

def generate_embeddings_and_store(doc_collection: Dict, collection):
    """Generate embeddings and store in ChromaDB"""
    # print("🔄 Generating embeddings and storing...")

    # Generate embeddings
    # embeddings_model = HuggingFaceEmbeddings( model_name="sentence-transformers/all-MiniLM-L6-v2" )
    # embeddings = embeddings_model.embed_documents(doc_collection["documents"])

    # Store in ChromaDB
    # collection.add(
    #     ids=doc_collection["ids"],
    #     documents=doc_collection["documents"],
    #     embeddings=embeddings,
    #     metadatas=doc_collection["metadatas"],
    # )

    print(f"✅ Stored {len(doc_collection['ids'])} chunks with embeddings in ChromaDB")

def setup_chromadb_client():
    """Setup ChromaDB client and collection"""
    # print("🔄 Creating ChromaDB client connection...")
    # try:
    #     client = chromadb.HttpClient(
    #         host="localhost",
    #         port=8001,
    #         headers={"Authorization": "Bearer my-secret-token"},
    #         tenant="ptc",
    #         database="docs"
    #     )
    #     heartbeat = client.heartbeat()
    #     print(f"✅ ChromaDB client created successfully! Server heartbeat: {heartbeat}")
        
    #     collection = client.get_or_create_collection(name="requirements")
    #     print("✅ ChromaDB setup complete")
    #     return client, collection
    # except Exception as e:
    #     print(f"❌ Error creating ChromaDB client: {e}")
    #     return None, None
    
def main_pipeline():
    """Main execution pipeline"""
    print("🚀 Starting PDF loader pipeline...")
    
    # Load PDFs
    documents = load_pdf_documents()
    
    # Create chunks
    chunks = create_text_chunks(documents)

    # Get doc collection
    doc_collection = get_doc_collection(chunks)
    return doc_collection
    # # Setup ChromaDB
    # client, collection = setup_chromadb_client()
    # if client is None or collection is None:
    #     print("❌ Failed to setup ChromaDB. Exiting...")
    #     return
    
    # # Generate embeddings and store
    # generate_embeddings_and_store(doc_collection, collection)
    
    print("🎉 Pipeline completed successfully!")

if __name__ == "__main__":
    main_pipeline()
