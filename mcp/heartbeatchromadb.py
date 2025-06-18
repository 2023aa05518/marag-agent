import chromadb
from chromadb.utils import embedding_functions

# Configuration details from your Docker command
CHROMA_HOST = "chromadb"
CHROMA_PORT = 8000
CHROMA_AUTH_TOKEN = "my-secret-token"
CHROMA_AUTH_HEADER = "X_CHROMA_TOKEN" # This is the header name you defined

try:
    # Create an HTTP client for ChromaDB
    client = chromadb.HttpClient(
        ssl=False,
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        headers={CHROMA_AUTH_HEADER: CHROMA_AUTH_TOKEN}
    )

    # You can then interact with your ChromaDB instance.
    # For example, to check the heartbeat (though you already did this with curl):
    heartbeat_status = client.heartbeat()
    print(f"ChromaDB Heartbeat: {heartbeat_status}")

  

except Exception as e:
    print(f"Error connecting to ChromaDB: {e}")