#!/bin/bash
# Set up Python virtual environment and paths for Multi-Agent MARAG system

# Get the current directory (project root)
PROJECT_ROOT="$(pwd)"

# Set up Python virtual environment and paths
if [ -d ".venv" ]; then
    source .venv/Scripts/activate
    export VIRTUAL_ENV="$PROJECT_ROOT/.venv"
    export PATH="$VIRTUAL_ENV/bin:$PATH"
else
    echo "Warning: .venv directory not found. Please run 'uv venv' first."
fi

# Set PYTHONPATH to include project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Create useful aliases
alias l="ls -lrt"
alias c="clear"
alias run-supervisor="uv run src/agents/supervisor.py"
alias run-api="uv run main.py"
alias run-tests="uv run pytest tests/"

echo "Environment setup complete!"
echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "PYTHONPATH: $PYTHONPATH"
echo ""
echo "Available commands:"
echo "  run-supervisor  - Run the supervisor agent"
echo "  run-api        - Run the FastAPI server"
echo "  run-tests      - Run the test suite"
echo ""
echo "You can now run: uv run src/agents/supervisor.py"