# Ollama Conversation System - Protocol Summary

## Overview
These protocols define how to have effective asynchronous, tool-assisted conversations with Ollama models for deep thinking and problem-solving.

## Core Protocols

### 1. [Problem Decomposition](./problem_decomposition.md)
- Break complex problems into focused sub-problems
- Size for context windows
- Order by dependencies
- Aim for single-responsibility questions

### 2. [Context Assembly (Vibecoding)](./context_assembly_vibecoding.md)
- Use MCP tools to gather all relevant context
- Combine multiple information sources
- Filter and structure for Ollama
- The art of assembling puzzle pieces

### 3. [Conversation Management](./ollama_conversation.md)  
- Conduct async conversations through log files
- Handle information requests with MCP tools
- Track conversation lifecycle
- Format for clarity and parsing

### 4. [Context Preparation](./context_preparation.md)
- Format gathered context within token limits
- Use compression techniques
- Enable progressive information disclosure
- Include tool instructions

### 5. [Model Selection](./model_selection.md)
- Choose right model for the task
- Balance speed vs depth
- Understand model characteristics
- Consider resource constraints

### 6. [Synthesis Process](./synthesis_process.md)
- Combine sub-problem solutions
- Resolve contradictions
- Build coherent narratives
- Extract emergent insights

## Key Principles

1. **Asynchronous by Design** - Ollama takes time; design for it
2. **Progressive Disclosure** - Start minimal, let Ollama request details
3. **Tool Assistance** - Ollama can ask for information via NEED: statements
4. **Problem Decomposition** - Complex problems need breaking down
5. **Model Fit** - Different models for different tasks

## Workflow Example

1. **Decompose** big problem into sub-problems
2. **Select** appropriate model for each
3. **Prepare** focused context
4. **Initiate** conversation with clear instructions
5. **Monitor** for information requests
6. **Provide** requested data via MCP tools
7. **Collect** completed responses
8. **Synthesize** into complete solution

## Next Steps

These protocols need:
1. Implementation of conversation system
2. Integration with MCP tools
3. Testing with real problems
4. Refinement based on usage

Once proven, these can be added to the master protocol index.
