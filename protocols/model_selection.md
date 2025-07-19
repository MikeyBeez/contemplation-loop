# Protocol: Ollama Model Selection

## Purpose
Define which Ollama model to use for different types of thinking tasks.

## Available Models and Characteristics

### deepseek-r1:latest
- **Strengths**: Deep reasoning, exploring unconventional angles, complex problem solving
- **Weaknesses**: Slow (3-10 minutes), verbose, includes thinking process
- **Context**: Good with medium context
- **Use for**: Architecture decisions, complex debugging, finding hidden assumptions

### llama3.2:latest  
- **Strengths**: Fast (10-30 seconds), follows instructions well, concise
- **Weaknesses**: Less creative, more conventional thinking
- **Context**: Handles up to 4k tokens well
- **Use for**: Quick questions, summaries, standard analysis

### gemma2:latest
- **Strengths**: Balanced speed/quality, good at explanations
- **Weaknesses**: Sometimes too helpful/verbose
- **Context**: Medium capacity
- **Use for**: Documentation, explaining concepts, teaching

### phi3:latest
- **Strengths**: Very fast, efficient, good for simple tasks
- **Weaknesses**: Limited reasoning depth
- **Context**: Smaller context window
- **Use for**: Quick checks, simple questions, formatting

## Selection Matrix

| Task Type | First Choice | Second Choice | Avoid |
|-----------|--------------|---------------|-------|
| Architecture Design | deepseek-r1 | llama3.2 | phi3 |
| Bug Analysis | deepseek-r1 | llama3.2 | phi3 |
| Quick Summary | llama3.2 | phi3 | deepseek-r1 |
| Code Review | llama3.2 | gemma2 | deepseek-r1 |
| Documentation | gemma2 | llama3.2 | deepseek-r1 |
| Brainstorming | deepseek-r1 | gemma2 | phi3 |
| Data Analysis | llama3.2 | deepseek-r1 | phi3 |
| Quick Question | phi3 | llama3.2 | deepseek-r1 |

## Time Considerations

When choosing models, consider urgency:

- **Need answer in < 1 minute**: Use phi3 or llama3.2
- **Can wait 2-5 minutes**: Use llama3.2 or gemma2  
- **Can wait 10+ minutes**: Use deepseek-r1 for best insights
- **Overnight thinking**: Always use deepseek-r1

## Conversation Patterns by Model

### deepseek-r1
- Expect `<think>` tags with reasoning process
- Will explore multiple angles
- May request varied information types
- Best for open-ended exploration

### llama3.2
- Direct responses
- Good at following specific formats
- Efficient information requests
- Best for structured tasks

### gemma2
- Explanatory style
- May include examples
- Good at teaching/documentation
- Best for clarity

### phi3
- Minimal responses
- Very specific information needs
- No exploration
- Best for simple lookups

## Model Switching Strategy

You can switch models mid-conversation:

1. Start with phi3 for quick clarification
2. Upgrade to llama3.2 for deeper analysis
3. Bring in deepseek-r1 for complex decisions

Example:
```
Claude -> phi3: "Is this a concurrency issue?"
phi3 -> Claude: "Yes, race condition in state updates"
Claude -> llama3.2: "What solutions exist for this race condition?"
llama3.2 -> Claude: [lists 3 approaches]
Claude -> deepseek-r1: "Which approach best fits our architecture and why?"
deepseek-r1 -> Claude: [deep analysis with tradeoffs]
```

## Resource Management

- Only run one deepseek-r1 conversation at a time
- Can run multiple llama3.2/phi3 conversations in parallel
- Monitor system resources - Ollama can be memory intensive
