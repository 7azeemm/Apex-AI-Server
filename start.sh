#!/bin/bash
# Run uvicorn using the venv's python, no need to activate manually

if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif [ -f ".venv/Scripts/python.exe" ]; then
    PYTHON_CMD=".venv/Scripts/python.exe"
else
    echo "❌ Could not find .venv python executable."
    exit 1
fi

"$PYTHON_CMD" -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload