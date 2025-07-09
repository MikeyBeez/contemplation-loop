#!/usr/bin/env python3
"""
Bridge to communicate with the contemplation loop subprocess
"""
import subprocess
import json
import threading
import queue
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys


class ContemplationBridge:
    """Bridge for communicating with contemplation loop"""
    
    def __init__(self, loop_script: str = None):
        if loop_script is None:
            loop_script = str(Path(__file__).parent / "contemplation_loop.py")
            
        self.loop_script = loop_script
        self.process = None
        self.response_queue = queue.Queue()
        self.error_log_path = Path("/Users/bard/Code/contemplation-loop/logs/contemplation_stderr.log")
        self.is_running = False
        
        # Ensure log directory exists
        self.error_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def start(self) -> bool:
        """Start the contemplation loop subprocess"""
        try:
            # Open error log file
            self.error_log = open(self.error_log_path, 'a')
            self.error_log.write(f"\n=== New session started at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            self.error_log.flush()
            
            # Start subprocess
            self.process = subprocess.Popen(
                [sys.executable, self.loop_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=self.error_log,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Start reader thread
            self.reader_thread = threading.Thread(
                target=self._read_output,
                daemon=True
            )
            self.reader_thread.start()
            
            # Wait for ready signal
            timeout = 5.0
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    response = self.response_queue.get(timeout=0.1)
                    if response.get('status') == 'ready':
                        self.is_running = True
                        print(f"Contemplation loop ready with model: {response.get('model')}")
                        return True
                except queue.Empty:
                    continue
            
            raise TimeoutError("Contemplation loop failed to start")
            
        except Exception as e:
            print(f"Failed to start contemplation loop: {e}")
            self.stop()
            return False
    
    def _read_output(self):
        """Read output from subprocess in background thread"""
        if not self.process:
            return
            
        for line in self.process.stdout:
            try:
                response = json.loads(line.strip())
                self.response_queue.put(response)
            except json.JSONDecodeError:
                # Log non-JSON output
                with open(self.error_log_path.parent / "raw_output.log", 'a') as f:
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] RAW: {line}")
    
    def send_thought(self, thought_type: str, content: str, 
                    metadata: Dict[str, Any] = None) -> str:
        """Send a thought to the contemplation loop"""
        if not self.is_running:
            raise RuntimeError("Contemplation loop is not running")
        
        thought = {
            'id': f"{time.time()}_{hash(content) % 10000}",
            'type': thought_type,
            'content': content,
            'timestamp': time.time()
        }
        
        if metadata:
            thought.update(metadata)
        
        # Send to loop
        self.process.stdin.write(json.dumps(thought) + '\n')
        self.process.stdin.flush()
        
        return thought['id']
    
    def get_responses(self, timeout: float = 0.1) -> List[Dict[str, Any]]:
        """Get any available responses from the loop"""
        responses = []
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            try:
                response = self.response_queue.get(timeout=0.01)
                responses.append(response)
            except queue.Empty:
                if responses:  # Got some responses, return them
                    break
                continue
        
        return responses
    
    def check_errors(self, last_n_lines: int = 10) -> List[str]:
        """Read recent errors from stderr log"""
        if not self.error_log_path.exists():
            return []
        
        with open(self.error_log_path, 'r') as f:
            lines = f.readlines()
            return lines[-last_n_lines:] if lines else []
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of the contemplation loop"""
        status = {
            'running': self.is_running,
            'process_alive': self.process and self.process.poll() is None,
            'recent_errors': self.check_errors(5)
        }
        
        # Try to get responses to see if it's responsive
        responses = self.get_responses(timeout=0.1)
        status['recent_responses'] = len(responses)
        
        return status
    
    def stop(self):
        """Stop the contemplation loop"""
        self.is_running = False
        
        if self.process:
            # Try graceful shutdown
            self.process.stdin.close()
            try:
                self.process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                self.process.kill()
                self.process.wait()
            
            self.process = None
        
        if hasattr(self, 'error_log') and self.error_log:
            self.error_log.close()
    
    def restart(self) -> bool:
        """Restart the contemplation loop"""
        print("Restarting contemplation loop...")
        self.stop()
        time.sleep(0.5)  # Brief pause
        return self.start()


def demo():
    """Demo the contemplation bridge"""
    bridge = ContemplationBridge()
    
    try:
        # Start the loop
        if not bridge.start():
            print("Failed to start contemplation loop")
            return
        
        # Send some thoughts
        thoughts = [
            ("pattern", "Users often ask about memory limits in the same anxious way"),
            ("connection", "Context windows and human memory both have boundaries that create anxiety"),
            ("question", "Why do we fear being forgotten by systems?"),
            ("general", "The intersection of technical limits and emotional needs")
        ]
        
        for thought_type, content in thoughts:
            print(f"\nSending {thought_type} thought: {content[:50]}...")
            thought_id = bridge.send_thought(thought_type, content)
            
            # Wait for response
            time.sleep(0.5)
            responses = bridge.get_responses(timeout=1.0)
            
            for response in responses:
                print(f"Response: {json.dumps(response, indent=2)}")
        
        # Check status
        print("\nLoop status:")
        print(json.dumps(bridge.get_status(), indent=2))
        
    finally:
        bridge.stop()
        print("\nDemo complete")


if __name__ == "__main__":
    demo()
