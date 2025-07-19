#!/bin/bash
# Quick command to view subconscious activity

cd /Users/bard/Code/contemplation-loop

echo "=== SUBCONSCIOUS ACTIVITY LOG ==="
echo ""

# Show last 30 lines
tail -n 30 logs/subconscious_activity.log

echo ""
echo "---"
echo "Commands:"
echo "  Follow live: cd /Users/bard/Code/contemplation-loop && ./view_activity.py -f"
echo "  Search: cd /Users/bard/Code/contemplation-loop && ./view_activity.py -s 'pattern'"
echo "  Stats: cd /Users/bard/Code/contemplation-loop && ./view_activity.py --stats"
