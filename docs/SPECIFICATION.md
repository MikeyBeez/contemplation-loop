# Ollama Conversation System - Engineering Specification

## System Overview

An asynchronous conversation system that enables Claude to have deep, tool-assisted dialogues with Ollama models for complex problem-solving.

## Architecture Hierarchy

### Level 1: Infrastructure Components

#### 1.1 Conversation Manager Service
- **Type**: Background service (launchctl)
- **Purpose**: Monitor conversation directories and manage lifecycle
- **Location**: `/Users/bard/Code/contemplation-loop/src/conversation_manager.py`

#### 1.2 Ollama Client Library  
- **Type**: Python module
- **Purpose**: Handle Ollama API communication
- **Location**: `/Users/bard/Code/contemplation-loop/src/ollama_client.py` (enhance existing)

#### 1.3 File-Based Message Queue
- **Type**: Directory structure
- **Purpose**: Async message passing via filesystem
- **Location**: `/Users/bard/Code/contemplation-loop/conversations/`

### Level 2: Core Components

#### 2.1 Message Parser
- **Purpose**: Parse conversation logs and extract requests
- **Inputs**: Log files with structured format
- **Outputs**: Parsed messages, request types, metadata

#### 2.2 Context Assembler
- **Purpose**: Use MCP tools to gather relevant context
- **Inputs**: Problem description, context requirements
- **Outputs**: Structured context package

#### 2.3 Request Router
- **Purpose**: Route Ollama's NEED: requests to appropriate MCP tools
- **Inputs**: Parsed requests from Ollama
- **Outputs**: MCP tool calls and responses

#### 2.4 Response Formatter
- **Purpose**: Format tool responses for Ollama consumption
- **Inputs**: Raw MCP tool responses
- **Outputs**: Formatted context snippets

### Level 3: Organ Systems

#### 3.1 Conversation Engine
- **Components**: Message Parser + Request Router + Response Formatter
- **Purpose**: Handle the conversation flow mechanics
- **Interface**: 
  - Input: New messages in conversation log
  - Output: Responses appended to log

#### 3.2 Context Assembly Pipeline
- **Components**: Context Assembler + MCP tool integrations
- **Purpose**: Implement vibecoding - gathering all puzzle pieces
- **Interface**:
  - Input: Problem description
  - Output: Complete context package

#### 3.3 Monitoring Dashboard
- **Components**: Log viewer + Status tracker + Metrics
- **Purpose**: Visibility into ongoing conversations
- **Interface**:
  - Web UI or terminal UI
  - Real-time conversation status

### Level 4: Complete System

#### 4.1 Ollama Conversation Service
- **Organs**: Conversation Engine + Context Pipeline + Monitoring
- **Purpose**: Complete async conversation system
- **External Interfaces**:
  - MCP tools for Claude to interact
  - Conversation directories
  - Status API

## Detailed Component Specifications

### 1. Conversation Manager Service

```python
class ConversationManager:
    """
    Background service that monitors conversation directories
    """
    
    def __init__(self, conversations_dir: Path):
        self.conversations_dir = conversations_dir
        self.active_conversations = {}
        self.ollama_client = OllamaClient()
    
    def scan_for_new_messages(self):
        """Check all conversation logs for new messages"""
        
    def process_claude_message(self, conversation_id: str, message: dict):
        """Send Claude's message to Ollama"""
        
    def process_ollama_response(self, conversation_id: str, response: str):
        """Parse Ollama's response for NEED: requests"""
        
    def handle_need_request(self, request_type: str, request_data: str):
        """Route NEED: request to appropriate handler"""
```

**Specifications:**
- Polls conversation directory every 5 seconds
- Maintains state of active conversations
- Handles errors gracefully (network, Ollama unavailable)
- Logs all activity for debugging

### 2. File-Based Message Queue

**Directory Structure:**
```
conversations/
├── active/
│   ├── conv_[timestamp]_[topic]/
│   │   ├── messages.log      # Main conversation log
│   │   ├── metadata.json     # Model, status, created
│   │   ├── context/          # Assembled context files
│   │   └── state.json        # Current conversation state
│   └── conv_[timestamp]_[topic]/
├── completed/
│   └── [archived conversations]
└── templates/
    └── [conversation templates]
```

**Message Format:**
```
=== CLAUDE -> OLLAMA [2024-01-19 10:00:00] ===
[Message content]

=== OLLAMA -> CLAUDE [2024-01-19 10:00:45] ===
[Response content]
NEED: Brain memory about [topic]

=== CLAUDE -> OLLAMA [2024-01-19 10:01:00] ===
RESPONSE TO NEED:
[Tool response content]
```

### 3. Context Assembler

```python
class ContextAssembler:
    """
    Implements vibecoding - assembles context from multiple sources
    """
    
    def __init__(self, mcp_tools: dict):
        self.tools = mcp_tools
        
    async def assemble_context(self, problem: str, requirements: dict) -> dict:
        """
        Gather context from multiple sources in parallel
        """
        tasks = []
        
        if requirements.get('code_structure'):
            tasks.append(self.get_code_context(requirements['project_path']))
            
        if requirements.get('history'):
            tasks.append(self.get_historical_context(problem))
            
        if requirements.get('current_state'):
            tasks.append(self.get_system_state())
            
        contexts = await asyncio.gather(*tasks)
        return self.merge_and_filter(contexts)
```

**Specifications:**
- Parallel context gathering for speed
- Automatic summarization if over token limits
- Caching of frequently accessed context
- Progressive loading based on Ollama requests

### 4. Request Router

```python
class RequestRouter:
    """
    Routes Ollama's NEED: requests to appropriate MCP tools
    """
    
    ROUTE_MAP = {
        'Brain memory about': 'brain:brain_recall',
        'Obsidian notes matching': 'brain:obsidian_note', 
        'File contents of': 'filesystem:read_file',
        'Search results for': 'web_search',
        'Current state of': 'brain:state_get'
    }
    
    def route_request(self, need_statement: str) -> tuple[str, dict]:
        """
        Parse NEED: statement and return (tool, params)
        """
```

**Specifications:**
- Extensible routing rules
- Error handling for unavailable tools
- Response formatting per tool type
- Request queuing for rate limits

### 5. Monitoring Dashboard

```python
class ConversationMonitor:
    """
    Real-time monitoring of conversation system
    """
    
    def get_active_conversations(self) -> list[dict]:
        """List all active conversations with status"""
        
    def get_conversation_details(self, conv_id: str) -> dict:
        """Get full details of a conversation"""
        
    def get_metrics(self) -> dict:
        """System metrics: response times, request counts, etc"""
```

**Specifications:**
- Web interface on port 5556
- Real-time updates via polling or SSE
- Conversation search and filtering
- Export conversations for analysis

## Integration Points

### MCP Tools for Claude

New tools to add:
```javascript
{
  name: 'ollama_conversation_start',
  description: 'Start a new conversation with Ollama',
  inputs: {
    topic: 'string',
    model: 'string', 
    initial_prompt: 'string',
    context_requirements: 'object'
  }
}

{
  name: 'ollama_conversation_check',
  description: 'Check status of Ollama conversation',
  inputs: {
    conversation_id: 'string'
  }
}

{
  name: 'ollama_conversation_respond',
  description: 'Respond to Ollama request in conversation',
  inputs: {
    conversation_id: 'string',
    response: 'string'
  }
}
```

## Performance Specifications

- Conversation check latency: < 100ms
- Context assembly: < 5 seconds for typical request
- Message parsing: < 50ms
- Support for 10+ concurrent conversations
- Log rotation after 10MB per conversation

## Error Handling

- Ollama unavailable: Queue messages, retry with backoff
- Tool failures: Provide degraded context, note in response
- Parsing errors: Save raw content, alert in monitor
- File system errors: Fallback to alternate storage

## Security Considerations

- Validate all file paths before access
- Sanitize Ollama responses before tool execution
- Rate limit tool requests per conversation
- No arbitrary code execution from conversations
