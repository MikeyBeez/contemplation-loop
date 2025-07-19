#!/usr/bin/env python3
"""
Contemplation Pipeline - Connects the kind thought generator to the contemplation loop
"""
import subprocess
import sys
import time
import signal
import json
from pathlib import Path

def signal_handler(signum, frame):
    """Handle shutdown gracefully"""
    print("\nShutting down contemplation pipeline...", file=sys.stderr)
    sys.exit(0)

def main():
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Paths
    base_dir = Path("/Users/bard/Code/contemplation-loop")
    generator_path = base_dir / "src" / "kind_thought_generator.py"
    loop_path = base_dir / "src" / "contemplation_loop.py"
    
    print("Starting contemplation pipeline...", file=sys.stderr)
    
    try:
        # Start the contemplation loop
        loop_process = subprocess.Popen(
            [sys.executable, str(loop_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Start the thought generator
        generator_process = subprocess.Popen(
            [sys.executable, str(generator_path), "--rate", "12"],  # 12 thoughts per hour
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        print("Pipeline started successfully", file=sys.stderr)
        
        # Connect generator output to loop input
        while True:
            # Read thought from generator
            thought_line = generator_process.stdout.readline()
            if not thought_line:
                break
                
            # Send to contemplation loop
            loop_process.stdin.write(thought_line)
            loop_process.stdin.flush()
            
            # Read response from loop
            response_line = loop_process.stdout.readline()
            if response_line:
                try:
                    response = json.loads(response_line)
                    if response.get('has_insight'):
                        print(f"💡 New insight found!", file=sys.stderr)
                except:
                    pass
            
            # Check if processes are still running
            if generator_process.poll() is not None or loop_process.poll() is not None:
                break
                
    except Exception as e:
        print(f"Error in pipeline: {e}", file=sys.stderr)
    finally:
        # Clean up
        if 'generator_process' in locals():
            generator_process.terminate()
        if 'loop_process' in locals():
            loop_process.terminate()
            
    print("Pipeline stopped", file=sys.stderr)

if __name__ == "__main__":
    main()
