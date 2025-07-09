#!/usr/bin/env python3
"""
Note Review System - Manages contemplation loop notes
Reviews scratch notes, promotes significant ones, archives processed ones
"""
import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any


class NoteReviewer:
    """Reviews and manages contemplation notes"""
    
    def __init__(self):
        self.scratch_dir = Path("/Users/bard/Code/contemplation-loop/tmp/contemplation")
        self.obsidian_dir = Path.home() / "Documents/Obsidian/Brain/Contemplation"
        self.archive_dir = Path("/Users/bard/Code/contemplation-loop/tmp/archive")
        self.processed_dir = Path("/Users/bard/Code/contemplation-loop/tmp/processed")
        
        # Ensure directories exist
        self.obsidian_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def review_notes(self, auto_promote_threshold: int = 8) -> Dict[str, Any]:
        """Review all unprocessed notes"""
        results = {
            'reviewed': 0,
            'promoted': 0,
            'archived': 0,
            'insights': []
        }
        
        # Check each day directory
        for day_dir in self.scratch_dir.glob("day_*"):
            if not day_dir.is_dir():
                continue
                
            for note_file in day_dir.glob("thought_*.json"):
                try:
                    with open(note_file, 'r') as f:
                        note = json.load(f)
                    
                    results['reviewed'] += 1
                    
                    # Check if already processed
                    if self._is_processed(note_file):
                        continue
                    
                    # Evaluate note
                    if note.get('insight'):
                        significance = self._calculate_significance(note)
                        
                        if significance >= auto_promote_threshold:
                            # Promote to Obsidian
                            self._promote_to_obsidian(note, note_file)
                            results['promoted'] += 1
                            results['insights'].append({
                                'file': note_file.name,
                                'insight': note['insight'][:100] + '...',
                                'significance': significance
                            })
                        
                    # Mark as processed
                    self._mark_processed(note_file)
                    
                except Exception as e:
                    print(f"Error processing {note_file}: {e}")
        
        return results
    
    def _calculate_significance(self, note: Dict[str, Any]) -> int:
        """Calculate significance score (1-10)"""
        score = 5  # Base score
        
        # Length indicates depth
        insight = note.get('insight', '')
        if len(insight) > 200:
            score += 1
        if len(insight) > 400:
            score += 1
            
        # Type weights
        if note.get('type') == 'pattern':
            score += 1
        elif note.get('type') == 'connection':
            score += 2
            
        # Keywords that suggest importance
        important_keywords = ['realize', 'understand', 'connect', 'pattern', 
                            'significant', 'important', 'notice']
        insight_lower = insight.lower()
        keyword_count = sum(1 for kw in important_keywords if kw in insight_lower)
        score += min(keyword_count, 2)
        
        return min(score, 10)
    
    def _promote_to_obsidian(self, note: Dict[str, Any], source_file: Path):
        """Promote insight to Obsidian vault"""
        timestamp = datetime.fromtimestamp(note.get('timestamp', 0))
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M")
        
        # Create note content
        content = f"""# Contemplation Insight: {note.get('type', 'general').title()}
*{date_str} {time_str}*

## Insight
{note.get('insight', 'No insight recorded')}

## Context
**Original thought**: {note.get('input', 'N/A')}

**Full response**: 
{note.get('response', 'No response recorded')}

---
*Source: {source_file.name}*
*Significance: {self._calculate_significance(note)}/10*
*Auto-promoted from contemplation loop*

#contemplation #{note.get('type', 'general')}
"""
        
        # Save to Obsidian
        filename = f"insight_{date_str}_{source_file.stem}.md"
        obsidian_path = self.obsidian_dir / filename
        
        with open(obsidian_path, 'w') as f:
            f.write(content)
        
        print(f"✓ Promoted to Obsidian: {filename}")
    
    def _is_processed(self, note_file: Path) -> bool:
        """Check if note has been processed"""
        marker_file = self.processed_dir / f"{note_file.name}.processed"
        return marker_file.exists()
    
    def _mark_processed(self, note_file: Path):
        """Mark note as processed"""
        marker_file = self.processed_dir / f"{note_file.name}.processed"
        marker_file.touch()
    
    def cleanup_old_notes(self, days_to_keep: int = 4):
        """Archive notes older than N days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        archived_count = 0
        
        for day_dir in self.scratch_dir.glob("day_*"):
            if not day_dir.is_dir():
                continue
                
            # Check age of notes in directory
            for note_file in day_dir.glob("thought_*.json"):
                if note_file.stat().st_mtime < cutoff_date.timestamp():
                    # Archive the note
                    archive_path = self.archive_dir / note_file.name
                    shutil.move(str(note_file), str(archive_path))
                    archived_count += 1
        
        # Clean up empty directories
        for day_dir in self.scratch_dir.glob("day_*"):
            if day_dir.is_dir() and not list(day_dir.iterdir()):
                day_dir.rmdir()
        
        return archived_count
    
    def get_pending_insights(self) -> List[Dict[str, Any]]:
        """Get insights that haven't been reviewed yet"""
        pending = []
        
        for day_dir in self.scratch_dir.glob("day_*"):
            for note_file in day_dir.glob("thought_*.json"):
                if self._is_processed(note_file):
                    continue
                    
                try:
                    with open(note_file, 'r') as f:
                        note = json.load(f)
                    
                    if note.get('insight'):
                        pending.append({
                            'file': note_file.name,
                            'type': note.get('type'),
                            'insight': note.get('insight'),
                            'significance': self._calculate_significance(note),
                            'timestamp': note.get('timestamp')
                        })
                except:
                    pass
        
        return sorted(pending, key=lambda x: x['significance'], reverse=True)


def main():
    """Review notes when run directly"""
    reviewer = NoteReviewer()
    
    print("Contemplation Note Review")
    print("=" * 50)
    
    # Get pending insights
    pending = reviewer.get_pending_insights()
    print(f"\nFound {len(pending)} pending insights:")
    
    for insight in pending[:5]:  # Show top 5
        print(f"\n- {insight['type']}: {insight['insight'][:80]}...")
        print(f"  Significance: {insight['significance']}/10")
    
    if pending:
        response = input("\nAuto-promote insights with significance >= 8? (y/n): ")
        if response.lower() == 'y':
            results = reviewer.review_notes(auto_promote_threshold=8)
            print(f"\nReviewed: {results['reviewed']} notes")
            print(f"Promoted: {results['promoted']} to Obsidian")
    
    # Cleanup old notes
    archived = reviewer.cleanup_old_notes()
    if archived:
        print(f"\nArchived {archived} old notes")


if __name__ == "__main__":
    main()
