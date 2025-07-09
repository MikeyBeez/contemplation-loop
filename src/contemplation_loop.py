#!/usr/bin/env python3
"""
Contemplation Loop - A background thinking process for AI
Designed to work with smaller Ollama models with limited context
"""
import json
import sys
import time
import os
from datetime import datetime
from pathlib import Path
import traceback
import hashlib
from typing import Dict, Any, List, Optional
from ollama_client import ollama

# Configuration
MODEL = os.getenv("CONTEMPLATION_MODEL", "llama3.2:latest")  # Smaller model
MAX_CONTEXT_TOKENS = 2048  # Conservative limit
OBSIDIAN_PATH = Path.home() / "Documents/Obsidian/Brain/Contemplation"
SCRATCH_PATH = Path("/Users/bard/Code/contemplation-loop/tmp/contemplation")
MAX_SCRATCH_SIZE_MB = 10
SIGNIFICANCE_THRESHOLD = 7  # 1-10 scale for Obsidian notes


class ContemplationLoop:
    """A contemplative background process with context management"""
    
    def __init__(self):
        self.model = MODEL
        self.context_tokens = 0
        self.current_session = []
        self.session_start = time.time()
        self.thoughts_processed = 0
        self.insights_found = 0
        
        # Ensure directories exist
        OBSIDIAN_PATH.mkdir(parents=True, exist_ok=True)
        SCRATCH_PATH.mkdir(parents=True, exist_ok=True)
        
        self._log("Contemplation loop initialized", "info")
    
    def _log(self, message: str, level: str = "info"):
        """Log to stderr for monitoring"""
        timestamp = datetime.now().isoformat()
        sys.stderr.write(f"[{timestamp}] [{level.upper()}] {message}\n")
        sys.stderr.flush()
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (conservative)"""
        # Assume ~3 chars per token for safety with small models
        return len(str(text)) // 3
    
    def _get_context_usage(self) -> float:
        """Calculate current context usage percentage"""
        total_tokens = sum(self._estimate_tokens(str(item)) 
                          for item in self.current_session)
        return (total_tokens / MAX_CONTEXT_TOKENS) * 100
    
    def process_thought(self, thought: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single thought with context awareness"""
        try:
            thought_id = thought.get('id', str(time.time()))
            thought_type = thought.get('type', 'general')
            content = thought.get('content', '')
            
            self._log(f"Processing thought {thought_id} (type: {thought_type})")
            
            # Check context before processing
            if self._get_context_usage() > 70:  # 70% full
                self._log("Context approaching limit, compressing...")
                self._compress_context()
            
            # Simple prompt for small model
            prompt = self._build_prompt(thought_type, content)
            
            # Process with Ollama
            response = self._ollama_process(prompt)
            
            # Extract any insights
            insight = self._extract_insight(response, thought)
            
            # Save to scratch
            self._save_scratch_note({
                'thought_id': thought_id,
                'type': thought_type,
                'input': content,
                'response': response,
                'insight': insight,
                'timestamp': time.time()
            })
            
            # Update session
            self.current_session.append({
                'thought': content[:100],  # Truncate for context
                'insight': insight
            })
            self.thoughts_processed += 1
            
            # Return result
            return {
                'status': 'ok',
                'thought_id': thought_id,
                'insight': insight,
                'has_insight': insight is not None
            }
            
        except Exception as e:
            self._log(f"Error processing thought: {e}", "error")
            return {
                'status': 'error',
                'error': str(e),
                'thought_id': thought.get('id', 'unknown')
            }
    
    def _build_prompt(self, thought_type: str, content: str) -> str:
        """Build simple, focused prompts for small models"""
        if thought_type == 'pattern':
            return f"What pattern do you notice in: {content}\nPattern:"
        elif thought_type == 'connection':
            return f"What connects these ideas: {content}\nConnection:"
        elif thought_type == 'question':
            return f"What's interesting about: {content}\nInsight:"
        else:
            return f"Reflect on: {content}\nThought:"
    
    def _ollama_process(self, prompt: str) -> str:
        """Process with Ollama"""
        self._log(f"Processing with {self.model}: {prompt[:50]}...")
        
        response = ollama.generate(prompt, model=self.model, max_tokens=150)
        
        if response:
            return response
        else:
            self._log("Ollama not available, using fallback", "warning")
            return "[Contemplation in progress - Ollama offline]"
    
    def _extract_insight(self, response: str, original_thought: Dict) -> Optional[str]:
        """Extract significant insights from response"""
        # Simple heuristic for small model responses
        response_lower = response.lower()
        
        # Look for insight indicators
        if any(word in response_lower for word in ['realize', 'notice', 'pattern', 'interesting', 'connect']):
            # Calculate significance (simple heuristic)
            significance = 5
            if len(response) > 100:
                significance += 2
            if original_thought.get('type') == 'pattern':
                significance += 1
                
            if significance >= SIGNIFICANCE_THRESHOLD:
                self.insights_found += 1
                return response.strip()
        
        return None
    
    def _compress_context(self):
        """Compress context to essential points"""
        if len(self.current_session) < 3:
            return
            
        # Keep only insights and recent thoughts
        compressed = []
        
        # Keep all insights
        for item in self.current_session:
            if item.get('insight'):
                compressed.append({
                    'type': 'insight',
                    'content': item['insight'][:50]
                })
        
        # Keep last 2 thoughts
        compressed.extend(self.current_session[-2:])
        
        self._log(f"Compressed context from {len(self.current_session)} to {len(compressed)} items")
        self.current_session = compressed
    
    def _save_scratch_note(self, note: Dict[str, Any]):
        """Save note to scratch directory"""
        # Determine which day directory
        day_dir = SCRATCH_PATH / "day_0"
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"thought_{timestamp}_{note['thought_id'][:8]}.json"
        
        # Save
        with open(day_dir / filename, 'w') as f:
            json.dump(note, f, indent=2)
    
    def _save_to_obsidian(self, insight: str, context: Dict[str, Any]):
        """Save significant insight to Obsidian"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M")
        
        # Create note content
        content = f"""# Contemplation Insight
*{date_str} {time_str}*

{insight}

---
*Context: {context.get('type', 'general')} thought*
*Significance: {context.get('significance', 'unknown')}/10*
"""
        
        # Save to Obsidian
        filename = f"insight_{date_str}_{int(time.time())}.md"
        with open(OBSIDIAN_PATH / filename, 'w') as f:
            f.write(content)
            
        self._log(f"Saved insight to Obsidian: {filename}")
    
    def run(self):
        """Main loop - read thoughts from stdin"""
        self._log("Contemplation loop starting...")
        print(json.dumps({"status": "ready", "model": self.model}))
        sys.stdout.flush()
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                # Parse thought
                thought = json.loads(line.strip())
                
                # Process
                result = self.process_thought(thought)
                
                # Send response
                print(json.dumps(result))
                sys.stdout.flush()
                
                # Periodic status
                if self.thoughts_processed % 10 == 0:
                    self._log(f"Processed {self.thoughts_processed} thoughts, "
                            f"found {self.insights_found} insights, "
                            f"context usage: {self._get_context_usage():.1f}%")
                
            except json.JSONDecodeError as e:
                self._log(f"Invalid JSON input: {e}", "error")
            except KeyboardInterrupt:
                self._log("Received shutdown signal")
                break
            except Exception as e:
                self._log(f"Unexpected error: {e}", "error")
                traceback.print_exc(file=sys.stderr)
        
        self._log(f"Contemplation loop ending. Processed {self.thoughts_processed} thoughts.")


if __name__ == "__main__":
    loop = ContemplationLoop()
    loop.run()
