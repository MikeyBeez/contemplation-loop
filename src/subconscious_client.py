#!/usr/bin/env python3
"""
Subconscious Client - Interface for Claude to interact with the subconscious
"""
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import sqlite3
import hashlib
from datetime import datetime

# Import the DB class
sys.path.append(str(Path(__file__).parent))
from subconscious import SubconsciousDB, ThoughtPriority

class SubconsciousClient:
    """Client for interacting with the subconscious"""
    
    def __init__(self):
        self.db = SubconsciousDB(Path.home() / ".subconscious" / "thoughts.db")
    
    def think_about(self, thought_type: str, content: str, 
                    context: Dict[str, Any] = None,
                    priority: str = "normal") -> str:
        """Send a thought to the subconscious"""
        priority_map = {
            "background": ThoughtPriority.BACKGROUND.value,
            "normal": ThoughtPriority.NORMAL.value,
            "high": ThoughtPriority.HIGH.value,
            "urgent": ThoughtPriority.URGENT.value
        }
        
        thought_id = hashlib.sha256(
            f"{thought_type}:{content}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Create thought record
        with self.db.conn:
            self.db.conn.execute("""
                INSERT INTO thoughts (
                    id, type, content, context, priority, status, created_at
                ) VALUES (?, ?, ?, ?, ?, 'queued', ?)
            """, (
                thought_id, thought_type, content,
                json.dumps(context or {}),
                priority_map.get(priority, ThoughtPriority.NORMAL.value),
                time.time()
            ))
        
        return thought_id
    
    def check_thought(self, thought_id: str) -> Dict[str, Any]:
        """Check the status of a thought"""
        thought = self.db.get_thought(thought_id)
        if thought:
            return {
                'id': thought.id,
                'type': thought.type,
                'status': thought.status,
                'created_at': datetime.fromtimestamp(thought.created_at).isoformat(),
                'completed_at': datetime.fromtimestamp(thought.completed_at).isoformat() if thought.completed_at else None,
                'result': thought.result
            }
        return {'error': 'Thought not found'}
    
    def get_insights(self, hours: int = 24, limit: int = 10) -> List[Dict]:
        """Get recent insights from the subconscious"""
        return self.db.get_recent_insights(hours=hours, limit=limit)
    
    def get_completed_thoughts(self, thought_type: str = None, limit: int = 10) -> List[Dict]:
        """Get recently completed thoughts"""
        query = """
            SELECT * FROM thoughts
            WHERE status = 'completed'
        """
        params = []
        
        if thought_type:
            query += " AND type = ?"
            params.append(thought_type)
            
        query += " ORDER BY completed_at DESC LIMIT ?"
        params.append(limit)
        
        with self.db.conn:
            rows = self.db.conn.execute(query, params).fetchall()
            
        results = []
        for row in rows:
            results.append({
                'id': row['id'],
                'type': row['type'],
                'content': row['content'][:100] + '...' if len(row['content']) > 100 else row['content'],
                'completed_at': datetime.fromtimestamp(row['completed_at']).isoformat(),
                'result_summary': self._summarize_result(json.loads(row['result']) if row['result'] else {})
            })
            
        return results
    
    def _summarize_result(self, result: Dict) -> str:
        """Create a brief summary of a result"""
        if not result:
            return "No result"
            
        # Try to extract key points
        summary_parts = []
        
        if 'insights' in result:
            summary_parts.append(f"{len(result['insights'])} insights")
            
        if 'connections' in result:
            summary_parts.append(f"{len(result['connections'])} connections")
            
        for key in ['recommendation', 'conclusion', 'key finding']:
            if key in result:
                summary_parts.append(result[key][:50] + '...')
                break
                
        return "; ".join(summary_parts) if summary_parts else "Processed"
    
    def find_related(self, query: str, limit: int = 5) -> List[Dict]:
        """Find thoughts related to a query"""
        # Simple keyword search for now
        with self.db.conn:
            rows = self.db.conn.execute("""
                SELECT * FROM thoughts
                WHERE status = 'completed'
                AND (content LIKE ? OR result LIKE ?)
                ORDER BY completed_at DESC
                LIMIT ?
            """, (f'%{query}%', f'%{query}%', limit)).fetchall()
            
        results = []
        for row in rows:
            results.append({
                'id': row['id'],
                'type': row['type'],
                'content': row['content'][:100] + '...',
                'relevance': 'keyword match'  # Could be more sophisticated
            })
            
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get subconscious system status"""
        with self.db.conn:
            stats = self.db.conn.execute("""
                SELECT 
                    status,
                    COUNT(*) as count
                FROM thoughts
                GROUP BY status
            """).fetchall()
            
            total_thoughts = self.db.conn.execute(
                "SELECT COUNT(*) as count FROM thoughts"
            ).fetchone()['count']
            
            total_insights = self.db.conn.execute(
                "SELECT COUNT(*) as count FROM insights"
            ).fetchone()['count']
        
        return {
            'total_thoughts': total_thoughts,
            'total_insights': total_insights,
            'by_status': {row['status']: row['count'] for row in stats},
            'db_path': str(Path.home() / ".subconscious" / "thoughts.db")
        }


def main():
    """CLI interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Subconscious client")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Think command
    think_parser = subparsers.add_parser('think', help='Send a thought')
    think_parser.add_argument('type', choices=['problem', 'design', 'analysis', 'connection', 'exploration'])
    think_parser.add_argument('content', help='Thought content')
    think_parser.add_argument('--priority', choices=['background', 'normal', 'high', 'urgent'], default='normal')
    think_parser.add_argument('--context', help='JSON context', default='{}')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check thought status')
    check_parser.add_argument('thought_id', help='Thought ID to check')
    
    # Insights command
    insights_parser = subparsers.add_parser('insights', help='Get recent insights')
    insights_parser.add_argument('--hours', type=int, default=24)
    insights_parser.add_argument('--limit', type=int, default=10)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List completed thoughts')
    list_parser.add_argument('--type', help='Filter by type')
    list_parser.add_argument('--limit', type=int, default=10)
    
    # Find command
    find_parser = subparsers.add_parser('find', help='Find related thoughts')
    find_parser.add_argument('query', help='Search query')
    find_parser.add_argument('--limit', type=int, default=5)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get system status')
    
    args = parser.parse_args()
    
    client = SubconsciousClient()
    
    if args.command == 'think':
        context = json.loads(args.context)
        thought_id = client.think_about(args.type, args.content, context, args.priority)
        print(f"Thought delegated: {thought_id}")
        
    elif args.command == 'check':
        result = client.check_thought(args.thought_id)
        print(json.dumps(result, indent=2))
        
    elif args.command == 'insights':
        insights = client.get_insights(args.hours, args.limit)
        for insight in insights:
            print(f"\n{insight['thought_id']}: {insight['insight']}")
            print(f"  Significance: {insight['significance']:.2f}")
            
    elif args.command == 'list':
        thoughts = client.get_completed_thoughts(args.type, args.limit)
        for thought in thoughts:
            print(f"\n{thought['id']} ({thought['type']})")
            print(f"  {thought['content']}")
            print(f"  Completed: {thought['completed_at']}")
            print(f"  Result: {thought['result_summary']}")
            
    elif args.command == 'find':
        related = client.find_related(args.query, args.limit)
        for thought in related:
            print(f"\n{thought['id']} ({thought['type']})")
            print(f"  {thought['content']}")
            print(f"  Relevance: {thought['relevance']}")
            
    elif args.command == 'status':
        status = client.get_status()
        print(json.dumps(status, indent=2))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
