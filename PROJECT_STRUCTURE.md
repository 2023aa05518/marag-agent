# MARAG Project Structure

## Overview
MARAG (Multi-Agent Retrieval Augmented Generation) is a sophisticated system that combines multi-agent orchestration with vector database capabilities for enhanced document retrieval and generation. The project consists of two main components: an agents module for LLM orchestration and an MCP (Model Context Protocol) server for Chroma vector database integration.

## Root Directory Structure

```
langchain/agentic/marag/
├── agents/                          # Main agents application
│   ├── data/                        # Data storage
│   │   └── india.pdf               # Sample document for processing
│   ├── src/                        # Source code
│   │   ├── __init__.py
│   │   ├── agents/                 # Agent implementations
│   │   │   ├── __init__.py
│   │   │   ├── simple_agent.py     # Basic ReAct agent implementation
│   │   │   ├── supervisor.py       # Supervisor agent for orchestration
│   │   │   └── test.py            # Agent testing utilities
│   │   ├── loader/                 # Document loading utilities
│   │   │   ├── __init__.py
│   │   │   └── doc_loader.py      # PDF and document processing
│   │   ├── utils/                  # Utility modules
│   │   │   ├── __init__.py
│   │   │   ├── llm_utils.py       # LLM configuration and utilities
│   │   │   ├── mcp_utils.py       # MCP client configuration
│   │   │   └── pretty_print.py    # Output formatting utilities
│   │   └── ux/                    # User experience components
│   ├── tests/                      # Test suite
│   │   ├── conftest.py            # Pytest configuration
│   │   ├── sse_agent.py           # Server-sent events testing
│   │   └── test_doc_loader.py     # Document loader tests
│   ├── agent_response.json         # Sample agent response data
│   ├── main.py                     # Main application entry point
│   ├── pyproject.toml             # Python project configuration
│   ├── README.md                  # Project documentation
│   ├── setup.sh                   # Setup script
│   ├── um.md                      # User manual
│   └── uv.lock                    # UV package lock file
│
├── mcp/                            # MCP Server for Chroma integration
│   ├── src/
│   │   └── chroma_mcp/            # Chroma MCP server implementation
│   │       ├── __init__.py
│   │       └── server.py          # FastMCP server with Chroma integration
│   ├── tests/                     # MCP server tests
│   │   ├── mcp_client.py         # MCP client testing utilities
│   │   └── test_server.py        # Server functionality tests
│   ├── CHANGELOG.md              # Version history
│   ├── docker_build.sh           # Docker build script
│   ├── docker_compose_build.sh   # Docker Compose build script
│   ├── docker-compose.yml        # Docker Compose configuration
│   ├── Dockerfile                # Docker container definition
│   ├── glama.json               # Glama configuration
│   ├── heartbeatchromadb.py     # Health check utilities
│   ├── LICENSE                  # Apache 2.0 License
│   ├── pyproject.toml          # Python project configuration
│   ├── README.md               # MCP server documentation
│   ├── SECURITY.md             # Security guidelines
│   ├── smithery.yaml           # Smithery configuration
│   ├── um.md                   # User manual
│   └── uv.lock                 # UV package lock file
│
└── PROJECT_STRUCTURE.md           # This documentation file
```

## Component Details

### 1. Agents Module (`/agents/`)

**Purpose**: Main application for multi-agent orchestration using LangChain and LangGraph.

**Key Components**:

#### Source Code (`/src/`)
- **`agents/`**: Agent implementations
  - `simple_agent.py`: ReAct agent with MCP tool integration
  - `supervisor.py`: Supervisor pattern for agent orchestration
  - `test.py`: Agent testing and validation utilities

- **`loader/`**: Document processing pipeline
  - `doc_loader.py`: PDF processing and document ingestion

- **`utils/`**: Core utilities
  - `llm_utils.py`: LLM configuration (OpenAI, Google Gemini)
  - `mcp_utils.py`: MCP client setup and configuration
  - `pretty_print.py`: Response formatting and display

- **`ux/`**: User experience components (placeholder for UI/UX)

#### Data and Configuration
- **`data/`**: Document storage for RAG processing
- **`pyproject.toml`**: Dependencies include LangChain, LangGraph, ChromaDB, MCP adapters

#### Testing
- **`tests/`**: Comprehensive test suite with pytest configuration

### 2. MCP Server Module (`/mcp/`)

**Purpose**: Model Context Protocol server providing Chroma vector database integration.

**Key Components**:

#### Core Server (`/src/chroma_mcp/`)
- **`server.py`**: FastMCP server with comprehensive Chroma operations
  - Collection management (create, modify, delete, list)
  - Document operations (add, query, update, delete)
  - Advanced filtering and search capabilities
  - Multiple client types (ephemeral, persistent, HTTP, cloud)

#### Deployment
- **Docker Support**: Complete containerization with Dockerfile and docker-compose
- **Configuration**: Smithery and Glama integration for MCP discovery

#### Features
- **Flexible Client Types**: In-memory, file-based, HTTP, and cloud clients
- **Advanced Search**: Vector search, full-text search, metadata filtering
- **HNSW Configuration**: Optimized vector search parameters
- **Embedding Functions**: Support for multiple embedding providers

## Technology Stack

### Core Frameworks
- **LangChain**: LLM application framework
- **LangGraph**: Multi-agent orchestration
- **FastMCP**: Model Context Protocol server implementation
- **ChromaDB**: Vector database for embeddings

### Language Models
- **OpenAI**: GPT models integration
- **Google Gemini**: Alternative LLM provider
- **Embedding Providers**: Cohere, OpenAI, Jina, Voyage AI

### Development Tools
- **UV**: Fast Python package manager
- **Pytest**: Testing framework
- **Docker**: Containerization
- **Opik**: LLM observability and monitoring

## Key Features

### Multi-Agent System
- ReAct agent pattern with tool integration
- Supervisor pattern for agent orchestration
- MCP tool adapters for external service integration

### Vector Database Integration
- Chroma vector database with MCP protocol
- Document ingestion and processing pipeline
- Advanced search and retrieval capabilities

### Observability
- Opik integration for LLM monitoring
- Response tracking and analysis
- Performance metrics and debugging

## Getting Started

### Prerequisites
- Python 3.13+ (agents) or Python 3.10+ (MCP server)
- UV package manager
- Docker (optional, for MCP server deployment)

### Quick Start
1. **Agents Module**: Run `main.py` for basic agent functionality
2. **MCP Server**: Use `chroma-mcp` command or Docker deployment
3. **Integration**: Configure MCP client in agents to connect to Chroma server

## Development Workflow

### Testing
- Use pytest for both modules
- Integration tests for MCP client-server communication
- Document loader tests for RAG pipeline validation

### Deployment
- Local development with UV virtual environments
- Docker deployment for MCP server
- Cloud deployment options for Chroma Cloud integration

## Future Enhancements

### Planned Features
- Enhanced UX components in `/agents/src/ux/`
- Additional agent types and patterns
- Extended document format support
- Advanced retrieval strategies

### Scalability
- Distributed agent deployment
- High-availability Chroma server setup
- Load balancing and monitoring

This structure provides a robust foundation for building sophisticated multi-agent RAG applications with vector database integration through standardized MCP protocols.
