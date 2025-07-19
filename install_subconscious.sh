#!/bin/bash
# Install script for the sophisticated subconscious system with uv

echo "Installing Subconscious System..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create .venv if it doesn't exist
if [ ! -d "${SCRIPT_DIR}/.venv" ]; then
    echo "Creating virtual environment with uv..."
    cd "${SCRIPT_DIR}" && uv venv
fi

# Install requirements
echo "Installing requirements..."
cd "${SCRIPT_DIR}" && uv pip install -r requirements.txt --quiet

# Create the plist file for the subconscious service
cat > ~/Library/LaunchAgents/com.user.subconscious.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.subconscious</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>${SCRIPT_DIR}/.venv/bin/python</string>
        <string>${SCRIPT_DIR}/src/subconscious.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>${SCRIPT_DIR}/logs/subconscious.log</string>
    
    <key>StandardErrorPath</key>
    <string>${SCRIPT_DIR}/logs/subconscious_error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>SUBCONSCIOUS_REASONING_MODEL</key>
        <string>deepseek-r1:latest</string>
        <key>SUBCONSCIOUS_FAST_MODEL</key>
        <string>llama3.2:latest</string>
    </dict>
</dict>
</plist>
EOF

# Create logs directory
mkdir -p "${SCRIPT_DIR}/logs"

# Create the .subconscious directory
mkdir -p ~/.subconscious

# Stop any existing service
echo "Stopping any existing subconscious service..."
launchctl unload ~/Library/LaunchAgents/com.user.subconscious.plist 2>/dev/null

# Load the service
echo "Starting subconscious service..."
launchctl load ~/Library/LaunchAgents/com.user.subconscious.plist

echo ""
echo "Installation complete!"
echo ""
echo "The Subconscious system is now running with:"
echo "- Sophisticated reasoning using deepseek-r1 and llama3.2"
echo "- Always-on background processing via launchctl"
echo "- SQLite database for persistent thought storage"
echo "- Priority-based processing queue"
echo "- Virtual environment managed by uv"
echo ""
echo "Check status with:"
echo "  launchctl list | grep subconscious"
echo "  uv run python src/subconscious_client.py status"
echo ""
echo "View logs:"
echo "  tail -f ${SCRIPT_DIR}/logs/subconscious_error.log"
echo ""
echo "Test the system:"
echo "  cd ${SCRIPT_DIR} && uv run python src/subconscious_client.py think problem 'How can we improve the contemplation system architecture?'"
echo ""
echo "Stop service:"
echo "  launchctl unload ~/Library/LaunchAgents/com.user.subconscious.plist"
