# Set up Python virtual environment and paths
source .venv/Scripts/activate
export VIRTUAL_ENV="$(pwd)/.venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
export PYTHONPATH="$(pwd):$PYTHONPATH"
# export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# alias  run="uv run with_current_setup.py"
alias  l="ls -lrt"
alias  c="clear"