#!/bin/bash
# Install Ollama as a Launch Agent service

echo "Installing Ollama as Launch Agent..."

PLIST_FILE="com.ollama.server.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
SOURCE_PLIST="$(dirname "$0")/$PLIST_FILE"
DEST_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_FILE"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Error: Ollama is not installed"
    echo "Install with: brew install ollama"
    exit 1
fi

# Create LaunchAgents directory if needed
mkdir -p "$LAUNCH_AGENTS_DIR"

# Create log directory
sudo mkdir -p /usr/local/var/log
sudo chmod 755 /usr/local/var/log

# Stop existing service if running
if launchctl list | grep -q "com.ollama.server"; then
    echo "Stopping existing Ollama service..."
    launchctl unload "$DEST_PLIST" 2>/dev/null
fi

# Copy plist
echo "Installing plist..."
cp "$SOURCE_PLIST" "$DEST_PLIST"
chmod 644 "$DEST_PLIST"

# Load service
echo "Starting Ollama service..."
launchctl load "$DEST_PLIST"

# Wait a moment for it to start
sleep 2

# Check if running
if launchctl list | grep -q "com.ollama.server"; then
    echo "✓ Ollama service installed and running!"
    echo ""
    echo "Test with:"
    echo "  curl http://localhost:11434/api/tags"
    echo ""
    echo "View logs:"
    echo "  tail -f /usr/local/var/log/ollama-stderr.log"
    echo ""
    echo "Stop service:"
    echo "  launchctl unload ~/Library/LaunchAgents/$PLIST_FILE"
else
    echo "❌ Failed to start Ollama service"
    echo "Check logs at: /usr/local/var/log/ollama-stderr.log"
    exit 1
fi