#!/usr/bin/env python3
"""
Simple direct test of the contemplation loop with real output
"""
import sys
import os
sys.path.insert(0, 'src')

from contemplation_bridge import ContemplationBridge
import time
import json


def main():
    print("Direct Contemplation Loop Test")
    print("=" * 50)
    
    bridge = ContemplationBridge()
    
    # Start the loop
    print("Starting contemplation loop...")
    if not bridge.start():
        print("ERROR: Failed to start loop")
        return 1
    
    print("✓ Loop started")
    time.sleep(1)
    
    # Send a single test thought
    print("\nSending test thought...")
    thought_id = bridge.send_thought(
        thought_type="pattern",
        content="Users often ask 'will you remember me?' - why this specific phrasing?"
    )
    print(f"Sent thought ID: {thought_id}")
    
    # Wait longer for Ollama response
    print("\nWaiting for Ollama to process (this may take 10-15 seconds)...")
    for i in range(20):  # Wait up to 20 seconds
        time.sleep(1)
        responses = bridge.get_responses(timeout=0.5)
        
        if responses:
            print(f"\nGot {len(responses)} response(s):")
            for resp in responses:
                print(json.dumps(resp, indent=2))
            break
        else:
            print(".", end="", flush=True)
    
    # Check for files
    print("\n\nChecking for saved thoughts...")
    thought_dir = "tmp/contemplation/day_0"
    if os.path.exists(thought_dir):
        files = os.listdir(thought_dir)
        print(f"Found {len(files)} thought file(s)")
        
        for f in files[:2]:  # Show first 2
            path = os.path.join(thought_dir, f)
            with open(path, 'r') as file:
                data = json.load(file)
                print(f"\nFile: {f}")
                print(f"Response: {data.get('response', 'No response')[:200]}...")
                if data.get('insight'):
                    print(f"💡 Insight: {data['insight']}")
    
    # Cleanup
    print("\nStopping loop...")
    bridge.stop()
    print("✓ Test complete")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
