#!/bin/bash
# Cleanup script for development - removes orphaned processes and services

echo "🧹 Cleaning up development processes and services..."

# Check for orphaned processes
echo ""
echo "Checking for orphaned processes..."
ORPHANS=$(ps aux | grep -E "(contemplation|thought_generator|curator|dashboard)" | grep -v grep | grep -v "com.user.subconscious")

if [ -z "$ORPHANS" ]; then
    echo "✓ No orphaned processes found"
else
    echo "Found orphaned processes:"
    echo "$ORPHANS"
    echo ""
    echo "Killing orphaned processes..."
    pkill -f "dashboard/api_server.py" 2>/dev/null
    pkill -f "dashboard/standalone_server.py" 2>/dev/null
    pkill -f "start_dashboard.sh" 2>/dev/null
    pkill -f "contemplation_loop.py" 2>/dev/null
    pkill -f "thought_generator.py" 2>/dev/null
    pkill -f "thought_curator.py" 2>/dev/null
    echo "✓ Cleaned up processes"
fi

# Check for orphaned services
echo ""
echo "Checking for orphaned launchctl services..."
SERVICES=$(launchctl list | grep -E "(contemplation|thought|curator|pipeline)" | grep -v "com.user.subconscious" | awk '{print $3}')

if [ -z "$SERVICES" ]; then
    echo "✓ No orphaned services found"
else
    echo "Found orphaned services:"
    echo "$SERVICES"
    echo ""
    for service in $SERVICES; do
        echo "Removing $service..."
        launchctl unload ~/Library/LaunchAgents/$service.plist 2>/dev/null
        rm -f ~/Library/LaunchAgents/$service.plist
    done
    echo "✓ Cleaned up services"
fi

# Clean up old virtual environments
echo ""
echo "Checking for old virtual environments..."
if [ -d "${PWD}/venv" ] && [ -d "${PWD}/.venv" ]; then
    echo "Found old 'venv' directory (we use '.venv' with uv now)"
    echo "Remove it? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        rm -rf "${PWD}/venv"
        echo "✓ Removed old venv"
    fi
fi

# Check active services
echo ""
echo "=== Active Services ==="
launchctl list | grep -E "(subconscious)" | grep -v grep || echo "No active services"

echo ""
echo "=== Active Processes ==="
ps aux | grep -E "subconscious.py" | grep -v grep || echo "No active processes"

echo ""
echo "✅ Cleanup complete!"
