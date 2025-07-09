# Launch Agent Setup

This document explains how to run the contemplation loop as a macOS Launch Agent.

## Quick Install

```bash
./install_service.sh
```

## Manual Installation

1. **Ensure virtual environment exists:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Copy plist to LaunchAgents:**
   ```bash
   cp com.user.contemplation-loop.plist ~/Library/LaunchAgents/
   chmod 644 ~/Library/LaunchAgents/com.user.contemplation-loop.plist
   ```

3. **Load the service:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.user.contemplation-loop.plist
   ```

## Service Management

### Check Status
```bash
launchctl list | grep contemplation
```

### View Logs
```bash
# Error log (most important)
tail -f logs/contemplation_stderr.log

# Standard output
tail -f logs/contemplation.log
```

### Stop Service
```bash
launchctl unload ~/Library/LaunchAgents/com.user.contemplation-loop.plist
```

### Start Service
```bash
launchctl load ~/Library/LaunchAgents/com.user.contemplation-loop.plist
```

### Remove Service
```bash
launchctl unload ~/Library/LaunchAgents/com.user.contemplation-loop.plist
rm ~/Library/LaunchAgents/com.user.contemplation-loop.plist
```

## Configuration

The plist file configures:

- **Python Path**: Uses virtual environment Python at `/Users/bard/Code/contemplation-loop/venv/bin/python`
- **Working Directory**: Set to project root
- **Environment Variables**:
  - `CONTEMPLATION_MODEL`: The Ollama model to use
  - `PATH`: Standard system paths
  - `HOME`: User home directory
- **Logs**: 
  - stdout → `logs/contemplation.log`
  - stderr → `logs/contemplation_stderr.log`
- **Restart Policy**: 
  - Restarts on crash
  - 30-second throttle to prevent rapid restarts
  - Daily restart at midnight

## Troubleshooting

### Service won't start
1. Check logs: `tail logs/contemplation_stderr.log`
2. Verify Python path: `ls -la venv/bin/python`
3. Test manually: `venv/bin/python src/contemplation_loop.py`

### Python module errors
- Ensure virtual environment is activated when installing packages
- Check that plist uses venv Python, not system Python

### Permission errors
- Check plist permissions: `ls -la ~/Library/LaunchAgents/*.plist`
- Should be 644 (readable by all, writable by owner)

### Ollama connection errors
- Ensure Ollama is running: `ollama list`
- Check Ollama is accessible on localhost:11434

## How It Works

1. **At Login**: Service starts automatically (RunAtLoad=true)
2. **Daily**: Restarts at midnight to rotate scratch notes
3. **On Crash**: Automatically restarts after 30 seconds
4. **Continuous**: Runs as long as user is logged in

The service runs the contemplation loop in the background, processing thoughts sent via the bridge interface or discovered through pattern analysis.
