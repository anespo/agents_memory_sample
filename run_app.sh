#!/bin/bash

# Agent Memory Management Application Launcher
# This script checks dependencies and launches the Streamlit application

set -e

echo "🧠 Amazon Bedrock Agent Core Memory Management"
echo "=============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "✅ uv package manager detected"
    echo ""
    echo "📦 Syncing dependencies with uv..."
    uv sync
    echo ""
    echo "🚀 Launching Streamlit application..."
    uv run streamlit run app.py
else
    # Check if streamlit is installed
    if ! python3 -c "import streamlit" &> /dev/null; then
        echo "⚠️  Streamlit not found. Installing dependencies..."
        pip3 install -r requirements.txt
    else
        echo "✅ Dependencies already installed"
    fi
    
    echo ""
    echo "🚀 Launching Streamlit application..."
    streamlit run app.py
fi
