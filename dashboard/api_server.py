#!/usr/bin/env python3
"""
Dashboard API Server for Subconscious System
Provides real-time data to the web dashboard
"""
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import from src package
try:
    from src.subconscious import SubconsciousDB
except ImportError:
    # Fallback if running from different directory
    sys.path.append(str(Path(__file__).parent.parent / 'src'))
    from subconscious import SubconsciousDB

app = Flask(__name__)
CORS(app)

# Database connection
db = SubconsciousDB(Path.home() / ".subconscious" / "thoughts.db")

@app.route('/')
def index():
    """Serve the dashboard"""
    dashboard_path = Path(__file__).parent / "index.html"
    with open(dashboard_path, 'r') as f:
        return f.read()

@app.route('/api/status')
def get_status():
    """Get overall system status"""
    with db.conn:
        # Get counts by status
        status_counts = db.conn.execute("""
            SELECT status, COUNT(*) as count
            FROM thoughts
            GROUP BY status
        """).fetchall()
        
        status_dict = {row['status']: row['count'] for row in status_counts}
        
        # Get total counts
        total_thoughts = sum(status_dict.values())
        total_insights = db.conn.execute(
            "SELECT COUNT(*) FROM insights"
        ).fetchone()[0]
        
    return jsonify({
        'total_thoughts': total_thoughts,
        'processing': status_dict.get('processing', 0),
        'completed': status_dict.get('completed', 0),
        'queued': status_dict.get('queued', 0),
        'failed': status_dict.get('failed', 0),
        'insights': total_insights
    })

@app.route('/api/active_thoughts')
def get_active_thoughts():
    """Get currently active (queued or processing) thoughts"""
    with db.conn:
        rows = db.conn.execute("""
            SELECT id, type, content, status, created_at, priority
            FROM thoughts
            WHERE status IN ('queued', 'processing')
            ORDER BY priority DESC, created_at ASC
            LIMIT 20
        """).fetchall()
        
    thoughts = []
    for row in rows:
        thoughts.append({
            'id': row['id'],
            'type': row['type'],
            'content': row['content'],
            'status': row['status'],
            'priority': row['priority'],
            'created_at': datetime.fromtimestamp(row['created_at']).isoformat()
        })
        
    return jsonify({'active_thoughts': thoughts})

@app.route('/api/recent_insights')
def get_recent_insights():
    """Get recent high-value insights"""
    insights = db.get_recent_insights(hours=24, limit=10)
    
    formatted_insights = []
    for insight in insights:
        formatted_insights.append({
            'thought_id': insight['thought_id'],
            'insight': insight['insight'],
            'significance': float(insight['significance']),
            'created_at': datetime.fromtimestamp(insight['created_at']).isoformat()
        })
        
    return jsonify({'recent_insights': formatted_insights})

@app.route('/api/completed_thoughts/<int:limit>')
def get_completed_thoughts(limit=10):
    """Get recently completed thoughts"""
    with db.conn:
        rows = db.conn.execute("""
            SELECT id, type, content, status, created_at, completed_at, result
            FROM thoughts
            WHERE status = 'completed'
            ORDER BY completed_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        
    thoughts = []
    for row in rows:
        result = json.loads(row['result']) if row['result'] else {}
        thoughts.append({
            'id': row['id'],
            'type': row['type'],
            'content': row['content'][:200] + '...' if len(row['content']) > 200 else row['content'],
            'created_at': datetime.fromtimestamp(row['created_at']).isoformat(),
            'completed_at': datetime.fromtimestamp(row['completed_at']).isoformat(),
            'has_insights': len(result.get('insights', [])) > 0,
            'model_used': result.get('model', 'unknown')
        })
        
    return jsonify({'completed_thoughts': thoughts})

@app.route('/api/thought/<thought_id>')
def get_thought_detail(thought_id):
    """Get detailed information about a specific thought"""
    thought = db.get_thought(thought_id)
    
    if not thought:
        return jsonify({'error': 'Thought not found'}), 404
        
    return jsonify({
        'id': thought.id,
        'type': thought.type,
        'content': thought.content,
        'context': thought.context,
        'status': thought.status,
        'priority': thought.priority,
        'created_at': datetime.fromtimestamp(thought.created_at).isoformat(),
        'started_at': datetime.fromtimestamp(thought.started_at).isoformat() if thought.started_at else None,
        'completed_at': datetime.fromtimestamp(thought.completed_at).isoformat() if thought.completed_at else None,
        'result': thought.result,
        'model_used': thought.model_used,
        'iterations': thought.iterations
    })

@app.route('/api/connections/<thought_id>')
def get_thought_connections(thought_id):
    """Get connections for a specific thought"""
    connections = db.find_connections(thought_id)
    return jsonify({'connections': connections})

if __name__ == '__main__':
    print("Starting Subconscious Dashboard API Server...")
    print("Dashboard available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
