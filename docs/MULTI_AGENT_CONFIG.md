# Multi-Agent Contemplation Configuration

The contemplation system can run multiple specialized agents for different types of thinking:

## Agent Types

### 1. Pattern Recognition Agent (llama3.2)
- **Model**: `llama3.2:latest` (fast, lightweight)
- **Focus**: Quick pattern matching, anomaly detection
- **Response time**: 5-10 seconds
- **Best for**: Noticing recurring themes, behavioral patterns

### 2. Deep Analysis Agent (deepseek-r1)
- **Model**: `deepseek-r1:latest` (slower, deeper thinking)
- **Focus**: System design, architectural improvements
- **Response time**: 30-60 seconds
- **Best for**: Complex reasoning, multi-step solutions
- **Note**: Shows thinking process with `<think>` tags

### 3. Creative Synthesis Agent (gemma2)
- **Model**: `gemma2:latest` (balanced)
- **Focus**: Connecting disparate ideas, generating hypotheses
- **Response time**: 10-20 seconds
- **Best for**: Finding unexpected connections

## Resource Management

With multiple agents, limit concurrent operations:
- Maximum 2-3 agents running simultaneously
- Stagger requests by priority
- Use process monitoring to prevent resource exhaustion

## Agent Communication

Agents can share insights through:
1. Shared scratch notes directory
2. Incubation folder for cross-pollination
3. Semantic linking in review system

## Configuration

Set agent model via environment:
```bash
export CONTEMPLATION_MODEL=deepseek-r1:latest
```

Or in Launch Agent plist:
```xml
<key>CONTEMPLATION_MODEL</key>
<string>llama3.2:latest</string>
```

## Usage Patterns

1. **Quick thoughts** → llama3.2 (immediate patterns)
2. **System improvements** → deepseek-r1 (deep analysis)
3. **Creative exploration** → gemma2 (synthesis)

The behavioral learning system will track which agent's insights prove most valuable over time.
