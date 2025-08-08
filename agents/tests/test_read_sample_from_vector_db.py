"""
Test script to read sample records from ChromaDB vector database
Displays chunk content, vectors (embeddings), and metadata for verification
"""

import logging
import chromadb
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def setup_chromadb_client():
    """Setup ChromaDB client connection"""
    logger.info("Connecting to ChromaDB...")
    try:
        client = chromadb.HttpClient(
            host="localhost",
            port=8001,
            headers={"Authorization": "Bearer my-secret-token"},
        )
        
        # Test connection
        heartbeat = client.heartbeat()
        logger.info(f"ChromaDB connection successful! Heartbeat: {heartbeat}")
        
        # Get the docs collection
        collection = client.get_collection(name="docs")
        logger.info(f"Retrieved 'docs' collection successfully")
        
        return client, collection
    except Exception as e:
        logger.error(f"Failed to connect to ChromaDB: {e}")
        return None, None


def read_sample_records(collection, limit: int = 5) -> Dict[str, Any]:
    """Read sample records from the collection"""
    logger.info(f"Fetching {limit} sample records...")
    
    try:
        # Get records with all data types
        results = collection.get(
            limit=limit,
            include=["documents", "metadatas", "embeddings"]
        )
        
        logger.info(f"Successfully retrieved {len(results['ids'])} records")
        return results
        
    except Exception as e:
        logger.error(f"Failed to read records: {e}")
        return {}


def display_records(results: Dict[str, Any]):
    """Display the retrieved records in a readable format"""
    if not results or not results.get('ids'):
        logger.warning("No records to display")
        return
    
    print("\n" + "="*80)
    print("SAMPLE RECORDS FROM CHROMADB VECTOR DATABASE")
    print("="*80)
    
    for i, record_id in enumerate(results['ids']):
        print(f"\n📄 RECORD {i+1}")
        print("-" * 40)
        
        # Record ID
        print(f"🆔 ID: {record_id}")
        
        # Metadata
        metadata = results['metadatas'][i] if results.get('metadatas') else {}
        print(f"📋 METADATA:")
        for key, value in metadata.items():
            print(f"   {key}: {value}")
        
        # Document content (chunk)
        document = results['documents'][i] if results.get('documents') else ""
        print(f"📝 CHUNK CONTENT ({len(document)} chars):")
        print(f"   {document[:200]}{'...' if len(document) > 200 else ''}")
        
        # Embeddings/Vectors  
        try:
            embeddings_data = results.get('embeddings')
            if embeddings_data is not None and len(embeddings_data) > i:
                embeddings = embeddings_data[i]
                if embeddings is not None and hasattr(embeddings, '__len__') and len(embeddings) > 0:
                    print(f"🔢 VECTOR INFO:")
                    print(f"   Dimensions: {len(embeddings)}")
                    print(f"   First 5 values: {embeddings[:5]}")
                    print(f"   Vector range: [{min(embeddings):.4f}, {max(embeddings):.4f}]")
                else:
                    print(f"🔢 VECTOR: No embeddings found (using ChromaDB default embeddings)")
            else:
                print(f"🔢 VECTOR: No embeddings found (using ChromaDB default embeddings)")
        except Exception as e:
            print(f"🔢 VECTOR: Error reading embeddings - {str(e)}")
        
        print("-" * 40)


def get_collection_stats(collection):
    """Get basic statistics about the collection"""
    try:
        # Get total count
        total_records = collection.count()
        logger.info(f"Total records in collection: {total_records}")
        
        # Get a few records to check structure
        sample = collection.peek(limit=3)
        
        print(f"\n📊 COLLECTION STATISTICS")
        print(f"Total records: {total_records}")
        
        if sample and sample.get('metadatas'):
            metadata_keys = set()
            for meta in sample['metadatas']:
                if meta:
                    metadata_keys.update(meta.keys())
            print(f"Metadata fields: {sorted(metadata_keys)}")
        
        return total_records
        
    except Exception as e:
        logger.error(f"Failed to get collection stats: {e}")
        return 0


def main():
    """Main test execution"""
    logger.info("Starting ChromaDB sample read test...")
    
    # Setup connection
    client, collection = setup_chromadb_client()
    if not client or not collection:
        logger.error("Cannot proceed without database connection")
        return
    
    # Get collection statistics
    total_records = get_collection_stats(collection)
    if total_records == 0:
        logger.warning("No records found in the database")
        return
    
    # Read sample records
    sample_size = min(5, total_records)
    results = read_sample_records(collection, limit=sample_size)
    
    # Display results
    display_records(results)
    
    logger.info("Test completed successfully!")


if __name__ == "__main__":
    main()
