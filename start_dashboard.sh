#!/bin/bash
# Start the subconscious system and dashboard using uv

echo "Starting Subconscious Dashboard..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if .venv exists, create if not
if [ ! -d "${SCRIPT_DIR}/.venv" ]; then
    echo "Creating virtual environment with uv..."
    cd "${SCRIPT_DIR}" && uv venv
fi

# Install/update requirements
echo "Ensuring requirements are installed..."
cd "${SCRIPT_DIR}" && uv pip install -r requirements.txt --quiet

# Check if subconscious service is running
if launchctl list | grep -q "com.user.subconscious"; then
    echo "✓ Subconscious service is running"
else
    echo "Starting subconscious service..."
    "${SCRIPT_DIR}/install_subconscious.sh"
fi

# Start the dashboard server
echo ""
echo "Starting dashboard server..."
echo "Dashboard will be available at: http://localhost:5555"
echo ""
echo "Press Ctrl+C to stop the dashboard (subconscious will continue running)"
echo ""

# Run the standalone dashboard server with uv
cd "${SCRIPT_DIR}" && uv run python dashboard/standalone_server.py
