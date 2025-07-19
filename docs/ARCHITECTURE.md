# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ollama Conversation System                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    ORGAN: Context Pipeline                │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │  Context    │  │     MCP      │  │   Response   │   │   │
│  │  │ Assembler   │──│ Integrations │──│  Formatter   │   │   │
│  │  └─────────────┘  └──────────────┘  └──────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 ORGAN: Conversation Engine                │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │   Message   │  │   Request    │  │   Response   │   │   │
│  │  │   Parser    │──│   Router     │──│  Formatter   │   │   │
│  │  └─────────────┘  └──────────────┘  └──────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    ORGAN: Monitoring                      │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │   Status    │  │   Metrics    │  │  Dashboard   │   │   │
│  │  │  Tracker    │──│  Collector   │──│     UI       │   │   │
│  │  └─────────────┘  └──────────────┘  └──────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Infrastructure Components:                                      │
│  ┌──────────────────┐  ┌──────────────┐  ┌───────────────┐    │
│  │  Conversation    │  │   Ollama     │  │  File-Based   │    │
│  │    Manager       │  │   Client     │  │ Message Queue │    │
│  │   (Service)      │  │  (Library)   │  │ (Directory)   │    │
│  └──────────────────┘  └──────────────┘  └───────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

External Interfaces:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│    Claude   │────▶│  MCP Tools   │────▶│  Conv. Mgr   │
│   (User)    │     │  Interface   │     │              │
└─────────────┘     └──────────────┘     └──────────────┘
                                                 │
┌─────────────┐     ┌──────────────┐            ▼
│   Ollama    │◀────│  Conv. Logs  │◀────────────┘
│  (Models)   │────▶│              │
└─────────────┘     └──────────────┘
```

## Data Flow

1. **Claude initiates conversation**
   - Uses MCP tool `ollama_conversation_start`
   - Provides initial prompt + context requirements
   - Receives conversation ID

2. **Context Assembly (Vibecoding)**
   - Context Assembler uses MCP tools in parallel
   - Gathers code, history, state, etc.
   - Formats into structured package

3. **Message Exchange**
   - Messages written to conversation log
   - Conversation Manager detects changes
   - Sends to Ollama via client

4. **Ollama Processes**
   - Thinks about problem
   - May request additional info via NEED:
   - Writes response to log

5. **Request Handling**
   - Parser extracts NEED: requests
   - Router maps to MCP tools
   - Claude provides requested info

6. **Iteration**
   - Continues until Ollama signals completion
   - All exchanges logged for analysis

7. **Monitoring**
   - Dashboard shows active conversations
   - Metrics track performance
   - Logs available for debugging
