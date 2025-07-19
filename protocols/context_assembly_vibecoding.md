# Protocol: Context Assembly (Modern Vibecoding)

## Purpose
Define how to use MCP tools to assemble comprehensive context before delegating to Ollama - the essence of modern vibecoding.

## Core Concept
**Vibecoding**: Using tools to gather all the puzzle pieces, then handing the complete picture to an LLM for deep analysis.

## The Assembly Pipeline

### 1. Question Analysis
Before gathering context, analyze what information would help:
- What system components are involved?
- What historical context matters?
- What constraints exist?
- What similar problems have we solved?

### 2. Parallel Context Gathering

Execute multiple MCP tool calls in parallel:

```javascript
const contextPromises = [
  // Code structure
  filesystem.directory_tree(projectPath),
  filesystem.read_multiple_files(keyFiles),
  
  // Historical context
  brain.brain_recall(relevantQuery),
  brain.unified_search(problemDescription),
  
  // Current state
  brain.state_get("project", projectName),
  todo.todo_list({project: projectName}),
  
  // Previous insights
  contemplation.get_insights({thought_type: "analysis"}),
  
  // External research (if needed)
  web_search(technicalQuery)
];

const contexts = await Promise.all(contextPromises);
```

### 3. Context Filtering and Summarization

Not all gathered context is useful:

```javascript
// Filter by relevance
const relevant = contexts.filter(item => 
  item.content.includes(keyTerms) || 
  item.metadata.score > threshold
);

// Summarize if too long
const summarized = relevant.map(item => {
  if (item.length > 500) {
    return extractKeyPoints(item);
  }
  return item;
});
```

### 4. Context Structuring

Organize for Ollama's consumption:

```
BACKGROUND:
[Historical decisions and rationale]

CURRENT STATE:
[Code structure, active issues, recent changes]

CONSTRAINTS:
[Technical, business, time constraints]

SIMILAR PROBLEMS:
[How we solved related issues before]

RELEVANT INSIGHTS:
[From previous contemplations]

EXTERNAL CONTEXT:
[Industry patterns, best practices if researched]
```

## Vibecoding Patterns

### Pattern 1: Archaeological Dig
When debugging mysterious issues:
1. Search error logs for patterns
2. Find when the issue first appeared (git history)
3. Recall decisions made around that time
4. Check what changed in the system
5. Present timeline to Ollama

### Pattern 2: Architecture Review
When designing new systems:
1. Map current architecture
2. Find all related design documents
3. List integration points
4. Gather performance metrics
5. Check similar systems we've built
6. Present complete picture to Ollama

### Pattern 3: Knowledge Synthesis
When learning new concepts:
1. Search Brain for related knowledge
2. Find relevant code examples
3. Get external documentation
4. Check our past experiments
5. Present learning context to Ollama

### Pattern 4: Decision Support
When making technical choices:
1. Gather all options considered
2. Find past similar decisions
3. Check current constraints
4. Get team preferences/skills
5. Research industry trends
6. Present decision matrix to Ollama

## Tool Combination Examples

### Debugging Context Assembly
```javascript
// 1. Find the error
const errors = await filesystem.search_files(logsPath, "ERROR");

// 2. Get code context
const errorFile = extractFileFromError(errors[0]);
const code = await filesystem.read_file(errorFile);

// 3. Check recent changes
const fileInfo = await filesystem.get_file_info(errorFile);
const recentTasks = await todo.todo_list({
  project: projectName,
  filter: `modified>${fileInfo.modified}`
});

// 4. Find similar past issues
const similar = await brain.brain_recall(`error ${errorType}`);

// 5. Assemble and send to Ollama
```

### Feature Planning Assembly
```javascript
// 1. Get current architecture
const structure = await filesystem.directory_tree(projectPath);

// 2. Find related features
const similar = await brain.unified_search(`feature ${featureType}`);

// 3. Check technical debt
const debt = await todo.todo_list({tags: ["tech-debt"], status: "open"});

// 4. Get performance baseline
const metrics = await brain.state_get("cache", "performance_metrics");

// 5. Research best practices
const research = await web_search(`${featureType} implementation patterns`);
```

## Success Metrics

Good context assembly:
- ✓ Ollama rarely needs to request additional info
- ✓ Insights reference specific gathered context
- ✓ Solutions consider historical decisions
- ✓ Edge cases from past issues are addressed
- ✓ Recommendations align with constraints

Poor context assembly:
- ✗ Ollama asks for basic information
- ✗ Solutions ignore existing patterns
- ✗ Recommendations conflict with constraints
- ✗ Missing obvious relevant context
- ✗ Too much irrelevant information

## The Vibe Check

Before sending to Ollama, ask:
1. Could a human expert answer this with this context?
2. Are all the puzzle pieces here?
3. Is the context telling a coherent story?
4. Would I need to look anything else up?

If yes to all, you've achieved good vibecoding.
