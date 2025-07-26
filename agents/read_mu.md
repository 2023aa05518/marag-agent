# Multi-Agent MARAG System

## Run uvicorn

uvicorn main:app --host 0.0.0.0 --port 8100 --reload

## How to Execute

    . ./setup.sh
    uv run src/agents/supervisor.py
    or
    uv run main.py

## Environment Configuration

Create a .env file with below info:

```env
GOOGLE_API_KEY=''
# LANGSMITH_TRACING=true
# LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
# LANGSMITH_API_KEY=""
# LANGSMITH_PROJECT=""

OPIK_API_KEY=''
OPIK_WORKSPACE = ""
```

## Setting up Opik

1. uv add opik
2. Add workspace and api key in .env file
3. import dependencies in code
4. initialize the OpikTracer object
5. implement callback in async invocation command of supervisor

## Command to Run with  Debug logs

$env:LOG_LEVEL = "DEBUG"; $env:PYTHONPATH = (Get-Location).Path; uv run tests/test_simple_pipeline.py