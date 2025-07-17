# Multi-Agent MARAG System - Architecture & Flow

## 🏗️ High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTTP Client   │ -> │   FastAPI App   │ -> │  API Router     │
│  (curl/browser) │    │   (main.py)     │    │ (router.py)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        v
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Query Response │ <- │ Supervisor      │ <- │ Pipeline        │
│   (JSON)        │    │ (LangGraph)     │    │ (pipeline.py)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                v                       │
                    ┌─────────────────┐                │
                    │   MCP Client    │ <--------------┘
                    │  (ChromaDB)     │
                    └─────────────────┘
                                │
                                v
                    ┌─────────────────┐
                    │   Agents        │
                    │ • Retriever     │
                    │ • Critique      │
                    └─────────────────┘
```

## 🔄 Detailed Request Flow

### 1. Entry Point: HTTP Request
```
POST /api/v1/query
{
  "query_text": "What are environmental challenges in India?",
  "collection_name": "docs", 
  "k": 2
}
```

### 2. Class Structure & Flow

```
main.py (FastAPI App)
│
├── FastAPI Application
│   ├── Lifespan Management
│   ├── CORS Middleware
│   └── Router Registration
│
└── app.include_router(router)
    │
    └── src/api/router.py
        │
        ├── POST /api/v1/query -> process_query()
        │   │
        │   ├── Pydantic Validation (QueryRequest)
        │   │   └── src/api/models.py
        │   │       ├── QueryRequest (input validation)
        │   │       └── QueryResponse (output format)
        │   │
        │   └── Dependency Injection: get_pipeline()
        │       │
        │       └── src/agents/pipeline.py
        │           │
        │           └── SupervisorPipeline Class
        │               │
        │               ├── initialize() -> Setup MCP & Agents
        │               │   ├── MultiServerMCPClient
        │               │   ├── load_mcp_tools()
        │               │   ├── _create_retriever_agent()
        │               │   ├── _create_critique_agent()
        │               │   └── create_supervisor()
        │               │
        │               └── process_query() -> Execute Pipeline
        │                   ├── Format Query
        │                   ├── Setup Opik Tracing
        │                   ├── Stream Supervisor Execution
        │                   ├── Collect Agent Results
        │                   └── Format Response
        │
        ├── GET /api/v1/health -> health_check()
        └── GET /api/v1/ -> api_info()
```

## 📊 Detailed Method Call Flow

### Step-by-Step Execution:

```
1. HTTP Request Received
   └── FastAPI App (main.py)
       └── Router (router.py)

2. Route Matching: POST /api/v1/query
   └── process_query(request: QueryRequest, pipeline: SupervisorPipeline)

3. Dependency Injection
   └── get_pipeline() -> Returns singleton SupervisorPipeline instance

4. Pipeline Initialization (if not already done)
   └── SupervisorPipeline.initialize()
       ├── MultiServerMCPClient(get_mcp_server_config())
       ├── client.session("chroma")
       ├── load_mcp_tools(session)
       ├── _create_retriever_agent()
       │   └── create_react_agent(name="retriever_query_agent", tools=tools)
       ├── _create_critique_agent()
       │   └── create_react_agent(name="critique_agent", tools=[])
       └── create_supervisor(agents=[retriever, critique])

5. Query Processing
   └── SupervisorPipeline.process_query(request)
       ├── _format_query(request) -> Format input for supervisor
       ├── OpikTracer setup for monitoring
       ├── supervisor.astream() -> Stream execution
       │   ├── Supervisor dispatches to Retriever Agent
       │   │   └── Agent queries ChromaDB via MCP tools
       │   ├── Supervisor dispatches to Critique Agent  
       │   │   └── Agent validates retriever results
       │   └── Supervisor manages workflow until completion
       ├── Collect streaming results
       ├── _format_results() -> Clean up output
       └── Return QueryResponse with metadata

6. Response Formatting
   └── QueryResponse object with:
       ├── status: "success" | "error"
       ├── result: formatted answer
       ├── metadata: execution details
       └── timestamp
```

## 🎯 Key Classes & Responsibilities

### 1. **FastAPI App** (`main.py`)
```python
class FastAPIApp:
    responsibilities:
        - HTTP server setup
        - Middleware configuration
        - Router registration
        - Lifespan management
        - Pipeline initialization on startup
```

### 2. **API Router** (`src/api/router.py`)
```python
class APIRouter:
    endpoints:
        - POST /api/v1/query: process_query()
        - GET /api/v1/health: health_check()  
        - GET /api/v1/: api_info()
    
    responsibilities:
        - HTTP request handling
        - Input validation via Pydantic
        - Error handling & HTTP status codes
        - Pipeline coordination
```

### 3. **Pydantic Models** (`src/api/models.py`)
```python
class QueryRequest:
    fields:
        - query_text: str
        - collection_name: str = "docs"
        - k: int = 2
    
class QueryResponse:
    fields:
        - status: str
        - result: str  
        - metadata: Dict[str, Any]
        - timestamp: datetime
```

### 4. **SupervisorPipeline** (`src/agents/pipeline.py`)
```python
class SupervisorPipeline:
    state:
        - client: MultiServerMCPClient
        - supervisor: CompiledGraph
        - tools: List[Tool]
        - _initialized: bool
    
    methods:
        - initialize(): Setup MCP client & create agents
        - process_query(): Execute multi-agent workflow
        - _create_retriever_agent(): Setup retriever with MCP tools
        - _create_critique_agent(): Setup validation agent
        - _format_query(): Prepare input for supervisor
        - _format_results(): Clean output for API response
```

### 5. **Agent Architecture** (LangGraph/LangChain)
```python
Supervisor (LangGraph):
    role: Orchestrates agent workflow
    agents: [retriever_query_agent, critique_agent]
    workflow:
        1. Assign query to retriever_query_agent
        2. Pass results to critique_agent for validation
        3. Re-run retriever if critique requests more context
        4. Complete when critique approves

Retriever Agent:
    tools: MCP ChromaDB tools
    role: Query vector database for relevant documents
    
Critique Agent:
    tools: None (LLM only)
    role: Validate responses for hallucinations
```

## 🔧 Configuration & Dependencies

### Environment Setup:
```python
Utils Package (src/utils/):
    - llm_utils.py: LLM model configuration
    - mcp_utils.py: MCP server configuration  
    - pretty_print.py: Output formatting

External Dependencies:
    - FastAPI: Web framework
    - LangChain: LLM orchestration
    - LangGraph: Multi-agent workflows
    - ChromaDB (via MCP): Vector database
    - Opik: Tracing and monitoring
```

## 🚀 Execution Example

```python
# 1. Client sends request
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query_text": "Environmental challenges in India", "k": 2}'

# 2. FastAPI processes through pipeline
# 3. Supervisor coordinates agents:
#    - Retriever → ChromaDB query → Returns documents
#    - Critique → Validates response → Approves/Requests more context
# 4. Pipeline formats and returns response

{
  "status": "success",
  "result": "India faces several environmental challenges including...",
  "metadata": {
    "agents_used": ["retriever_query_agent", "critique_agent"],
    "execution_time_seconds": 5.2,
    "collection_name": "docs",
    "k_results": 2
  },
  "timestamp": "2025-01-07T10:30:00"
}
```

This architecture provides clear separation of concerns, making the system modular, testable, and easy to extend with new agents or API endpoints.
