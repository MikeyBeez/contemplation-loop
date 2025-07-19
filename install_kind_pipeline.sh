#!/bin/bash
# Install script for contemplation pipeline with kind thoughts

echo "Installing Contemplation Pipeline with Kind Thoughts..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create the plist file for the pipeline
cat > ~/Library/LaunchAgents/com.user.contemplation-pipeline.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.contemplation-pipeline</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>${SCRIPT_DIR}/venv/bin/python</string>
        <string>${SCRIPT_DIR}/contemplation_pipeline.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>${SCRIPT_DIR}/logs/pipeline.log</string>
    
    <key>StandardErrorPath</key>
    <string>${SCRIPT_DIR}/logs/pipeline_error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>CONTEMPLATION_MODEL</key>
        <string>llama3.2:latest</string>
    </dict>
</dict>
</plist>
EOF

# Create the plist for daily curation
cat > ~/Library/LaunchAgents/com.user.thought-curator.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.thought-curator</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>${SCRIPT_DIR}/venv/bin/python</string>
        <string>${SCRIPT_DIR}/src/thought_curator.py</string>
        <string>--daily</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>${SCRIPT_DIR}/logs/curator.log</string>
    
    <key>StandardErrorPath</key>
    <string>${SCRIPT_DIR}/logs/curator_error.log</string>
</dict>
</plist>
EOF

# Create logs directory
mkdir -p "${SCRIPT_DIR}/logs"

# Load the services
echo "Loading contemplation pipeline service..."
launchctl unload ~/Library/LaunchAgents/com.user.contemplation-pipeline.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.user.contemplation-pipeline.plist

echo "Loading thought curator service..."
launchctl unload ~/Library/LaunchAgents/com.user.thought-curator.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.user.thought-curator.plist

echo ""
echo "Installation complete!"
echo ""
echo "The contemplation pipeline is now running with:"
echo "- Kind random thoughts generated every 5 minutes"
echo "- Thoughts processed by contemplation loop"
echo "- Daily curation at 9:00 AM of top 3 insights"
echo ""
echo "Check status with:"
echo "  launchctl list | grep contemplation"
echo ""
echo "View logs:"
echo "  tail -f ${SCRIPT_DIR}/logs/pipeline.log"
echo "  tail -f ${SCRIPT_DIR}/logs/pipeline_error.log"
echo ""
echo "Stop services:"
echo "  launchctl unload ~/Library/LaunchAgents/com.user.contemplation-pipeline.plist"
echo "  launchctl unload ~/Library/LaunchAgents/com.user.thought-curator.plist"
