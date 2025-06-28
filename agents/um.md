how to execute :

    . ./setup.sh
    uv run src/agents/supervisor.py

create a .env file with   below  info:

GOOGLE_API_KEY=''
# LANGSMITH_TRACING=true
# LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
# LANGSMITH_API_KEY=""
# LANGSMITH_PROJECT=""

OPIK_API_KEY=''
OPIK_WORKSPACE = ""

Setting up opik
    1. uv add opik
    2. Add workspace and api key in .env file
    3. import dependencies in code
    4. initialize the OpikTracer object
    5. implement callback in async invocation commad of supervisro