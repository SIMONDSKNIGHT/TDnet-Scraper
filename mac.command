#!/bin/bash
# Get the directory of the currently running script
CURRENT_DIR="$(cd "$(dirname "$0")"; pwd)"

# Change to the script's directory
cd "$CURRENT_DIR"

# (Optional) Activate the virtual environment, if any
# source "$CURRENT_DIR/venv/bin/activate"

# Run the Python script
python3 "$CURRENT_DIR/main.py"
