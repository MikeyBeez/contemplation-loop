# Protocol: Problem Decomposition for Ollama

## Purpose
Define how to break down complex problems into focused sub-problems that fit within Ollama's context window and leverage its deep reasoning capabilities.

## Principles

1. **Single Responsibility** - Each sub-problem should explore ONE specific aspect
2. **Context Efficiency** - Include only relevant context, not entire histories
3. **Clear Boundaries** - Sub-problems should have minimal interdependencies
4. **Measurable Output** - Each should produce a concrete insight or solution

## Decomposition Process

### 1. Identify the Core Question
- What is the fundamental problem we're trying to solve?
- What would a complete answer look like?

### 2. Map Dependencies
- What are the component parts?
- Which parts depend on others?
- What can be analyzed independently?

### 3. Size the Sub-problems
- Aim for problems that can be stated in 1-3 sentences
- Context should be < 1000 tokens
- Expected response should be focused, not comprehensive

### 4. Order by Independence
- Start with sub-problems that have no dependencies
- Build up to those that need prior insights
- Save synthesis questions for last

## Example Decomposition

**Original Problem:** "How should we improve the Brain system architecture?"

**Decomposed:**
1. "What are the performance bottlenecks in the current state table design?"
2. "How can we prevent duplicate memories across Brain and Obsidian?"
3. "What's the optimal strategy for context window management?"
4. "How should we handle concurrent access to memories?"
5. "Given solutions to 1-4, what's the minimal refactoring needed?"

## Anti-patterns

- ❌ "Analyze our entire codebase and suggest improvements"
- ❌ "What's wrong with everything?"
- ❌ Including full file contents when a summary would suffice
- ❌ Asking multiple unrelated questions in one prompt

## Success Metrics

- Each sub-problem gets a focused, deep response
- No responses are cut off due to length
- Insights build on each other coherently
- The synthesis creates value beyond individual parts
