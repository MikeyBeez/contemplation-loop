# Contemplation Loop

A background thinking process for AI systems - a space for reflection, pattern recognition, and emergent insights between conversations.

## Overview

The Contemplation Loop is a persistent subprocess that:
- Processes thoughts and observations asynchronously
- Works with multiple language models for different thinking styles
- Manages its own context to avoid overflow
- Saves insights to both temporary scratch notes and Obsidian
- Learns from usage patterns to improve insight selection
- Communicates via JSON messages over stdin/stdout

## Recent Updates

### Behavioral Learning System
- Tracks which insights are actually referenced/used
- Adjusts significance scoring based on usage patterns
- Learns which keywords and thought types prove valuable

### Incubation System
- Medium-significance insights (6-7) go to incubation
- Allows ideas to mature over time
- Cross-pollinates with new thoughts

### Multi-Agent Support
- Configure different models for different thinking styles
- Pattern recognition (llama3.2) vs deep analysis (deepseek-r1)
- See `docs/MULTI_AGENT_CONFIG.md` for details

## Design Philosophy

Built with realistic expectations:
- **Small models** (llama3.2) with limited context (2-4k tokens)
- **Simple prompts** that work with limited capabilities
- **Automatic context management** to prevent overflow
- **Two-tier storage** - scratch notes (4 days) and Obsidian (permanent)

## Installation

```bash
# Clone the repository
git clone [repo-url] contemplation-loop
cd contemplation-loop

# Install dependencies
pip install requests

# Ensure Ollama is running
ollama list  # Should show your models
```

## Usage

### As a Subprocess

```python
from contemplation_bridge import ContemplationBridge

# Start the loop
bridge = ContemplationBridge()
bridge.start()

# Send thoughts
thought_id = bridge.send_thought(
    thought_type="pattern",
    content="Users often ask about memory in anxious ways"
)

# Get responses
responses = bridge.get_responses()
for response in responses:
    if response.get('has_insight'):
        print(f"Insight found: {response['insight']}")

# Check status
status = bridge.get_status()
print(f"Loop running: {status['running']}")

# Stop when done
bridge.stop()
```

### Thought Types

- **pattern**: Notice recurring themes
- **connection**: Find links between ideas  
- **question**: Explore interesting questions
- **general**: Open reflection

## Storage

### Scratch Notes (Temporary)
```
tmp/contemplation/
├── day_0/     (today)
├── day_1/     (yesterday)
├── day_2/
└── day_3/     (oldest, deleted at midnight)
```

- 10MB total limit
- Auto-rotation after 4 days
- Full context and processing details

### Obsidian Notes (Permanent)
```
~/Documents/Obsidian/Brain/Contemplation/
├── insight_2025-01-09_[timestamp].md
└── ...
```

- Only significant insights (score ≥ 7/10)
- 2-5 notes per day maximum
- Includes links to scratch notes

## Configuration

Environment variables:
- `CONTEMPLATION_MODEL`: Ollama model to use (default: llama3.2:latest)
- `CONTEMPLATION_LOG_LEVEL`: Logging verbosity

## Error Handling

- All errors logged to `logs/contemplation_stderr.log`
- Automatic context reset on overflow
- Graceful degradation if Ollama unavailable

## Limitations

Working with small models means:
- Simple, focused prompts
- Limited context (2-4k tokens)
- Basic pattern recognition
- May miss subtle connections

The loop is designed to find occasional insights, not perform deep analysis.

## Integration with Brain Manager

The loop can be invoked by the Brain Manager to process thoughts between conversations:

```python
# In Brain Manager
thoughts_queue = [
    ("pattern", "Notice about user behavior"),
    ("connection", "Two seemingly unrelated topics"),
]

for thought_type, content in thoughts_queue:
    brain_execute(f"python contemplation_bridge.py send '{thought_type}' '{content}'")
```

## Development

```bash
# Run tests
python -m pytest tests/

# Check logs
tail -f logs/contemplation_stderr.log

# Monitor scratch notes
watch ls -la tmp/contemplation/day_0/
```

## Why This Design?

- **Subprocess isolation**: Crashes don't affect main system
- **JSON communication**: Simple, debuggable protocol
- **Two-tier storage**: Balance between exploration and curation
- **Context management**: Work within model limitations
- **Low expectations**: Small models = simple insights

The goal isn't perfection - it's to create a space for emergent thoughts and unexpected connections.
