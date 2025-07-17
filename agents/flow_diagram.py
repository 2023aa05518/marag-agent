"""
Data Flow Visualization for Multi-Agent MARAG System
This script shows the actual flow of data through the system.
"""

def print_flow_diagram():
    print("""
🔄 MULTI-AGENT MARAG SYSTEM - DATA FLOW DIAGRAM
================================================================

1. CLIENT REQUEST
   │
   ├── HTTP POST /api/v1/query
   ├── Body: {"query_text": "...", "collection_name": "docs", "k": 2}
   └── Headers: {"Content-Type": "application/json"}
   
   │
   ▼
   
2. FASTAPI APP (main.py)
   │
   ├── app = FastAPI(lifespan=lifespan)
   ├── Middleware: CORS, Error Handling
   ├── Route Matching: /api/v1/query
   └── Forward to Router
   
   │
   ▼
   
3. API ROUTER (src/api/router.py)
   │
   ├── @router.post("/query")
   ├── async def process_query(request: QueryRequest, pipeline: SupervisorPipeline)
   ├── Pydantic Validation: QueryRequest.parse_obj()
   └── Dependency Injection: get_pipeline()
   
   │
   ▼
   
4. PIPELINE MANAGER (src/agents/pipeline.py)
   │
   ├── SupervisorPipeline.process_query(request)
   ├── Format Query: _format_query(request)
   ├── Setup Tracing: OpikTracer(graph=supervisor.get_graph())
   └── Execute Supervisor: supervisor.astream()
   
   │
   ▼
   
5. SUPERVISOR ORCHESTRATION (LangGraph)
   │
   ├── Compiled Graph with Agents
   ├── State Management: {"messages": [...]}
   ├── Agent Dispatch Logic
   └── Workflow Control
   
   │
   ├─────────────────────────────────────┐
   ▼                                     ▼
   
6A. RETRIEVER AGENT                 6B. CRITIQUE AGENT
    │                                   │
    ├── MCP Tools Available             ├── No Tools (LLM Only)
    ├── ChromaDB Query                  ├── Response Validation
    ├── Vector Search                   ├── Hallucination Check
    ├── Document Retrieval              ├── Context Sufficiency
    └── Return Results                  └── Approve/Request More
    
    │                                   │
    └─────────────┬─────────────────────┘
                  ▼
                  
7. RESULT AGGREGATION
   │
   ├── Collect Streaming Chunks
   ├── Extract Agent Messages
   ├── Track Execution Metadata
   └── Format Final Response
   
   │
   ▼
   
8. RESPONSE FORMATTING
   │
   ├── QueryResponse Object
   ├── Status: "success" | "error"
   ├── Result: Formatted Answer
   ├── Metadata: {agents_used, execution_time, ...}
   └── Timestamp: ISO Format
   
   │
   ▼
   
9. HTTP RESPONSE
   │
   ├── JSON Serialization
   ├── HTTP 200 OK | 500 Error
   ├── Content-Type: application/json
   └── Return to Client

================================================================
""")

def print_class_relationships():
    print("""
🏗️ CLASS STRUCTURE & RELATIONSHIPS
================================================================

main.py
├── FastAPI()
├── CORSMiddleware 
├── @asynccontextmanager lifespan()
└── app.include_router(router)

src/api/
├── models.py
│   ├── QueryRequest(BaseModel)
│   │   ├── query_text: str
│   │   ├── collection_name: str = "docs"
│   │   └── k: int = 2
│   │
│   └── QueryResponse(BaseModel)
│       ├── status: str
│       ├── result: str
│       ├── metadata: Dict[str, Any]
│       └── timestamp: datetime
│
└── router.py
    ├── APIRouter(prefix="/api/v1")
    ├── process_query(request, pipeline)
    ├── health_check()
    └── api_info()

src/agents/
├── pipeline.py
│   ├── SupervisorPipeline
│   │   ├── __init__(): Initialize state
│   │   ├── initialize(): Setup MCP & agents
│   │   ├── process_query(): Main execution
│   │   ├── _create_retriever_agent()
│   │   ├── _create_critique_agent()
│   │   ├── _format_query()
│   │   └── _format_results()
│   │
│   └── get_pipeline(): Singleton pattern
│
└── supervisor.py (Legacy/Refactored)
    └── main_pipeline(): Backward compatibility

src/utils/
├── llm_utils.py: get_llm()
├── mcp_utils.py: get_mcp_server_config()
└── pretty_print.py: pretty_print_messages()

External Dependencies:
├── LangChain: LLM abstractions
├── LangGraph: Multi-agent workflows
├── FastMCP: MCP client implementation
├── ChromaDB: Vector database (via MCP)
├── Opik: Tracing and monitoring
└── FastAPI: Web framework

================================================================
""")

def print_execution_sequence():
    print("""
⚡ EXECUTION SEQUENCE WITH METHOD CALLS
================================================================

1. SERVER STARTUP
   main.py:main()
   ├── uvicorn.run("main:app")
   ├── FastAPI app initialization
   ├── @asynccontextmanager lifespan() 
   ├── get_pipeline() # Pre-initialize
   └── Server ready on http://localhost:8000

2. INCOMING REQUEST
   curl -X POST /api/v1/query -d '{"query_text": "..."}'
   
3. FASTAPI ROUTING
   app(scope, receive, send)
   ├── Route matching: /api/v1/query
   ├── Method validation: POST
   └── Call endpoint function

4. API ENDPOINT
   router.py:process_query(request, pipeline)
   ├── QueryRequest.parse_obj(request_data)
   ├── Depends(get_pipeline) # Dependency injection
   ├── pipeline.process_query(request)
   └── Return QueryResponse

5. PIPELINE EXECUTION
   pipeline.py:SupervisorPipeline.process_query()
   ├── await self.initialize() # If not already done
   ├── formatted_query = self._format_query(request)
   ├── OpikTracer(graph=self.supervisor.get_graph())
   ├── async for chunk in supervisor.astream():
   │   ├── Supervisor evaluates next agent
   │   ├── Agent execution (retriever/critique)
   │   └── Collect results
   ├── final_result = self._format_results(results)
   └── return QueryResponse(...)

6. AGENT ORCHESTRATION
   LangGraph Supervisor.astream()
   ├── Initial state: {"messages": [{"role": "user", "content": query}]}
   ├── Agent selection logic
   ├── Retriever Agent execution:
   │   ├── MCP tool invocation
   │   ├── ChromaDB query
   │   └── Document return
   ├── Critique Agent execution:
   │   ├── Response evaluation
   │   ├── Hallucination check
   │   └── Approval/rejection
   └── Workflow completion

7. RESPONSE ASSEMBLY
   pipeline.py:_format_results()
   ├── Filter meaningful results
   ├── Calculate execution metadata
   ├── QueryResponse object creation
   └── JSON serialization

8. HTTP RESPONSE
   FastAPI automatic serialization
   ├── Pydantic model → JSON
   ├── HTTP headers
   └── Status code

================================================================
""")

if __name__ == "__main__":
    print_flow_diagram()
    print_class_relationships() 
    print_execution_sequence()

    print("""
🔧 KEY DESIGN PATTERNS USED:
================================================================

1. DEPENDENCY INJECTION
   - FastAPI Depends() for SupervisorPipeline
   - Singleton pattern for pipeline instance
   - Clean separation of concerns

2. FACTORY PATTERN  
   - Agent creation methods (_create_*_agent)
   - Supervisor compilation
   - Tool loading

3. ADAPTER PATTERN
   - MCP client adapts ChromaDB to LangChain tools
   - Pydantic models adapt HTTP to Python objects

4. OBSERVER PATTERN
   - Opik tracing observes execution
   - Streaming results collection
   - Event-driven agent orchestration

5. COMMAND PATTERN
   - HTTP endpoints as commands
   - Agent actions as commands
   - Pipeline execution as command

6. TEMPLATE METHOD PATTERN
   - SupervisorPipeline.process_query() defines algorithm
   - Subclasses can override specific steps
   - Consistent execution flow

================================================================
""")
