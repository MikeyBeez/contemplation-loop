# Contemplation Loop - Sophisticated Subconscious System

A sophisticated thinking system that enables asynchronous, tool-assisted conversations with Ollama models for deep problem-solving.

## 🧠 Overview

This system creates a "subconscious" that can:
- Process complex problems asynchronously using Ollama models
- Access tools (filesystem, memory, search) while thinking
- Maintain transparent logs of all thinking processes
- Handle multiple concurrent thought streams
- Provide a real-time monitoring dashboard

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) for package management
- [Ollama](https://ollama.ai/) with models installed (deepseek-r1, llama3.2, etc.)
- macOS (for launchctl service management)

### Installation

```bash
# Clone the repository
git clone https://github.com/MikeyBeez/contemplation-loop.git
cd contemplation-loop

# Install the subconscious service
./install_subconscious.sh

# Start the monitoring dashboard
./start_dashboard.sh
```

Dashboard will be available at http://localhost:5555

## 🎯 Key Features

### 1. Subconscious Service
- Always-running background service via launchctl
- Processes thoughts asynchronously with Ollama
- SQLite database for persistent thought storage
- Priority-based processing queue

### 2. Transparency Logging
- Complete activity log of all operations
- See every prompt sent to Ollama
- Track processing times and results
- FIFO log limited to 100 entries

### 3. Real-time Dashboard
- Monitor active thoughts
- View completed insights
- Track system metrics
- Beautiful dark-mode UI with neural network animation

### 4. Ollama Conversation Protocols
Comprehensive protocols for effective LLM interaction:
- **Problem Decomposition** - Break complex problems into manageable pieces
- **Context Assembly (Vibecoding)** - Gather all relevant context before thinking
- **Conversation Management** - Async conversations through log files
- **Model Selection** - Choose the right model for each task
- **Synthesis Process** - Combine insights into coherent solutions

## 📁 Project Structure

```
contemplation-loop/
├── src/                    # Core source code
│   ├── subconscious.py    # Main thinking service
│   ├── subconscious_client.py  # CLI client
│   └── ollama_client.py   # Ollama API interface
├── protocols/             # Ollama conversation protocols
├── dashboard/             # Web monitoring dashboard
├── logs/                  # Activity and error logs
└── docs/                  # Architecture and specifications
```

## 🔧 Usage

### Send a thought for processing
```bash
cd contemplation-loop
uv run python src/subconscious_client.py think problem "How can we optimize database queries?" --priority high
```

### Check thought status
```bash
uv run python src/subconscious_client.py check <thought_id>
```

### View activity log
```bash
./show_activity.sh
# or follow live:
./view_activity.py -f
```

### View system status
```bash
uv run python src/subconscious_client.py status
```

## 🏗️ Architecture

The system follows a hierarchical architecture:

1. **Infrastructure Components**
   - Conversation Manager Service
   - Ollama Client Library
   - File-Based Message Queue

2. **Core Components**
   - Message Parser
   - Context Assembler
   - Request Router
   - Response Formatter

3. **Organ Systems**
   - Conversation Engine
   - Context Assembly Pipeline
   - Monitoring Dashboard

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed diagrams.

## 📋 Protocols

The `protocols/` directory contains detailed protocols for:
- Problem decomposition strategies
- Context assembly (modern vibecoding)
- Conversation management patterns
- Model selection criteria
- Synthesis processes

These protocols ensure effective use of LLMs for complex thinking tasks.

## 🛠️ Development

### Running tests
```bash
./test_subconscious.sh
```

### Cleanup orphaned processes
```bash
./cleanup.sh
```

### Virtual environment (using uv)
```bash
uv venv
uv pip install -r requirements.txt
```

## 📝 Philosophy

This system implements "modern vibecoding" - using tools to gather all puzzle pieces before handing them to an LLM for deep analysis. It's designed for:

- **Asynchronous thinking** - Delegate complex problems and check back later
- **Tool-assisted reasoning** - LLMs can request information while thinking
- **Transparency** - See exactly what the system is doing
- **Composability** - Break problems down, solve pieces, synthesize results

## 🤝 Contributing

This is an experimental system for augmented thinking. Contributions, ideas, and feedback are welcome!

## 📄 License

MIT License - see LICENSE file for details.
