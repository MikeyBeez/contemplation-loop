#!/bin/bash
# Install script for contemplation loop Launch Agent

echo "Installing Contemplation Loop as Launch Agent..."

# Paths
PLIST_FILE="com.user.contemplation-loop.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
SOURCE_PLIST="$(dirname "$0")/$PLIST_FILE"
DEST_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_FILE"

# Check if source plist exists
if [ ! -f "$SOURCE_PLIST" ]; then
    echo "Error: $SOURCE_PLIST not found"
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Stop existing service if running
if launchctl list | grep -q "com.user.contemplation-loop"; then
    echo "Stopping existing service..."
    launchctl unload "$DEST_PLIST" 2>/dev/null
fi

# Copy plist file
echo "Copying plist file..."
cp "$SOURCE_PLIST" "$DEST_PLIST"

# Set correct permissions
chmod 644 "$DEST_PLIST"

# Load the service
echo "Loading service..."
launchctl load "$DEST_PLIST"

# Check if loaded successfully
if launchctl list | grep -q "com.user.contemplation-loop"; then
    echo "✓ Service installed and loaded successfully!"
    echo ""
    echo "To check status:"
    echo "  launchctl list | grep contemplation"
    echo ""
    echo "To view logs:"
    echo "  tail -f logs/contemplation_stderr.log"
    echo ""
    echo "To stop service:"
    echo "  launchctl unload ~/Library/LaunchAgents/$PLIST_FILE"
    echo ""
    echo "To start service:"
    echo "  launchctl load ~/Library/LaunchAgents/$PLIST_FILE"
else
    echo "❌ Failed to load service"
    exit 1
fi