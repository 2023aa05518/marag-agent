import chromadb
from chromadb.config import Settings

# For a persistent client (local Chroma instance)
# admin_client = chromadb.AdminClient(Settings(
#     is_persistent=True,
#     persist_directory="path/to/your/chroma/data"
# ))

# For a remote Chroma server (HTTP client)
admin_client = chromadb.AdminClient(Settings(
    chroma_api_impl="chromadb.api.fastapi.FastAPI",
    chroma_server_host="localhost", 
    chroma_server_http_port="8001", 
))

try:
    # List all collections
    databases = admin_client.list_databases
    print("Databases:")
    for db in databases:
        # If db is a dict and has a 'name' key
        print(f"- {db['name']}")

except Exception as e:
    print(f"An error occurred: {e}")