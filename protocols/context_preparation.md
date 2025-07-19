# Protocol: Context Preparation for Ollama

## Purpose
Define how to prepare optimal context for Ollama that maximizes insight while staying within token limits.

## Context Gathering Process

### 1. Define What's Needed
- What aspects of the problem need context?
- What information would help Ollama reason better?
- What constraints or history matter?

### 2. Use MCP Tools to Gather Context

#### For Code Architecture Questions:
```
1. filesystem:directory_tree - Get project structure
2. filesystem:read_file - Read key files (interfaces, configs)
3. brain:brain_recall - Find past decisions about this component
4. brain:obsidian_note - Get design documents
5. todo-manager:todo_list - Check related open tasks
```

#### For Problem Solving:
```
1. brain:brain_recall - Search for similar problems solved before
2. filesystem:search_files - Find error patterns in logs
3. brain:unified_search - Look for related discussions
4. web_search - Research known solutions (if needed)
```

#### For System Analysis:
```
1. brain:state_get - Get current system state
2. filesystem:get_file_info - Check file timestamps/sizes
3. brain:brain_analyze - Get system insights
4. contemplation:get_insights - Check previous analyses
```

### 3. Assemble Context Package
- Combine gathered information
- Summarize if too long
- Structure for clarity
- Include tool instructions for Ollama

## Context Components

### 1. Problem Statement (Required)
- Clear, specific question
- Success criteria  
- Constraints

### 2. Gathered Context (From Tools)
- Relevant code/architecture
- Historical decisions
- Current state
- Known issues

### 3. Progressive Disclosure Setup
- What Ollama can request
- How to format requests
- Available data sources

## Context Sizing Guidelines

### Token Budgets
- Problem statement: 100-200 tokens
- Background: 300-500 tokens  
- Current state: 200-300 tokens
- Tool instructions: 100 tokens
- **Total: ~1000 tokens max**

### Compression Techniques

1. **Summarize Code** 
   - Instead of full functions, describe purpose and interface
   - Include only relevant snippets

2. **Extract Patterns**
   - Instead of listing all instances, describe the pattern
   - Give 1-2 concrete examples

3. **Use References**
   - "Details available via: NEED: File contents of [path]"
   - Let Ollama request specifics

4. **Hierarchical Information**
   - Start with high-level overview
   - Let Ollama drill down as needed

## Context Templates

### For Architecture Questions

#### Step 1: Gather Context
```javascript
// Get project structure
const tree = await filesystem.directory_tree(projectPath);

// Read key architecture files  
const interfaces = await filesystem.read_file(`${projectPath}/src/interfaces.ts`);
const config = await filesystem.read_file(`${projectPath}/config.json`);

// Get historical context
const decisions = await brain.brain_recall("architecture decisions " + projectName);
const designDocs = await brain.obsidian_note({action: "read", identifier: projectName + "/design"});

// Check current issues
const tasks = await todo.todo_list({project: projectName, status: "open"});
```

#### Step 2: Format for Ollama
```
CONTEXT:
System: [name]
Purpose: [extracted from docs]

Current architecture:
[summary from tree + interfaces]

Past decisions:
[relevant items from decisions]

Known issues:
[filtered from tasks]

You can request:
- Code files via NEED: File contents of [path]
- Design docs via NEED: Obsidian notes matching [query]  
- Metrics via NEED: Brain memory about [topic]

QUESTION: [specific architectural question]
```

### For Problem Solving
```
PROBLEM: [clear statement]

CURRENT APPROACH:
[2-3 sentences describing what we do now]

ISSUES:
- [specific issue 1]
- [specific issue 2]

CONSTRAINTS:
- [constraint 1]
- [constraint 2]

You can request additional context using NEED: statements.

QUESTION: [what we want to solve]
```

### For Analysis
```
ANALYZE: [what to analyze]

DATA AVAILABLE:
- [data source 1]: [brief description]
- [data source 2]: [brief description]

Request specific data via:
- NEED: Brain memory about [topic]
- NEED: Search results for [query]

FOCUS: [specific aspect to analyze]
```

## Context Anti-patterns

❌ **Information Dumping**
```
"Here's our entire README, all our code, every decision we've made..."
```

❌ **Vague Background**
```
"We have a system that does stuff with data"
```

❌ **No Tool Instructions**
```
[Sending context without explaining how Ollama can request more info]
```

❌ **Multiple Contexts**
```
"Also, while you're at it, can you look at this other unrelated thing..."
```

## Quality Checklist

- [ ] Problem is specific and answerable
- [ ] Context is under 1000 tokens
- [ ] Ollama knows how to request more info
- [ ] Only essential background included
- [ ] Success criteria are clear
- [ ] One focused question per conversation
