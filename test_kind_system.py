#!/usr/bin/env python3
"""
Test the kind thought contemplation system
"""
import subprocess
import json
import sys
import time
from pathlib import Path

def test_generator():
    """Test the kind thought generator"""
    print("Testing Kind Thought Generator...")
    print("-" * 50)
    
    generator_path = Path(__file__).parent / "src" / "kind_thought_generator.py"
    
    # Generate a few test thoughts
    result = subprocess.run(
        [sys.executable, str(generator_path), "--batch", "5"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        thoughts = []
        for line in result.stdout.strip().split('\n'):
            if line:
                thought = json.loads(line)
                thoughts.append(thought)
                print(f"\nThought {len(thoughts)}:")
                print(f"  Type: {thought['type']}")
                print(f"  Theme: {thought['theme']}")
                print(f"  Content: {thought['content']}")
                print(f"  Priority: {thought['priority']}")
        return thoughts
    else:
        print(f"Error: {result.stderr}")
        return []

def test_contemplation(thoughts):
    """Test processing thoughts through contemplation loop"""
    print("\n\nTesting Contemplation Processing...")
    print("-" * 50)
    
    loop_path = Path(__file__).parent / "src" / "contemplation_loop.py"
    
    # Start contemplation loop
    process = subprocess.Popen(
        [sys.executable, str(loop_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Wait for ready signal
    ready_line = process.stdout.readline()
    if ready_line:
        print(f"Loop status: {ready_line.strip()}")
    
    # Process thoughts
    results = []
    for i, thought in enumerate(thoughts[:3]):  # Test first 3
        print(f"\nProcessing thought {i+1}...")
        
        # Send thought
        process.stdin.write(json.dumps(thought) + '\n')
        process.stdin.flush()
        
        # Get response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            results.append(response)
            
            print(f"  Status: {response['status']}")
            if response.get('has_insight'):
                print(f"  💡 Insight found: {response['insight'][:100]}...")
            else:
                print(f"  No significant insight")
    
    # Clean up
    process.terminate()
    return results

def test_curator():
    """Test the thought curator"""
    print("\n\nTesting Thought Curator...")
    print("-" * 50)
    
    curator_path = Path(__file__).parent / "src" / "thought_curator.py"
    
    # Test curation on today's thoughts
    result = subprocess.run(
        [sys.executable, str(curator_path), "--test"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")

def main():
    """Run all tests"""
    print("Kind Contemplation System Test")
    print("=" * 50)
    
    # Test thought generation
    thoughts = test_generator()
    
    if thoughts:
        # Test contemplation processing
        results = test_contemplation(thoughts)
        
        # Test curator
        test_curator()
    
    print("\n\nTest complete!")
    print("\nTo start the full system, run:")
    print("  ./install_kind_pipeline.sh")

if __name__ == "__main__":
    main()
