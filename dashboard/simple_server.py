#!/usr/bin/env python3
"""
Dashboard API Server for Subconscious System (No Flask version)
Provides real-time data to the web dashboard using built-in http.server
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import mimetypes

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from src.subconscious import SubconsciousDB

# Database connection
db = SubconsciousDB(Path.home() / ".subconscious" / "thoughts.db")

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        url = urlparse(self.path)
        
        # Enable CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        
        if url.path == '/':
            # Serve the dashboard HTML
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            dashboard_path = Path(__file__).parent / "index.html"
            with open(dashboard_path, 'rb') as f:
                self.wfile.write(f.read())
                
        elif url.path == '/api/status':
            # Get system status
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            with db.conn:
                status_counts = db.conn.execute("""
                    SELECT status, COUNT(*) as count
                    FROM thoughts
                    GROUP BY status
                """).fetchall()
                
                status_dict = {row['status']: row['count'] for row in status_counts}
                
                total_thoughts = sum(status_dict.values())
                total_insights = db.conn.execute(
                    "SELECT COUNT(*) FROM insights"
                ).fetchone()[0]
                
            response = {
                'total_thoughts': total_thoughts,
                'processing': status_dict.get('processing', 0),
                'completed': status_dict.get('completed', 0),
                'queued': status_dict.get('queued', 0),
                'failed': status_dict.get('failed', 0),
                'insights': total_insights
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        elif url.path == '/api/active_thoughts':
            # Get active thoughts
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
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
                
            self.wfile.write(json.dumps({'active_thoughts': thoughts}).encode())
            
        elif url.path == '/api/recent_insights':
            # Get recent insights
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            insights = db.get_recent_insights(hours=24, limit=10)
            
            formatted_insights = []
            for insight in insights:
                formatted_insights.append({
                    'thought_id': insight['thought_id'],
                    'insight': insight['insight'],
                    'significance': float(insight['significance']),
                    'created_at': datetime.fromtimestamp(insight['created_at']).isoformat()
                })
                
            self.wfile.write(json.dumps({'recent_insights': formatted_insights}).encode())
            
        else:
            # 404 for unknown paths
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def run_server(port=5000):
    """Run the HTTP server"""
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"Starting Subconscious Dashboard Server...")
    print(f"Dashboard available at: http://localhost:{port}")
    print(f"Press Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == '__main__':
    run_server()
