#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# ================= INSTRUCTIONS =================
echo "=============================================="
echo " Starting the FastAPI application locally..."
echo "=============================================="
echo ""

# ================= CREATE & ACTIVATE VENV =================
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
# Activate venv for current session.
source venv/bin/activate

# ================= INSTALL REQUIREMENTS =================
echo "Installing/updating dependencies from requirements.txt..."
pip install -r requirements.txt -r other_requirements.txt

# ================= START UVICORN =================
echo "Starting uvicorn server..."

# Check if uvicorn is now available
if ! command -v uvicorn &> /dev/null
then
    echo "ERROR: uvicorn command not found after installation. Please check requirements.txt."
    exit 1
fi

uvicorn main:app --reload --host 0.0.0.0 --port 8000