#!/bin/bash
# Quick test of the subconscious system with simple, fast prompts

echo "🧪 Testing Subconscious System..."
echo ""

# Test with a simple one-sentence prompt
PROMPT="What is 2+2? Answer in exactly one sentence."
echo "Sending test thought: $PROMPT"

cd /Users/bard/Code/contemplation-loop
THOUGHT_ID=$(uv run python src/subconscious_client.py think problem "$PROMPT" --priority high | grep -o '[a-f0-9]\{16\}')

echo "Thought ID: $THOUGHT_ID"
echo ""
echo "Waiting for processing..."

# Check status every 2 seconds for up to 20 seconds
for i in {1..10}; do
    sleep 2
    STATUS=$(uv run python src/subconscious_client.py check $THOUGHT_ID 2>/dev/null | grep '"status"' | cut -d'"' -f4)
    echo -n "."
    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "✓ Completed!"
        echo ""
        echo "Result:"
        uv run python src/subconscious_client.py check $THOUGHT_ID | jq -r '.result.raw_response' 2>/dev/null || echo "No response found"
        exit 0
    fi
done

echo ""
echo "⏱️  Timeout - thought still processing"
echo "Check manually with: uv run python src/subconscious_client.py check $THOUGHT_ID"
