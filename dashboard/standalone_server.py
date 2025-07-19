#!/usr/bin/env python3
"""
Standalone Dashboard Server for Subconscious System
Direct database access without complex imports
"""
from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
from pathlib import Path
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Database path
DB_PATH = Path.home() / ".subconscious" / "thoughts.db"

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Serve the dashboard"""
    dashboard_path = Path(__file__).parent / "index.html"
    with open(dashboard_path, 'r') as f:
        return f.read()

@app.route('/api/status')
def get_status():
    """Get overall system status"""
    conn = get_db_connection()
    try:
        # Get counts by status
        cursor = conn.execute("""
            SELECT status, COUNT(*) as count
            FROM thoughts
            GROUP BY status
        """)
        status_counts = cursor.fetchall()
        
        status_dict = {row['status']: row['count'] for row in status_counts}
        
        total_thoughts = sum(status_dict.values())
        
        cursor = conn.execute("SELECT COUNT(*) FROM insights")
        total_insights = cursor.fetchone()[0]
        
        return jsonify({
            'total_thoughts': total_thoughts,
            'processing': status_dict.get('processing', 0),
            'completed': status_dict.get('completed', 0),
            'queued': status_dict.get('queued', 0),
            'failed': status_dict.get('failed', 0),
            'insights': total_insights
        })
    finally:
        conn.close()

@app.route('/api/active_thoughts')
def get_active_thoughts():
    """Get currently active (queued or processing) thoughts"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            SELECT id, type, content, status, created_at, priority
            FROM thoughts
            WHERE status IN ('queued', 'processing')
            ORDER BY priority DESC, created_at ASC
            LIMIT 20
        """)
        rows = cursor.fetchall()
        
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
    finally:
        conn.close()

@app.route('/api/recent_insights')
def get_recent_insights():
    """Get recent high-value insights"""
    conn = get_db_connection()
    try:
        # Get insights from last 24 hours
        cutoff = datetime.now().timestamp() - (24 * 3600)
        
        cursor = conn.execute("""
            SELECT i.*, t.type as thought_type
            FROM insights i
            JOIN thoughts t ON i.thought_id = t.id
            WHERE i.created_at > ?
            ORDER BY i.significance DESC, i.created_at DESC
            LIMIT 10
        """, (cutoff,))
        
        rows = cursor.fetchall()
        
        insights = []
        for row in rows:
            insights.append({
                'thought_id': row['thought_id'],
                'insight': row['insight'],
                'significance': float(row['significance']) if row['significance'] else 0,
                'created_at': datetime.fromtimestamp(row['created_at']).isoformat()
            })
            
        return jsonify({'recent_insights': insights})
    finally:
        conn.close()

@app.route('/api/completed_thoughts/<int:limit>')
def get_completed_thoughts(limit=10):
    """Get recently completed thoughts"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            SELECT id, type, content, status, created_at, completed_at, result
            FROM thoughts
            WHERE status = 'completed'
            ORDER BY completed_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        
        thoughts = []
        for row in rows:
            result = json.loads(row['result']) if row['result'] else {}
            thoughts.append({
                'id': row['id'],
                'type': row['type'],
                'content': row['content'][:200] + '...' if len(row['content']) > 200 else row['content'],
                'created_at': datetime.fromtimestamp(row['created_at']).isoformat(),
                'completed_at': datetime.fromtimestamp(row['completed_at']).isoformat() if row['completed_at'] else None,
                'has_insights': len(result.get('insights', [])) > 0 if result else False,
                'model_used': result.get('model', 'unknown') if result else 'unknown'
            })
            
        return jsonify({'completed_thoughts': thoughts})
    finally:
        conn.close()

if __name__ == '__main__':
    print("Starting Subconscious Dashboard API Server...")
    print("Dashboard available at: http://localhost:5555")
    app.run(host='0.0.0.0', port=5555, debug=False)
