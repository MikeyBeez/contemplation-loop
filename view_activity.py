#!/usr/bin/env python3
"""
View the subconscious activity log
"""
import sys
from pathlib import Path
from datetime import datetime
import argparse

LOG_FILE = Path(__file__).parent / "logs" / "subconscious_activity.log"

def view_log(lines=50, follow=False):
    """View the activity log"""
    if not LOG_FILE.exists():
        print("No activity log found. The subconscious may not have started yet.")
        return
    
    if follow:
        # Follow mode - like tail -f
        import time
        last_size = 0
        print(f"Following {LOG_FILE} (Ctrl+C to stop)...\n")
        
        try:
            while True:
                current_size = LOG_FILE.stat().st_size
                if current_size != last_size:
                    with open(LOG_FILE, 'r') as f:
                        f.seek(last_size)
                        new_content = f.read()
                        if new_content:
                            print(new_content, end='')
                    last_size = current_size
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nStopped following log.")
    else:
        # Just show last N lines
        with open(LOG_FILE, 'r') as f:
            all_lines = f.readlines()
        
        if not all_lines:
            print("Activity log is empty.")
            return
        
        # Get last N lines
        display_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        print(f"=== Subconscious Activity Log (last {len(display_lines)} entries) ===\n")
        for line in display_lines:
            print(line.rstrip())
        
        print(f"\nTotal entries: {len(all_lines)}")
        print(f"Log file: {LOG_FILE}")

def search_log(pattern):
    """Search for a pattern in the log"""
    if not LOG_FILE.exists():
        print("No activity log found.")
        return
    
    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()
    
    matches = []
    for i, line in enumerate(lines):
        if pattern.lower() in line.lower():
            matches.append((i, line.rstrip()))
    
    if matches:
        print(f"Found {len(matches)} matches for '{pattern}':\n")
        for i, line in matches:
            print(f"{i+1}: {line}")
    else:
        print(f"No matches found for '{pattern}'")

def stats_log():
    """Show statistics about the log"""
    if not LOG_FILE.exists():
        print("No activity log found.")
        return
    
    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()
    
    # Count event types
    event_counts = {}
    thought_ids = set()
    
    for line in lines:
        if '[' in line and ']' in line:
            # Extract event type
            start = line.find('[', line.find(']') + 1) + 1
            end = line.find(']', start)
            if start > 0 and end > start:
                event_type = line[start:end]
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # Extract thought ID if present
            if '[ID:' in line:
                id_start = line.find('[ID:') + 4
                id_end = line.find(']', id_start)
                if id_end > id_start:
                    thought_id = line[id_start:id_end].strip()
                    thought_ids.add(thought_id)
    
    print("=== Subconscious Activity Statistics ===\n")
    print(f"Total log entries: {len(lines)}")
    print(f"Unique thoughts processed: {len(thought_ids)}")
    print("\nEvent counts:")
    for event, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {event}: {count}")

def main():
    parser = argparse.ArgumentParser(description="View subconscious activity log")
    parser.add_argument('-n', '--lines', type=int, default=50,
                      help='Number of lines to show (default: 50)')
    parser.add_argument('-f', '--follow', action='store_true',
                      help='Follow the log in real-time (like tail -f)')
    parser.add_argument('-s', '--search', type=str,
                      help='Search for a pattern in the log')
    parser.add_argument('--stats', action='store_true',
                      help='Show statistics about the log')
    
    args = parser.parse_args()
    
    if args.search:
        search_log(args.search)
    elif args.stats:
        stats_log()
    else:
        view_log(args.lines, args.follow)

if __name__ == "__main__":
    main()
