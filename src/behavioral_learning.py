#!/usr/bin/env python3
"""
Behavioral Learning for Note Review
Tracks which insights are actually used and adjusts scoring accordingly
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime


class BehavioralLearning:
    """Learn from actual usage patterns of promoted insights"""
    
    def __init__(self):
        self.usage_db_path = Path("/Users/bard/Code/contemplation-loop/data/usage_tracking.json")
        self.incubation_path = Path("/Users/bard/Code/contemplation-loop/tmp/incubation")
        self.usage_data = self._load_usage_data()
        
        # Create incubation directory
        self.incubation_path.mkdir(parents=True, exist_ok=True)
    
    def _load_usage_data(self) -> Dict:
        """Load usage tracking data"""
        if self.usage_db_path.exists():
            with open(self.usage_db_path, 'r') as f:
                return json.load(f)
        return {
            'insights': {},
            'patterns': {
                'keywords_that_matter': {},
                'types_that_succeed': {},
                'length_correlation': []
            }
        }
    
    def track_usage(self, insight_id: str, usage_type: str):
        """Track when an insight is actually used"""
        if insight_id not in self.usage_data['insights']:
            self.usage_data['insights'][insight_id] = {
                'promoted_at': time.time(),
                'usage_count': 0,
                'usage_types': []
            }
        
        self.usage_data['insights'][insight_id]['usage_count'] += 1
        self.usage_data['insights'][insight_id]['usage_types'].append({
            'type': usage_type,  # 'referenced', 'quoted', 'built_upon'
            'timestamp': time.time()
        })
        
        self._save_usage_data()
    
    def calculate_adjusted_significance(self, note: Dict, base_score: int) -> int:
        """Adjust significance based on learned patterns"""
        adjusted = base_score
        
        # Boost for keywords that historically matter
        for keyword, success_rate in self.usage_data['patterns']['keywords_that_matter'].items():
            if keyword.lower() in note.get('insight', '').lower():
                adjusted += min(2, int(success_rate * 3))
        
        # Adjust for type patterns
        note_type = note.get('type', 'general')
        if note_type in self.usage_data['patterns']['types_that_succeed']:
            success_rate = self.usage_data['patterns']['types_that_succeed'][note_type]
            adjusted += min(1, int(success_rate * 2))
        
        return min(10, adjusted)
    
    def learn_patterns(self):
        """Analyze usage data to learn patterns"""
        insights = self.usage_data['insights']
        
        # Learn which keywords correlate with usage
        keyword_usage = {}
        for insight_id, data in insights.items():
            if data['usage_count'] > 0:
                # Extract keywords from successful insights
                # (In real implementation, would load the actual insight content)
                pass
        
        # Update patterns
        self._save_usage_data()
    
    def _save_usage_data(self):
        """Save usage data"""
        self.usage_db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.usage_db_path, 'w') as f:
            json.dump(self.usage_data, f, indent=2)


class IncubationManager:
    """Manage insights in incubation (scores 6-7)"""
    
    def __init__(self):
        self.incubation_path = Path("/Users/bard/Code/contemplation-loop/tmp/incubation")
        self.incubation_path.mkdir(parents=True, exist_ok=True)
    
    def add_to_incubation(self, note: Dict, source_file: Path):
        """Add medium-significance note to incubation"""
        incubation_file = self.incubation_path / f"incubating_{source_file.name}"
        
        incubation_data = {
            'original_note': note,
            'incubated_at': time.time(),
            'source_file': str(source_file),
            'review_count': 0,
            'related_thoughts': []
        }
        
        with open(incubation_file, 'w') as f:
            json.dump(incubation_data, f, indent=2)
    
    def review_incubating(self) -> List[Dict]:
        """Review incubating insights for promotion"""
        ready_for_promotion = []
        
        for incubation_file in self.incubation_path.glob("incubating_*.json"):
            with open(incubation_file, 'r') as f:
                data = json.load(f)
            
            # Check if it's been incubating for at least 24 hours
            if time.time() - data['incubated_at'] > 86400:
                data['review_count'] += 1
                
                # Check if related new thoughts have emerged
                # (Would implement semantic similarity checking here)
                
                ready_for_promotion.append(data)
        
        return ready_for_promotion
