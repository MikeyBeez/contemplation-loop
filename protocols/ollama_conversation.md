# Protocol: Ollama Conversation Management

## Purpose
Define how to conduct asynchronous, tool-assisted conversations with Ollama through log files.

## Conversation Lifecycle

### 1. Initiation
- Create a new conversation log file: `conversations/ollama_{timestamp}_{topic}.log`
- Write initial prompt with clear context and question
- Include metadata: model, temperature, expected response time

### 2. Monitoring
- Check log file periodically (every 30-60 seconds)
- Look for Ollama's requests for information
- Identify when Ollama has completed its response

### 3. Information Requests
When Ollama asks for information:
- Parse the specific request
- Use appropriate MCP tools to gather data
- Format response clearly
- Append to conversation log

### 4. Completion
- Ollama signals completion with a marker (e.g., "=== COMPLETE ===")
- Extract final insights
- Archive conversation for future reference

## Log Format

```
=== CLAUDE -> OLLAMA [timestamp] ===
[Initial prompt or response to request]

=== OLLAMA -> CLAUDE [timestamp] ===
[Ollama's response or request for information]

=== METADATA ===
Model: deepseek-r1:latest
Status: [thinking|requesting|complete]
Request: [specific data needed]
```

## Tool Request Patterns

Ollama can request:
- `NEED: Brain memory about [topic]`
- `NEED: Obsidian notes matching [query]`
- `NEED: File contents of [path]`
- `NEED: Current state of [system]`
- `NEED: Search results for [query]`

## Response Guidelines

1. **Be Precise** - Give exactly what was asked for
2. **Add Context** - Include source and timestamp
3. **Limit Size** - Summarize if response > 500 tokens
4. **Indicate Completeness** - Say if more data exists

## Conversation Strategies

### Focused Exploration
- Single topic, deep dive
- Let Ollama guide the research
- Provide requested information promptly

### Comparative Analysis
- Present multiple options/approaches
- Let Ollama request details on specific options
- Build toward recommendation

### Problem Solving
- Start with problem statement
- Provide constraints when asked
- Let Ollama explore solution space

## Example Conversation

```
=== CLAUDE -> OLLAMA [2024-01-19 10:00:00] ===
What's the best way to handle memory persistence in our Brain system? 
Current approach uses SQLite with JSON fields.

=== OLLAMA -> CLAUDE [2024-01-19 10:00:45] ===
I need to understand the current usage patterns first.
NEED: Brain memory about query patterns and performance metrics

=== CLAUDE -> OLLAMA [2024-01-19 10:01:15] ===
From Brain memory:
- Average query time: 5-10ms
- Most common: exact key lookups (70%)
- Search queries: 30% 
- Database size: ~500MB
- Daily growth: ~10MB

=== OLLAMA -> CLAUDE [2024-01-19 10:02:30] ===
[Detailed analysis based on the data...]
=== COMPLETE ===
```

## Success Indicators

- Ollama asks targeted, specific questions
- Information exchange is efficient
- Conclusions incorporate provided data
- Novel insights emerge from the exchange
