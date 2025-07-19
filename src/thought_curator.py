#!/usr/bin/env python3
"""
Thought Curator - Curates the best contemplation insights daily
Implements spiral thinking: collect many, distill to few
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import shutil

SCRATCH_PATH = Path("/Users/bard/Code/contemplation-loop/tmp/contemplation")
OBSIDIAN_PATH = Path.home() / "Documents/Obsidian/Brain/Contemplation"
CURATED_PATH = OBSIDIAN_PATH / "Curated"
ARCHIVE_PATH = OBSIDIAN_PATH / "Archive"


class ThoughtCurator:
    """Curates the best thoughts from contemplation scratch to Obsidian"""
    
    def __init__(self):
        # Ensure directories exist
        CURATED_PATH.mkdir(parents=True, exist_ok=True)
        ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)
        
    def get_scratch_thoughts(self, day_offset: int = 0) -> List[Dict[str, Any]]:
        """Get all thoughts from a specific day's scratch"""
        day_dir = SCRATCH_PATH / f"day_{day_offset}"
        thoughts = []
        
        if not day_dir.exists():
            return thoughts
            
        for file_path in day_dir.glob("thought_*.json"):
            try:
                with open(file_path, 'r') as f:
                    thought_data = json.load(f)
                    thought_data['file_path'] = str(file_path)
                    thoughts.append(thought_data)
            except:
                continue
                
        return thoughts
    
    def score_thought(self, thought: Dict[str, Any]) -> float:
        """Score a thought based on various criteria"""
        score = 0.0
        
        # Has insight? Major bonus
        if thought.get('insight'):
            score += 5.0
            
            # Longer insights often more valuable
            insight_length = len(thought['insight'])
            if insight_length > 200:
                score += 2.0
            elif insight_length > 100:
                score += 1.0
        
        # Type scoring - patterns and connections valued highly
        thought_type = thought.get('type', 'general')
        if thought_type == 'pattern':
            score += 2.0
        elif thought_type == 'connection':
            score += 1.5
        elif thought_type == 'question':
            score += 1.0
            
        # Response quality
        response = thought.get('response', '')
        if len(response) > 50:
            score += 0.5
            
        # Look for key insight words
        insight_indicators = ['realize', 'notice', 'pattern', 'connect', 
                            'interesting', 'fascinating', 'elegant', 'beautiful']
        response_lower = response.lower()
        for word in insight_indicators:
            if word in response_lower:
                score += 0.3
                
        return score
    
    def curate_daily_thoughts(self, top_n: int = 3, day_offset: int = 0) -> List[Dict[str, Any]]:
        """Select the top N thoughts from a day"""
        thoughts = self.get_scratch_thoughts(day_offset)
        
        if not thoughts:
            return []
            
        # Score and sort thoughts
        scored_thoughts = []
        for thought in thoughts:
            score = self.score_thought(thought)
            thought['curation_score'] = score
            scored_thoughts.append(thought)
            
        # Sort by score descending
        scored_thoughts.sort(key=lambda x: x['curation_score'], reverse=True)
        
        # Return top N
        return scored_thoughts[:top_n]
    
    def create_curated_note(self, thoughts: List[Dict[str, Any]], date: datetime) -> str:
        """Create a beautifully formatted curated note"""
        date_str = date.strftime("%Y-%m-%d")
        
        content = f"""# Curated Contemplations - {date_str}

*These are the most insightful thoughts from today's contemplation loop.*

---

"""
        
        for i, thought in enumerate(thoughts, 1):
            thought_type = thought.get('type', 'general').title()
            insight = thought.get('insight', thought.get('response', 'No insight recorded'))
            original = thought.get('input', '')
            score = thought.get('curation_score', 0)
            
            content += f"""## {i}. {thought_type} Insight

**Original thought:** {original}

**Insight:**
{insight}

*Score: {score:.1f}*

---

"""
        
        # Add metadata
        content += f"""
## Metadata

- Total thoughts processed: {len(thoughts)}
- Curation date: {datetime.now().strftime("%Y-%m-%d %H:%M")}
- Day offset: {day_offset}

#contemplation #curated #insights
"""
        
        return content
    
    def save_curated_note(self, thoughts: List[Dict[str, Any]], date: datetime):
        """Save curated thoughts to Obsidian"""
        if not thoughts:
            return None
            
        date_str = date.strftime("%Y-%m-%d")
        content = self.create_curated_note(thoughts, date)
        
        # Save to curated folder
        filename = f"curated_{date_str}.md"
        file_path = CURATED_PATH / filename
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        return file_path
    
    def archive_scratch_thoughts(self, day_offset: int = 1):
        """Archive yesterday's scratch thoughts"""
        day_dir = SCRATCH_PATH / f"day_{day_offset}"
        if not day_dir.exists():
            return
            
        # Create archive directory for this day
        date = datetime.now() - timedelta(days=day_offset)
        date_str = date.strftime("%Y-%m-%d")
        archive_day_dir = ARCHIVE_PATH / f"scratch_{date_str}"
        archive_day_dir.mkdir(exist_ok=True)
        
        # Move all thought files
        for file_path in day_dir.glob("thought_*.json"):
            shutil.move(str(file_path), str(archive_day_dir / file_path.name))
            
        # Remove empty directory
        try:
            day_dir.rmdir()
        except:
            pass
    
    def create_weekly_summary(self):
        """Create a weekly summary of curated thoughts"""
        weekly_thoughts = []
        
        # Collect last 7 days of curated thoughts
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            curated_file = CURATED_PATH / f"curated_{date_str}.md"
            
            if curated_file.exists():
                weekly_thoughts.append({
                    'date': date_str,
                    'file': curated_file
                })
        
        if not weekly_thoughts:
            return
            
        # Create weekly summary
        week_end = datetime.now()
        week_start = week_end - timedelta(days=6)
        
        content = f"""# Weekly Contemplation Summary

*Week of {week_start.strftime("%Y-%m-%d")} to {week_end.strftime("%Y-%m-%d")}*

---

## This Week's Curated Insights

"""
        
        for entry in weekly_thoughts:
            content += f"- [[curated_{entry['date']}|{entry['date']}]]\n"
            
        content += f"""

---

*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}*

#contemplation #weekly #summary
"""
        
        # Save weekly summary
        filename = f"weekly_{week_end.strftime('%Y-%m-%d')}.md"
        with open(CURATED_PATH / filename, 'w') as f:
            f.write(content)
    
    def run_daily_curation(self):
        """Run the daily curation process"""
        print("Starting daily thought curation...")
        
        # Curate yesterday's thoughts (day_offset=1)
        yesterday = datetime.now() - timedelta(days=1)
        top_thoughts = self.curate_daily_thoughts(top_n=3, day_offset=1)
        
        if top_thoughts:
            # Save curated note
            note_path = self.save_curated_note(top_thoughts, yesterday)
            print(f"Saved curated thoughts to: {note_path}")
            
            # Archive the scratch thoughts
            self.archive_scratch_thoughts(day_offset=1)
            print("Archived scratch thoughts")
        else:
            print("No thoughts found to curate")
        
        # Create weekly summary on Sundays
        if datetime.now().weekday() == 6:  # Sunday
            self.create_weekly_summary()
            print("Created weekly summary")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Curate contemplation thoughts")
    parser.add_argument("--daily", action="store_true", 
                      help="Run daily curation process")
    parser.add_argument("--test", action="store_true",
                      help="Test curation on today's thoughts")
    parser.add_argument("--weekly", action="store_true",
                      help="Create weekly summary")
    
    args = parser.parse_args()
    
    curator = ThoughtCurator()
    
    if args.daily:
        curator.run_daily_curation()
    elif args.test:
        # Test on today's thoughts
        thoughts = curator.curate_daily_thoughts(top_n=3, day_offset=0)
        if thoughts:
            print(f"Found {len(thoughts)} top thoughts:")
            for i, thought in enumerate(thoughts, 1):
                print(f"{i}. Score: {thought['curation_score']:.1f} - {thought.get('type')}")
                print(f"   {thought.get('insight', 'No insight')[:100]}...")
        else:
            print("No thoughts found for today")
    elif args.weekly:
        curator.create_weekly_summary()
        print("Created weekly summary")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
