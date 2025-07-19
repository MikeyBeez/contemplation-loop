#!/usr/bin/env python3
"""
Subconscious - A sophisticated background thinking system for Claude
Uses Ollama for deep reasoning on delegated problems
"""
import json
import sys
import time
import os
import asyncio
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import hashlib
from dataclasses import dataclass, asdict
import threading
import queue

try:
    from .ollama_client import OllamaClient
except ImportError:
    # When running as a script
    from ollama_client import OllamaClient

# Create ollama instance
ollama = OllamaClient()

# Configuration
REASONING_MODEL = os.getenv("SUBCONSCIOUS_REASONING_MODEL", "deepseek-r1:latest")
FAST_MODEL = os.getenv("SUBCONSCIOUS_FAST_MODEL", "llama3.2:latest")
DB_PATH = Path.home() / ".subconscious" / "thoughts.db"
MAX_CONCURRENT_THOUGHTS = 3
PROCESSING_INTERVAL = 30  # seconds between processing cycles


class ThoughtPriority(Enum):
    """Priority levels for thoughts"""
    BACKGROUND = 1  # Process when idle
    NORMAL = 5      # Standard priority
    HIGH = 8        # Process soon
    URGENT = 10     # Process immediately


class ThoughtStatus(Enum):
    """Status of thought processing"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass
class Thought:
    """A thought to be processed"""
    id: str
    type: str  # problem, design, analysis, connection, exploration
    content: str
    context: Dict[str, Any]
    priority: int
    status: str
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    model_used: Optional[str] = None
    iterations: int = 0
    parent_id: Optional[str] = None  # For thought chains


class SubconsciousDB:
    """Database for persistent thought storage"""
    
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        self.lock = threading.Lock()
    
    def _init_db(self):
        """Initialize database schema"""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS thoughts (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'queued',
                created_at REAL NOT NULL,
                started_at REAL,
                completed_at REAL,
                result TEXT,
                model_used TEXT,
                iterations INTEGER DEFAULT 0,
                parent_id TEXT,
                FOREIGN KEY (parent_id) REFERENCES thoughts(id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_status ON thoughts(status);
            CREATE INDEX IF NOT EXISTS idx_priority ON thoughts(priority);
            CREATE INDEX IF NOT EXISTS idx_type ON thoughts(type);
            CREATE INDEX IF NOT EXISTS idx_created ON thoughts(created_at);
            
            CREATE TABLE IF NOT EXISTS insights (
                id TEXT PRIMARY KEY,
                thought_id TEXT NOT NULL,
                insight TEXT NOT NULL,
                significance REAL,
                tags TEXT,
                created_at REAL NOT NULL,
                FOREIGN KEY (thought_id) REFERENCES thoughts(id)
            );
            
            CREATE TABLE IF NOT EXISTS connections (
                id TEXT PRIMARY KEY,
                thought_id_1 TEXT NOT NULL,
                thought_id_2 TEXT NOT NULL,
                connection_type TEXT,
                strength REAL,
                description TEXT,
                created_at REAL NOT NULL,
                FOREIGN KEY (thought_id_1) REFERENCES thoughts(id),
                FOREIGN KEY (thought_id_2) REFERENCES thoughts(id)
            );
        """)
        self.conn.commit()
    
    def add_thought(self, thought: Thought) -> str:
        """Add a thought to the queue"""
        with self.lock:
            self.conn.execute("""
                INSERT INTO thoughts (
                    id, type, content, context, priority, status,
                    created_at, parent_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                thought.id, thought.type, thought.content,
                json.dumps(thought.context), thought.priority,
                thought.status, thought.created_at, thought.parent_id
            ))
            self.conn.commit()
        return thought.id
    
    def get_next_thought(self) -> Optional[Thought]:
        """Get the next thought to process"""
        with self.lock:
            row = self.conn.execute("""
                SELECT * FROM thoughts
                WHERE status = 'queued'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            """).fetchone()
            
            if row:
                return self._row_to_thought(row)
        return None
    
    def update_thought(self, thought: Thought):
        """Update thought status and results"""
        with self.lock:
            self.conn.execute("""
                UPDATE thoughts SET
                    status = ?, started_at = ?, completed_at = ?,
                    result = ?, model_used = ?, iterations = ?
                WHERE id = ?
            """, (
                thought.status, thought.started_at, thought.completed_at,
                json.dumps(thought.result) if thought.result else None,
                thought.model_used, thought.iterations, thought.id
            ))
            self.conn.commit()
    
    def get_thought(self, thought_id: str) -> Optional[Thought]:
        """Get a specific thought"""
        with self.lock:
            row = self.conn.execute(
                "SELECT * FROM thoughts WHERE id = ?", (thought_id,)
            ).fetchone()
            if row:
                return self._row_to_thought(row)
        return None
    
    def get_recent_insights(self, hours: int = 24, limit: int = 10) -> List[Dict]:
        """Get recent high-value insights"""
        cutoff = time.time() - (hours * 3600)
        with self.lock:
            rows = self.conn.execute("""
                SELECT t.*, i.* FROM insights i
                JOIN thoughts t ON i.thought_id = t.id
                WHERE i.created_at > ?
                ORDER BY i.significance DESC, i.created_at DESC
                LIMIT ?
            """, (cutoff, limit)).fetchall()
            
            return [dict(row) for row in rows]
    
    def find_connections(self, thought_id: str) -> List[Dict]:
        """Find connections to other thoughts"""
        with self.lock:
            rows = self.conn.execute("""
                SELECT * FROM connections
                WHERE thought_id_1 = ? OR thought_id_2 = ?
                ORDER BY strength DESC
            """, (thought_id, thought_id)).fetchall()
            
            return [dict(row) for row in rows]
    
    def _row_to_thought(self, row) -> Thought:
        """Convert database row to Thought object"""
        return Thought(
            id=row['id'],
            type=row['type'],
            content=row['content'],
            context=json.loads(row['context']) if row['context'] else {},
            priority=row['priority'],
            status=row['status'],
            created_at=row['created_at'],
            started_at=row['started_at'],
            completed_at=row['completed_at'],
            result=json.loads(row['result']) if row['result'] else None,
            model_used=row['model_used'],
            iterations=row['iterations'],
            parent_id=row['parent_id']
        )


class Subconscious:
    """The main subconscious processing system"""
    
    def __init__(self):
        self.db = SubconsciousDB(DB_PATH)
        self.processing_queue = queue.Queue()
        self.active_thoughts = {}
        self.running = False
        self.log_file = Path(__file__).parent.parent / "logs" / "subconscious_activity.log"
        self.log_file.parent.mkdir(exist_ok=True)
        self._init_activity_log()
        self._log("Subconscious initialized", "info")
        self._log_activity("SYSTEM", "Subconscious initialized")
    
    def _init_activity_log(self):
        """Initialize the activity log file"""
        if not self.log_file.exists():
            self.log_file.write_text("")
    
    def _log_activity(self, event_type: str, message: str, thought_id: str = None):
        """Log activity to a rotating log file (max 100 entries)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{event_type}]"
        if thought_id:
            log_entry += f" [ID: {thought_id}]"
        log_entry += f" {message}\n"
        
        # Read existing logs
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
        except:
            lines = []
        
        # Add new entry
        lines.append(log_entry)
        
        # Keep only last 100 entries
        if len(lines) > 100:
            lines = lines[-100:]
        
        # Write back
        with open(self.log_file, 'w') as f:
            f.writelines(lines)
    
    def _log(self, message: str, level: str = "info"):
        """Log to stderr"""
        timestamp = datetime.now().isoformat()
        sys.stderr.write(f"[{timestamp}] [{level.upper()}] {message}\n")
        sys.stderr.flush()
    
    def delegate_thought(self, thought_type: str, content: str, 
                        context: Dict[str, Any] = None,
                        priority: int = ThoughtPriority.NORMAL.value) -> str:
        """Delegate a thought for background processing"""
        thought_id = hashlib.sha256(
            f"{thought_type}:{content}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        thought = Thought(
            id=thought_id,
            type=thought_type,
            content=content,
            context=context or {},
            priority=priority,
            status=ThoughtStatus.QUEUED.value,
            created_at=time.time()
        )
        
        self.db.add_thought(thought)
        self._log(f"Delegated thought {thought_id} (type: {thought_type}, priority: {priority})")
        self._log_activity("DELEGATED", f"Type: {thought_type}, Priority: {priority}, Content: {content[:100]}...", thought_id)
        
        # If urgent, process immediately
        if priority >= ThoughtPriority.URGENT.value:
            self.processing_queue.put(thought_id)
        
        return thought_id
    
    def process_thought(self, thought: Thought) -> Dict[str, Any]:
        """Process a single thought using appropriate model and strategy"""
        self._log(f"Processing thought {thought.id} (type: {thought.type})")
        self._log_activity("PROCESSING", f"Starting to process {thought.type} thought", thought.id)
        
        # Update status
        thought.status = ThoughtStatus.PROCESSING.value
        thought.started_at = time.time()
        self.db.update_thought(thought)
        
        try:
            # Choose model based on thought type
            if thought.type in ['problem', 'design', 'analysis']:
                model = REASONING_MODEL
                max_tokens = 4096
            else:
                model = FAST_MODEL
                max_tokens = 1024
            
            thought.model_used = model
            
            # Build prompt based on thought type
            prompt = self._build_prompt(thought)
            
            # Process with Ollama
            self._log(f"Using {model} for processing")
            self._log_activity("OLLAMA_REQUEST", f"Model: {model}, Prompt length: {len(prompt)} chars", thought.id)
            self._log_activity("PROMPT", prompt[:500] + "..." if len(prompt) > 500 else prompt, thought.id)
            
            response = ollama.generate(prompt, model=model, max_tokens=max_tokens)
            
            self._log_activity("OLLAMA_RESPONSE", f"Response length: {len(response)} chars", thought.id)
            self._log_activity("RESPONSE", response[:500] + "..." if len(response) > 500 else response, thought.id)
            
            # Parse and structure response
            result = self._parse_response(response, thought)
            
            # Check if needs iteration
            if result.get('needs_iteration') and thought.iterations < 3:
                # Create follow-up thought
                follow_up = self.delegate_thought(
                    thought_type=thought.type,
                    content=result.get('iteration_prompt', thought.content),
                    context={**thought.context, 'previous_result': result},
                    priority=thought.priority,
                )
                result['follow_up_id'] = follow_up
                thought.iterations += 1
            
            # Save insights if significant
            if result.get('insights'):
                for insight in result['insights']:
                    self._save_insight(thought.id, insight)
            
            # Find connections to other thoughts
            connections = self._find_connections(thought, result)
            if connections:
                result['connections'] = connections
            
            thought.result = result
            thought.status = ThoughtStatus.COMPLETED.value
            thought.completed_at = time.time()
            
            self._log(f"Completed thought {thought.id} in {thought.completed_at - thought.started_at:.1f}s")
            self._log_activity("COMPLETED", f"Processing time: {thought.completed_at - thought.started_at:.1f}s, Insights: {len(result.get('insights', []))}", thought.id)
            
        except Exception as e:
            self._log(f"Error processing thought {thought.id}: {e}", "error")
            thought.status = ThoughtStatus.FAILED.value
            thought.result = {'error': str(e)}
        
        self.db.update_thought(thought)
        return thought.result
    
    def _build_prompt(self, thought: Thought) -> str:
        """Build sophisticated prompts based on thought type"""
        base_context = ""
        if thought.context:
            base_context = f"\nContext: {json.dumps(thought.context, indent=2)}"
        
        if thought.type == 'problem':
            return f"""You are a sophisticated reasoning system. Analyze this problem deeply:

{thought.content}
{base_context}

Provide:
1. Core problem decomposition
2. Key constraints and dependencies  
3. Multiple solution approaches with trade-offs
4. Recommended approach with justification
5. Potential edge cases and failure modes
6. Connections to similar problems or patterns

Be thorough but concise. Think step by step."""

        elif thought.type == 'design':
            return f"""You are an expert system architect. Design a solution for:

{thought.content}
{base_context}

Include:
1. High-level architecture
2. Key components and their interactions
3. Data flow and state management
4. Scalability considerations
5. Security implications
6. Alternative design patterns considered
7. Future extensibility

Focus on elegance and maintainability."""

        elif thought.type == 'analysis':
            return f"""You are an analytical reasoning system. Analyze:

{thought.content}
{base_context}

Examine:
1. Current state assessment
2. Patterns and anomalies
3. Root cause analysis
4. Implications and consequences
5. Risk factors
6. Optimization opportunities
7. Predictive insights

Use first principles thinking."""

        elif thought.type == 'connection':
            return f"""You are a pattern recognition system. Find deep connections in:

{thought.content}
{base_context}

Explore:
1. Conceptual bridges between domains
2. Shared underlying principles
3. Analogies and metaphors
4. Cross-pollination opportunities
5. Synthesis possibilities
6. Emergent properties

Look for non-obvious connections."""

        elif thought.type == 'exploration':
            return f"""You are a creative exploration system. Explore:

{thought.content}
{base_context}

Consider:
1. Adjacent possibilities
2. Thought experiments
3. "What if" scenarios
4. Unconventional perspectives
5. Second and third-order effects
6. Paradigm shifts

Be imaginative but grounded."""
            
        else:
            return f"""Thoughtfully consider:

{thought.content}
{base_context}

Provide deep insights and connections."""
    
    def _parse_response(self, response: str, thought: Thought) -> Dict[str, Any]:
        """Parse and structure the model response"""
        result = {
            'raw_response': response,
            'timestamp': time.time(),
            'model': thought.model_used
        }
        
        # Extract structured insights
        insights = []
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            if line.endswith(':') and len(line) < 50:
                current_section = line[:-1].lower()
                result[current_section] = []
            elif current_section and line.startswith(('- ', '• ', '* ', '1.', '2.', '3.')):
                result[current_section].append(line[2:].strip())
            
            # Detect insights
            if any(marker in line.lower() for marker in 
                   ['insight:', 'realization:', 'key finding:', 'important:']):
                insights.append(line)
        
        if insights:
            result['insights'] = insights
        
        # Check if needs iteration
        if any(phrase in response.lower() for phrase in 
               ['need more information', 'requires further', 'should explore']):
            result['needs_iteration'] = True
        
        return result
    
    def _save_insight(self, thought_id: str, insight: str):
        """Save a significant insight"""
        insight_id = hashlib.sha256(
            f"{thought_id}:{insight}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Simple significance scoring
        significance = len(insight) / 100.0  # Basic heuristic
        if any(word in insight.lower() for word in 
               ['breakthrough', 'key', 'critical', 'fundamental']):
            significance *= 2
        
        with self.db.conn:
            self.db.conn.execute("""
                INSERT INTO insights (id, thought_id, insight, significance, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (insight_id, thought_id, insight, significance, time.time()))
    
    def _find_connections(self, thought: Thought, result: Dict) -> List[Dict]:
        """Find connections to other processed thoughts"""
        # This is a placeholder for more sophisticated connection finding
        # Could use embeddings, semantic search, etc.
        connections = []
        
        # Simple keyword matching for now
        keywords = set(thought.content.lower().split())
        
        recent_thoughts = self.db.conn.execute("""
            SELECT id, type, content FROM thoughts
            WHERE id != ? AND status = 'completed'
            ORDER BY completed_at DESC
            LIMIT 100
        """, (thought.id,)).fetchall()
        
        for other in recent_thoughts:
            other_keywords = set(other['content'].lower().split())
            overlap = keywords & other_keywords
            
            if len(overlap) > 3:  # Arbitrary threshold
                connections.append({
                    'thought_id': other['id'],
                    'type': other['type'],
                    'strength': len(overlap) / len(keywords),
                    'shared_concepts': list(overlap)
                })
        
        return connections[:5]  # Top 5 connections
    
    def get_insights(self, thought_id: str = None, hours: int = 24) -> List[Dict]:
        """Retrieve insights, optionally filtered by thought"""
        if thought_id:
            thought = self.db.get_thought(thought_id)
            if thought and thought.result:
                return thought.result
            return []
        else:
            return self.db.get_recent_insights(hours=hours)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the subconscious"""
        with self.db.conn:
            stats = self.db.conn.execute("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    AVG(priority) as avg_priority
                FROM thoughts
                GROUP BY status
            """).fetchall()
            
            status_dict = {row['status']: {
                'count': row['count'],
                'avg_priority': row['avg_priority']
            } for row in stats}
        
        return {
            'running': self.running,
            'stats': status_dict,
            'active_thoughts': len(self.active_thoughts),
            'models': {
                'reasoning': REASONING_MODEL,
                'fast': FAST_MODEL
            }
        }
    
    def run(self):
        """Main processing loop"""
        self.running = True
        self._log("Subconscious processing loop started")
        
        while self.running:
            try:
                # Get next thought
                thought = self.db.get_next_thought()
                
                if thought:
                    # Process it
                    self.active_thoughts[thought.id] = thought
                    result = self.process_thought(thought)
                    del self.active_thoughts[thought.id]
                    
                    # Notify if urgent
                    if thought.priority >= ThoughtPriority.HIGH.value:
                        self._log(f"High priority thought {thought.id} completed", "info")
                else:
                    # No thoughts to process, wait
                    time.sleep(PROCESSING_INTERVAL)
                    
            except KeyboardInterrupt:
                self._log("Received shutdown signal")
                break
            except Exception as e:
                self._log(f"Error in main loop: {e}", "error")
                time.sleep(5)
        
        self.running = False
        self._log("Subconscious processing loop stopped")


def main():
    """Main entry point for the subconscious service"""
    subconscious = Subconscious()
    
    # Start processing loop
    subconscious.run()


if __name__ == "__main__":
    main()
