# Multi-Agent MARAG System API

A FastAPI-based RESTful API for document retrieval and analysis using a multi-agent system with ChromaDB vector database.

## 🏗️ Architecture

This system uses a multi-agent approach for document retrieval and validation:

- **Retriever Agent**: Queries ChromaDB collections for relevant documents
- **Critique Agent**: Validates responses for hallucinations and accuracy
- **Supervisor**: Orchestrates the agents and manages the workflow

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- ChromaDB server running (via Docker or local installation)
- Required Python packages (install via uv or pip)

### Installation

1. Install dependencies:
```bash
uv sync
# or
pip install -e .
```

2. Make sure ChromaDB is running and accessible

3. Configure your environment variables (if needed)

### Running the API

```bash
python main.py
```

The API will start on `http://localhost:8000`

- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📝 API Endpoints

### Query Processing
```
POST /api/v1/query
```

Process a query through the multi-agent system.

**Request Body:**
```json
{
  "query_text": "What are the primary environmental challenges India is facing?",
  "collection_name": "docs",
  "k": 2
}
```

**Response:**
```json
{
  "status": "success",
  "result": "Environmental challenges in India include...",
  "metadata": {
    "agents_used": ["retriever_query_agent", "critique_agent"],
    "execution_time_seconds": 5.2,
    "collection_name": "docs",
    "k_results": 2
  },
  "timestamp": "2025-01-07T10:30:00"
}
```

### Health Check
```
GET /api/v1/health
```

Check if the system is healthy and ready.

### API Information
```
GET /api/v1/
```

Get information about available endpoints and agents.

## 🧪 Testing

### Using the Test Script
```bash
python test_api.py
```

### Using cURL
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Query processing
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What are environmental challenges?",
    "collection_name": "docs",
    "k": 2
  }'
```

### Using Python requests
```python
import requests

# Query the API
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "query_text": "What are environmental challenges?",
        "collection_name": "docs",
        "k": 2
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Result: {result['result']}")
```

## 🏗️ Project Structure

```
src/
├── agents/
│   ├── pipeline.py      # Core pipeline logic
│   ├── supervisor.py    # Legacy supervisor (refactored)
│   └── simple_agent.py  # Simple agent implementation
├── api/
│   ├── models.py        # Pydantic request/response models
│   └── router.py        # FastAPI router with endpoints
├── loader/
│   └── doc_loader.py    # Document loading utilities
└── utils/
    ├── llm_utils.py     # LLM configuration
    ├── mcp_utils.py     # MCP server configuration
    └── pretty_print.py  # Output formatting
```

## 🔧 Configuration

The system uses several configurable components:

- **LLM Model**: Configured in `src/utils/llm_utils.py`
- **MCP Server**: Configured in `src/utils/mcp_utils.py`
- **ChromaDB**: Connection details in MCP configuration

## 📊 Monitoring

The system includes:

- **Opik Tracing**: Automatic tracing of agent interactions
- **Execution Timing**: Response metadata includes execution time
- **Agent Tracking**: Metadata shows which agents were used
- **Error Handling**: Structured error responses

## 🔄 Legacy Compatibility

The original `supervisor.py` functionality is preserved:

```bash
python src/agents/supervisor.py
```

This runs the pipeline in standalone mode for testing.

## 🛠️ Development

### Adding New Agents

1. Create agent in `SupervisorPipeline._create_*_agent()` methods
2. Add to supervisor agent list
3. Update agent descriptions in API info

### Extending the API

1. Add new Pydantic models in `src/api/models.py`
2. Add new endpoints in `src/api/router.py`
3. Update API documentation

## 📚 Dependencies

Key dependencies:
- FastAPI: Web framework
- LangChain: LLM orchestration
- LangGraph: Multi-agent workflows
- ChromaDB: Vector database
- Opik: Tracing and monitoring

## 🐛 Troubleshooting

### Common Issues

1. **ChromaDB Connection Error**: Ensure ChromaDB server is running
2. **Agent Timeout**: Check LLM API keys and connectivity
3. **Import Errors**: Verify all dependencies are installed

### Logs

The application logs to console with INFO level by default. Check logs for detailed error information.

## 📄 License

[Add your license information here]
