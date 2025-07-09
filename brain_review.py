#!/usr/bin/env python3
"""
Brain integration for reviewing contemplation notes
This script is called by Brain to check and process contemplation insights
"""
import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from note_reviewer import NoteReviewer


def check_insights():
    """Check for new insights and return summary"""
    reviewer = NoteReviewer()
    pending = reviewer.get_pending_insights()
    
    summary = {
        'pending_count': len(pending),
        'high_significance': [],
        'by_type': {}
    }
    
    # Count by type
    for insight in pending:
        insight_type = insight.get('type', 'general')
        if insight_type not in summary['by_type']:
            summary['by_type'][insight_type] = 0
        summary['by_type'][insight_type] += 1
        
        # Collect high significance ones
        if insight['significance'] >= 7:
            summary['high_significance'].append({
                'insight': insight['insight'][:150] + '...',
                'significance': insight['significance'],
                'type': insight_type
            })
    
    return summary


def auto_review(threshold=8):
    """Automatically review and promote significant insights"""
    reviewer = NoteReviewer()
    results = reviewer.review_notes(auto_promote_threshold=threshold)
    return results


def main():
    """Main entry point for Brain integration"""
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'No command specified',
            'usage': 'brain_review.py [check|review|cleanup]'
        }))
        return
    
    command = sys.argv[1]
    
    try:
        if command == 'check':
            # Check for pending insights
            summary = check_insights()
            print(json.dumps(summary, indent=2))
            
        elif command == 'review':
            # Auto-review with optional threshold
            threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 8
            results = auto_review(threshold)
            print(json.dumps(results, indent=2))
            
        elif command == 'cleanup':
            # Cleanup old notes
            reviewer = NoteReviewer()
            archived = reviewer.cleanup_old_notes()
            print(json.dumps({
                'archived': archived,
                'status': 'success'
            }))
            
        else:
            print(json.dumps({
                'error': f'Unknown command: {command}'
            }))
            
    except Exception as e:
        print(json.dumps({
            'error': str(e),
            'command': command
        }))


if __name__ == "__main__":
    main()
