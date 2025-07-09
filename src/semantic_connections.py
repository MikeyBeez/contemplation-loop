#!/usr/bin/env python3
"""
Semantic Connection System
Connects insights by meaning rather than time
"""
import json
from pathlib import Path
from typing import List, Dict, Tuple, Set
import re
import time
from collections import defaultdict


class SemanticConnector:
    """Find and maintain semantic connections between insights"""
    
    def __init__(self):
        self.connections_path = Path("/Users/bard/Code/contemplation-loop/data/semantic_connections.json")
        self.connections = self._load_connections()
        
    def _load_connections(self) -> Dict:
        """Load existing semantic connections"""
        if self.connections_path.exists():
            with open(self.connections_path, 'r') as f:
                return json.load(f)
        return {
            'nodes': {},  # insight_id -> content
            'edges': [],  # list of (id1, id2, similarity_score)
            'clusters': {}  # cluster_name -> [insight_ids]
        }
    
    def extract_concepts(self, text: str) -> Set[str]:
        """Extract key concepts from text"""
        # Simple concept extraction - could be enhanced with NLP
        text_lower = text.lower()
        
        # Key phrases that indicate important concepts
        concept_patterns = [
            r'pattern[s]?\s+(?:of|in)\s+(\w+)',
            r'connect(?:ion|s)?\s+between\s+(\w+)\s+and\s+(\w+)',
            r'(\w+)\s+(?:is|are)\s+like\s+(\w+)',
            r'concept\s+of\s+(\w+)',
            r'idea\s+(?:of|that)\s+(\w+)'
        ]
        
        concepts = set()
        
        # Extract based on patterns
        for pattern in concept_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    concepts.update(match)
                else:
                    concepts.add(match)
        
        # Extract significant nouns (simple heuristic)
        words = text_lower.split()
        for i, word in enumerate(words):
            if word in ['pattern', 'system', 'memory', 'context', 'insight', 
                       'connection', 'learning', 'behavior', 'thought']:
                concepts.add(word)
                # Also add the next word if it exists
                if i + 1 < len(words):
                    concepts.add(f"{word}_{words[i+1]}")
        
        return concepts
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        concepts1 = self.extract_concepts(text1)
        concepts2 = self.extract_concepts(text2)
        
        if not concepts1 or not concepts2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(concepts1.intersection(concepts2))
        union = len(concepts1.union(concepts2))
        
        return intersection / union if union > 0 else 0.0
    
    def add_insight(self, insight_id: str, content: str):
        """Add new insight and find connections"""
        # Store the insight
        self.connections['nodes'][insight_id] = {
            'content': content,
            'concepts': list(self.extract_concepts(content)),
            'added_at': time.time()
        }
        
        # Find connections to existing insights
        new_edges = []
        for existing_id, existing_data in self.connections['nodes'].items():
            if existing_id != insight_id:
                similarity = self.calculate_similarity(
                    content, 
                    existing_data['content']
                )
                
                if similarity > 0.3:  # Threshold for connection
                    new_edges.append((insight_id, existing_id, similarity))
        
        # Add edges
        self.connections['edges'].extend(new_edges)
        
        # Update clusters
        self._update_clusters()
        
        # Save
        self._save_connections()
        
        return new_edges
    
    def find_related(self, insight_id: str, max_results: int = 5) -> List[Tuple[str, float]]:
        """Find insights related to a given insight"""
        related = []
        
        for edge in self.connections['edges']:
            if insight_id in edge[:2]:
                other_id = edge[1] if edge[0] == insight_id else edge[0]
                similarity = edge[2]
                related.append((other_id, similarity))
        
        # Sort by similarity
        related.sort(key=lambda x: x[1], reverse=True)
        
        return related[:max_results]
    
    def _update_clusters(self):
        """Update concept clusters using simple community detection"""
        # Group insights by shared concepts
        concept_groups = defaultdict(set)
        
        for insight_id, data in self.connections['nodes'].items():
            for concept in data.get('concepts', []):
                concept_groups[concept].add(insight_id)
        
        # Create clusters from concept groups
        self.connections['clusters'] = {}
        for concept, insight_ids in concept_groups.items():
            if len(insight_ids) > 1:  # Only create cluster if multiple insights
                self.connections['clusters'][concept] = list(insight_ids)
    
    def get_cluster_summary(self) -> Dict[str, int]:
        """Get summary of current clusters"""
        return {
            cluster: len(insights) 
            for cluster, insights in self.connections['clusters'].items()
        }
    
    def _save_connections(self):
        """Save connections to disk"""
        self.connections_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.connections_path, 'w') as f:
            json.dump(self.connections, f, indent=2)


# Integration with note reviewer
def connect_new_insight(insight_id: str, content: str) -> List[str]:
    """Connect new insight and return related insight IDs"""
    connector = SemanticConnector()
    edges = connector.add_insight(insight_id, content)
    
    related_ids = [edge[1] for edge in edges if edge[2] > 0.5]  # High similarity
    return related_ids
