#!/bin/bash
set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create and activate root virtual environment
echo "Setting up root environment..."
uv venv .venv
source .venv/bin/activate
uv pip install .
deactivate

# Find and install dependencies for each server
find servers -type d -maxdepth 1 -mindepth 1 | while read server_dir; do
    echo "Setting up environment for $server_dir..."
    cd "$server_dir"
    
    # Create and activate server virtual environment
    uv venv
    source .venv/bin/activate
    
    # Install dependencies
    uv pip install .
    
    deactivate
    cd - > /dev/null
done

echo "Installation complete!"
