#!/usr/bin/env python3
"""
Test the contemplation loop
"""
import sys
import time
sys.path.insert(0, 'src')

from contemplation_bridge import ContemplationBridge


def main():
    print("Testing Contemplation Loop...")
    print("-" * 50)
    
    bridge = ContemplationBridge()
    
    # Start the loop
    print("Starting contemplation loop...")
    if not bridge.start():
        print("ERROR: Failed to start loop")
        return 1
    
    print("✓ Loop started successfully")
    
    # Test thoughts
    test_thoughts = [
        ("pattern", "Users repeatedly express anxiety about AI memory limits"),
        ("connection", "Context windows and human relationships both involve fear of forgetting"),
        ("question", "Why do technical limits trigger emotional responses?"),
        ("general", "The boundary between tool and companion blurs at the memory interface")
    ]
    
    print(f"\nSending {len(test_thoughts)} test thoughts...")
    
    for i, (thought_type, content) in enumerate(test_thoughts):
        print(f"\n{i+1}. Sending {thought_type}: {content[:60]}...")
        
        try:
            thought_id = bridge.send_thought(thought_type, content)
            print(f"   Sent with ID: {thought_id}")
            
            # Wait for response
            time.sleep(1)
            responses = bridge.get_responses(timeout=2.0)
            
            for response in responses:
                status = response.get('status', 'unknown')
                print(f"   Response status: {status}")
                
                if response.get('has_insight'):
                    print(f"   💡 Insight found: {response.get('insight', 'N/A')[:100]}")
                
                if response.get('error'):
                    print(f"   ❌ Error: {response['error']}")
                    
        except Exception as e:
            print(f"   ERROR: {e}")
    
    # Check final status
    print("\n" + "-" * 50)
    print("Final Status:")
    status = bridge.get_status()
    print(f"  Running: {status['running']}")
    print(f"  Process alive: {status['process_alive']}")
    print(f"  Recent responses: {status['recent_responses']}")
    
    if status['recent_errors']:
        print("\nRecent errors:")
        for error in status['recent_errors'][-3:]:
            print(f"  {error.strip()}")
    
    # Cleanup
    print("\nStopping loop...")
    bridge.stop()
    print("✓ Test complete")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
