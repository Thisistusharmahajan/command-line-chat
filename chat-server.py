from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import threading
import time

class ChatHandler(BaseHTTPRequestHandler):
    """Handles POST requests to /chat endpoint"""
    
    def log_message(self, format, *args):
        """Override to show thread info in logs"""
        thread_name = threading.current_thread().name
        print(f"[{thread_name}] {self.address_string()} - {format % args}")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/chat':
            try:
                # Read request body
                content_length_str = self.headers.get('Content-Length')
                if content_length_str is None:
                    self._send_error(400, "Missing Content-Length header")
                    return
                
                content_length = int(content_length_str)
                post_data = self.rfile.read(content_length)
                
                # Parse JSON body
                try:
                    data = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    self._send_error(400, "Invalid JSON in request body")
                    return
                
                # Get username from request
                username = data.get('username', 'Anonymous')
                message = data.get('message', '')
                
                # Simulate some processing time to demonstrate concurrency
                time.sleep(0.5)
                
                # Build response
                response = {
                    "status": "success",
                    "reply": f"hello {username}",
                    "received_message": message,
                    "thread": threading.current_thread().name,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                self._send_json(200, response)
                
            except Exception as e:
                self._send_error(500, str(e))
        else:
            self._send_error(404, "Endpoint not found. Use POST /chat")
    
    def do_GET(self):
        """Handle GET requests - health check"""
        if self.path == '/':
            self._send_json(200, {
                "service": "Chat Server",
                "status": "running",
                "endpoints": ["POST /chat"],
                "thread_count": threading.active_count()
            })
        else:
            self._send_error(404, "Not found")
    
    def _send_json(self, status_code, data):
        """Send JSON response"""
        response_body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response_body))
        self.end_headers()
        self.wfile.write(response_body)
    
    def _send_error(self, status_code, message):
        """Send error response"""
        self._send_json(status_code, {"status": "error", "message": message})


def run_server(host='0.0.0.0', port=8765):
    """Start the multithreaded chat server"""
    server = ThreadingHTTPServer((host, port), ChatHandler)
    
    print("=" * 60)
    print("🚀 Multithreaded Chat Server Started!")
    print("=" * 60)
    print(f"URL: http://localhost:{port}")
    print(f"Threads: Each request handled in a new thread")
    print("=" * 60)
    print("\nPOST /chat  - Send JSON: {\"username\": \"yourname\", \"message\": \"hello\"}")
    print("GET  /       - Health check")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server shutting down...")
        server.shutdown()


if __name__ == '__main__':
    run_server()