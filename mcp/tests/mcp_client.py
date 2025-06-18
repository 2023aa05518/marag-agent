
from fastmcp import Client
import asyncio

async def main():
    try:
        client = Client("http://localhost:8000/sse")
        
        async with client:
            print("🔧 Available MCP Tool Names:\n")
            tools = await client.list_tools()
            for t in tools:
                print(f" • {t.name}")
            print(f"\nTotal tools: {len(tools)}")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the server is running at http://127.0.0.1:8000/")

if __name__ == "__main__":
    asyncio.run(main())
