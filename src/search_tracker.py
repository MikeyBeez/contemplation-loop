#!/usr/bin/env python3
"""
Search Usage Tracker
Tracks and manages search usage across Brave and DuckDuckGo
"""
import json
from datetime import datetime, timezone
from typing import Dict, Literal, Tuple


class SearchUsageTracker:
    """Track search usage to optimize between Brave and DuckDuckGo"""
    
    # Brave has 100/hour limit according to code
    BRAVE_HOURLY_LIMIT = 100
    BRAVE_CONSERVATIVE_LIMIT = 50  # Leave buffer for important searches
    
    def __init__(self, brain_state_get, brain_state_set):
        self.state_get = brain_state_get
        self.state_set = brain_state_set
        self._ensure_tracking_exists()
    
    def _ensure_tracking_exists(self):
        """Ensure tracking state exists"""
        try:
            self.state_get("system", "search_usage_tracking")
        except:
            # Initialize if doesn't exist
            initial_state = {
                "brave_searches": {
                    "this_hour": 0,
                    "today": 0,
                    "last_reset": datetime.now(timezone.utc).isoformat()
                },
                "ddg_searches": {
                    "today": 0,
                    "total": 0
                },
                "history": []
            }
            self.state_set("system", "search_usage_tracking", initial_state)
    
    def should_use_brave(self, 
                        query: str, 
                        importance: Literal["critical", "normal", "low"] = "normal") -> Tuple[bool, str]:
        """
        Decide whether to use Brave or DuckDuckGo
        
        Returns: (use_brave, reason)
        """
        # Get current usage
        state = self.state_get("system", "search_usage_tracking")
        self._check_reset_needed(state)
        
        hourly_count = state["brave_searches"]["this_hour"]
        
        # Decision logic
        if importance == "critical" and hourly_count < 95:
            return True, "Critical query with Brave quota available"
        
        if importance == "low":
            return False, "Low priority - use DuckDuckGo"
        
        # For normal importance, check if it's a simple query
        simple_patterns = [
            "what is", "define", "meaning of", "capital of",
            "how many", "when was", "who is", "where is"
        ]
        
        query_lower = query.lower()
        if any(pattern in query_lower for pattern in simple_patterns):
            return False, "Simple factual query - use DuckDuckGo"
        
        # Check quota
        if hourly_count >= self.BRAVE_CONSERVATIVE_LIMIT:
            return False, f"Brave quota high ({hourly_count}/100) - preserving for critical searches"
        
        # For normal importance complex queries
        return True, "Complex query with available Brave quota"
    
    def record_search(self, 
                     search_type: Literal["brave", "ddg"], 
                     query: str,
                     was_sufficient: bool = True):
        """Record a search was performed"""
        state = self.state_get("system", "search_usage_tracking")
        self._check_reset_needed(state)
        
        # Update counts
        if search_type == "brave":
            state["brave_searches"]["this_hour"] += 1
            state["brave_searches"]["today"] += 1
        else:
            state["ddg_searches"]["today"] += 1
            state["ddg_searches"]["total"] += 1
        
        # Add to history
        state["history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": search_type,
            "query": query[:100],  # Truncate long queries
            "sufficient": was_sufficient
        })
        
        # Keep only last 100 history entries
        state["history"] = state["history"][-100:]
        
        # Save
        self.state_set("system", "search_usage_tracking", state)
    
    def _check_reset_needed(self, state: Dict):
        """Check if hourly/daily counters need reset"""
        last_reset = datetime.fromisoformat(state["brave_searches"]["last_reset"])
        now = datetime.now(timezone.utc)
        
        # Reset hourly
        if (now - last_reset).total_seconds() > 3600:
            state["brave_searches"]["this_hour"] = 0
            state["brave_searches"]["last_reset"] = now.isoformat()
        
        # Reset daily
        if last_reset.date() < now.date():
            state["brave_searches"]["today"] = 0
            state["ddg_searches"]["today"] = 0
    
    def get_usage_summary(self) -> Dict:
        """Get current usage summary"""
        state = self.state_get("system", "search_usage_tracking")
        self._check_reset_needed(state)
        
        return {
            "brave": {
                "hourly": f"{state['brave_searches']['this_hour']}/100",
                "today": state["brave_searches"]["today"]
            },
            "ddg": {
                "today": state["ddg_searches"]["today"],
                "total": state["ddg_searches"]["total"]
            },
            "recommendations": self._get_recommendations(state)
        }
    
    def _get_recommendations(self, state: Dict) -> list:
        """Get recommendations based on usage"""
        recs = []
        
        hourly = state["brave_searches"]["this_hour"]
        if hourly > 80:
            recs.append("Brave quota nearly exhausted - use DuckDuckGo for non-critical searches")
        elif hourly < 20:
            recs.append("Brave quota available - can use for quality searches")
        
        # Analyze history for patterns
        ddg_insufficient = sum(1 for h in state["history"][-20:] 
                              if h["type"] == "ddg" and not h.get("sufficient", True))
        
        if ddg_insufficient > 3:
            recs.append("Recent DuckDuckGo searches insufficient - consider using Brave for complex queries")
        
        return recs


# Integration function for contemplation loop
def smart_search(query: str, importance: str = "normal") -> Tuple[str, list]:
    """
    Smart search that chooses between Brave and DuckDuckGo
    Returns: (search_type_used, results)
    """
    # This would be integrated with actual Brain state access
    # For now, showing the pattern
    pass
